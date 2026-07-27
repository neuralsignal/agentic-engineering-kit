# Engineering Constitution

These are steering constraints: rules that require judgment to uphold. Toolchain-enforceable rules (formatting, import order, type errors) belong in tool configs, not here. The hard rules below are stated as absolutes — a deviation is a bug, not a style choice. Audit periodically: when a linter rule comes to cover a constitutional rule, remove the redundancy.

---

## Intent-First — The Governing Principle

This precedes everything else. When any rule below conflicts with it, this wins.

**The hierarchy of truth is: intent and goals → documentation → code → tests.** Code serves the documented intent; the intent never bends to fit existing code. A package is *what it is meant to do*, written down — not the sum of what its code currently does.

- **Align to goals, not to code.** When the code diverges from the documented intent, the code is wrong. Overhaul it to match the intent. This is of supreme importance.
- **Backwards compatibility is not desired by default.** Do not preserve old formats, signatures, or call sites to spare the existing code. At the start of every new session or plan, **ask whether backwards compatibility is required** — never assume it is. (Once a package is production-gated, see Change Safety §11, the answer changes.)
- **Intent is overwritable.** A session may be asked to change a package's stated goals. That is legitimate. When it happens, treat it rigorously: rewrite the intent docs first, then overhaul the code to match — do not patch around the old intent.
- **Write intent down before writing code.** The agnostic intent (goals, scope, non-goals, principles, data contracts) is authored and aligned across all docs *before* implementation, and reviewed *before* any change.

### Canonical artifacts

Every package or project carries these. They are named, not optional.

| Artifact | Location | Holds |
|----------|----------|-------|
| `INTENT.md` | package root | Agnostic goal, scope, non-goals, principles. The source of truth. Mirrors the production-gate status. |
| `CONTRACTS.md` | package root | Data contracts, public interfaces, invariants. Language-agnostic. Freely overhaul-able unless production-gated. |
| `CLAUDE.md` | package root | Repo-specific agent instructions. **Declares the production gate** (deployed AND in active use). |
| `docs/decisions/NNNN-kebab.md` | `docs/decisions/` | ADRs — one per architectural decision. Status · Context · Decision. |
| `docs/<initiative>/PLAN.md` | per initiative | Language/SDK-specific design and plan. |
| `docs/<initiative>/TASKS.md` | per initiative | Task and progress tracking (ID · owner · status · deps · gate). |

### Development order

Every change follows this sequence, and every change leaves a written trace in repo markdown — no exceptions, however small:

1. **Intent & contracts** — agnostic goals, principles, data contracts. Authored/aligned first.
2. **Specifics & plan** — the SDK/language/package detail, plus `PLAN.md` and `TASKS.md`.
3. **Core code.**
4. **Tests** — property-based by preference; usually written in a separate session, often with subagents.

When you hit a problem at any step, stop and ask the user, and follow the intent docs that state the explicit end state. Do not improvise away from the documented goal.

---

## 1. Supreme Principles

Violating any of these is a bug. Stop and fix before proceeding.

