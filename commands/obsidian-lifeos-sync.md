---
description: Sync vault task notes to and from life-os (tasks-os front + calendar bridge)
category: vault
triggers_en: ["sync lifeos", "sync tasks", "push tasks to lifeos", "pull tasks from lifeos", "sync life os"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-lifeos-sync $ARGUMENTS`.

This command keeps the vault (source of truth) and life-os (task tracking
front + Google Calendar bridge) in sync. Tasks move both ways — the vault
owns the definition, life-os owns the execution state.

## What you do

1. **Read `_CLAUDE.md`** at the vault root first so your project/area
   taxonomy is fresh in mind. You need it to classify priority areas
   correctly when a task note is missing `lifeos-area`.

2. **Run the sync in dry-run mode and capture the plan:**

   ```bash
   python3 -m scripts.sync.lifeos_sync --dry-run --json
   ```

   This prints a JSON summary like:

   ```json
   {
     "create": 2,
     "update_definition": 1,
     "pull_execution": 0,
     "noop": 5,
     "errors": 0,
     "plan": { "create": 2, "update_definition": 1, "noop": 5 },
     "dry_run": true
   }
   ```

   Re-run with `--verbose` to see the full per-action detail (sync_id,
   payload, notes) for any actions that need human judgment.

3. **Classify priority areas for any `create` actions whose payload uses
   the default `professional`.** For each such note:
   - Read the note. Look at `related-projects`, the folder path
     (`1 Projects/Interface School/...` -> usually `professional`;
     `2 Areas/Family/...` -> `family`; etc.), and the body text.
   - If the default `professional` is wrong, edit the note's frontmatter
     to add `lifeos-area: <god|self|family|service|professional|secular>`.
   - Optionally add `lifeos-goal: <1-8>` to link to one of the 8 metas.
   - Do NOT touch `lifeos-sync-id`, `lifeos-id`, or `lifeos-synced` —
     those are bridge-owned.

4. **Narrate conflicts** if the plan lists any. (Fase 2 detects only
   field-level differences and resolves them by ownership; explicit
   conflict markers come in Fase 3. For now, just summarize what
   changed where.)

5. **Apply the sync for real:**

   ```bash
   python3 -m scripts.sync.lifeos_sync
   ```

   The script writes `lifeos-id` and `lifeos-synced` back to each note's
   frontmatter so the next run is incremental.

6. **Report a one-paragraph summary to the user** with counts (created /
   updated / pulled / noop / errors) and a short list of which tasks
   moved and why.

## Environment

The script reads from `~/.config/sho-brain/secrets.env` (preferred) or
`~/.config/obsidian-second-brain/.env`:

- `LIFEOS_BASE_URL` — e.g. `https://sho.johanvillalba.com` or `http://127.0.0.1:8000`
- `LIFEOS_SERVICE_TOKEN` — matches `SYNC_SERVICE_TOKEN` in life-os `.env`
- `OBSIDIAN_VAULT_PATH` — defaults to `~/Documents/Sho`

If any required var is missing the script exits with a clear message
pointing to the config files. Surface that to the user verbatim.

## When to run

- On demand when you have just edited or created several task notes.
- Automatically once a night via `~/Documents/Sho/_meta/scripts/codex-daily.sh`
  (wired by Fase 4 of the bridge plan).

## What this command does NOT do (yet)

- Kanban-board cards (the `Boards/` or `My tasks.md`-style files) are
  not parsed; only `type: task` notes round-trip. Coming in a later fase.
- Goals and important dates have their own commands
  (`/obsidian-goal`, `/obsidian-date`) shipped in Fase 3.
- Calendar lecture/escritura: `/obsidian-agenda`, `/obsidian-schedule`,
  `/obsidian-focus-day` (Fase 3).

---

**AI-first rule:** every note this command touches MUST keep the
non-negotiable contract from `references/ai-first-rules.md` — the
`## For future Claude` preamble, rich frontmatter, recency markers,
mandatory `[[wikilinks]]` for people/projects, sources verbatim with
URLs, and confidence levels where applicable. Sync fields (`lifeos-*`,
`google-event-id`) sit alongside the regular task frontmatter; never
let the sync delete or reformat the rest.
