---
description: Create a launch block (mother-task with an internal checklist) for a course or project launch
category: vault
triggers_en: ["launch block", "course launch task", "mother task", "block with checklist"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-launch-block $ARGUMENTS`:

The argument names the course/launch and the block topic (and optionally the block number). Use this instead of scattering many loose tasks.

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Use the `launch-block` template if the vault has one (e.g. `_meta/templates/launch-block.md`); otherwise build: Objetivo del bloque, Checklist, Notas
3. Set frontmatter: `type: task`, `status`, `priority`, `area`, `course`, `block-number`, and `depends-on` (wikilinks to other blocks this one needs). Title as `<Course> - bloque <N> <topic>`
4. Capture the block's work as an internal checklist (one mother-task), not separate task notes
5. Propagate: link the block from the course/launch project note, add it to the right board, and append a one-line entry to today's daily note and `log.md`. Because each block is a `type: task` note with `depends-on`, it shows up as a node in the Task Graph plugin with dependency arrows

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
