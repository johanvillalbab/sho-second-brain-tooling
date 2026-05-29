---
description: Convene an advisor panel on a decision and record each advisor's verdict
category: vault
triggers_en: ["advisor panel", "ask the advisors", "run a panel", "what would my advisors say"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-panel $ARGUMENTS`:

The argument states the question or situation. Infer which advisors are relevant (from the vault's `Advisors/` folder) unless the user names them.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Read each relevant advisor note in `Advisors/` so each verdict reflects that advisor's stated lens and prior guidance
3. Use the `advisor-panel` template if the vault has one (e.g. `_meta/templates/advisor-panel.md`); otherwise build: a Contexto table, one section per advisor with an independent Veredicto + Razonamiento, a Síntesis y decisión, and a Propagación list
4. Set frontmatter: `type: advisor-panel`, `participants` (advisor wikilinks), `subject`, `trigger` (verbatim quote or event), `verdict` (one-line synthesis). Save under `Advisors/Panels/YYYY-MM-DD - <slug>.md`
5. Propagate: update the affected entity notes (project, person) with the decision, and append an entry to the relevant board (e.g. `Boards/Advisory Board`), today's daily note, and `log.md`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
