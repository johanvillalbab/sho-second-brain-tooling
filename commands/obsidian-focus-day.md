---
description: Auto-schedule today's Big 3 + high-priority tasks into Google Calendar focus blocks
category: vault
triggers_en: ["focus day", "auto schedule", "schedule my day", "plan my day", "obsidian focus day"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-focus-day $ARGUMENTS`.

Calls life-os's existing `schedule_focus_blocks` engine (which mirrors
the user's Ideal Week) to drop the day's priority tasks into free
calendar slots as 90/60-minute focus blocks. life-os is the auto-
scheduler; this command is the thin trigger.

## What you do

1. **Resolve the target date** from `$ARGUMENTS`:
   - no args  -> today
   - "today"  -> today
   - "tomorrow" -> tomorrow
   - explicit `YYYY-MM-DD`

   Format as `YYYY-MM-DD`.

2. **Always run dry-run first** so the user sees the plan before
   anything hits Google Calendar:

   ```bash
   python3 -m scripts.sync.calendar_cli schedule-day \
       --date 2026-05-26 --scope big3_high --dry-run
   ```

   The response shows scheduled blocks, overflow tasks (no slot found),
   and remaining availability.

3. **Summarize the plan in plain language** to the user:
   - "Mañana: 3 bloques agendados — Deep Work 9:00-10:30 (Big 3 #1),
     People sync 11:00-12:00, Closing 14:00-15:30. 1 tarea quedó en
     overflow porque no había slot suficiente."

4. **If the user confirms**, re-run without `--dry-run`:

   ```bash
   python3 -m scripts.sync.calendar_cli schedule-day \
       --date 2026-05-26 --scope big3_high
   ```

5. **After scheduling**, suggest running `/obsidian-lifeos-sync` to
   pull the new `scheduled_start/end` + `google_event_id` back into
   the corresponding vault task notes (so the daily note's
   `## Calendar (snapshot)` reflects the agenda).

## Scope flags

- `big3_high` (default): the day's Big 3 plus any task with `priority: high`
- `big3`: only the Big 3
- `selected`: pass `--task-ids 12 34 56` to schedule a specific set

## What this command does NOT do

- Does not re-arrange already-scheduled events. life-os respects
  existing busy windows when finding slots; it will not move what's
  already in your calendar.
- Does not create tasks. If the day has no Big 3 / high-priority
  tasks, the dry-run will return an empty plan — that's the signal to
  add tasks via `/obsidian-task` first.
- Does not work weekends — `focus_planner.py` returns overflow for
  Sat/Sun because the Ideal Week has no slots configured there. That
  is intentional (sacred rest).

---

**AI-first rule:** if you want the agenda preserved in the vault for
future-Claude, follow up with `/obsidian-daily` so the day's note
gets the `## Calendar (snapshot)` block with recency markers.
