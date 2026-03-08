---
name: github-actions-claude
description: >
  Scaffold or audit GitHub Actions workflows that use anthropics/claude-code-action@v1.
  Use when creating new Claude-powered CI workflows, configuring permissions and tools,
  selecting models, debugging existing actions, or testing locally with act.
compatibility: Requires gh CLI and git. Designed for GitHub Actions environments.
license: MIT
---

# GitHub Actions + Claude -- Pattern Catalog

Reference for authoring and debugging GitHub Actions workflows that use
[`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action).
Covers permissions, tool configuration, model selection, output patterns, MCP servers,
structured outputs, testing, and common failure modes.

---

## When to Use This Skill

- Creating a new Claude-powered workflow from scratch
- Adding Claude to an existing workflow
- Debugging a failing Claude workflow (auth errors, permission denied, tool blocked)
- Auditing permissions on an existing workflow for least-privilege compliance
- Looking up action documentation or inputs via `gh` CLI

---

## Official Documentation

- [README + quickstart](https://github.com/anthropics/claude-code-action)
- [Solutions guide](https://github.com/anthropics/claude-code-action/blob/main/docs/solutions.md) -- ready-to-use automation patterns
- [Configuration](https://github.com/anthropics/claude-code-action/blob/main/docs/configuration.md) -- MCP servers, permissions, env vars, custom tools
- [Usage guide](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md) -- inputs, triggers, structured outputs
- [Security](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md) -- access control, commit signing

### Looking Up Action Docs via `gh`

```bash
gh api repos/anthropics/claude-code-action/readme --jq '.content' | base64 -d

gh api repos/anthropics/claude-code-action/contents/action.yml --jq '.content' | base64 -d

gh api repos/anthropics/claude-code-action/contents/docs/solutions.md --jq '.content' | base64 -d
```

---

## Permission Matrix

Request minimum GitHub permissions. `id-token: write` is always required for OIDC auth.

```yaml
permissions:
  # Interactive @claude mentions (comment-triggered)
  contents: read
  pull-requests: read
  issues: read
  id-token: write

  # PR review (read PR + post comment)
  contents: read
  pull-requests: write
  id-token: write

  # Issue triage (label + comment)
  contents: read
  issues: write
  id-token: write

  # Code changes (edit files + push)
  contents: write
  pull-requests: write
  id-token: write

  # CI/CD debugging (view workflow logs)
  actions: read
  id-token: write
```

When a step uses a Personal Access Token (PAT) to push to another repo, that step
does not need elevated `contents: write` on the current workflow -- the PAT handles
auth independently.

For CI debugging, also pass `additional_permissions`:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    additional_permissions: |
      actions: read
```

### Commit Signing

Enable signed commits for auditability:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    use_commit_signing: true
    # or for full git CLI support (rebasing, cherry-pick):
    # ssh_signing_key: ${{ secrets.SSH_SIGNING_KEY }}
    # bot_id: "41898282"
    # bot_name: "claude[bot]"
```

---

## Tool Configuration

Use `claude_args` with `--allowedTools` and `--disallowedTools` to control what Claude
can do. By default, Claude has access to file operations and GitHub APIs but NOT
arbitrary Bash commands.

```yaml
# Read-only audit
claude_args: |
  --allowedTools Read,Glob,Grep,Bash

# Review + comment
claude_args: |
  --allowedTools Read,Write,Glob,Grep,Bash

# Full edit + PR creation
claude_args: |
  --allowedTools Read,Write,Edit,Glob,Grep,Bash

# Allow specific Bash commands only
claude_args: |
  --allowedTools "Read,Glob,Grep,Bash(npm test),Bash(npm run lint)"
```

### Permissions via Settings

For granular allow/deny control, use the `settings` input. Settings support permissions,
model overrides, environment variables, and pre/post tool execution hooks:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    settings: |
      {
        "permissions": {
          "allow": ["Bash", "Read", "Write", "Edit"],
          "deny": ["WebFetch"]
        }
      }
```

Full `settings` shape (all fields optional):

```yaml
settings: |
  {
    "model": "claude-sonnet-4-6",
    "env": {"NODE_ENV": "test", "CI": "true"},
    "permissions": {"allow": ["Bash", "Read"], "deny": ["WebFetch"]},
    "hooks": {
      "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo running..."}]}]
    }
  }
```

Use `claude_args` for simple overrides and `settings` for complex configurations with
hooks and environment variables. `claude_args` takes precedence over `settings`.

---

## Model and Turn Configuration

Pass model and turn limits via `claude_args`:

```yaml
claude_args: |
  --model claude-sonnet-4-6
  --max-turns 12
```

| Task | Model | `--max-turns` |
|------|-------|--------------|
| Issue triage (classify + label) | `claude-haiku-4-5-20251001` | 5 |
| PR review (comment) | `claude-sonnet-4-6` | 12 |
| Complex document generation | `claude-sonnet-4-6` | 30 |
| Multi-file code changes | `claude-sonnet-4-6` | 50 |

Keep `--max-turns` as low as the task requires -- lower turns = lower cost + faster runs.

---

## File-Based Output Pattern

Write Claude output to `/tmp/` then post with `--body-file` to avoid shell escaping
issues with colons, backticks, and special characters in issue/PR comments.

```yaml
steps:
  - uses: anthropics/claude-code-action@v1
    with:
      claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
      claude_args: |
        --model claude-sonnet-4-6
        --max-turns 12
        --allowedTools Read,Write,Glob,Grep,Bash
      prompt: |
        Review the PR diff. Write a concise review to /tmp/review.md.
        Check: valid structure, English language, no personal data.

  - name: Post review comment
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      gh pr comment ${{ github.event.pull_request.number }} \
        --body-file /tmp/review.md
```

---

## Structured Outputs

Use `--json-schema` to get validated JSON results from Claude that become GitHub Action
outputs. Useful for automation workflows where subsequent steps depend on Claude's analysis.

```yaml
- name: Analyze test failures
  id: analyze
  uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    claude_args: |
      --json-schema '{"type":"object","properties":{"is_flaky":{"type":"boolean"},"confidence":{"type":"number"},"summary":{"type":"string"}},"required":["is_flaky"]}'
    prompt: |
      Check the CI logs and determine if this is a flaky test.

- name: Retry if flaky
  if: fromJSON(steps.analyze.outputs.structured_output).is_flaky == true
  run: gh workflow run CI
```

Access fields via `fromJSON(steps.<id>.outputs.structured_output).<field>`.

---

## MCP Server Configuration

Add custom MCP servers to extend Claude's capabilities using `claude_args --mcp-config`:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    claude_args: |
      --mcp-config '{"mcpServers":{"sequential-thinking":{"command":"npx","args":["-y","@modelcontextprotocol/server-sequential-thinking"]}}}'
      --allowedTools mcp__sequential-thinking__sequentialthinking
```

For servers that need secrets, write a config file first:

```yaml
- name: Create MCP config
  run: |
    cat > /tmp/mcp-config.json << 'EOF'
    {
      "mcpServers": {
        "custom-server": {
          "command": "npx",
          "args": ["-y", "@example/server"],
          "env": {
            "API_KEY": "${{ secrets.CUSTOM_API_KEY }}"
          }
        }
      }
    }
    EOF

- uses: anthropics/claude-code-action@v1
  with:
    claude_args: |
      --mcp-config /tmp/mcp-config.json
```

If the repo has a `.mcp.json` at the root, Claude automatically uses it.

---

## Plugins

Extend Claude with plugins from marketplaces:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    plugin_marketplaces: "https://github.com/user/marketplace.git"
    plugins: "code-review@claude-code-plugins"
```

Marketplaces are added before plugin installation. Newline-separate multiple entries.

---

## Workflow Features

### Progress Tracking

Enable visual checkboxes that update as Claude completes tasks:

```yaml
track_progress: true
```

Only works with `pull_request` and `issue` events (opened, synchronize, ready_for_review,
reopened, edited, labeled, assigned).

### Fix Links in PR Reviews

Include "Fix this" links in review feedback that open Claude Code with context (enabled
by default):

```yaml
include_fix_links: true   # default
```

### Sticky Comments

Use a single comment that updates in place instead of posting multiple comments:

```yaml
use_sticky_comment: true
```

### Bot Triggers

Allow bot users to trigger the action:

```yaml
allowed_bots: "dependabot[bot],renovate[bot]"
# or allow all bots:
allowed_bots: "*"
```

### Base Branch

Override the default branch when Claude creates new branches:

```yaml
base_branch: develop
```

### Session Resumption

The action outputs a `session_id` that can be used to continue conversations:

```yaml
- name: Initial analysis
  id: first_run
  uses: anthropics/claude-code-action@v1
  with:
    prompt: "Analyze this codebase"

- name: Follow-up
  uses: anthropics/claude-code-action@v1
  with:
    claude_args: |
      --resume ${{ steps.first_run.outputs.session_id }}
    prompt: "Now fix the issues you found"
```

---

## `gh` CLI Critical Patterns

```bash
# Labels: one --add-label flag per label (NOT comma-separated -- gh ignores extras)
gh issue edit $N --add-label "type:feat" --add-label "priority:2"

# Post a comment from a file
gh pr comment $PR --body-file /tmp/output.md
gh issue comment $N --body-file /tmp/output.md

# Check if a PR already exists (avoid duplicates in scheduled workflows)
gh pr list --head "$BRANCH" --json number --jq '.[0].number'
```

---

## Preventing Infinite Loops

Workflows that auto-commit must include `[skip ci]` in the commit message to prevent
the push from re-triggering the same workflow.

```yaml
- uses: stefanzweifel/git-auto-commit-action@v5
  with:
    commit_message: "chore: auto-update [skip ci]"
```

Also filter the actor to avoid triggering on your own bot's commits:

```yaml
on:
  push:
    branches: [main]
jobs:
  sync:
    if: github.actor != 'github-actions[bot]'
```

---

## Testing: Local with `act`

`act` runs GitHub Actions workflows locally using Docker.

```bash
# Install act
brew install act
# or: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash

# Run a specific workflow against a pull_request event
act pull_request -W .github/workflows/review.yml

# Simulate an issue event with a custom payload
act issues -e .github/test-events/issue-opened.json \
  -W .github/workflows/triage.yml

# Pass secrets
act pull_request \
  -s CLAUDE_CODE_OAUTH_TOKEN=<token> \
  -W .github/workflows/review.yml
```

Store test event JSON payloads in `.github/test-events/` (add to `.gitignore` if they
contain tokens or real data).

Example `.github/test-events/issue-opened.json`:

```json
{
  "action": "opened",
  "issue": {
    "number": 99,
    "title": "Test issue for act",
    "body": "This is a test issue body.",
    "labels": []
  }
}
```

---

## Testing: GitHub UI Patterns

### `workflow_dispatch` trigger for manual runs

Add to any workflow to enable the "Run workflow" button in the Actions tab:

```yaml
on:
  pull_request:
    types: [opened, synchronize]
  workflow_dispatch:
    inputs:
      pr_number:
        description: 'PR number to review'
        required: true
        type: number
```

### Draft PRs for PR-scoped workflows

Open a draft PR targeting a test branch (not `main`). This triggers `pull_request`
events without merging. Close the draft when done.

### Reading logs

**Actions tab** -> select a run -> expand individual steps. Claude's tool calls and
output are logged step-by-step. Look for the `claude-code-action` step for model output
and any error messages.

---

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `403 Forbidden` on `gh` commands | PAT missing required scope or wrong repo target | Check token scopes in GitHub Settings |
| `id-token: write` permission error | Missing from `permissions:` block | Add `id-token: write` at job level |
| Claude writes nothing, exits early | Prompt too vague or `--max-turns` too low | Add explicit output file path to prompt; increase `--max-turns` |
| Tool not allowed error | Tool missing from `--allowedTools` | Add the tool to `claude_args: "--allowedTools Tool1,Tool2"` |
| Labels not applied (silent) | `--add-label` args comma-separated | Use one `--add-label` flag per label |
| Workflow triggers itself after auto-commit | Missing `[skip ci]` in commit message | Add `[skip ci]` suffix to auto-commit messages |
| Deprecated input warning | Using old v0.x inputs (`model`, `allowed_tools`, `max_turns`) | Migrate to `claude_args` (see Migration table below) |

### v0.x to v1.0 Input Migration

| Deprecated Input | v1.0 Equivalent |
|-----------------|----------------|
| `allowed_tools` | `claude_args: "--allowedTools Read,Write,Edit"` |
| `disallowed_tools` | `claude_args: "--disallowedTools WebSearch"` |
| `max_turns` | `claude_args: "--max-turns 10"` |
| `model` | `claude_args: "--model claude-sonnet-4-6"` |
| `dangerously_skip_permissions` | Removed. Use `settings` with `permissions.allow` or `claude_args --allowedTools` |
| `custom_instructions` | `claude_args: "--system-prompt 'Your instructions'"` or use `prompt` |
| `mcp_config` | `claude_args: "--mcp-config '{...}'"` |
| `direct_prompt` | `prompt` |
