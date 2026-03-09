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
4. **Download selected components** — place each file per `install_target` (see file placement below)
5. **Set up platform symlinks** — if the user uses Cursor, Claude Code, or another platform (see symlink setup below)
6. **Create or update CLAUDE.md** — add relevant sections from `templates/CLAUDE-factory.md` for dark factory workflows
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
| `wf-claude-mention` | Interactive @claude mentions on issues/PRs |
| `wf-pr-code-review` | Automatic PR code review |
| `wf-issue-triage` | Auto-classify and label issues |
| `wf-issue-implement` | Implement labeled issues as PRs |
| `wf-factory-orchestrator` | Sweep orphaned issues |

Offer weekly audit workflows (`wf-dep-audit`, `wf-security-scan`, `wf-code-quality`, `wf-test-coverage`) and monthly checks (`wf-docs-freshness`, `wf-workflow-upgrade`) as a second tier.

### Documentation-heavy projects

| Component | Why |
|-----------|-----|
| `source-citations` | Citation conventions for external claims |
| `mermaid-obsidian` | Mermaid diagram compatibility (if using Obsidian) |

### Multi-session agent work

| Component | Why |
|-----------|-----|
| `memory-trace-protocol` | Cross-session continuity via memory traces |

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
3. CONSTITUTION.md is accessible — referenced from the project's CLAUDE.md or placed at root
4. Workflows (if installed) — `.github/workflows/` contains the YAML files; repository secrets (`ANTHROPIC_API_KEY`, optionally `FACTORY_PAT`) are configured
5. Labels (if using dark factory) — run `scripts/setup-labels.sh` or manually create labels per the taxonomy in `templates/CLAUDE-factory.md`
