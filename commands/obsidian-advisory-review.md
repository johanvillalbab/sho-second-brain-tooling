---
description: Weekly advisory review - synthesize the week's advisor sessions, surface conflicts between recommendations, and set next-week priorities
category: vault
triggers_en: ["advisory review", "weekly advisor panel", "advisor retro", "panel review"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-advisory-review $ARGUMENTS`:

The optional argument names the week (e.g. `semana 1` or a date). Default to the current ISO week. This closes the loop on the week's 1:1 sessions and sets the next week up.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Read `Boards/Advisory Board.md` and every `type: advisor-session` note from the period (look in `Advisors/Sessions/`)
3. Synthesize: what advanced, what is blocked, and which commitments were kept vs dropped (cross-check the minted `type: task` notes)
4. Surface where advisors contradict each other (e.g. Commercial says raise the rate vs Family says protect time). Name the tension explicitly; do not paper over it
5. Optionally convene a short multi-advisor exchange on the single biggest open tension, reusing the panel mechanic (independent verdicts, then a synthesis)
6. Close with the top 3 priorities for next week and a Big 3 style focus contract (this maps to the Personal Coach mandate)
7. Use the `advisory-review` template if the vault has one (e.g. `_meta/templates/advisory-review.md`); otherwise build: Resumen de la semana, Avances, Bloqueos, Conflictos entre advisors, Compromisos (cumplidos / caidos), Top 3 prioridades. Set frontmatter: `type: advisory-review`, `period-start`, `period-end`, `sessions-reviewed` (wikilinks), `commitments-kept`, `commitments-dropped`, `top-priorities`. Save under `Advisors/Reviews/YYYY-MM-DD - semana NN.md`
8. Propagate: update the sprint tracker with the week's outcome, append a one-line entry to today's daily note and `log.md`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
