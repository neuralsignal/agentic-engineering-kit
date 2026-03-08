---
description: Git commit conventions -- commit format, staging rules, branch naming
alwaysApply: true
---

# Git Commit Conventions

## Commit Message Format

Use type-prefix + imperative subject. Keep the subject under ~50 characters.

```
<type>: <short imperative summary>

[optional body: explain WHY, wrap at 72 chars]
```

Valid types:

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation, rules, README changes |
| `chore` | Deps, config, lock files, `.gitignore` |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or fixing tests |

Examples:

```
feat: add vector sync to data pipeline
chore: update lock file after adding hypothesis
docs: expand git-commit-conventions rule
fix: handle missing API key in auth module
refactor: rename src package to data_pipeline
test: add property tests for chunk splitter
```

## What to Stage (and What Not To)

**Commit:**
- All source code (`*.py`, `*.ts`, `*.toml`, `*.yaml`, `*.md`)
- Lock files (`pixi.lock`, `uv.lock`, `poetry.lock`, `package-lock.json`) for deterministic builds
- Documentation, rules, skills, agents, templates
- Config templates (without secrets)

**Never commit:**
- Virtual environments (`.venv/`, `node_modules/`, `.pixi/`)
- Database files (`*.db`, `*.sqlite`)
- `.env` files containing secrets
- Runtime output (`logs/`, `state/`, `dist/`, `build/`)
- Machine-specific IDE config (`.vscode/settings.json`, `.idea/`)
- Large data files or model artifacts

## Branch Conventions

- **`main`**: Primary branch. Day-to-day work commits directly here in personal/small-team repos.
- **Feature branches**: `kebab-case-description` for exploratory or PR-based work. Delete after merge.
