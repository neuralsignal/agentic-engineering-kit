# Creating a New Skill

Skills are on-demand workflows with documentation and optional executable scripts. Unlike rules (which are auto-loaded), skills are invoked by the agent when they match the task at hand. Each skill is fully isolated with its own dependencies.

## Directory Structure

Every skill lives at `skills/<skill-name>/` and must contain:

| Path | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | Yes | Agent-facing documentation with frontmatter |
| `scripts/` | If skill has scripts | Executable scripts the agent can invoke |
| `schemas/` | No | Data schemas (YAML, JSON Schema) |
| `references/` | No | Reference documentation for the skill |

Dependency management is up to your project. Common options:

| Tool | Config File | Isolation |
|------|-------------|-----------|
| pixi | `pixi.toml` + `pixi.lock` | Conda-based, per-skill environments |
| uv | `pyproject.toml` + `uv.lock` | Fast Python venv per skill |
| venv | `requirements.txt` | Standard Python virtual environments |
| poetry | `pyproject.toml` + `poetry.lock` | Python dependency management |
| npm | `package.json` + `package-lock.json` | Node.js projects |

The key principle: each skill's dependencies are isolated from other skills and from the rest of the project. Adding a dependency to one skill never affects another.

## Step-by-Step

### 1. Create the directory

```bash
mkdir -p skills/<skill-name>/scripts
```

### 2. Set up dependency management

Choose your package manager and create the appropriate config file. Example with `pyproject.toml`:

```toml
[project]
name = "<skill-name>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    # Add dependencies here with pinned ranges
]
```

Pin dependency versions to avoid surprises:
- Stable libs (>=1.0): `>=current, <next-major` (e.g., `>=2.0, <3`)
- Pre-1.0 libs: `>=current, <next-minor` (e.g., `>=0.7.4, <0.8`)

### 3. Write SKILL.md

The SKILL.md file is the agent-facing documentation. It must include YAML frontmatter:

```yaml
---
name: <skill-name>
description: One-sentence description for agent discovery.
---
```

Document these sections:

1. **What this skill does** -- brief overview
2. **Running Scripts** -- how to invoke scripts (both agent and human invocation patterns)
3. **Script Reference** -- each script with usage, arguments, and examples
4. **Dependencies** -- human-readable table of what the skill requires

Example SKILL.md:

```markdown
---
name: data-profiler
description: Profile datasets and generate summary statistics with visualizations.
---

# Data Profiler Skill

Generate profiling reports for CSV, Parquet, and database tables.

## Running Scripts

All scripts run from the skill directory:

\```bash
cd skills/data-profiler && python scripts/profile.py --input data.csv --output report.html
\```

## Script Reference

### profile.py

Generate a profiling report for a dataset.

**Arguments:**
- `--input` (required): Path to the input dataset
- `--output` (required): Path for the output report
- `--format` (optional): Output format (html, json). Default: html

**Example:**
\```bash
python scripts/profile.py --input /data/sales.csv --output /tmp/sales_profile.html
\```

## Dependencies

| Package | Purpose |
|---------|---------|
| pandas | Data manipulation |
| ydata-profiling | Report generation |
```

### 4. Register in catalog (if contributing to this kit)

Add an entry to `catalog.yaml`:

```yaml
  - id: data-profiler
    type: skill
    path: skills/data-profiler
    name: Data Profiler
    description: Profile datasets and generate summary statistics.
    category: data
    platforms: [generic]
    dependencies: []
    install_target: skills
```

## Dependency Isolation

Each skill has its own environment. This means:

- Skills can have conflicting dependency versions without interference
- Adding a dependency to one skill never affects another
- Lock files are committed to the repo; environment directories are gitignored
- First run in a session installs the environment if it is missing

## Skill Discovery

Skills in `skills/` are automatically visible to agents when the platform symlink exists:

```
skills/                                  <- canonical
.<platform-name>/skills/ --symlink-->    skills/
```

No per-skill registration is needed beyond adding the directory and SKILL.md.

## Minimal Skill Template

```
skills/<skill-name>/
├── SKILL.md
└── scripts/
    └── example.py
```

SKILL.md:

```markdown
---
name: <skill-name>
description: <One-sentence description>
---

# <Skill Name>

<What this skill does.>

## Running Scripts

\```bash
cd skills/<skill-name> && python scripts/example.py <ARGS>
\```

## Script Reference

### example.py

<Description and usage.>

## Dependencies

| Package | Purpose |
|---------|---------|
| <package> | <purpose> |
```