- **KISS** — One tool per job. No fallback chains. If a library exists, use it. No clever abstractions, no premature generalization. Do not add abstraction until duplication or change pressure clearly demands it.
- **YAGNI** — No capabilities, config keys, feature flags, abstractions, or code paths without a concrete, current use case. Speculative "future-proof" code is a liability. If nothing calls it today, it does not exist today.
- **DRY — one source of truth for contracts and policy.** Schemas, contracts, policies, and reusable transformations are defined exactly once. Two copies that must stay in sync is a defect — redesign until one place is authoritative. This applies hardest to *meaning*: do not tolerate two definitions of the same contract. It does not mandate collapsing every superficially-similar block — prefer a little duplication over forcing the wrong abstraction.
- **No Default Arguments** — Zero default values in function signatures, constructors, or CLI args. Every value comes from config or the caller; a missing value crashes, and that is correct. The single exception: a parameter may default to `None` only when (a) passing nothing is genuinely meaningful, AND (b) it is internal — not a configuration concern and not something a user needs to know about. The moment a user should know about it, there is no default — `None` is passed explicitly.
- **Fail Fast and Loud** — No silent swallowing, no catch-and-ignore, no graceful degradation. Errors propagate with full context. Missing config crashes with a clear message. A bad response is logged with exactly what went wrong, then stops. Domain rules may intentionally exclude data; engineering failures must never masquerade as success.
- **Everything From Config** — Configuration files are the single source of truth for all runtime values: intervals, paths, scopes, flags, API settings, thresholds, model names, provider names. Code reads config; code never invents values. A module-level `TIMEOUT = 120` is a violation.
- **Idempotency** — Every script and operation is re-runnable without additional side effects. Interrupted and restarted, the result equals a single clean run.
- **Observability / Traceability** — Work leaves a durable trace. Operations log what they did; pipelines emit telemetry; multi-step work tracks its progress in repo markdown. Untraceable work is unfinished work.
- **Determinism / Reproducibility** — A run reproduces from its recorded inputs: pinned dependencies, fixed seeds, logged parameters and data versions. If a result cannot be reproduced from its trace, it does not count.
- **Explicit over Implicit** — No magic, no hidden state, no inferred ownership or attribution. State assumptions; surface them in code and in reports. Where a value, owner, or decision is unknown, say so — never quietly fill it with something "reasonable."

---

## 2. Architecture and Design

- **Modularity** — Each module is standalone with a single responsibility, understandable without reading everything around it. Enable, disable, and schedule independently. No god objects, no shared mutable state. New capabilities arrive as new modules or clearly bounded extensions, not as accreting special cases. A module too big to hold in your head is too big — split it.
- **Agnostic core, adapters at the edges** — Business logic stays language-, SDK-, and vendor-agnostic. Provider-specific code (Databricks, Microsoft Graph, Azure, a given LLM API) lives only in thin adapter layers at the boundary. Swapping a provider touches an adapter, not the core.
- **Pure core, side-effects at the boundary** — Keep the core pure and property-testable. Push I/O, network, and other side effects to the edges where they are easy to fake and isolate.
- **Composition over inheritance** — Compose behavior from small parts rather than deep inheritance hierarchies.
- **Explicit interfaces** — Define clear contracts between modules. Do not rely on implicit state or side effects.
- **Inward dependency direction** — Concrete implementations depend on shared contracts, interfaces, and config — never on other concrete implementations. No cross-subsystem coupling where one integration imports another's internals.
- **Flat hierarchies** — Avoid nesting containers inside containers. Deep nesting signals unclear boundaries.
- **Thin wrappers** — CLI entry points parse args, validate, and set exit codes. Business logic lives in library modules; scripts import it, never duplicate it.
- **Descriptive names** — Importable package directories, modules, and public symbols have project-specific, self-documenting names. Never `src`, `lib`, `utils`, or `core` as an importable package name — they collide across editable installs.
- **Real packaging, no import hacks** — Use real package and module boundaries. Never modify import paths at runtime. Shared code is installed as a proper package.
- **Contracts are overhaul-able by default** — Data contracts and public interfaces may be rewritten freely to serve the intent, *unless* the package is production-gated (§11). They are not versioned defensively before then.

---

## 3. Error Handling

- Every catch block logs, re-raises, or takes a corrective action. Never catch-and-ignore.
- Error messages state what failed, with what input, and what the caller should do.
- Distinguish recoverable errors (retry, surface to user) from fatal ones (crash immediately).
- Never return `null`/`None` to signal failure when an exception is the correct mechanism.
- Use custom exception classes. Do not catch bare `Exception`.
- ML and data systems are especially prone to silent failure: stale tables, feature drift, and coverage changes produce reasonable-looking but wrong outputs. Apply defensive checks on freshness, schema shape, and value distributions — do not rely on the model to surface data problems.

---

## 4. Configuration and Portability

