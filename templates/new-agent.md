# Creating a New Agent (Subagent)

Agents are autonomous, narrowly-scoped AI subagents that can be invoked by the parent agent to handle specific tasks. Each agent runs in an isolated context with its own system prompt and tool restrictions.

## Critical: No Inherited Context

Subagents do **NOT** receive:

- Auto-loaded rules from `rules/`
- The main system prompt (CLAUDE.md, .cursorrules, etc.)
- Any parent conversation context beyond what is passed in the invocation prompt

This means **all critical rules must be embedded directly in each agent's system prompt**. If an agent must follow engineering principles, copy them inline -- do not assume they will be loaded automatically.

## Platform Support

| Platform | Agent Support | Location |
|----------|--------------|----------|
| Claude Code | Native `.claude/agents/` | `agents/` (symlinked) |
| Cursor | Via Task tool with `subagent_type` | `agents/` (symlinked) |

Agent files are most directly supported by Claude Code. Other platforms may adopt similar conventions in the future. The markdown content and structure are portable regardless of platform support.

## File Format

Agent files are `.md` files with YAML frontmatter.

### Frontmatter Fields

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `name` | string | Yes | Agent identifier (kebab-case, matches filename without `.md`) |
| `model` | string | No | Model to use: `inherit` (caller's model), `sonnet`, `haiku`, `opus`. Default: inherit |
| `memory` | string | No | Memory scope: `project`, `user`, `none`. Default: none |
| `tools` | list | No | Allowed tools. Omit to allow all tools |
| `disallowedTools` | list | No | Explicitly blocked tools (takes precedence over `tools`) |

### Example: Full-Access Agent

```yaml
---
name: my-implementer
model: inherit
memory: project
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
---
```

### Example: Read-Only Agent

```yaml
---
name: my-reviewer
model: sonnet
memory: project
tools:
  - Read
  - Grep
  - Glob
  - Bash
disallowedTools:
  - Write
  - Edit
---
```

## Model Selection Guidelines

| Use Case | Model | Rationale |
|----------|-------|-----------|
| General coding, complex reasoning | `inherit` | Matches caller's model |
| Code review, linting, quick checks | `sonnet` | Fast, cost-effective for structured analysis |
| Simple lookups, formatting | `haiku` | Fastest, cheapest for trivial tasks |
| Research, architecture decisions | `opus` or `inherit` | Needs deep reasoning |

## Tool Restriction Guidelines

- **Full-access agents** (engineers, implementers): Allow all tools needed for the workflow.
- **Read-only agents** (reviewers, auditors): Allow Read, Grep, Glob, Bash; disallow Write, Edit.
- **Read-only Bash use cases**: `git diff`, `git log`, `pytest`, `ls`, `wc` -- inspection commands only.
- **Restrict by principle of least privilege**: Only grant tools the agent actually needs.

## Step-by-Step

### 1. Create the file

```bash
touch agents/<agent-name>.md
```

Use kebab-case for the filename.

### 2. Add frontmatter

Choose the appropriate model, tools, and memory scope (see formats above). Every agent must have a `name`.

### 3. Write the system prompt

The markdown body after frontmatter is the agent's system prompt. Include:

- **Role description**: What the agent does and does not do.
- **Workspace context**: Environment details the agent needs (shell, package manager, config patterns).
- **Engineering principles**: Inline any rules the agent must follow (they are NOT auto-loaded).
- **Workflow**: Step-by-step process for the agent to follow.
- **Output format**: If the agent produces structured output, define the exact format.

### 4. Register in catalog (if contributing to this kit)

Add an entry to `catalog.yaml`:

```yaml
  - id: my-reviewer
    type: agent
    path: agents/my-reviewer.md
    name: My Reviewer
    description: Reviews code for correctness, security, and test adequacy.
    category: review
    platforms: [claude-code]
    dependencies: []
    install_target: agents
```

## Agent Discovery

Agents in `agents/` are automatically visible to platforms when the symlink exists:

```
agents/                                  <- canonical
.<platform-name>/agents/ --symlink-->    agents/
```

No per-agent registration is needed beyond adding the file.

## Content Guidelines

- Keep agent prompts focused on a single responsibility.
- Inline all rules the agent must follow -- never assume rules are auto-loaded.
- Include concrete examples of expected behavior.
- For structured output agents, define the exact output format with examples.
- Use descriptive, kebab-case filenames (e.g., `engineering-reviewer.md`, `docs-auditor.md`).

## Minimal Agent Template

```markdown
---
name: <agent-name>
model: inherit
tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# <Agent Name>

<Role description: what this agent does and does not do.>

## Context

<Environment details, project structure, relevant config patterns.>

## Rules

<Inline any engineering principles or rules the agent must follow.>

## Workflow

1. <Step 1>
2. <Step 2>
3. <Step 3>

## Output Format

<Define the exact output format, if applicable.>
```
