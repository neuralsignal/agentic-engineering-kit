# Changelog

## [0.2.0] - 2026-03-08

### Added
- `skill-creator` skill -- create, iteratively improve, and benchmark agent skills with eval runner, description optimizer, grader/comparator/analyzer subagents, and review webapp. Verbatim from [anthropics/skills](https://github.com/anthropics/skills) (Apache 2.0)
- First skill: `github-actions-claude` -- pattern catalog for Claude-powered GitHub Actions workflows (permissions, tools, models, testing, failure modes)
- Eval scaffolding for `github-actions-claude` with 3 test cases and assertions
- Cross-client `.agents/` symlink support in install script (agentskills.io convention)
- `.agents/skills/` and `.agents/rules/` cross-client convention documented in platform-setup.md
- 10 rules ported from production workspace:
  - `engineering-principles` -- KISS, DRY, no defaults, fail fast, config-driven, TDD, property testing
  - `planning-protocol` -- task assessment, structured questions, scope validation, re-planning triggers
  - `data-ml-principles` -- notebooks vs source, experiment provenance, feature hygiene, pipeline testing, monitoring
  - `git-commit-conventions` -- commit format, staging rules, branch naming
  - `workspace-portability` -- no hardcoded paths, config-derived roots, relative path resolution
  - `no-implicit-assumptions` -- never attribute ownership without explicit confirmation
  - `source-citations` -- citation conventions for knowledge docs
  - `memory-trace-protocol` -- append-only session memory for cross-session continuity
  - `git-submodules` -- decision framework and commands
  - `mermaid-obsidian` -- Mermaid diagram conventions for Obsidian

### Changed
- `templates/new-skill.md` fully aligned with [agentskills.io specification](https://agentskills.io/specification): progressive disclosure, optional frontmatter fields (`license`, `compatibility`, `metadata`, `allowed-tools`), self-contained scripts (PEP 723, npx), agentic script design guidelines, eval framework
- `skills/README.md` updated with first skill and spec reference
- `catalog.yaml` updated with github-actions-claude entry
- `README.md` components table and platform support section updated
- CONSTITUTION.md Section 2 (Supreme Principles): added **YAGNI** as explicit named principle -- no speculative capabilities, config keys, or abstractions without a current caller
- CONSTITUTION.md Section 3 (Architecture and Design): added **Inward Dependency Direction** -- concrete implementations depend on shared contracts, not on other concrete implementations
- CONSTITUTION.md Section 11 (Change Safety): added **Reversibility** -- define rollback path before merging risky changes
- CONSTITUTION.md Section 14 (Review Standards): added risk-tiered review depth -- classify changes by risk tier, default to higher when uncertain
- CONSTITUTION.md Section 20 (Multi-Agent Coordination): added **Handoff protocol** -- structured template for agent-to-agent and agent-to-human handoffs

## [0.1.0] - 2026-03-08

### Added
- Engineering Constitution (CONSTITUTION.md) -- 19 sections + Task Lifecycle + Implementation Decision Tree
- Component catalog (catalog.yaml)
- Bash installer (install.sh) with platform setup support for Cursor and Claude Code
- Creation procedure templates for rules, skills, and agents
- Composition guide (git subtree, manual copy, install script)
- Platform setup guide (Cursor, Claude Code)