- All runtime values live in config files, not code.
- Environment variables are read via explicit access (`os.environ["VAR"]` / `process.env.VAR`), never with fallback defaults. Missing variable = crash at startup naming the variable.
- No hardcoded absolute or user-specific paths in tracked files. Workspace root is derived from script location at runtime; relative config paths resolve against the config file's directory, not process CWD.
- Generated files (IDE settings, build caches) are gitignored.
- **Respect the project's package manager; never mix two in one project.** Use the manager a project already uses. (Stack-specific guidance — e.g. pixi vs uv — lives in the language section and per-repo rules.)

---

## 5. Dependencies

- **Prefer maintained libraries over hand-rolling** — if an established library solves the problem, use it. Do not add a library where the standard library suffices.
- **Evaluate before adding** against: active maintenance, healthy community, compatible license (prefer MIT/Apache-2.0/BSD; avoid GPL/AGPL unless authorized), reasonable size, transitive weight, security posture, and runtime fit. These are judgment factors, not numeric gates.
- **Pin versions and commit lock files.** Stable libs (≥1.0): `>=current, <next-major`. Pre-1.0: `>=current, <next-minor`. This is absolute.
- **Dependency direction** — Packages never import from scripts or application modules. Application code imports from packages. No circular dependencies.
- **Audit before upgrading** — Check changelogs for breaking changes before bumping. Do not opportunistically upgrade or swap dependencies as cleanup.

---

## 6. Security and Privacy

- Validate all external input at system boundaries. Sanitize outputs to prevent injection.
- Never log secrets, tokens, passwords, or PII. Mask sensitive values in error messages.
- Least privilege: request only the scopes and access the task needs.
- Never embed credentials in source. Secrets live in environment variables or secret managers.
- Keep secrets, sensitive identifiers, and real sensitive data out of prompts, fixtures, screenshots, docs, and commits unless explicitly required and approved. Prefer synthetic or pseudonymized data in examples, tests, and fixtures by default.
- Security and privacy are first-class constraints, not polish tasks.

---

## 7. Testing and Verification

- **Property-based first** — Use property-based testing (Hypothesis, fast-check) for pure functions: transformers, parsers, serializers, validators — anything with a crisp invariant. Pair with example-based tests; do not treat them as substitutes. Prefer reproducible seeds when debugging generated failures.
- **Tests follow the code, often in a separate session** — Per the development order, tests are written after the core code, frequently in a dedicated session with subagents. They must exist and pass before a change is done.
- **No hardcoded test data** — Assertions derive expected values from inputs, not magic numbers. Exception: well-known constants (π, HTTP status codes).
- **Test isolation** — No dependence on execution order, shared mutable state, or external services. Use fixtures, fakes, or in-memory backends.
- **Validate data, not just logic** — Test pipelines with schema checks, null/cardinality assertions, and distribution sanity checks. Confirm inputs conform to documented assumptions before processing.
- **Verify by change type** — Start with the narrowest check that proves the change. Dependency changes need deterministic install, manifest/lockfile review, and verification in the intended runtime. Interface, schema, and generated-artifact changes need downstream-consumer or regeneration checks. Then run the broader relevant suite.
- **Verify, do not trust** — Assume generated code is buggy until proven otherwise. Review diffs and outputs before declaring success. If you cannot run a check, say so explicitly.

---

## 8. Agentic Workflow

This section is the single home for how an agent runs a task — understanding, clarifying, planning, executing, verifying, reporting.

