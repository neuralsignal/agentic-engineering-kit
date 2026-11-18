# Integration Guide

This file is written for AI coding assistants. When a user asks you to integrate the Agentic Engineering Kit into their project, follow this protocol.

## URL Pattern

Download raw files from:

```
https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/{path}
```

Where `{path}` comes from the `path` field in `catalog.yaml`. For version pinning, replace `main` with a tag (e.g., `v0.2.0`).

## Integration Protocol

1. **Fetch the catalog** — download `catalog.yaml` from this repo
2. **Assess the target project** — language, CI platform, existing `rules/`/`skills/`/`agents/` dirs
3. **Present components** — group by category, recommend based on project type (see heuristics below)
4. **Install selected components** — copy standalone files per `install_target`. For `wf-maintainer-claude-pixi` and `wf-dependabot-review`, add the pinned caller from the [maintainer workflow guide](docs/lean-factory.md).
5. **Set up platform symlinks** — if the user uses Cursor, Claude Code, or another platform (see symlink setup below)
6. **Create or update AGENTS.md** — the canonical instruction file; `CLAUDE.md` is a symlink to it (`ln -s AGENTS.md CLAUDE.md`). Describe the project's actual build, test, and release commands.
7. **Verify** — confirm files are in place and agent can discover them

## Component Selection Heuristics

Recommend components based on the project type. Start with the essentials and offer extras.

### Every project

| Component | Why |
|-----------|-----|
| `constitution` | Foundational engineering standards |
| `engineering-principles` | Quick-reference principles (auto-loaded as a rule) |
| `git-commit-conventions` | Consistent commit messages |

### Projects with planning needs

| Component | Why |
|-----------|-----|
| `planning-protocol` | Structured task assessment and scope validation |

### Python data/ML projects

| Component | Why |
|-----------|-----|
| `data-ml-principles` | Notebook hygiene, experiment provenance, feature management |

### GitHub-hosted projects with CI

| Component | Why |
|-----------|-----|
| `github-actions-claude` | Patterns for Claude-powered GitHub Actions |
| `wf-maintainer-claude-pixi` | Explicit Claude requests in Pixi projects |
| `wf-dependabot-review` | CI-gated Claude review of Dependabot updates |

Keep the project's CI, docs, and release jobs. Use the [maintainer workflow guide](docs/lean-factory.md) for a pinned caller, dependency updates, and a staged migration from the older templates.

### Documentation-heavy projects

| Component | Why |
|-----------|-----|
| `source-citations` | Citation conventions for external claims |
| `mermaid-obsidian` | Mermaid diagram compatibility (if using Obsidian) |

### Teams and shared repos

| Component | Why |
|-----------|-----|
| `no-implicit-assumptions` | Prevent incorrect ownership attribution |
| `workspace-portability` | No hardcoded paths, portable configs |

## File Placement

Each component's `install_target` field in `catalog.yaml` determines where to place it:

| `install_target` | Destination |
|------------------|-------------|
| `.` | Project root |
| `rules` | `rules/` directory (create if needed) |
| `skills` | `skills/` directory (create if needed) |
| `agents` | `agents/` directory (create if needed) |
| `.github/workflows` | `.github/workflows/` directory (create if needed) |
| `templates` | `templates/` directory |
| `scripts` | `scripts/` directory |

For files (not directories), download the single file. For directories (skills), download the entire directory tree.

## Platform Symlink Setup

After placing components, set up platform symlinks so the AI assistant auto-discovers rules, skills, and agents.

### Cursor

```bash
mkdir -p .cursor
ln -sf ../rules .cursor/rules
ln -sf ../skills .cursor/skills
ln -sf ../agents .cursor/agents
```

### Claude Code

```bash
mkdir -p .claude
ln -sf ../rules .claude/rules
ln -sf ../skills .claude/skills
ln -sf ../agents .claude/agents
```

### Cross-client (.agents/)

```bash
mkdir -p .agents
ln -sf ../skills .agents/skills
ln -sf ../rules .agents/rules
```

Compatible with: Claude Code, Cursor, Gemini CLI, VS Code Copilot, OpenHands, Goose.

### Gitignore

Add symlink directories to `.gitignore`:

```
.cursor/rules
.cursor/skills
.cursor/agents
.claude/rules
.claude/skills
.claude/agents
.agents/skills
.agents/rules
```

## Post-Install Verification

After integration, verify:

1. Rules are auto-loaded — the AI assistant should see files in `rules/` without manual inclusion
2. Skills are discoverable — `skills/` contains SKILL.md files that the assistant can find
3. CONSTITUTION.md is accessible — referenced from the project's AGENTS.md or placed at root
4. Workflows (if installed) — `.github/workflows/` contains the caller and project CI. Verify the Claude credentials and run one maintainer request.
5. Labels — set up the taxonomy only when retaining an older label-driven workflow.
