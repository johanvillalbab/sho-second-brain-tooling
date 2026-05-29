# AI-First Note Rules

The vault is designed for **future-Claude** to read and reason over, not for human review. The owner rarely opens notes directly - they call Claude to retrieve, synthesize, and connect dots across years of accumulated knowledge. **Every command that writes to the vault must produce notes that follow these rules.**

This document is the canonical specification. It lives at `references/ai-first-rules.md` in the obsidian-second-brain repo and is referenced from `_CLAUDE.md` Section 0, every slash command, and `references/write-rules.md`.

---

## The 7 Rules

### 1. Self-contained context
Each note must explain itself. Future-Claude may pull this single note via `/obsidian-find` or vault scan with no surrounding context. Don't rely on backlinks alone for meaning. State the *what*, the *why*, and the *when* inside the note itself.

### 2. "For future Claude" preamble
Every note begins with a 2–3 sentence summary in plain English under a `## For future Claude` header (immediately after the frontmatter). Future-Claude reads this to decide relevance in 10 seconds before parsing the rest. State what's in the note, why it was saved, and any temporal/staleness caveat.

```markdown
## For future Claude
This note is a [type] about [topic] saved on [date]. It [main purpose].
[Optional caveat about staleness, confidence, or scope.]
```

### 3. Rich, consistent frontmatter
Filterable metadata. Different note types have different schemas (see below) but every note has machine-readable frontmatter.

**Universal fields (every note):**
```yaml
---
date: YYYY-MM-DD              # creation or update date
type: <note-type>             # see Type Schemas below
tags: [...]                   # always include the type as a tag
ai-first: true                # explicit flag
---
```

### 4. Recency markers per claim
When stating external facts, attach the date inline:

```markdown
- Mem0 raised $24M Series A (as of 2026-04, mem0.ai/blog/series-a)
- Anthropic released native memory tool (as of 2026-02, anthropic.com/news/memory)
```

So future-Claude knows what to verify before trusting individual facts.

### 5. Sources preserved verbatim
Every external claim has its source URL inline. Don't paraphrase a citation - keep the actual URL so the claim can be re-verified or refreshed years later.

### 6. Cross-links are mandatory
Every person, project, idea, decision, or concept referenced uses `[[wikilinks]]` so the graph is traversable by future-Claude:

```markdown
Sarah at [[People/Sarah Chen]] decided to ship the [[Projects/Dashboard Refactor]] by Friday.
```

If a linked note doesn't exist, create a stub (per `references/write-rules.md` § Stub Notes).

### 7. Confidence levels
Where applicable, mark claims with confidence:
- `stated` - directly quoted or claimed by a source
- `high` - multiple sources agree
- `medium` - single source, plausible
- `speculation` - your inference

Use this in frontmatter (`confidence: high`) or inline (`(confidence: speculation)`).

---

## Type Schemas

Frontmatter schemas by note type. **Add fields specific to your type - never remove the universal fields.**

### `type: daily`
```yaml
date: YYYY-MM-DD
type: daily
tags: [daily]
mood: ""        # optional
energy: ""      # optional
ai-first: true
```

### `type: project`
```yaml
date: YYYY-MM-DD              # creation
updated: YYYY-MM-DD           # last meaningful update
type: project
status: active                # active | planning | completed | archived | on-hold
tags: [project, ...]
related-people: ["[[People/...]]", ...]
related-projects: ["[[Projects/...]]", ...]
ai-first: true
```

### `type: person`
```yaml
date: YYYY-MM-DD              # first interaction logged
updated: YYYY-MM-DD
type: person
tags: [person, ...]
role: ""
company: "[[Companies/...]]"
relationship: weak | medium | strong
last-interaction: YYYY-MM-DD
related-projects: ["[[Projects/...]]", ...]
ai-first: true
```

### `type: idea`
```yaml
date: YYYY-MM-DD
type: idea
tags: [idea, ...]
status: captured              # captured | exploring | graduated | shelved
related-projects: ["[[Projects/...]]", ...]
ai-first: true
```

