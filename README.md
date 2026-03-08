# Agentic Engineering Kit

A composable library of engineering principles, rules, skills, and subagents for AI-assisted software development. Pick the components you need, install them into your project, and let your AI coding agents work within a well-defined framework.

## Quick Start

Three ways to use this kit. Choose whichever fits your workflow.

### Option 1: Git subtree (recommended for teams)

Embed the entire kit into your project. All contributors get it automatically on `git clone`.

```bash
git subtree add --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git main --squash
```

Update later:

```bash
git subtree pull --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git main --squash
```

### Option 2: Manual copy

Grab individual files directly:

```bash
curl -O https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/CONSTITUTION.md
```

### Option 3: Install script

Clone the repo and use the installer for selective installation with platform setup:

```bash
git clone https://github.com/neuralsignal/agentic-engineering-kit.git
cd agentic-engineering-kit

# See what's available
./install.sh --list

# Install the constitution into your project
./install.sh constitution --target ~/my-project

# Install and set up symlinks for your platform
./install.sh constitution --target ~/my-project --setup-platform cursor

# Install everything
./install.sh --all --target ~/my-project
```

See [docs/composition-guide.md](docs/composition-guide.md) for detailed instructions and trade-offs.

## Components

| ID | Type | Description |
|----|------|-------------|
| `constitution` | constitution | 19-section engineering constitution: supreme principles, architecture, error handling, testing, agentic engineering, planning and discovery, security, git discipline, data/ML pipelines, language-specific rules (Python, TypeScript), and a full task lifecycle. |

Components are listed in [catalog.yaml](catalog.yaml). Future releases will add rules, skills, and agents.

## Platform Support

This kit is platform-agnostic. Components are plain markdown files that work with any AI coding assistant. Most platforms auto-load rules and skills from a `.<platform-name>/` directory. The install script creates symlinks from `.<name>/` to the canonical `rules/`, `skills/`, and `agents/` directories:

```bash
# Example: set up for Cursor and Claude Code
./install.sh --setup-platform cursor --target ~/my-project
./install.sh --setup-platform claude --target ~/my-project
```

This creates `.<name>/rules/`, `.<name>/skills/`, and `.<name>/agents/` as symlinks. See [docs/platform-setup.md](docs/platform-setup.md) for details.

## Creating Your Own Components

The kit includes templates for creating new rules, skills, and agents that follow the standard conventions:

- [templates/new-rule.md](templates/new-rule.md) -- How to create a new rule
- [templates/new-skill.md](templates/new-skill.md) -- How to create a new skill
- [templates/new-agent.md](templates/new-agent.md) -- How to create a new agent (subagent)

## Repository Structure

```
agentic-engineering-kit/
├── CONSTITUTION.md          # Engineering constitution (core document)
├── catalog.yaml             # Machine-readable component manifest
├── install.sh               # Bash installer
├── rules/                   # Rules (auto-loaded guidance for agents)
├── skills/                  # Skills (on-demand workflows with scripts)
├── agents/                  # Agents (autonomous subagent definitions)
├── templates/               # Creation procedure guides
└── docs/                    # Detailed documentation
```

## Versioning

This repo uses [semantic versioning](https://semver.org/). Pin to a specific tag for stability:

```bash
# Subtree with a specific version
git subtree add --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git v0.1.0 --squash

# curl a specific version
curl -O https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/v0.1.0/CONSTITUTION.md
```

- **Major** (v1 -> v2): Breaking changes to component structure, catalog schema, or install script interface.
- **Minor** (v0.1 -> v0.2): New components added, non-breaking improvements to existing ones.
- **Patch** (v0.1.0 -> v0.1.1): Typo fixes, clarifications, documentation updates.

## License

MIT. See [LICENSE](LICENSE).
