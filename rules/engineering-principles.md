---
description: Non-negotiable engineering principles for all workspace code
alwaysApply: true
---

# Engineering Principles

Quick-reference subset. See `CONSTITUTION.md` at the workspace root for the full engineering constitution.

Non-negotiable. Violating these is a bug. If you see a violation, call it out, stop, and suggest a fix.

- **KISS** -- One tool per job. No fallback chains. If a library exists, use it. No clever abstractions, no premature generalization.
- **DRY** -- One source of truth for everything. Shared logic lives in shared modules. If you copy-paste, you already failed.
- **No Default Arguments** -- Ever. Zero default values in function signatures, constructors, or CLI args. Every value comes from config. If a caller doesn't provide it, the code crashes -- that's correct behavior. A default is a hidden assumption waiting to rot.
- **Fail Fast and Loud** -- No silent swallowing. No try-except-pass. No graceful degradation. Errors propagate with full stack traces. Missing config = crash with a clear message. Bad API response = log exactly what went wrong and stop. If something is wrong, SCREAM about it.
- **Everything From Config** -- Your project config file (e.g., `config.yaml`, `settings.toml`) is the single source of truth. Intervals, paths, scopes, feature flags, API settings -- all in config. Code reads config; code never invents values. Module-level constants like `_SAVE_INTERVAL = 25` or `TIMEOUT_SECONDS = 120` are violations -- these belong in config and are read via the config object.
- **Modular and Independent** -- Each module is standalone. Enable/disable independently. Schedule independently. Add a new one = new module + config section. No god objects, no shared mutable state.
- **No Backwards Compatibility** -- Refactor liberally. Test the new behavior. Do not handle old cases, old formats, or migration paths unless explicitly told to maintain backwards compatibility.
- **No sys.path Manipulation** -- Never `sys.path.append()` or `sys.path.insert()`. Shared code lives in a shared packages directory and is installed as an editable dependency in each consumer's project config (e.g., `pyproject.toml` with `pip install -e`, or equivalent for your package manager). Project-internal imports use proper package structure. Import hacks rot silently and break the moment directory structure changes.
- **Descriptive Package Names** -- Python package directories (the ones used in `import` statements) must have project-specific names. Never use generic names like `src`, `lib`, `utils`, or `core` -- they collide across editable installs and make imports ambiguous. Use snake_case names that identify the project (e.g., `my_project`, `data_pipeline`). Note: non-installable project subdirectories like `scripts/`, `tests/`, or similar folders that aren't Python packages are fine.
- **TDD** -- Tests come first. Write failing tests, then implement. All projects use `pytest`. Tests live in `<project>/tests/` as `test_*.py`. Every module has corresponding tests. No bare `assert` + `print` scripts -- if pytest cannot discover it, it is not a test.
- **Property-Based Testing** -- Use `hypothesis` (Python) or `fast-check` (TypeScript) for property-based tests on pure functions: data transformers, parsers, serializers, validators -- any function with a clear input/output contract. Standard unit tests are fine for integration and smoke tests.

Scope: all code in this workspace, across all projects.