### `type: task`
```yaml
date: YYYY-MM-DD
type: task
status: in-progress           # in-progress | done | waiting | cancelled
priority: 🔴 | 🟡 | 🟢
area: professional            # life area, free-form. Suggested set:
                              # god | self | family | service | professional | secular
due: YYYY-MM-DD
tags: [task, ...]
related-projects: ["[[Projects/...]]", ...]
related-people: ["[[People/...]]", ...]
depends-on: ["[[Tasks/...]]", ...]   # tasks this one depends on (directed edges)
ai-first: true
```

`area` groups the task into a life area. It is free-form, but the suggested set above
keeps the grouping stable across notes. `depends-on` lists other task notes this task is
blocked by, as `[[wikilinks]]` per Rule 6. Both fields feed the companion Task Graph
plugin, which renders tasks as floating cards clustered by `area`, connected by shared
project/person, and linked by `depends-on` arrows.

### `type: decision`
Decisions usually live INSIDE project notes' Key Decisions sections. When a standalone decision note is needed:
```yaml
date: YYYY-MM-DD
type: decision
tags: [decision, ...]
related-projects: ["[[Projects/...]]", ...]
confidence: stated | high | medium | speculation
sources: [...]                # inline URLs/wikilinks supporting the decision
ai-first: true
```

### `type: devlog` / `type: log`
```yaml
date: YYYY-MM-DD
type: devlog
tags: [devlog, ...]
project: "[[Projects/...]]"
related-people: ["[[People/...]]", ...]
ai-first: true
```

### `type: review`
```yaml
date: YYYY-MM-DD              # the date the review was generated
period-start: YYYY-MM-DD
period-end: YYYY-MM-DD
type: review                  # weekly | monthly
tags: [review, ...]
ai-first: true
```

### `type: agenda-snapshot`
Point-in-time snapshot of the user's Google Calendar, written by `/obsidian-agenda`. The calendar is the source of truth; the note is a re-derivable view. Default path: `wiki/agenda/YYYY-MM-DD — <range-label>.md`.
```yaml
date: YYYY-MM-DD              # date the snapshot was generated
type: agenda-snapshot
range: "YYYY-MM-DD..YYYY-MM-DD"
range-label: today | tomorrow | week | next-week | day | range
calendar-source: google-calendar
calendars: [primary]          # list of calendar IDs included
fetched-at: "YYYY-MM-DDTHH:MM:SS±HH:MM"   # ISO 8601 with offset — the recency anchor
event-count: <integer>
conflict-count: <integer>
superseded-at: "YYYY-MM-DDTHH:MM:SS±HH:MM"   # only when refreshing an older snapshot
tags: [agenda, calendar]
ai-first: true
```

### `type: meeting`
Vault record of a specific meeting, written by `/obsidian-meeting` from a Google Calendar event. The calendar event remains authoritative for time and attendees; this note is authoritative for what was said, decided, and acted on. Default path: `wiki/meetings/YYYY-MM-DD — <slug>.md`.
```yaml
date: YYYY-MM-DD              # event's start date in user's TZ
type: meeting
event-id: <google-event-id>
event-url: <htmlLink>
conference-url: <hangoutLink>     # optional, only if present
start: "YYYY-MM-DDTHH:MM:SS±HH:MM"
end: "YYYY-MM-DDTHH:MM:SS±HH:MM"
duration-min: <integer>
location: ""                      # verbatim from event; empty string if none
organizer: "<email>"
attendees: ["[[Person Name]]", ...]
recurrence: "<recurringEventId>"  # optional, only if recurring
linked-task: "[[wiki/tasks/...]]" # optional, when a scheduled task spawned this meeting
related-projects: ["[[Projects/...]]", ...]
calendar-source: google-calendar
tags: [meeting]                   # add `prep` tag when the meeting hasn't happened yet
ai-first: true
```

### `type: research` / `type: research-deep` / `type: x-read` / `type: x-pulse` / `type: youtube`
See `commands/research*.md` and `commands/x-*.md` and `commands/youtube.md` for the full schemas. All set `ai-first: true` and follow the universal rules.

### `type: adr`
```yaml
date: YYYY-MM-DD
type: adr
tags: [adr, decision]
decision: ""                  # one-line summary
status: proposed | accepted | superseded
related-projects: ["[[Projects/...]]", ...]
supersedes: "[[Knowledge/ADR-...]]"   # optional
ai-first: true
```

