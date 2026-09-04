---
description: Git commit conventions -- commit format, staging rules, branch naming
alwaysApply: true
---

# Git Commit Conventions

Type-prefix + imperative subject, under ~50 characters. Optional body explains WHY, wrapped at 72.

```
<type>: <short imperative summary>

[optional body]
```

| Type | When to use | Example |
|------|-------------|---------|
| `feat` | New feature or capability | `feat: add vector sync to the data pipeline` |
| `fix` | Bug fix | `fix: handle missing API key in auth module` |
| `docs` | Rules, README, architecture docs | `docs: expand git-commit-conventions rule` |
| `chore` | Deps, config, lock files, `.gitignore` | `chore: update lock file after adding hypothesis` |
| `refactor` | Code restructuring without behavior change | `refactor: rename src package to data_pipeline` |
| `test` | Adding or fixing tests | `test: add property tests for chunk splitter` |

## What to Stage

**Commit:** all source code (`*.py`, `*.ts`, `*.toml`, `*.yaml`, `*.md`); lock files (`pixi.lock`, `uv.lock`, `poetry.lock`, `package-lock.json`) for deterministic builds; documentation, rules, skills, agents, templates; config templates without secrets.

**Never commit:**

| Path | Why |
|---|---|
| `.venv/`, `node_modules/`, `.pixi/` | auto-generated environments |
| `*.db`, `*.sqlite` | derived indexes, regenerated at runtime |
| `.env` | secrets |
| `logs/`, `state/`, `dist/`, `build/` | runtime output |
| `.vscode/settings.json`, `.idea/` | machine-specific IDE config |
| large data files, model artifacts | belong in data versioning or object storage |
| data files riding inside a docs or notes folder (CSV exports, image sets) | `.gitignore` rules are path-based and do NOT follow a moved directory — re-check the ignore after any folder move |

## Branch Conventions

`main` is the primary branch; day-to-day work commits directly here in personal or small-team repos. Feature branches are `kebab-case-description` for exploratory or PR-based work — delete after merge.
