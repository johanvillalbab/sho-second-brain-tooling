---
description: Create an event operations note with pre, day-of, and post checklists
category: vault
triggers_en: ["event ops", "plan an event", "event checklist", "luma event"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-event $ARGUMENTS`:

The argument names the event (and optionally the date and platform). Pull detail from recent conversation or the registration link.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Use the `event-ops` template if the vault has one (e.g. `_meta/templates/event-ops.md`); otherwise build: Resumen, Checklist (pre), Día D, Post, Related
3. Set frontmatter: `type: event`, `event-date`, `platform`, `registered`, `venue`, `status` (planning to start)
4. Link the event playbook if one exists (e.g. `[[Luma - engagement y operación de eventos]]`) so the checklist reflects prior lessons
5. Propagate: create or link a `type: task` for the day-of ops, add it to the right board, and append a one-line entry to today's daily note and `log.md`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
