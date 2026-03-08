# Rules

Rules are markdown files with YAML frontmatter that provide always-available or contextually loaded guidance to AI coding agents. They are auto-loaded by the platform -- no manual inclusion needed.

This directory is currently empty. Future releases will add general-purpose rules for common engineering concerns.

## How Rules Work

- **Always-apply rules** are loaded every session, regardless of which files are open.
- **File-scoped rules** are loaded only when files matching a glob pattern are open or being edited.
- Rules are auto-discovered from this directory via platform symlinks (`.<platform-name>/rules/`).

## Creating a New Rule

See [templates/new-rule.md](../templates/new-rule.md) for the creation procedure, file format, and frontmatter conventions.
