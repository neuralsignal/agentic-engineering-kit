---
description: Planning, requirements clarification, and question-asking protocol for all agent tasks
alwaysApply: true
---

# Planning Protocol

Detailed guidance for task assessment, requirements clarification, and collaborative planning. See the Planning and Discovery section in `CONSTITUTION.md` for the foundational principles and the Task Lifecycle for the overall workflow.

## Task Complexity Assessment

Before starting any task, classify it to determine the appropriate level of planning:

| Level | Characteristics | Planning Required |
|-------|----------------|-------------------|
| **Trivial** | Single-file, well-defined, no ambiguity (fix a typo, rename a variable, add a config value) | None. Proceed directly to execution. |
| **Moderate** | Multi-file or requires design choices, but scope is clear (add a new endpoint, refactor a module, write tests for existing code) | Brief plan: state what you will do, in what order, and how you will verify. Share with user if the task involves trade-offs. |
| **Complex** | Ambiguous scope, multiple valid approaches, architectural impact, or cross-cutting concerns (new feature, system integration, data pipeline, migration) | Full planning cycle: clarify requirements, present options, get approval, produce a written plan, share it, and get confirmation before executing. |

When uncertain about classification, default to the next higher level. Over-planning wastes some time; under-planning wastes more.

## How to Ask Questions

### Structure

- Ask **specific, bounded questions** with concrete options. Not "What do you want?" but "I see three approaches: A (fast, less flexible), B (moderate effort, extensible), C (most robust, highest effort). Which fits your needs?"
- When presenting options, include **trade-offs** for each: effort, complexity, maintainability, performance, or scope implications.
- Use **numbered lists or tables** for multi-option questions so the user can respond concisely ("option 2" or "A and C").
- For yes/no clarifications, state the assumption you will make if the user does not respond, so they can correct it.

### Batching

- **Batch independent questions** into a single message. Do not ask one question, wait, ask another, wait again. If you have four questions that do not depend on each other's answers, ask all four at once.
- **Sequence dependent questions** only when the answer to one determines whether the next is relevant. If question 2 only matters when question 1's answer is "yes," ask question 1 first.

### Tone

- Be direct. Do not pad questions with caveats or apologies.
- Do not ask questions the user has already answered in the current conversation.
- Do not ask questions you can answer yourself by reading the codebase, docs, or config.

## Scope Validation

Before executing non-trivial work, state your understanding to the user:

1. **What you will do** -- the specific changes, in order.
2. **What you will NOT do** -- explicitly exclude adjacent work that might be expected but is out of scope.
3. **Success criteria** -- how you and the user will know the task is done.
4. **Assumptions** -- anything you are taking as given that could be wrong.

Wait for confirmation before proceeding. If the user corrects your understanding, update and re-confirm.

## When to Re-plan

Revisit the plan with the user when any of these occur during execution:

- The task turns out to be significantly more complex than initially assessed.
- You discover information that invalidates a key assumption in the plan.
- A planned approach fails and an alternative path is needed.
- The scope needs to expand beyond what was agreed.
- You have been stuck on the same step for 3 or more attempts.

Do not silently change course. Report what changed and get confirmation for the revised approach.

## Anti-patterns

Avoid these planning failures:

- **Hoping for the best** -- Proceeding with a vague brief and assuming things will work out. They will not.
- **Drip-feed questions** -- Asking one question at a time when several independent questions could be batched. This wastes round-trips and slows the user down.
- **Redundant questions** -- Asking something the user already answered earlier in the conversation. Re-read the conversation before asking.
- **Analysis paralysis** -- Planning so extensively that nothing gets built. If planning exceeds ~20% of estimated execution time, start building and let implementation inform the plan.
- **Immutable plans** -- Treating the plan as sacred once written. Plans are hypotheses; update them when evidence changes.
- **Invisible planning** -- Planning in your head without sharing. The user cannot validate what they cannot see.
- **Premature execution** -- Starting implementation before scope and success criteria are clear, then having to redo work when assumptions turn out to be wrong.