- **Understand before editing** — Read the relevant intent, contracts, code, tests, and config before changing behavior. Review the documented intent first; it governs. Search for existing patterns before inventing new ones.
- **Ask before guessing** — Proactively surface ambiguities, unstated assumptions, and missing success criteria *before* you are confused. If scope, rollout, ownership, or policy is unclear or conflicting — or whether backwards compatibility is required — ask first. Present concrete options with trade-offs, not open-ended questions. Never infer that a missing value should fall back to something "reasonable": replace uncertainty with a specific question, an explicit TODO, or a clear failure.
- **Plan explicitly** — Use a written plan (`PLAN.md` / `TASKS.md`) for multi-step, multi-file, or architectural work, with verification steps included from the start. For uncertain or UX-facing work, a quick prototype beats extended planning — let implementation inform the plan. Revise the plan when evidence invalidates it; do not brute-force through confusion with speculative edits.
- **Preserve human trust** — Never claim completion without evidence. State what was verified, what was not, and why. Call out risks, assumptions, and open questions plainly.
- **Least privilege** — Use the minimum tools and permissions for the task. Read-only review stays read-only. Dangerous, irreversible, external, or user-facing actions require explicit approval.
- **Stop on unexpected state** — Do not overwrite or revert unrelated user changes. If the repo state shifts unexpectedly, stop and ask. If verification reveals a deeper issue, report it before widening scope.
- **No hallucinations** — Do not invent library versions, API methods, or factual claims from memory. Verify. When uncertain, say so.
- **Instruction precedence** — Resolve conflicts in this order: Intent-First governing principle → direct user/task instruction → local project docs (`INTENT.md`, `CLAUDE.md`) → workspace rules → this constitution → external guidance.

### Task Lifecycle

Steps 1–3 are mandatory for non-trivial work; trivial tasks (single-line fixes, config edits) skip to step 4.

1. **Understand** — Identify what is asked, what is ambiguous, what is unstated. Investigate intent, code, and context.
2. **Clarify** — Ask specific, batched, option-shaped questions. Confirm scope, success criteria, and whether backwards compatibility is required. Do not proceed on a vague brief.
3. **Plan** — For multi-step work, write what changes, in what order, and how it will be verified. Share it; get confirmation; revise as evidence arrives.
4. **Execute** — Follow the Implementation Decision Tree. Work iteratively; revise as you learn.
5. **Verify** — Run tests, check lints, review diffs. State what was and was not verified.
6. **Report** — Summarize what was done, what was verified, what remains, and the risks. Flag out-of-scope issues found along the way.

### Implementation Decision Tree

1. **Config or code?** Config-only → edit config, verify, done. Otherwise continue.
2. **Does existing code handle this?** Yes → reuse. Partially → extend it. No → continue.
3. **Does a maintained library solve it?** Yes → add the dependency (§5). No → write new code.
4. **Where does it live?** Shared across projects → shared package. Project-specific → project module. CLI entry point → thin wrapper in `scripts/`.
5. **Execute iteratively** — implement → run tests → refactor → verify → document. Read a file before modifying it; never edit blind.

---

## 9. Communication and Reporting

How agents report to the user:

- **Evidence first, terse.** Lead with what was verified and the result. No flattery, no filler, no narrating intentions you are about to act on anyway.
- **Surface risks, unknowns, and assumptions plainly.** High-signal truth beats reassuring noise. If something is unverified, say which step and why.
- **Offer options with trade-offs**, not open-ended questions, when a decision is the user's to make. Recommend one.
- **No implicit attribution.** Never assign ownership, responsibility, or a decision to a named person unless the user stated it. Use role-based language when unknown.
- **Be honest about partial or failed work.** Report what was skipped or failed with the actual output — never round a partial result up to "done."

---

## 10. Subagent Orchestration

- **Subagents are isolated.** They do not inherit the parent's rules or context. Any critical rule a subagent must follow is written into its own prompt.
- **Scope narrowly.** One clear responsibility per subagent, with an explicit tool allowlist and read-only by default unless the task needs writes.
- **Fan out for independent or context-heavy work** — parallel searches across many files, dimensions that can be reviewed independently, or work whose detail would bloat the main context (e.g. writing tests in a dedicated session). Keep the conclusion, not the file dumps.
- **Verify what comes back.** A subagent's report is an input, not a fact. Spot-check claims that matter before acting on them.

---

## 11. Change Safety

