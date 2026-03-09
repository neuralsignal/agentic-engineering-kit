# Skills

Skills are on-demand workflows with documentation and optional executable scripts. Unlike rules (which are auto-loaded), skills are invoked by the agent when they match the task at hand. Each skill is fully isolated with its own dependencies.

Skills in this kit follow the [Agent Skills specification](https://agentskills.io/specification).

## Available Skills

| Skill | Description |
|-------|-------------|
| [conda-forge-publish](conda-forge-publish/) | Publish Python packages to conda-forge — recipe authoring, staged-recipes PR submission, and feedstock maintenance |
| [docs-site](docs-site/) | Set up MkDocs + Material documentation with auto-generated API reference for Python packages |
| [github-actions-claude](github-actions-claude/) | Pattern catalog for authoring, debugging, and testing GitHub Actions workflows that use `anthropics/claude-code-action` |
| [skill-creator](skill-creator/) | Create, iteratively improve, and benchmark agent skills with eval runner, description optimizer, and review webapp. (Apache 2.0, from [anthropics/skills](https://github.com/anthropics/skills)) |

## How Skills Work

- Each skill lives in its own subdirectory: `skills/<skill-name>/`.
- Every skill must have a `SKILL.md` with YAML frontmatter (`name`, `description`).
- Skills may include executable scripts in a `scripts/` subdirectory.
- Each skill manages its own dependencies independently.
- Skills are auto-discovered via platform symlinks (`.<platform-name>/skills/`) and the cross-client `.agents/skills/` convention.

## Creating a New Skill

See [templates/new-skill.md](../templates/new-skill.md) for the creation procedure, directory structure, frontmatter spec, and dependency management.
