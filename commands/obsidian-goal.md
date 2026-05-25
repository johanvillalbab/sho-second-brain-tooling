---
description: Set or update one of the 8 intentional goals in the vault and push it to life-os
category: vault
triggers_en: ["new goal", "update goal", "edit goal", "set my goal", "obsidian goal", "intentional goal"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-goal $ARGUMENTS`.

The vault is the **source of truth** for the 8 intentional goals of the
year. life-os just renders them in `/goals` (read-only display for the
human; updates flow vault -> life-os via `/obsidian-lifeos-sync`).

## What you do

1. **Read `_CLAUDE.md`** at the vault root and any existing
   `MOCs/000 Goals.md` (or wherever goal notes live) so you know the
   current 8 goals before editing.

2. **Identify the goal** from `$ARGUMENTS`:
   - If the user named a goal number 1-8, find or create
     `1 Projects/Goals/Goal <n> - <title>.md` (or wherever your goal
     notes live — check `_CLAUDE.md` Structure).
   - If they described the goal by name ("the AI/UX one"), match to
     the existing 8 by `title` / `statement`.
   - Only numbers 1-8 are valid — the 8 metas of the year are fixed.

3. **Apply the changes** to the note's frontmatter:
   - `quarter_status`: `{1: on_track, 2: at_risk, 3: on_track, 4: on_track}`
     where each value is `on_track | at_risk | off_track | completed`.
   - `next_steps`: list of short imperative strings. Additive sync —
     anything new on this list will be POSTed to life-os; existing
     steps are preserved (no edits/deletes yet, that's a later fase).
   - `title`, `statement`, `area`, `emoji` if creating or rephrasing.

4. **AI-first the note** if it's new or you're rewriting:
   - `## For future Claude` preamble explaining why this goal exists,
     who it serves, and the operational definition of "done".
   - Wikilinks to the projects/areas/people the goal touches:
     `[[Projects/Interface School]]`, `[[Areas/Family]]`, etc.
   - Sources where applicable (`(as of YYYY-MM, source.com)`).
   - Confidence levels for any aspirational claim.

5. **Run `/obsidian-lifeos-sync`** scoped to goals so the changes hit
   life-os immediately:

   ```bash
   python3 -m scripts.sync.lifeos_sync --entities goals
   ```

   Surface the JSON summary (counts of `goal_status_updates` and
   `next_steps_added`).

## Field schema

See `references/ai-first-rules.md` -> `type: goal`. Required fields:

- `type: goal`
- `number: 1..8`
- `area: god|self|family|service|professional|secular`
- `title`, `statement`
- `quarter_status: {1..4: on_track|at_risk|off_track|completed}`
- `next_steps: [string, ...]`

The bridge writes back `lifeos-synced` after a successful push.

## What this command does NOT do (yet)

- Cannot create goal #9 or higher. life-os reserves 1-8 (matches the
  hardcoded `DEFAULT_GOALS` seed). To change the set, edit life-os's
  seed and re-migrate.
- Cannot edit or delete an existing `next_step` (additive sync only).
  Edit life-os UI directly and re-run sync to pull, or wait for the
  paired-id refactor in a later fase.
- Does not move goals between numbers (number is the stable key).

---

**AI-first rule:** the goal note MUST keep its `## For future Claude`
preamble, full frontmatter, wikilinks, recency markers, and confidence
levels. The bridge writes only the sync fields (`lifeos-synced`); it
does not edit the note body. See `references/ai-first-rules.md`.