- **No backwards compatibility by default** — Refactor liberally to align with intent. Do not handle old cases, formats, or migration paths unless explicitly told to. Confirm at session start whether backwards compatibility is required (see Intent-First); never assume it.
- **Production gate** — A package is *production-gated* only when its `CLAUDE.md` and `INTENT.md` declare it **deployed AND in active use** (deployed alone does not count). Until then, contracts and interfaces are freely overhaul-able. Once gated:
  - Schema/API/contract changes require a documented migration or backfill, rollout order, and an abort/rollback path before merge.
  - Any contract or schema change requires an ADR in `docs/decisions/` documenting consumer impact.
  - Any breaking change requires stop-and-ask: explicit human approval first.
- **One concern per change** — A commit addresses one logical concern. Do not bundle unrelated fixes.
- **Reversibility** — Keep changes easy to revert; for risky changes define the rollback path before merging.
- **Follow established architecture** unless there is a clear, documented reason to change it. Prefer reproducible pipelines and generated artifacts over one-off manual edits.

---

## 12. Stop / Ask / Never

### Stop and confirm first
Describe the impact and wait for confirmation before:
- Destructive or irreversible operations (data deletion, schema migrations, dropping tables, file removal) — state what will be lost.
- Scope expansion beyond what was agreed.
- Choosing among architecturally different approaches with meaningful trade-offs — present options instead.
- Breaking a public interface's existing callers.
- Acting on external systems: production APIs, sending messages, modifying cloud resources, running migrations.

### Ask when unsure
- Requirements ambiguous or multiple valid interpretations → ask a specific, option-shaped question.
- Tests fail after 3 focused attempts → stop, report the failing test with full output, request guidance.
- A dependency is missing or a command needs elevated privileges → explain and provide the exact command for the user to run.

### Never (without explicit instruction)
- Force-push, rewrite shared history, or skip hooks.
- Fabricate data, invent API responses, or make factual claims from memory alone.
- Assume who is responsible for a decision — use role-based language.
- Modify code outside the task scope to work around a problem.
- Auto-send messages, rotate secrets, or delete data.
- Delete a file or directory you did not create without asking — an unexpected file is usually legitimate work-in-progress.

---

## 13. Git Discipline

- **Commit message:** `<type>: <imperative summary>` — subject under 50 chars, body explains *why*. Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.
- **Never commit:** secrets (`.env`), generated environments, runtime output, machine-specific config.
- **Always commit:** lock files, source code, config templates.
- **Branches:** `kebab-case-description`; delete after merge.
- **Worktree awareness** — In a worktree, stay on the assigned branch. Do not push from worktrees. Do not run destructive git operations (reset, clean, gc) that touch the shared object store. (Full multi-agent protocol: §17.)

---

## 14. Review Standards

- Review for correctness, regression risk, security, data safety, and test adequacy before style.
- Report findings in severity order; favor high-confidence, actionable findings over noisy completeness.
- Match review depth to risk tier. Docs-only and test-only changes warrant lighter review; security boundaries, access control, external integrations, and infrastructure warrant deeper scrutiny. When uncertain about tier, classify higher.
- A clean review is defense in depth, not proof of safety.

---

## 15. Documentation and Provenance

- Update the relevant docs when behavior, setup, architecture, workflow, or agent instructions materially change. Intent and contract docs update *first* (Intent-First), not last.
- External factual claims in knowledge-style docs carry sources.
- Keep operational gotchas near the code or skill that needs them.
- **No narration comments.** Comments explain how the code relates to the system, what it assumes about inputs/outputs, and why an unusual approach was chosen — never what the line does.

---

## 16. Data, ML, and Pipeline Engineering

- **Pipeline before model** — Build and test the full pipeline end-to-end with a trivial model (heuristic, linear, random baseline) before adding sophistication. Infrastructure reliability matters more than model complexity.
- **Data quality before model complexity** — Improving data quality almost always beats model tuning. Understand, clean, and validate data first.
- **Raw data is immutable** — Never modify raw data in place; treat it as an append-only system of record. All transformations are code producing regenerable derived artifacts.
- **Training-serving parity** — The code and data that train a model match what serves it. Re-use code across both; measure and monitor skew.
- **Watch for silent failures** — ML masks errors by producing plausible outputs from stale or corrupted data. Monitor staleness, feature drift, and coverage. A model that silently degrades is worse than one that crashes.

