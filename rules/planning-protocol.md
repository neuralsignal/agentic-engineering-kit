---
description: Planning, requirements clarification, and question-asking protocol for all agent tasks
alwaysApply: true
---

# Planning Protocol

Foundations live in `CONSTITUTION.md` (the Agentic Workflow section; its Task Lifecycle governs the
overall workflow). This rule covers how much planning a task warrants and how to ask for what you
are missing.

## Task complexity

| Level | Characteristics | Planning required |
|-------|----------------|-------------------|
| **Trivial** | Single-file, well-defined, no ambiguity (fix a typo, rename a variable, add a config value) | None. Proceed directly to execution. |
| **Moderate** | Multi-file or requires design choices, but scope is clear (add an endpoint, refactor a module, write tests for existing code) | Brief plan: what you will do, in what order, how you will verify. Share it if the task involves trade-offs. |
| **Complex** | Ambiguous scope, several valid approaches, architectural impact, or cross-cutting concerns (new feature, integration, data pipeline, migration) | Full cycle: clarify requirements, present options, get approval, produce a written plan, confirm before executing. |

**Question discipline.** Never ask what you can answer yourself by reading the codebase, docs, or
config — look first, ask second. Batch independent questions into one message; sequence them only
when one answer decides whether the next is relevant. Never re-ask something already answered
earlier in the conversation. Present options with their trade-offs, numbered so the user can reply
"option 2". For yes/no clarifications, state the assumption you will make absent an answer, so the
user can correct it instead of confirming it.

**Scope validation.** Before non-trivial work, state four things and wait for confirmation:
what you will do (the specific changes, in order); what you will NOT do (explicitly exclude
adjacent work that might be expected); success criteria (how both sides know it is done);
assumptions (anything taken as given that could be wrong). Corrected? Update and re-confirm.

**When to re-plan.** Stop and revisit with the user when, mid-execution: the task is materially
more complex than assessed; a key assumption is invalidated; a planned approach fails and an
alternative is needed; scope must expand beyond what was agreed; you have been stuck on the same
step 3+ times. Never change course silently — report what changed and get confirmation.

**Calibration.** Uncertain how much planning a task warrants → default to the next level up;
over-planning wastes some time, under-planning wastes more. Exception: planning exceeding ~20% of
estimated execution time → start building and let implementation inform the plan.

**Anti-patterns.** Proceeding on a vague brief and hoping. Drip-feeding one question at a time.
Re-asking what was already answered. Planning in your head without sharing it — the user cannot
validate what they cannot see. Treating a written plan as immutable once evidence contradicts it.
