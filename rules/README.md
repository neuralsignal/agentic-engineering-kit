# Rules

Rules are markdown files with YAML frontmatter that provide always-available or contextually loaded guidance to AI coding agents. They are auto-loaded by the platform -- no manual inclusion needed.

## Available Rules

| Rule | Category | Always Apply | Description |
|------|----------|:------------:|-------------|
| [engineering-principles](engineering-principles.md) | core | yes | Non-negotiable engineering principles: KISS, DRY, no defaults, fail fast, config-driven, TDD |
| [planning-protocol](planning-protocol.md) | planning | yes | Task assessment, structured questions, scope validation, re-planning triggers |
| [data-ml-principles](data-ml-principles.md) | data-ml | yes | Notebooks vs source, experiment provenance, feature hygiene, pipeline testing, monitoring |
| [git-commit-conventions](git-commit-conventions.md) | git | yes | Commit format, staging rules, branch naming |
| [workspace-portability](workspace-portability.md) | core | yes | No hardcoded paths, config-derived roots, relative path resolution |
| [no-implicit-assumptions](no-implicit-assumptions.md) | agentic | yes | Never attribute ownership without explicit confirmation |
| [source-citations](source-citations.md) | documentation | yes | Citation conventions for external claims in knowledge docs |
| [memory-trace-protocol](memory-trace-protocol.md) | agentic | yes | Append-only session memory traces for cross-session continuity |
| [git-submodules](git-submodules.md) | git | no | Decision framework and commands for git submodules |
| [mermaid-obsidian](mermaid-obsidian.md) | documentation | yes | Mermaid diagram conventions for Obsidian compatibility |

## How Rules Work

- **Always-apply rules** are loaded every session, regardless of which files are open.
- **File-scoped rules** are loaded only when files matching a glob pattern are open or being edited.
- Rules are auto-discovered from this directory via platform symlinks (`.<platform-name>/rules/`) and the `.agents/rules/` cross-client convention.

## Creating a New Rule

See [templates/new-rule.md](../templates/new-rule.md) for the creation procedure, file format, and frontmatter conventions.