### `type: synthesis` / `type: emerge` / `type: connect` / `type: challenge`
Outputs from thinking tools. Each saves to `Knowledge/` or `Ideas/` with:
```yaml
date: YYYY-MM-DD
type: <thinking-tool-type>
tags: [research, thinking, ...]
sources: [...]                # vault notes that informed this
related-people: [...]
related-projects: [...]
ai-first: true
```

### `type: proposal`
Written by `/obsidian-proposal`. A commercial proposal for a client.
```yaml
date: YYYY-MM-DD
updated: YYYY-MM-DD
type: proposal
status: draft                 # draft | sent | negotiating | won | lost
client: "[[Companies/...]]"
contact: "[[People/...]]"
pax: ""                       # number or range
price: ""
currency: COP
valid-until: YYYY-MM-DD
sent-date: YYYY-MM-DD          # set when status -> sent
related-projects: ["[[Projects/...]]", ...]
tags: [proposal, b2b]
ai-first: true
```

### `type: opportunity`
Written by `/obsidian-proposal`. The deal tracker; one per opportunity, links its proposals.
```yaml
date: YYYY-MM-DD
updated: YYYY-MM-DD
type: opportunity
company: "[[Companies/...]]"
contact: "[[People/...]]"
stage: lead                   # lead | scoping | proposed | negotiating | won | lost
pax: ""
price-range: ""
currency: COP
next-step: ""
next-step-date: YYYY-MM-DD
proposals: ["[[...]]", ...]
related-people: ["[[People/...]]", ...]
tags: [opportunity, b2b, pipeline]
ai-first: true
```

### `type: advisor-panel`
Written by `/obsidian-panel`. A panel of advisor verdicts on one decision.
```yaml
date: YYYY-MM-DD
type: advisor-panel
participants: ["[[Advisors/...]]", ...]
subject: ""
trigger: ""                   # verbatim quote or event that prompted the panel
verdict: ""                   # one-line synthesized verdict
tags: [advisors, panel, ...]
ai-first: true
```

### `type: student-meeting`
Written by `/obsidian-1on1`. A student 1:1 whose learnings roll up to the learnings log.
```yaml
date: YYYY-MM-DD
type: student-meeting
student: "[[People/...]]"
course: "[[Projects/...]]"
tags: [student, 1on1, ...]
ai-first: true
```

### `type: event`
Written by `/obsidian-event`. Operations note for an event (pre / day-of / post).
```yaml
date: YYYY-MM-DD
type: event
event-date: YYYY-MM-DD
platform: ""                  # e.g. luma
registered: 0
venue: ""
status: planning              # planning | confirmed | done
tags: [event, ops]
ai-first: true
```

### `type: recurring-task`
Written by `/obsidian-recurring`. A recurring obligation with a cadence and next due date.
```yaml
date: YYYY-MM-DD
type: recurring-task
status: active                # active | paused | done-this-cycle
cadence: ""                   # e.g. "monthly day 20" | "first days of month"
owner: "[[People/...]]"
blocker: ""                   # "[[...]]" if a person/vendor gates it
next-due: YYYY-MM-DD
amount: ""                    # optional, for payments/invoices
tags: [recurring-task, admin]
ai-first: true
```

Launch blocks created by `/obsidian-launch-block` use `type: task` (see above) with
`course`, `block-number`, and `depends-on`, plus an internal checklist in the body.

---

## Preamble Templates by Type

### Daily note
```markdown
## For future Claude
Daily note for YYYY-MM-DD. Captures what was worked on, who was met, decisions made, and energy/mood for the day. Skim the section headers; specific work logs link to dev logs and project notes.
```

### Project note
```markdown
## For future Claude
[Project name] is a [type — work / personal / open-source] project with status [status] as of [date]. The Overview section explains what it is and why it exists. Recent Activity captures the last 30 days. Key Decisions documents major directional choices with rationale.
```

### Person note
```markdown
## For future Claude
[Name] is [role] at [[Company]]. Relationship strength: [weak/medium/strong] as of [date]. Last interaction: [date]. The Recent Interactions section logs every conversation chronologically.
```

