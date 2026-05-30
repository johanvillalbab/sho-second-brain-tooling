---
description: Hold a 1:1 advisor session - the advisor brings a Second-Brain-derived agenda, coaches, and leaves tracked commitments
category: vault
triggers_en: ["advisor 1on1", "session with my advisor", "meet with advisor", "advisor check-in"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-advisor $ARGUMENTS`:

The argument names the advisor (fuzzy-match against the vault's `Advisors/` folder) plus an optional topic. If no advisor is named, propose the one whose session is due today from the current sprint tracker (`Advisors/<YYYY-MM> Advisor Sprint.md`) or the calendar. This is a live, interactive session: you role-play the advisor, you do not just write a note.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Load `Advisors/<Name>.md` and internalize the advisor's `voice`, `expertise`, `frameworks`, `biases`, and `when-to-consult`. Read `Boards/Advisory Board.md` for that advisor's mandate and anchor projects
3. Build the agenda context (this is the core): read the advisor's anchor projects (status, recent activity), open `type: task` notes in the advisor's `area`/domain, the last ~7 daily notes and `log.md` for progress signals, and the most recent prior `type: advisor-session` for this same advisor to carry forward open commitments
4. Open the session by presenting a 3 to 5 point agenda derived from that context, in the advisor's voice. Lead with accountability: name what was committed in the prior session and ask what happened before moving on
5. Conduct the conversation interactively and in character: coaching, challenge, disruptive ideas, motivation. Stay inside the advisor's lens and respect the board's scope limits (no licensed legal, medical, tax, or clinical advice; refer to the professional named in `Boards/Advisory Board.md`)
6. On close, use the `advisor-session` template if the vault has one (e.g. `_meta/templates/advisor-session.md`); otherwise build: Agenda, Conversacion (key points), Consejo clave (with confidence `stated | high | medium | speculation`), Decisiones, Compromisos (action items with due dates). Set frontmatter: `type: advisor-session`, `advisor` (wikilink), `domain`, `session` (nth this sprint), `agenda`, `commitments`, `prev-session` (backlink to last session), `related-projects`. Save under `Advisors/Sessions/YYYY-MM-DD - <Advisor> - <slug>.md`
7. Propagate: mint or update a `type: task` note per commitment (`area`, `related-projects`, `due`); append the session to a `## Historial de sesiones` section in the advisor note; update the sprint tracker; append a one-line entry to today's daily note and `log.md`. If a real decision emerged, suggest `/obsidian-decide` or `/obsidian-panel`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
