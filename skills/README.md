# Skills

Skills are on-demand workflows with documentation and optional executable scripts. Unlike rules (which are auto-loaded), skills are invoked by the agent when they match the task at hand. Each skill is fully isolated with its own dependencies.

This directory is currently empty. Future releases will add general-purpose skills for common development tasks.

## How Skills Work

- Each skill lives in its own subdirectory: `skills/<skill-name>/`.
- Every skill must have a `SKILL.md` with YAML frontmatter (`name`, `description`).
- Skills may include executable scripts in a `scripts/` subdirectory.
- Each skill manages its own dependencies independently.
- Skills are auto-discovered from this directory via platform symlinks (`.<platform-name>/skills/`).

## Creating a New Skill

See [templates/new-skill.md](../templates/new-skill.md) for the creation procedure, directory structure, and dependency management.
