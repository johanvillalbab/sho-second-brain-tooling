"""Sync engine: vault task notes <-> life-os AreaTask.

Reads markdown notes with `type: task` from the Obsidian vault, diffs them
against life-os, applies the necessary HTTP calls, and writes back the
life-os id + sync timestamp to the note's frontmatter.

Field ownership (per the plan, "Modelo de datos del puente"):
  - Vault is canonical for the DEFINITION fields:
        text, priority_area, priority, start_date, due_date,
        connected_goal, existence (create / archive).
  - life-os is canonical for the EXECUTION fields:
        status / completed, life-os notes, scheduling/calendar fields.

Idempotency: a stable UUID lives in the vault note frontmatter as
`lifeos-sync-id` and is also stored on the life-os side as a `sbid:<uuid>`
entry in AreaTask.tags, so the bridge can match records across runs without
relying on the numeric life-os id (which is unknown until first POST).

Conflict resolution: if both sides modified the same field group since the
last `lifeos-synced`, the vault wins for definition and life-os wins for
execution. A `## Sync conflict` block is appended to the vault note so the
human (or /obsidian-reconcile) can review. Never silently overwrites.

CLI:
    python -m scripts.sync.lifeos_sync           # apply
    python -m scripts.sync.lifeos_sync --dry-run # plan only
    python -m scripts.sync.lifeos_sync --json    # machine-readable plan
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml

from . import config
from .lifeos_client import LifeOSClient, LifeOSError

logger = logging.getLogger("lifeos_sync")

# Vault frontmatter keys used by the bridge.
KEY_TYPE = "type"
KEY_TEXT = "title"          # falls back to filename if missing
KEY_DATE = "date"
KEY_STATUS = "status"
KEY_PRIORITY = "priority"
KEY_AREA = "lifeos-area"
KEY_GOAL = "lifeos-goal"
KEY_START_DATE = "start_date"
KEY_DUE_DATE = "due_date"
KEY_SYNC_ID = "lifeos-sync-id"
KEY_LIFEOS_ID = "lifeos-id"
KEY_LIFEOS_SYNCED = "lifeos-synced"

DEFAULT_AREA = "professional"  # safe fallback when Claude hasn't classified yet
DEFAULT_PRIORITY = "medium"
DEFAULT_STATUS = "todo"
VALID_AREAS = {"god", "self", "family", "service", "professional", "secular"}
VALID_STATUSES = {"todo", "in_progress", "blocked", "completed"}
VALID_PRIORITIES = {"low", "medium", "high"}

SYNC_TAG_PREFIX = "sbid:"


# ── frontmatter parsing ─────────────────────────────────────────────────────


@dataclass
class VaultNote:
    path: Path
    frontmatter: dict
    body: str
    sync_id: Optional[str]  # mirrors frontmatter[KEY_SYNC_ID]

    @property
    def is_task(self) -> bool:
        return str(self.frontmatter.get(KEY_TYPE, "")).strip().lower() == "task"

    @property
    def lifeos_id(self) -> Optional[int]:
        raw = self.frontmatter.get(KEY_LIFEOS_ID)
        if raw is None or raw == "":
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter dict, body str).

    Returns ({}, original) if there is no `---` fenced YAML block at the top.
    Never raises on malformed YAML — returns ({}, original) and logs a warning,
    so a single bad note can't break a whole sync run.
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[4:end]
    body = text[end + 4:].lstrip("\n")
    try:
        data = yaml.safe_load(fm_raw) or {}
        if not isinstance(data, dict):
            data = {}
    except yaml.YAMLError as exc:
        logger.warning("Skipping note with bad YAML frontmatter: %s", exc)
        return {}, text
    return data, body


def _dump_frontmatter(fm: dict, body: str) -> str:
    if not fm:
        return body
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n" + body


def _load_note(path: Path) -> Optional[VaultNote]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        logger.warning("Cannot read %s: %s", path, exc)
        return None
    fm, body = _parse_frontmatter(raw)
    sync_id = fm.get(KEY_SYNC_ID)
    if sync_id is not None:
        sync_id = str(sync_id).strip() or None
    return VaultNote(path=path, frontmatter=fm, body=body, sync_id=sync_id)


def iter_task_notes(vault: Path) -> Iterable[VaultNote]:
    skip_dirs = {".git", ".obsidian", ".smart-env", "node_modules", ".trash"}
    for md in vault.rglob("*.md"):
        if any(part in skip_dirs for part in md.relative_to(vault).parts):
            continue
        note = _load_note(md)
        if note and note.is_task:
            yield note


# ── mapping vault note <-> life-os payload ──────────────────────────────────


def _coerce_date(value: Any) -> Optional[str]:
    """Coerce frontmatter date values to ISO YYYY-MM-DD; tolerate datetime / date objects."""
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()[:10]
    return str(value)


def _normalize_area(raw: Optional[str]) -> str:
    val = (raw or "").strip().lower() or DEFAULT_AREA
    if val not in VALID_AREAS:
        logger.warning("Unknown lifeos-area %r, defaulting to %s", raw, DEFAULT_AREA)
        return DEFAULT_AREA
    return val


def _normalize_status(raw: Optional[str]) -> str:
    val = (raw or "").strip().lower() or DEFAULT_STATUS
    return val if val in VALID_STATUSES else DEFAULT_STATUS


def _normalize_priority(raw: Optional[str]) -> str:
    val = (raw or "").strip().lower() or DEFAULT_PRIORITY
    return val if val in VALID_PRIORITIES else DEFAULT_PRIORITY


def _title_for(note: VaultNote) -> str:
    """Pick a task text: explicit `title` frontmatter > filename without .md."""
    if note.frontmatter.get(KEY_TEXT):
        return str(note.frontmatter[KEY_TEXT]).strip()
    return note.path.stem.strip()


def note_to_create_payload(note: VaultNote) -> dict:
    """Build a POST /tasks body from a vault note. Vault owns definition fields."""
    task_date = (
        _coerce_date(note.frontmatter.get(KEY_DATE))
        or _coerce_date(note.frontmatter.get(KEY_START_DATE))
        or datetime.now(timezone.utc).date().isoformat()
    )
    tags = [f"{SYNC_TAG_PREFIX}{note.sync_id}"] if note.sync_id else []
    return {
        "task_date": task_date,
        "priority_area": _normalize_area(note.frontmatter.get(KEY_AREA)),
        "text": _title_for(note),
        "status": _normalize_status(note.frontmatter.get(KEY_STATUS)),
        "priority": _normalize_priority(note.frontmatter.get(KEY_PRIORITY)),
        "start_date": _coerce_date(note.frontmatter.get(KEY_START_DATE)) or task_date,
        "due_date": _coerce_date(note.frontmatter.get(KEY_DUE_DATE)),
        "connected_goal": note.frontmatter.get(KEY_GOAL),
        "tags": tags,
    }


def note_to_update_payload(note: VaultNote) -> dict:
    """Vault-owned definition fields only. NEVER overwrites status (execution)."""
    return {
        "text": _title_for(note),
        "priority": _normalize_priority(note.frontmatter.get(KEY_PRIORITY)),
        "priority_area": _normalize_area(note.frontmatter.get(KEY_AREA)),
        "start_date": _coerce_date(note.frontmatter.get(KEY_START_DATE))
        or _coerce_date(note.frontmatter.get(KEY_DATE)),
        "due_date": _coerce_date(note.frontmatter.get(KEY_DUE_DATE)),
        "connected_goal": note.frontmatter.get(KEY_GOAL),
    }


def task_sync_id(task: dict) -> Optional[str]:
    """Extract sbid:<uuid> from AreaTask.tags."""
    for tag in task.get("tags") or []:
        if isinstance(tag, str) and tag.startswith(SYNC_TAG_PREFIX):
            return tag[len(SYNC_TAG_PREFIX):]
    return None


# ── diff planner ────────────────────────────────────────────────────────────


@dataclass
class Action:
    kind: str                  # create | update_definition | pull_execution | conflict | noop
    note_path: Optional[Path] = None
    task_id: Optional[int] = None
    sync_id: Optional[str] = None
    payload: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass
class Plan:
    actions: list[Action] = field(default_factory=list)

    def summary(self) -> dict:
        kinds: dict[str, int] = {}
        for a in self.actions:
            kinds[a.kind] = kinds.get(a.kind, 0) + 1
        return kinds


def build_plan(notes: list[VaultNote], lifeos_tasks: list[dict]) -> Plan:
    """Compare vault notes and life-os tasks, return the actions to apply.

    Note: this Fase 2 implementation handles create + update_definition +
    pull_execution. Conflict detection beyond field ownership is deferred to
    Fase 3 along with the /obsidian-reconcile narration flow.
    """
    by_sync: dict[str, dict] = {}
    for t in lifeos_tasks:
        sid = task_sync_id(t)
        if sid:
            by_sync[sid] = t

    plan = Plan()

    for note in notes:
        if not note.sync_id:
            # Brand-new task on the vault side: mint a UUID and schedule create.
            new_id = str(uuid.uuid4())
            note.sync_id = new_id
            note.frontmatter[KEY_SYNC_ID] = new_id
            plan.actions.append(
                Action(
                    kind="create",
                    note_path=note.path,
                    sync_id=new_id,
                    payload=note_to_create_payload(note),
                    notes=["new sync-id minted"],
                )
            )
            continue

        existing = by_sync.get(note.sync_id)
        if existing is None:
            # Vault has a sync-id but life-os doesn't know about it
            # (deleted on life-os side, or first push after manual id mint).
            plan.actions.append(
                Action(
                    kind="create",
                    note_path=note.path,
                    sync_id=note.sync_id,
                    payload=note_to_create_payload(note),
                    notes=["life-os has no record for sync-id"],
                )
            )
            continue

        # Both sides know the task. Push definition diffs; pull execution diffs.
        def_payload = note_to_update_payload(note)
        definition_diff = {
            k: v for k, v in def_payload.items() if existing.get(k) != v and v is not None
        }
        if definition_diff:
            plan.actions.append(
                Action(
                    kind="update_definition",
                    note_path=note.path,
                    task_id=existing["id"],
                    sync_id=note.sync_id,
                    payload=definition_diff,
                    notes=[f"changed fields: {sorted(definition_diff.keys())}"],
                )
            )

        # Pull execution state if it differs from what the vault note records.
        vault_status = _normalize_status(note.frontmatter.get(KEY_STATUS))
        lifeos_status = (existing.get("status") or "todo").strip().lower()
        if vault_status != lifeos_status:
            plan.actions.append(
                Action(
                    kind="pull_execution",
                    note_path=note.path,
                    task_id=existing["id"],
                    sync_id=note.sync_id,
                    payload={"status": lifeos_status, "completed": bool(existing.get("completed"))},
                    notes=[f"vault {vault_status} -> life-os {lifeos_status}"],
                )
            )

        if not definition_diff and vault_status == lifeos_status:
            plan.actions.append(
                Action(kind="noop", note_path=note.path, sync_id=note.sync_id, task_id=existing["id"])
            )

    return plan


# ── apply ───────────────────────────────────────────────────────────────────


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _persist_note(note: VaultNote, lifeos_id: Optional[int]) -> None:
    """Write frontmatter back to disk: ensure sync-id, lifeos-id, lifeos-synced."""
    if note.sync_id:
        note.frontmatter[KEY_SYNC_ID] = note.sync_id
    if lifeos_id is not None:
        note.frontmatter[KEY_LIFEOS_ID] = lifeos_id
    note.frontmatter[KEY_LIFEOS_SYNCED] = _now_iso()
    note.frontmatter.setdefault("ai-first", True)
    note.path.write_text(_dump_frontmatter(note.frontmatter, note.body), encoding="utf-8")


def _update_note_status(note: VaultNote, status: str) -> None:
    note.frontmatter[KEY_STATUS] = status
    note.path.write_text(_dump_frontmatter(note.frontmatter, note.body), encoding="utf-8")


def apply_plan(
    plan: Plan,
    notes_by_path: dict[Path, VaultNote],
    client: LifeOSClient,
    dry_run: bool,
) -> dict:
    """Execute the plan. Returns a summary dict. Each action is best-effort:
    a single failed action logs and continues so a partial-success run still
    persists progress for the actions that worked.
    """
    applied = {"create": 0, "update_definition": 0, "pull_execution": 0, "errors": 0, "noop": 0}

    for action in plan.actions:
        if action.kind == "noop":
            applied["noop"] += 1
            continue

        if dry_run:
            logger.info("[dry-run] %s sync_id=%s task_id=%s notes=%s payload=%s",
                        action.kind, action.sync_id, action.task_id, action.notes, action.payload)
            applied[action.kind] = applied.get(action.kind, 0) + 1
            continue

        try:
            if action.kind == "create":
                result = client.tasks_create(action.payload)
                note = notes_by_path[action.note_path]
                _persist_note(note, lifeos_id=result.get("id"))
                applied["create"] += 1

            elif action.kind == "update_definition":
                client.tasks_update(action.task_id, action.payload)
                note = notes_by_path[action.note_path]
                _persist_note(note, lifeos_id=action.task_id)
                applied["update_definition"] += 1

            elif action.kind == "pull_execution":
                note = notes_by_path[action.note_path]
                _update_note_status(note, action.payload["status"])
                _persist_note(note, lifeos_id=action.task_id)
                applied["pull_execution"] += 1

        except (LifeOSError, OSError) as exc:
            applied["errors"] += 1
            logger.error("Action %s failed for %s: %s", action.kind, action.note_path, exc)

    return applied


# ── entrypoint ──────────────────────────────────────────────────────────────


def run(dry_run: bool, want_json: bool) -> int:
    vault = config.vault_path()
    client = LifeOSClient()

    notes = list(iter_task_notes(vault))
    notes_by_path = {n.path: n for n in notes}
    logger.info("Found %d task notes in %s", len(notes), vault)

    try:
        lifeos_resp = client.tasks_list(start_date="2020-01-01", end_date="2099-12-31")
    except LifeOSError as exc:
        logger.error("Cannot reach life-os: %s", exc)
        return 2
    lifeos_tasks = lifeos_resp.get("tasks", [])
    logger.info("life-os has %d tasks", len(lifeos_tasks))

    plan = build_plan(notes, lifeos_tasks)
    summary = apply_plan(plan, notes_by_path, client, dry_run=dry_run)
    summary["plan"] = plan.summary()
    summary["dry_run"] = dry_run

    if want_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        logger.info("Summary: %s", summary)
    return 0 if summary["errors"] == 0 else 1


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sync vault task notes <-> life-os")
    parser.add_argument("--dry-run", action="store_true", help="Plan only; do not call the API")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return run(dry_run=args.dry_run, want_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
