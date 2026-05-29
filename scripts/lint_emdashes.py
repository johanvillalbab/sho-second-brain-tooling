#!/usr/bin/env python3
"""Lint (and optionally fix) em-dashes in user-facing markdown prose.

CLAUDE.md forbids em-dashes (U+2014) in prose. This enforces that rule while
deliberately NOT touching contexts where an em-dash may be intentional:

  - fenced code blocks (``` or ~~~)
  - inline code spans (text between backticks) -- this protects documented vault
    filename conventions like `YYYY-MM-DD — slug.md`
  - generated output (the dist/ tree is gitignored, so git ls-files skips it)

Usage:
  python3 scripts/lint_emdashes.py                 # check tracked *.md, exit 1 if any found
  python3 scripts/lint_emdashes.py --fix           # rewrite prose em-dashes to "-"
  python3 scripts/lint_emdashes.py [files...]      # check only the given files
  python3 scripts/lint_emdashes.py --fix [files...]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EM_DASH = "—"
FENCE_PREFIXES = ("```", "~~~")


def _prose_segments(line: str):
    """Yield (text, is_code) chunks, splitting a line on backtick code spans.

    Even-indexed backtick-delimited chunks are prose; odd-indexed are inline code.
    """
    parts = line.split("`")
    for i, part in enumerate(parts):
        yield part, (i % 2 == 1)


def scan_text(text: str):
    """Return a list of (lineno, line) where an em-dash appears in prose."""
    hits = []
    in_fence = False
    for n, line in enumerate(text.split("\n"), start=1):
        stripped = line.lstrip()
        if stripped.startswith(FENCE_PREFIXES):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for chunk, is_code in _prose_segments(line):
            if not is_code and EM_DASH in chunk:
                hits.append((n, line))
                break
    return hits


def fix_text(text: str):
    """Replace em-dashes with "-" in prose only. Returns (new_text, count)."""
    out = []
    in_fence = False
    count = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(FENCE_PREFIXES):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        rebuilt = []
        for chunk, is_code in _prose_segments(line):
            if not is_code:
                count += chunk.count(EM_DASH)
                chunk = chunk.replace(EM_DASH, "-")
            rebuilt.append(chunk)
        out.append("`".join(rebuilt))
    return "\n".join(out), count


def tracked_markdown() -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    res = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [root / line for line in res.stdout.splitlines() if line]


def main(argv: list[str]) -> int:
    fix = "--fix" in argv
    files = [Path(a) for a in argv if not a.startswith("--")]
    if not files:
        files = tracked_markdown()

    total = 0
    touched = 0
    offenders = []
    for path in files:
        if not path.exists() or path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if fix:
            new_text, n = fix_text(text)
            if n:
                path.write_text(new_text, encoding="utf-8")
                touched += 1
                total += n
                print(f"  fixed {n:>3}  {path}")
        else:
            hits = scan_text(text)
            if hits:
                total += len(hits)
                for lineno, _line in hits:
                    offenders.append(f"{path}:{lineno}")

    if fix:
        print(f"\nFixed {total} em-dash(es) across {touched} file(s).")
        return 0

    if total:
        print("Em-dashes found in prose (use a regular dash or restructure):")
        for o in offenders:
            print(f"  {o}")
        print(f"\n{total} occurrence(s). Run: python3 scripts/lint_emdashes.py --fix")
        return 1
    print("No em-dashes in prose. Clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
