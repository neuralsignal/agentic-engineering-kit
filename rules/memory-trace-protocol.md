---
description: When and how to write session memory traces for cross-session continuity
alwaysApply: true
---

# Memory Trace Protocol

After completing non-trivial work in a session, append a memory trace to `memory.md` at the project root. Files are the source of truth; context that isn't written is lost.

## When to Write a Trace

Write a memory trace after sessions that involve:

- **Architectural decisions** — a design choice with lasting impact
- **Significant feature work** — a milestone or phase of work on a goal
- **Key interactions** — a meeting, conversation, or review that produced insights
- **Discoveries** — something unexpected learned that future sessions should know
- **Configuration changes** — changes to agents, rules, skills, or workspace structure

## When NOT to Write

Skip the trace for:

- Trivial single-line fixes (typos, renaming, small tweaks)
- Pure read/research sessions with no decisions or output
- Work already fully captured in updated task status or commit messages

## Format

Append a new entry to `memory.md` at the project root. Create the file if it does not exist. Each entry is a level-2 heading with a date and short description:

```markdown
## YYYY-MM-DD -- Short description

**Type:** session | decision | insight | discovery
**Trigger:** what initiated this (user request, scheduled task, bug report)

Summary of what happened (1-3 sentences).

### Decisions
- Decision 1 and its rationale
- Decision 2 and its rationale

### Context for future sessions
- Key fact future agents need to know
- Assumption that could change
```

### Field guidance

- **Type**: categorize the entry so future sessions can filter by relevance
- **Trigger**: explain what started the work -- this helps future sessions understand whether similar triggers should lead to similar actions
- **Decisions**: one line per key decision, with enough rationale that a future session can understand *why*, not just *what*
- **Context**: facts, constraints, or risks that are not captured elsewhere and that a future session would need to know

### Optional subsections

Add these when relevant:

- `### Agents involved` -- if multiple agents collaborated
- `### Related files` -- key files changed, with brief notes on what changed
- `### Open questions` -- unresolved issues flagged for future sessions

## Principles

- **Append-only** -- Never edit or delete existing entries. Memory is a log, not a living document.
- **Concise** -- Each entry should be readable in under 30 seconds. Link to detailed docs rather than duplicating them.
- **Searchable** -- Use specific terms in summaries and decisions that a future agent could search for (project names, technology names, pattern names).
- **Honest** -- Record what was actually done and what was not done. Do not omit failures or partial results.

## Integration with Task Lifecycle

Memory traces are written after the Verify step and before ending the session. They capture what the verify step and the commit history do not: the reasoning, trade-offs, and context behind the changes.
