# Creating a New Skill

Skills are on-demand workflows with documentation and optional executable scripts. Unlike rules (which are auto-loaded), skills are invoked by the agent when they match the task at hand. Each skill is fully isolated with its own dependencies.

This template follows the [Agent Skills specification](https://agentskills.io/specification).

## Directory Structure

Every skill lives at `skills/<skill-name>/` and must contain:

| Path | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | Yes | Agent-facing documentation with frontmatter |
| `scripts/` | No | Executable scripts the agent can invoke |
| `references/` | No | Detailed reference documentation, loaded on demand |
| `assets/` | No | Static resources: templates, images, data files, schemas |
| `evals/` | No | Evaluation test cases for measuring skill quality |

## Progressive Disclosure

Skills follow a three-tier loading strategy to keep agent context small:

| Tier | What | When Loaded | Token Budget |
|------|------|-------------|--------------|
| **1. Catalog** | `name` + `description` from frontmatter | Session start, for all skills | ~50-100 tokens per skill |
| **2. Instructions** | Full SKILL.md body | When the agent activates the skill | <5000 tokens recommended |
| **3. Resources** | Scripts, references, assets | When instructions reference them | As needed |

Keep SKILL.md under 500 lines. Move detailed reference material to `references/` files that the agent loads on demand.

## SKILL.md Frontmatter

### Required Fields

```yaml
---
name: <skill-name>
description: >
  What this skill does and when to use it. Be specific enough
  that an agent can decide whether to activate the skill from
  this field alone.
---
```

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | 1-64 chars, lowercase alphanumeric + hyphens, must match parent directory name |
| `description` | string | 1-1024 chars, describes what + when |

### Optional Fields

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: MIT
compatibility: Requires poppler-utils. Designed for Linux/macOS.
metadata:
  author: your-org
  version: "1.0"
allowed-tools: Bash(git:*) Read Write
---
```

| Field | Type | Purpose |
|-------|------|---------|
| `license` | string | License name or reference to a bundled LICENSE file |
| `compatibility` | string | Environment requirements: system packages, network access, intended platform |
| `metadata` | map | Arbitrary key-value pairs (author, version, etc.) |
| `allowed-tools` | string | Space-delimited list of pre-approved tools the skill may use (experimental) |

## Step-by-Step

### 1. Create the directory

```bash
mkdir -p skills/<skill-name>/scripts
```

### 2. Set up dependency management (if needed)

Choose your package manager and create the appropriate config file:

| Tool | Config File | Isolation |
|------|-------------|-----------|
| pixi | `pixi.toml` + `pixi.lock` | Conda-based, per-skill environments |
| uv | `pyproject.toml` + `uv.lock` | Fast Python venv per skill |
| venv | `requirements.txt` | Standard Python virtual environments |
| poetry | `pyproject.toml` + `poetry.lock` | Python dependency management |
| npm | `package.json` + `package-lock.json` | Node.js projects |

The key principle: each skill's dependencies are isolated from other skills and from the rest of the project.

Pin dependency versions:
- Stable libs (>=1.0): `>=current, <next-major` (e.g., `>=2.0, <3`)
- Pre-1.0 libs: `>=current, <next-minor` (e.g., `>=0.7.4, <0.8`)

For simple scripts, prefer self-contained inline dependencies over a full project manifest (see [Self-Contained Scripts](#self-contained-scripts) below).

### 3. Write SKILL.md

Document these sections:

1. **What this skill does** -- brief overview
2. **When to use this skill** -- trigger conditions for agent activation
3. **Running Scripts** -- how to invoke scripts
4. **Script Reference** -- each script with usage, arguments, and examples
5. **Dependencies** -- human-readable table of what the skill requires

### 4. Register in catalog (if contributing to this kit)

Add an entry to `catalog.yaml`:

```yaml
  - id: my-skill
    type: skill
    path: skills/my-skill
    name: My Skill
    description: What this skill does in one sentence.
    category: engineering
    platforms: [generic]
    dependencies: []
    install_target: skills
```

## Self-Contained Scripts

When a script has only a few dependencies, declare them inline instead of creating a full project manifest. The agent runs the script with a single command -- no separate install step.

### Python (PEP 723)

```python
# /// script
# dependencies = [
#   "beautifulsoup4>=4.12,<5",
# ]
# requires-python = ">=3.12"
# ///

from bs4 import BeautifulSoup
# ...
```

Run with [uv](https://docs.astral.sh/uv/):

```bash
uv run scripts/extract.py
```

`uv run` creates an isolated environment, installs declared dependencies, and runs the script. Use `uv lock --script` for a lockfile.

### Node.js (npx)

```bash
npx eslint@9 --fix .
npx create-vite@6 my-app
```

Pin versions with `package@version` for reproducibility.

### When to use inline vs. project dependencies

| Situation | Approach |
|-----------|----------|
| Script has 1-3 pure-Python deps | PEP 723 inline + `uv run` |
| Script needs native extensions or complex dep tree | Full `pyproject.toml` + lock file |
| One-off CLI tool invocation | `uvx`, `npx`, `bunx` |
| Multiple scripts share the same deps | Full project manifest |

## Designing Scripts for Agentic Use

Agents read stdout and stderr to decide what to do next. These design choices make scripts dramatically easier for agents to use.

### No interactive prompts

Agents run in non-interactive shells. A script that blocks on TTY input hangs indefinitely. Accept all input via flags, environment variables, or stdin.

### Document usage with `--help`

`--help` output is how agents learn a script's interface. Include a description, available flags, and usage examples. Keep it concise -- the output enters the agent's context window.

### Write helpful error messages

Say what went wrong, what was expected, and what to try:

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

### Use structured output

Prefer JSON, CSV, or TSV over free-form text. Send structured data to stdout and diagnostics to stderr.

### Further considerations

- **Idempotency** -- Agents may retry commands. Prefer "create if not exists" over "create and fail on duplicate."
- **Meaningful exit codes** -- Use distinct codes for different failure types and document them in `--help`.
- **Dry-run support** -- For destructive operations, support a `--dry-run` flag.
- **Predictable output size** -- Default to summaries. Support `--output FILE` for large outputs to avoid context window overflow.

## Evaluating Skill Quality

Use structured evaluations to measure whether a skill produces good outputs reliably.

### Eval directory structure

```
skills/<skill-name>/
└── evals/
    ├── evals.json          # Test cases and assertions
    └── files/              # Input files for test cases (optional)
```

### Test case format

Each test case has a prompt, expected output description, optional input files, and assertions:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "A realistic user message for this skill.",
      "expected_output": "Description of what success looks like.",
      "files": ["evals/files/sample-input.txt"],
      "assertions": [
        "The output includes a specific required element",
        "Error handling is mentioned for edge case X",
        "The response references the correct API endpoint"
      ]
    }
  ]
}
```

### Writing assertions

Good assertions are specific and verifiable:
- "The output includes a valid YAML permissions block" -- checkable
- "The response identifies at least 2 unnecessary permissions" -- countable
- "Error messages include the failing command" -- observable

Avoid vague assertions ("The output is helpful") or brittle ones ("Uses the exact phrase 'run npm install'").

### Running evals

For each test case, run the prompt twice: once with the skill loaded and once without. Compare pass rates to measure the skill's value. See the [agentskills.io eval guide](https://agentskills.io/skill-creation/evaluating-skills) for the full grading and benchmarking workflow.

## Skill Discovery

Skills in `skills/` are automatically visible to agents when a platform symlink or the cross-client `.agents/` directory exists:

```
skills/                                  <- canonical (single source of truth)
.<platform-name>/skills/ --symlink-->    skills/
.agents/skills/          --symlink-->    skills/    (cross-client convention)
```

The `.agents/skills/` path is the emerging cross-client standard. Skills placed here are discoverable by any compliant agent. The install script creates both platform-specific and `.agents/` symlinks automatically.

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
description: <One-sentence description of what this skill does and when to use it.>
---

# <Skill Name>

<What this skill does.>

## When to Use This Skill

- <Trigger condition 1>
- <Trigger condition 2>

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
