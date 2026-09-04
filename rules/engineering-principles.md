---
description: Non-negotiable engineering principles for all workspace code
alwaysApply: true
---

# Engineering Principles

Quick-reference subset. See `CONSTITUTION.md` at the workspace root for the full engineering constitution.

Non-negotiable. Violating these is a bug. If you see a violation, call it out, stop, and suggest a fix.

**Intent-First (governs everything).** The hierarchy of truth is intent/goals → docs → code → tests. Align code to the documented goals, never the reverse. Each package carries `INTENT.md` + `CONTRACTS.md` (root), ADRs in `docs/decisions/`, and `PLAN.md`/`TASKS.md` per initiative — written before code and tracked in repo markdown. A session may overwrite a package's intent; that triggers a rigorous overhaul, not a patch.

- **KISS** -- One tool per job. No fallback chains. If a library exists, use it. No clever abstractions, no premature generalization.
- **YAGNI** -- No capability, config key, flag, abstraction, or code path without a concrete current use. If nothing calls it today, it doesn't exist today.
- **DRY -- one source of truth for contracts and policy.** Schemas, contracts, and policies are defined exactly once; two copies that must stay in sync is a defect. Prefer a little duplication over forcing the wrong abstraction.
- **No Default Arguments** -- Zero defaults in signatures, constructors, or CLI args. Every value comes from config or the caller; a missing one crashes -- that's correct. Sole exception: a parameter may default to `None` only when passing nothing is genuinely meaningful AND it is internal (not a config concern, invisible to users). The moment a user should know about it, no default -- `None` is passed explicitly.
- **Fail Fast and Loud** -- No silent swallowing. No try-except-pass. No graceful degradation. Errors propagate with full context. Missing config = crash with a clear message. Domain rules may exclude data; engineering failures must never look like success.
- **Everything From Config** -- config files are the single source of truth for all runtime values (intervals, paths, scopes, flags, thresholds, model/provider names). Code reads config; it never invents values. A module-level `TIMEOUT = 120` is a violation.
- **Idempotency** -- every script and operation is re-runnable without extra side effects.
- **Observability / Traceability** -- work leaves a durable trace: logs, telemetry, in-repo markdown progress. Untraceable work is unfinished.
- **Determinism / Reproducibility** -- a run reproduces from its recorded inputs: pinned deps, fixed seeds, logged params and data versions.
- **Explicit over Implicit** -- no magic, no hidden state, no inferred ownership or attribution. State assumptions; never silently fill an unknown with something "reasonable."
- **Modular and Independent** -- each module is standalone; enable/disable/schedule independently. No god objects, no shared mutable state. Business logic stays language/SDK/vendor-agnostic; provider-specific code lives in thin adapters at the edges. Pure core, side-effects at the boundary.
- **Align to intent, not code (no backwards compatibility by default)** -- refactor liberally to match the documented goals. Don't preserve old formats, signatures, or call-sites unless explicitly told to. Confirm the backwards-compat expectation at session start; never assume it. (Once a package is declared deployed AND in active use, contract changes need a migration path + ADR + stop-and-ask.)
- **Package Manager** -- pick one per project and never mix two. Prefer a conda-style manager (pixi) for heavy data-analytics / ML code; prefer a pure-Python resolver (uv) for deploy-shaped services and where upstream-template parity matters. Respect the manager a project already uses.
- **No sys.path Manipulation** -- Never `sys.path.append()` or `sys.path.insert()`. Shared code lives in a shared packages directory and is installed as a local editable dependency in each consumer's project config. Project-internal imports use proper package structure with `pyproject.toml`. Packages never import from skills. Import hacks rot silently and break the moment directory structure changes.
- **Descriptive Package Names** -- Python package directories (the ones listed in `pyproject.toml` `packages` and used in `import` statements) must have project-specific names. Never use generic names like `src`, `lib`, `utils`, or `core` -- they collide across editable installs and make imports ambiguous. Use snake_case names that identify the project (e.g., `data_pipeline`). Note: non-installable project subdirectories like `scripts/` or `tests/` are fine.
- **Development order & testing** -- Sequence: intent & contracts → SDK/language specifics + plan → core code → tests. Tests follow the code (often a separate session with subagents) and must pass before done. Prefer `hypothesis` (Python) or `fast-check` (TypeScript) property-based tests for pure functions (transformers, parsers, serializers, validators); `pytest` for integration and smoke. No bare `assert` + `print` -- if pytest cannot discover it, it is not a test.

Scope: all code in this workspace, across all projects.
