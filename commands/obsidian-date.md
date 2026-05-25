---
description: Add or update an important date (birthday, anniversary, ministry anchor) and push it to life-os
category: vault
triggers_en: ["add date", "important date", "new birthday", "remember this date", "schedule anchor", "obsidian date"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-date $ARGUMENTS`.

The vault is the **source of truth** for important dates (family
birthdays, anniversary, ministry / school / review anchors). life-os
renders them in `/dates`. Updates flow vault -> life-os via
`/obsidian-lifeos-sync`.

## What you do

1. **Read `_CLAUDE.md`** so you know where date notes live in the
   vault (typically `2 Areas/Family/Dates/` or `MOCs/000 Dates.md`).

2. **Parse the event from `$ARGUMENTS`** (or pull from recent
   conversation context if no argument given). You need:
   - `event`: short label, e.g. "Wife's birthday"
   - `date`: ISO `YYYY-MM-DD`
   - `note`: short rationale ("plan 4 weeks ahead", "Trip 3 anchor")
   - `area`: priority area (`family | service | secular | god | self | professional`)
   - `category`: `birthday | ministry | school | review | anniversary | other`
   - `important`: boolean (rendered with emphasis in life-os)
   - `recurrence`: `yearly | once` (defaults `yearly`)

3. **Create or update the note** at the appropriate vault location
   following `references/ai-first-rules.md` -> `type: important-date`.
   Include the `## For future Claude` preamble that explains why this
   date matters and what to do about it (e.g. "buy gift 4 weeks
   ahead", "write yearly poem").

4. **Add wikilinks** for the people / projects / areas the date
   touches: `[[People/Wife]]`, `[[Areas/Family]]`. These keep the
   knowledge graph dense for future-Claude.

5. **Run `/obsidian-lifeos-sync`** scoped to dates:

   ```bash
   python3 -m scripts.sync.lifeos_sync --entities dates
   ```

   The bridge mints a `lifeos-sync-id` UUID on first push and stores
   the numeric `lifeos-id` from life-os back into the note. Re-runs
   are idempotent.

6. **Confirm in `app/dates`** that the date appears with correct
   category icon, area color, and days-until badge.

## Validation life-os will enforce

- `area` must be one of the 6 priority areas
- `category` must be one of: birthday, ministry, school, review,
  anniversary, other
- `recurrence` must be: once, yearly

If the bridge gets a validation error, surface the raw life-os message
to the user so they can fix the frontmatter.

## What this command does NOT do (yet)

- Recurrence is metadata only — life-os does not auto-roll forward to
  next year on its own. The yearly value tells the vault "this is an
  anniversary", but the date stays as written. Update annually if you
  need the year to roll.
- Does not create calendar events. For that, use `/obsidian-schedule`
  to drop a slot on Google Calendar via life-os.

---

**AI-first rule:** the date note MUST follow
`references/ai-first-rules.md`: `## For future Claude` preamble, full
frontmatter, wikilinks, recency markers on any external claim, sources
verbatim. The bridge writes only the sync fields.
