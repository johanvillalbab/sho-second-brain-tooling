---
description: Capture a student 1:1 and roll its learnings into the learnings log
category: vault
triggers_en: ["student 1:1", "log a student meeting", "1on1 notes", "student session"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-1on1 $ARGUMENTS`:

The argument names the student (and optionally the course). Pull what happened from recent conversation.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Use the `student-1on1` template if the vault has one (e.g. `_meta/templates/student-1on1.md`); otherwise build: Qué pasó, Aprendizajes (`ALE-###`), Implicaciones (curso, Demo Day, soporte 1:1, producto), Related
3. Set frontmatter: `type: student-meeting`, `student`, `course`. Link the student and course as `[[wikilinks]]`
4. Mint new `ALE-###` ids continuing the sequence already used in `[[Aprendizajes - reuniones con estudiantes]]` (read it first to find the next number); append the new learnings there with backlinks
5. Propagate: update the course note, the student's person note (Recent Interactions), and any planning note the implications touch (e.g. `[[Planning Q2]]`, `[[My tasks]]`). Append a one-line entry to today's daily note and `log.md`

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
