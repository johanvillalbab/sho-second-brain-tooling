---
description: Track a recurring obligation (payment, filing, ops) with cadence and next due date
category: vault
triggers_en: ["recurring task", "monthly obligation", "remind me every month", "recurring payment"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-recurring $ARGUMENTS`:

The argument states the obligation and its cadence (e.g. "pay social benefits, monthly day 20"). Pull blocker/owner detail from conversation.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Use the `recurring-obligation` template if the vault has one (e.g. `_meta/templates/recurring-obligation.md`); otherwise build: Qué, Cadencia, Bloqueantes, Historial
3. Set frontmatter: `type: recurring-task`, `cadence`, `owner`, `blocker` (wikilink if a person/vendor gates it), `next-due` (compute the next occurrence from today and the cadence), `amount` if it is a payment
4. Add a card for the next occurrence to the right board so it surfaces before `next-due`
5. Propagate: link from the relevant project/finance note, and append a one-line entry to today's daily note and `log.md`. On each completion, append a Historial row and advance `next-due`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
