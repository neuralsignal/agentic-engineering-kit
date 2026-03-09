# Agentic Engineering Kit

Composable engineering principles, rules, skills, and CI workflows for AI-assisted software development. Works with any AI coding assistant.

## Quick Start

Open your AI coding assistant in your project and say:

> Fetch the component catalog from
> https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/catalog.yaml
> and the integration guide from
> https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/INTEGRATING.md
> then help me select and install components for this project.

The assistant will read the catalog, assess your project, and install the components you choose.

## What's in the Kit

Components are defined in [catalog.yaml](catalog.yaml) — the machine-readable source of truth.

- **Constitution & Rules** — Engineering principles, planning protocols, git conventions, data/ML standards, and more. Rules are auto-loaded by AI assistants from the `rules/` directory.
- **Skills** — On-demand workflows with scripts: GitHub Actions patterns, skill creation and benchmarking. Skills follow the [Agent Skills specification](https://agentskills.io/specification).
- **Dark Factory Workflows** — GitHub Actions that use Claude to autonomously triage issues, review PRs, implement features, audit dependencies, scan for vulnerabilities, and more. See [workflows/README.md](workflows/README.md).

Browse all components: [`catalog.yaml`](catalog.yaml)

## Alternative Integration Methods

### AI-assisted (recommended)

The Quick Start prompt above. Your AI assistant reads `catalog.yaml` and [`INTEGRATING.md`](INTEGRATING.md) to select and install components. No manual steps.

### Git subtree

Embed the full kit into your repo:

```bash
git subtree add --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git main --squash
```

Update later with `git subtree pull`. Pin to a tag (e.g., `v0.2.0`) for stability.

### Manual download

Grab individual files:

```bash
curl -O https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/CONSTITUTION.md
```

### Install script

Clone the repo and use the interactive installer:

```bash
git clone https://github.com/neuralsignal/agentic-engineering-kit.git
cd agentic-engineering-kit
./install.sh --list              # see available components
./install.sh --all --target ~/my-project --setup-platform cursor
```

See [docs/composition-guide.md](docs/composition-guide.md) for detailed comparison of all approaches.

## Platform Support

Components are plain markdown files that work with any AI coding assistant. The install script creates platform-specific symlinks (`.<platform>/rules/` → `rules/`, etc.) for auto-discovery. See [docs/platform-setup.md](docs/platform-setup.md).

## Creating Your Own Components

Templates for extending the kit with your own rules, skills, and agents:

- [templates/new-rule.md](templates/new-rule.md)
- [templates/new-skill.md](templates/new-skill.md)
- [templates/new-agent.md](templates/new-agent.md)

## Versioning

This repo uses [semantic versioning](https://semver.org/). Pin to a specific tag for stability:

```bash
git subtree add --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git v0.2.0 --squash
```

- **Major**: Breaking changes to component structure or catalog schema
- **Minor**: New components, non-breaking improvements
- **Patch**: Typo fixes, clarifications

## License

MIT. See [LICENSE](LICENSE).

**Third-party:** `skills/skill-creator/` is from [anthropics/skills](https://github.com/anthropics/skills) (Apache 2.0). See [skills/skill-creator/LICENSE.txt](skills/skill-creator/LICENSE.txt).
