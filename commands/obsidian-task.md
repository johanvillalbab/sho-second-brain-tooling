---
description: Add a task to the right kanban board with inferred priority and due date
category: vault
triggers_en: ["add task", "new todo", "track this", "remind me"]
---

Use the obsidian-second-brain skill. Execute `/obsidian-task $ARGUMENTS`:

1. Read `_CLAUDE.md` first if it exists in the vault root
2. Parse the task from the argument, or pull from recent conversation context if no argument given
3. Infer: priority (🔴/🟡/🟢), due date, linked project, linked person, `area` (life area; suggested set: god, self, family, service, professional, secular), and any `depends-on` tasks the task mentions
4. Search for the right kanban board - use `_CLAUDE.md` board list or search `Boards/`
5. Add the task card to the correct column (`📋 This Week` or `📥 Backlog` depending on due date)
6. Always create a task note in `Tasks/` with the full task frontmatter, including `area` and `depends-on` (as `[[wikilinks]]` to other task notes) when applicable. Every task is a first-class note so it becomes a node in the Task Graph plugin.
7. Link the task from the relevant project note and today's daily note

---

**AI-first rule:** Every note created or updated by this command MUST follow `references/ai-first-rules.md` - `## For future Claude` preamble, rich frontmatter (`type`, `date`, `tags`, `ai-first: true`, plus type-specific fields), recency markers per external claim, mandatory `[[wikilinks]]` for every person/project/concept referenced, sources preserved verbatim with URLs inline, and confidence levels where applicable. The vault is for future-Claude retrieval - not human reading.