(Reproducibility and determinism are supreme principles — see §1.)

---

## 17. Multi-Agent Coordination

Applies when agents may work concurrently on one repository, or when a task benefits from isolation. Determine your working mode during planning. (Worktree commands and platform mechanics live in a workspace rule, not here.)

- **Own branch, own worktree** — Each agent works on its own branch in its own worktree. Never modify another agent's worktree. Merges happen through the primary tree, controlled by the user.
- **Shared state is a race condition** — Files outside version control (databases, `.env`, lock files, caches, runtime state) may be shared across worktrees. Do not write to them unless the task explicitly requires it; if exclusive access is needed, say so and wait.
- **Do not push from worktrees** — Commit to your branch; let the user push and merge. No destructive git operations on the shared object store.
- **Worktrees must initialize cleanly** — If a worktree is missing dependencies, fix the init script; do not hand-patch the worktree.
- **Explicit handoff** — When handing off, state: what changed, what did *not* change, what was verified and how, remaining risks, and the recommended next action.

---

## 18. Language-Specific: Python

- No `sys.path` manipulation. Shared code is installed as editable packages via proper packaging (`pyproject.toml`).
- `pytest` for all testing; no bare `assert` + `print` scripts. `hypothesis` for property-based tests on pure functions.
- **Pydantic models are the Python expression of `CONTRACTS.md`.** Define data contracts and schemas as Pydantic models; config via `pydantic-settings` (read from env/config, no code defaults).
- No `dict.get` / `list` fallbacks — prefer `[]` indexing to fail fast on missing keys.
- Strict typing: type hints on every argument and return value.
- Custom exception classes; do not catch bare `Exception`.
- Async by default for I/O-bound services (FastAPI, database access).
- **Package managers:** pixi and uv are both acceptable. Prefer pixi for heavy data-analytics / ML code; prefer uv for deploy-shaped services (e.g. Databricks Apps) and where upstream-template parity matters. Never mix two in one project.

---

## 19. Language-Specific: TypeScript

- Strict mode (`strict: true`). No `any` unless explicitly justified; use `unknown` for truly dynamic types.
- Explicit variant enums over boolean props: `variant="primary"`, not `primary={true}`.
- Typed context interfaces — never pass raw untyped state through context.
- Functional components with hooks; avoid class components. Compound components for complex multi-part UI.
- Keep data fetching near route/feature boundaries. Prefer server state (TanStack Query) over global client state.
- Stable list keys, explicit types, accessible UI states. Interactive elements have `aria-label` or visible text. Respect `prefers-reduced-motion` for non-essential animation.
- Property-based testing via a real library (fast-check), not ad hoc random tests.

---

## 20. Definition of Done

A task is done when ALL of the following hold. If any cannot be verified, name the blocked step — do not silently declare done.

- [ ] Intent and contract docs are current, and the change aligns with the documented goals
- [ ] Progress is tracked in repo markdown (`TASKS.md` / ADR where applicable)
- [ ] The implementation satisfies the stated requirement and stayed within approved scope
- [ ] Backwards-compatibility expectation was confirmed (not assumed) and honored
- [ ] Runtime behavior comes from config or explicit inputs, not hidden defaults
- [ ] Tests (property-based where applicable) pass; no untested new code paths
- [ ] Data assumptions documented and validated (schema, nulls, freshness, distributions)
- [ ] No secrets, tokens, or PII exposed in code or logs
- [ ] For production-gated packages: migration/rollback path defined and ADR written for contract changes
- [ ] The final report states evidence, limits, and residual risk honestly

(CI and linters enforce formatting, import order, type-checking, and build — those are not repeated here.)
