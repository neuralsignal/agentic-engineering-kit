# Dark Factory -- Agentic Software Engineering via GitHub Actions

A fully autonomous "dark factory" for software engineering using GitHub Actions + `anthropics/claude-code-action@v1`. The human's role is reduced to **reviewing and merging PRs** -- everything else is automated.

## The Autonomous Loop

```
Assessment Agents (scheduled)
  ├─ dep-audit         → finds vulnerabilities/outdated deps
  ├─ security-scan     → finds security issues
  ├─ test-coverage     → finds uncovered code
  ├─ code-quality      → finds code smells, complexity
  ├─ docs-freshness    → finds stale/missing docs
  └─ workflow-upgrade  → finds outdated actions
        │
        ▼
  Create GitHub Issues (with label `claude:implement`)
        │
        ▼
  issue-implement agent (label-triggered)
        │
        ▼
  Creates PR (feature branch, tests pass)
        │
        ▼
  pr-code-review + pr-docs-check (auto-review the PR)
        │
        ▼
  Human reviews & merges (the ONLY manual step)
```

## Workflows

### Reactive Agents (event-triggered)

| Workflow | Trigger | Model | Purpose |
|----------|---------|-------|---------|
| `claude-mention` | `@claude` in issue/PR | Sonnet | Interactive help |
| `pr-code-review` | PR opened/sync/reopened | Sonnet (plugin) | Auto code review |
| `issue-triage` | Issue opened | Haiku | Classify, label, comment |
| `pr-docs-check` | PR opened/sync | Sonnet | Documentation compliance |
| `issue-implement` | Issue labeled `claude:implement` | Sonnet (50 turns) | Implement issue as PR |

### Assessment Agents (scheduled -- create issues)

| Workflow | Schedule | Model | Creates Issues For |
|----------|----------|-------|--------------------|
| `dep-audit` | Weekly Mon 06:00 UTC | Sonnet | Outdated deps, vulnerabilities |
| `security-scan` | Weekly Wed 06:00 UTC | Sonnet | Hardcoded secrets, injection, insecure patterns |
| `code-quality` | Weekly Fri 06:00 UTC | Sonnet | Long files, complexity, duplication |
| `test-coverage` | Weekly Sun 06:00 UTC | Sonnet | Files below threshold, untested paths |
| `docs-freshness` | Monthly 1st 06:00 UTC | Haiku | Stale docs, README drift |
| `workflow-upgrade` | Monthly 1st 07:00 UTC | Haiku | Outdated action versions |

## Installation

### 1. Copy workflows

Copy desired workflow files to your project's `.github/workflows/`:

```bash
# From kit root:
cp workflows/claude-mention.yml /path/to/project/.github/workflows/
cp workflows/pr-code-review.yml /path/to/project/.github/workflows/
# ... etc.

# Or use install.sh:
./install.sh wf-claude-mention --target /path/to/project
```

### 2. Create labels

```bash
cd scripts/
./setup-labels.sh --repo owner/repo
```

### 3. Set up CLAUDE.md

Copy `templates/CLAUDE-factory.md` into your project's `CLAUDE.md` and fill in the project-specific sections (build commands, standards, etc.).

### 4. Add secrets

Add `CLAUDE_CODE_OAUTH_TOKEN` to your repo secrets (from `claude /install-github-app`).

### 5. Test

Manually dispatch each workflow from the Actions tab to verify.

## Core Design Decisions

1. **CLAUDE.md as the single customization surface** -- Every workflow prompt starts with "Read CLAUDE.md." Project-specific labels, commands, standards all live there.
2. **GitHub-native inter-agent communication** -- Assessment agents CREATE issues with `claude:implement` label; implementation agent watches for that label.
3. **File-based output** -- All Claude output to `/tmp/*.md`, posted via `--body-file` (no shell escaping bugs).
4. **No auto-merge** -- Agents create PRs, humans merge. This is the control point.
5. **No self-modifying workflows** -- Agents never edit `.github/workflows/`.
6. **Dedup via labels** -- Each assessment agent tags issues with `source:<agent-name>` and checks before creating duplicates.

## Inter-Agent Communication

| Channel | Pattern | Example |
|---------|---------|---------|
| Labels | State machine | `claude:implement` triggers implementation |
| Issues | Assessment → Implementation | dep-audit creates issue → issue-implement picks it up |
| PR comments | Review feedback | pr-code-review and pr-docs-check post reviews |
| `[skip ci]` | Loop prevention | Auto-commits don't re-trigger workflows |
| Concurrency groups | Dedup | One implementation per issue at a time |

## Permissions Matrix

| Workflow | contents | pull-requests | issues | id-token |
|----------|----------|---------------|--------|----------|
| claude-mention | read | read | read | write |
| pr-code-review | read | read | read | write |
| issue-triage | read | -- | write | write |
| pr-docs-check | read | write | -- | write |
| issue-implement | write | write | write | write |
| dep-audit | read | -- | write | write |
| security-scan | read | -- | write | write |
| code-quality | read | -- | write | write |
| test-coverage | read | -- | write | write |
| docs-freshness | read | -- | write | write |
| workflow-upgrade | read | -- | write | write |

## Customization

All customization happens in your project's `CLAUDE.md`. The workflows read CLAUDE.md at runtime for:

- **Label taxonomy** -- what labels to apply
- **Build & Test commands** -- how to run tests, lint, format
- **Quality standards** -- max file length, coverage threshold
- **Security standards** -- project-specific security rules
- **Documentation standards** -- what docs are required
- **CI Setup** -- steps needed before running tests (e.g., pixi install, npm install)

See `templates/CLAUDE-factory.md` for the full template.

## Estimated Cost

For a small-to-medium project (~15 PRs/month, ~10 issues/month):

| Category | Est. $/month |
|----------|-------------|
| Reactive agents (reviews, triage, mentions) | $7-15 |
| Assessment agents (6 scheduled) | $2-3 |
| Implementation agent (on-demand) | $5-15 |
| **Total** | **$15-35** |
