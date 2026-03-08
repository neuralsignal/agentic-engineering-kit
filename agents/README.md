# Agents (Subagents)

Agents are autonomous, narrowly-scoped AI subagents that can be invoked by the parent agent to handle specific tasks. Each agent runs in an isolated context with its own system prompt and tool restrictions.

This directory is currently empty. Future releases will add general-purpose agents for common engineering tasks (e.g., code review, documentation audit).

## How Agents Work

- Each agent is a `.md` file with YAML frontmatter (`name`, `model`, `tools`, etc.).
- Agents do **not** inherit rules, skills, or context from the parent agent. All critical instructions must be embedded in the agent's own system prompt.
- Agents are auto-discovered from this directory via platform symlinks (`.<platform-name>/agents/`).

## Creating a New Agent

See [templates/new-agent.md](../templates/new-agent.md) for the creation procedure, frontmatter fields, and content guidelines.
