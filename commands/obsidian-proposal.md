---
description: Draft a B2B commercial proposal and keep the opportunity tracker in sync
category: vault
triggers_en: ["new proposal", "draft proposal", "quote for client", "commercial proposal"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-proposal $ARGUMENTS`:

The argument names the client/opportunity (and optionally the pax count and price). Pull missing detail from recent conversation or the linked meeting note.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Use the `proposal` template if the vault has one (e.g. `_meta/templates/proposal.md`); otherwise build the same 8-section structure: Contexto, El programa, Qué incluye, Resultados esperados, Por qué Interface School, Inversión, Próximos pasos, Riesgo operativo y precondiciones
3. Set frontmatter: `type: proposal`, `status` (draft to start), `client`, `contact`, `pax`, `price`, `currency`, `valid-until`, `related-projects`. Link the client company and contact as `[[wikilinks]]`
4. Create or update the matching `type: opportunity` tracker note (one per deal): add this proposal to its `proposals` list, set `stage`, and record the pipeline row with today's date
5. Propagate: link the proposal from the client project note, the contact's note, and add or move a card on the relevant sales/board. Append a one-line entry to today's daily note and `log.md`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
