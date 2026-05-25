---
description: Create or update today's daily note — pulls calendar events, overdue tasks, and conversation context
category: vault
triggers_en: ["todays note", "create todays daily", "open daily", "today daily note"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-daily`:

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Read `CRITICAL_FACTS.md` for timezone

3. Check if `wiki/daily/YYYY-MM-DD.md` exists for today
   - If not: read `templates/Daily Note.md`, fill in date fields, create the file
   - If yes: update existing note (inject, don't overwrite)

4. Pull calendar events via life-os (preferred — no separate Google
   credentials needed in the skill; life-os owns the OAuth refresh
   token and proxies the request):

   ```bash
   python3 -m scripts.sync.calendar_cli events \
       --start <today>T00:00:00-05:00 \
       --end   <today>T23:59:59-05:00
   ```

   Then write a `## Calendar (snapshot)` section to the daily note
   (AI-first per `references/ai-first-rules.md`):
   - One line per event in chronological order
   - Format: `HH:MM-HH:MM — Title (location if any) [link]`
     where `[link]` is the verbatim `htmlLink` from the response
   - Append a recency marker at the section header:
     `## Calendar (snapshot as of <ISO timestamp>)`
   - For meetings with known people in the title, add a `[[People/X]]`
     wikilink alongside the line so the knowledge graph stays dense
   - "(focus block)" tag for events with `lifeOsTaskId` extended
     property — those are auto-scheduled work blocks from
     `/obsidian-focus-day`

   Fallback: if `calendar_cli status` reports `configured: false` or
   the call errors, skip the section silently (don't insert empty
   block, don't error out). Log a one-line note in the daily that the
   calendar bridge was unreachable so future-Claude can tell snapshot
   absence from "no events".

   Legacy: if a direct Google Calendar MCP tool is available in this
   surface (no life-os bridge configured), prefer the MCP tool. Both
   write the same `## Calendar (snapshot)` section.

5. Pull overdue and due-today tasks from kanban boards:
   - Scan `boards/` for items with `@{date}` that match today or are past due
   - Add to the daily note's Focus section with priority markers

6. Scan the current conversation for anything relevant to today:
   - Tasks in progress, people mentioned, decisions made, what's being worked on
   - Pre-fill or update the note's sections with that context

7. Check `log.md` for last night's sleeptime consolidation:
   - If the nightly agent ran, summarize what it did (reconciled, synthesized, healed)
   - Add a brief "Overnight changes" note so the user knows what happened while they slept

8. Return the path of the daily note when done.

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` — `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval — not human reading.
