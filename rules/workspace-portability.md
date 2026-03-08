---
description: Workspace portability -- no hardcoded paths, config-derived roots
alwaysApply: true
---

# Workspace Portability

Never hardcode user-specific or machine-specific paths in documentation, agent instructions, or config files that are tracked in git.

Hardcoded paths make the workspace non-portable across machines and users. Workspace root is derived from script/package location at runtime; project-specific paths live in each project's config file.

## Scope

All files in the workspace, especially agent-consumed docs (rules, skills, READMEs) and human-facing docs (setup guides, architecture docs).

Agent docs use only relative paths (from workspace root). Generated files may contain absolute paths since they are produced by setup scripts and gitignored.

## How Paths Are Derived

- **Workspace root**: Derived at runtime from the location of the script or package being executed (e.g., `Path(__file__).parent.parent`).
- **Runtime config paths**: Each project's config file (e.g., `config.yaml`) uses relative paths resolved against the config file's directory.

## Runtime Path Resolution

For scripts and daemons that read a config file containing relative paths:

- Treat all relative config paths as relative to the config file directory, not process CWD.
- Resolve path values explicitly (`config_dir / relative_path`) at runtime before file I/O.
- Do not rely on global `chdir` as the only correctness mechanism; path resolution should remain correct even when launched from arbitrary CWD.
- Use explicit env var assignment (`os.environ[...] = ...`), never `setdefault`, when a config file is the authoritative source for a value.
