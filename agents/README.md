# Agents (Subagents)

Agents are autonomous, narrowly-scoped AI subagents that can be invoked by the parent agent to handle specific tasks. Each agent runs in an isolated context with its own system prompt and tool restrictions.

| Agent | Description |
|-------|-------------|
| `engineering-reviewer.md` | Read-only compliance reviewer. Audits code against the 11 engineering principles and produces a structured PASS/VIOLATIONS/SUMMARY report. |
| `software-engineer.md` | Senior software engineer for coding-heavy tasks: new packages, multi-file refactors, TDD cycles, CLI tools. Enforces all engineering principles inline. |

## How Agents Work

- Each agent is a `.md` file with YAML frontmatter (`name`, `model`, `tools`, etc.).
- Agents do **not** inherit rules, skills, or context from the parent agent. All critical instructions must be embedded in the agent's own system prompt.
- Agents are auto-discovered from this directory via platform symlinks (`.<platform-name>/agents/`).

## Creating a New Agent

See [templates/new-agent.md](../templates/new-agent.md) for the creation procedure, frontmatter fields, and content guidelines.
