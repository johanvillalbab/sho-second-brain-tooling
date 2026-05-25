---
description: Read Google Calendar via life-os — show today's events, this week's events, or a custom range
category: vault
triggers_en: ["agenda", "show my calendar", "what's on my calendar", "today's events", "this week's events", "obsidian agenda"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-agenda $ARGUMENTS`.

The vault talks to Google Calendar **through life-os** (no Google
credentials live in the skill — life-os holds the OAuth refresh token
and proxies all requests). This command is read-only.

## What you do

1. **Parse the time window from `$ARGUMENTS`:**
   - "today" / no arguments  -> start of today, 24h window
   - "this week"              -> Monday 00:00 -> Sunday 23:59
   - "tomorrow"               -> tomorrow 00:00, 24h window
   - "next 3 days", "3 days"  -> today, 72h window
   - explicit dates "may 28"  -> parse and use that day

2. **Confirm life-os calendar is wired:**

   ```bash
   python3 -m scripts.sync.calendar_cli status
   ```

   If `{"configured": false}` is returned, tell the user the calendar
   bridge is not connected and point them to life-os's
   `/api/calendar/setup` to complete the OAuth flow. Do not try to
   recover; that's outside the skill's scope.

3. **Fetch events:**

   ```bash
   python3 -m scripts.sync.calendar_cli events \
       --start 2026-05-25T00:00:00-05:00 \
       --end   2026-05-25T23:59:59-05:00
   ```

   Use the timezone in `_CLAUDE.md` (typically `America/Bogota`,
   `-05:00`).

4. **Present a concise human-readable summary** of the events,
   ordered chronologically:
   - Time range (e.g. `09:00 - 10:30`)
   - Title
   - Location if present
   - "(focus block)" tag for events with `lifeOsTaskId` extended
     property (those are auto-scheduled work blocks)

5. **If the user asked for a snapshot in the daily note**, escribe el
   bloque `## Calendar (snapshot)` per `/obsidian-daily` instructions —
   do not invent ad-hoc formats.

## What this command does NOT do

- Does not create or modify events. For that use `/obsidian-schedule`
  or `/obsidian-focus-day`.
- Does not show the OAuth flow URL itself — life-os owns that surface.

---

**AI-first rule:** if you persist any calendar data to the vault (e.g.
in `/obsidian-daily`'s snapshot block), include the recency marker
`(as of <ISO timestamp>)` and link the original event URL verbatim
when present. See `references/ai-first-rules.md`.
