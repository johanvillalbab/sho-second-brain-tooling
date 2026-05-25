---
description: Schedule a slot on Google Calendar via life-os — either a free block or a slot for an existing task
category: vault
triggers_en: ["schedule", "block time", "agenda esto", "schedule a slot", "schedule task", "obsidian schedule"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-schedule $ARGUMENTS`.

Two modes depending on `$ARGUMENTS`:

1. **Schedule an existing task** — the user references a task that's
   already synced to life-os ("schedule the X task for tomorrow 9am").
2. **Schedule a free block** — the user describes a slot without
   tying it to a task ("90min deep work tomorrow 9am").

life-os holds the Google OAuth; the skill only proxies. This command
writes to your calendar — be conservative and confirm before
committing big changes.

## What you do

1. **Read `_CLAUDE.md`** so you know the user's Ideal Week
   (`_meta/references/04_IDEAL_WEEK.md`-style content) and prefer
   slots that respect it.

2. **Parse `$ARGUMENTS`** to extract:
   - The task reference (note title, lifeos-id) OR free-block label
   - Start datetime (timezone-aware; default user tz is `America/Bogota`)
   - Duration (default 60 min for free blocks; 90 min for big3-style
     deep-work blocks)

3. **Check existing events** in the target window first to avoid
   double-booking:

   ```bash
   python3 -m scripts.sync.calendar_cli events \
       --start <day_start> --end <day_end>
   ```

   If the proposed slot overlaps a busy event, surface the conflict
   and suggest an alternative.

4. **Mode A — schedule an existing task**: find the task's
   `lifeos-id` in the vault note's frontmatter (or call sync first to
   create it). Then:

   ```bash
   python3 -m scripts.sync.calendar_cli schedule-task \
       --task-id <id> \
       --start 2026-05-26T09:00:00-05:00 \
       --end   2026-05-26T10:30:00-05:00
   ```

   Add `--dry-run` first if the user wants a preview.

5. **Mode B — schedule a free block** (no task association):

   ```bash
   python3 -m scripts.sync.calendar_cli create-event \
       --title "Deep work" \
       --start 2026-05-26T09:00:00-05:00 \
       --end   2026-05-26T10:30:00-05:00
   ```

6. **Confirm with the user** the resulting event id + link (returned
   in the JSON response). If you scheduled a task, the vault note
   gains `google-event-id` and `scheduled_start/end` after the next
   `/obsidian-lifeos-sync` (life-os writes those fields on AreaTask;
   the pull-back picks them up).

## Defaults / heuristics

- Timezone: `America/Bogota` (`-05:00`) unless the user says otherwise.
- Duration: 60 min for a generic block, 90 min for "deep work" /
  "focus" / big3-style language, 30 min for "meeting" / "sync".
- Buffer: respect a 10-minute gap before/after existing events when
  proposing alternatives.

## What this command does NOT do

- Does not auto-schedule the whole day — that's `/obsidian-focus-day`.
- Does not reschedule existing events. To move an event, delete it via
  `/obsidian-schedule unschedule` (or life-os UI) and create a new one.
- Does not create the underlying task. If you are scheduling something
  that doesn't exist in life-os yet, run `/obsidian-task` first, then
  `/obsidian-lifeos-sync`, then this command.

---

**AI-first rule:** if you create the event from a vault task note,
make sure the note has a `## For future Claude` preamble explaining
the why behind the block (so future-Claude reading the vault can
reconstruct the intent without seeing Google Calendar).