### Idea note
```markdown
## For future Claude
Idea captured on [date] about [topic]. Status: [captured/exploring/graduated/shelved]. The body explains the idea, why it's interesting, and what would make it real. If shelved, the reason is documented at the bottom.
```

### Decision (standalone)
```markdown
## For future Claude
Decision made on [date] about [topic]. Context section explains what prompted it. Options Considered lists the alternatives evaluated. Rationale captures why this option won. Consequences documents what changed in the vault as a result.
```

### Dev log
```markdown
## For future Claude
Dev log for [date] about [project]. Captures work done, problems encountered, decisions made, and next steps. Specific file paths and commit hashes are preserved verbatim for re-verification.
```

### Review (weekly / monthly)
```markdown
## For future Claude
[Weekly / Monthly] review covering [period-start] through [period-end]. The review summarizes shipped work, decisions made, people met, and patterns that emerged. Use this as a baseline when researching what was true at the end of the period.
```

### Research (any research type)
```markdown
## For future Claude
[Research type] on "[topic]" performed on [datetime]. [Specific scope: what was searched, how many sources, what model.] [Caveat about recency or confidence.] Use the recency markers per claim to know what to verify before relying on individual facts.
```

### ADR
```markdown
## For future Claude
Architectural decision record from [date]. Documents a structural decision in the vault (folder rename, schema change, etc.) so future-Claude can answer "why is the vault structured this way?" without re-deriving the reasoning.
```

### Agenda snapshot
```markdown
## For future Claude
Point-in-time snapshot of the user's Google Calendar for [range], generated on [fetched-at]. Google Calendar is the source of truth — this note is a re-derivable view. To refresh, re-run `/obsidian-agenda [range-label]`. The `fetched-at` timestamp in frontmatter is the recency anchor; treat individual event details as stale beyond that point.
```

### Meeting
```markdown
## For future Claude
Vault record of a meeting on [date] with [attendees]. The calendar event ([event-url]) remains the source of truth for time and attendees; this note is the source of truth for what was discussed, decided, and committed to. The Notes / Decisions / Action items sections are filled by the human or by `/obsidian-save` from conversation context — not speculation.
```

---

## Common Anti-Patterns

Don't do these. They produce notes that are useless to future-Claude.

| Anti-pattern | Why it's bad |
|---|---|
| `date: today` | Use the actual `YYYY-MM-DD` - "today" is meaningless when read later |
| Bare claims without dates | "Mem0 is the leader" - leader as of when? |
| External URL omitted | "According to a study, X is true" - which study? |
| Plain text names instead of `[[wikilinks]]` | Breaks the link graph - future-Claude can't traverse |
| "See above" / "as mentioned" | Future-Claude may pull this note in isolation. Repeat the context. |
| Trusting the model to infer | Be explicit. State the type, the rule applied, the source. |
| Multi-paragraph human-readable narratives | Bullets and structure beat prose for retrieval. |
| Forgetting `ai-first: true` | The flag lets future-Claude know which notes meet the standard. |

---

## Audit Checklist

When auditing an existing note (Phase 2 work or one-off cleanup), verify:

- [ ] Has `## For future Claude` preamble below frontmatter
- [ ] `ai-first: true` in frontmatter
- [ ] `type:` field set correctly
- [ ] `date:` in YYYY-MM-DD format
- [ ] Tags include the type
- [ ] All people/projects/concepts use `[[wikilinks]]`
- [ ] External claims have recency markers AND source URLs
- [ ] If multi-source, confidence levels marked
- [ ] No "see above" or context-dependent references
- [ ] Self-contained - readable with zero context

---

## Migration Note

This rule was established 2026-04-25 and shipped as part of obsidian-second-brain v0.5.0 (Research Toolkit). All 5 research commands (`/x-read`, `/x-pulse`, `/research`, `/research-deep`, `/youtube`) follow it from day one. The 26 existing `/obsidian-*` commands were updated in v0.6.0 (Phase 2) to explicitly reference this document. Notes written before that may not yet meet the standard - `/obsidian-health` flags them.
