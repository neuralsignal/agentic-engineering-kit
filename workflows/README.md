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
  Creates Draft PR (feature branch)
        │
        ▼
  CI runs on draft PR
        │
    ┌───┴───┐
    ▼       ▼
  PASS    FAIL
    │       │
    ▼       ▼
  pr-autofix (ready job)    pr-autofix (fix job)
  promotes draft → ready    reads logs, fixes code, pushes
    │                         │ (max 3 attempts)
    ▼                         │
  pr-code-review +            ▼
  pr-docs-check             CI re-runs → PASS → promote
  (auto-review)               or → 3 failures → status:blocked
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
| `pr-docs-check` | PR opened/sync/ready | Sonnet | Documentation compliance |
| `issue-implement` | Issue labeled `claude:implement` | Opus (50 turns) | Implement issue as draft PR |
| `pr-autofix` | CI completes on `claude/` branch | Sonnet (30 turns) | Fix CI failures on agent PRs, promote drafts on pass |
| `factory-orchestrator` | Hourly schedule + manual | Shell only (no LLM) | Sweep orphaned issues, retry blocked, update dashboard |

### Assessment Agents (scheduled -- create issues)

| Workflow | Schedule | Model | Creates Issues For |
|----------|----------|-------|--------------------|
| `dep-audit` | Weekly Mon 06:00 UTC | Sonnet (30 turns) | Outdated deps, vulnerabilities |
| `security-scan` | Weekly Wed 06:00 UTC | Opus (30 turns) | Hardcoded secrets, injection, insecure patterns |
| `code-quality` | Weekly Fri 06:00 UTC | Sonnet | Long files, complexity, duplication |
| `test-coverage` | Weekly Sun 06:00 UTC | Sonnet | Files below threshold, untested paths |
| `docs-freshness` | Monthly 1st 06:00 UTC | Haiku | Stale docs, README drift |
| `workflow-upgrade` | Monthly 1st 07:00 UTC | Haiku | Outdated action versions |

## Known Limitation: GITHUB_TOKEN Cascade Prevention

GitHub Actions **prevents cascading triggers** when workflows use `secrets.GITHUB_TOKEN`. If a workflow creates or labels an issue using `GITHUB_TOKEN`, the resulting `issues.labeled` event does **not** trigger other workflows. This is by design to prevent infinite loops, but it breaks the autonomous loop:

```
Assessment agent (GITHUB_TOKEN) creates issue with claude:implement label
  → issues.labeled event is suppressed
  → issue-implement.yml never fires
  → Issue sits orphaned forever
```

**Fix**: Two mitigations:

1. **`issue-implement` creates PRs with `FACTORY_PAT`** — the draft PR creation and branch push events fire CI and other downstream workflows. Without this, CI never runs on agent-created PRs, and the auto-fix loop is dead.
2. **`factory-orchestrator` re-labels orphaned issues with `FACTORY_PAT`** — assessment agents create issues with `GITHUB_TOKEN`, so the `claude:implement` label event is suppressed. The orchestrator detects these orphaned issues hourly and re-applies the label using `FACTORY_PAT`, which does fire `issue-implement`.

## Prerequisites

Before installing the dark factory workflows, ensure:

- **`gh` CLI installed and authenticated** — required for `setup-factory.sh` and for monitoring workflow runs. Run `gh auth status` to verify.

- **`CLAUDE_CODE_OAUTH_TOKEN`** — an OAuth token that grants Claude Code permission to act on your repo. Generate it by running `claude /install-github-app` locally, then store the token as a repository secret (see Installation step 4).

- **`FACTORY_PAT`** — a personal access token used by `issue-implement` (PR creation) and `factory-orchestrator` (issue re-labeling) to bypass the GITHUB_TOKEN cascade limitation. Create a fine-grained PAT scoped to the target repo with read/write permissions for: actions, commit statuses, issues, and pull requests. Store as a repository secret named `FACTORY_PAT`. **Note**: fine-grained PATs have [known issues with label operations on public repos](https://github.com/cli/cli/issues/9166). If label operations fail, fall back to a classic PAT with `public_repo` scope.

- **`GITHUB_TOKEN`** — automatically provided by GitHub Actions to every workflow run. No setup needed. The workflows reference it as `${{ secrets.GITHUB_TOKEN }}`.

- **Workflow permissions** — GitHub Actions must have **read and write permissions** on the repository, and the option **"Allow GitHub Actions to create and approve pull requests"** must be enabled. Configure this at:

  > **Settings → Actions → General → Workflow permissions**

  Without this:
  - `issue-implement` will fail when attempting to create PRs (`"GitHub Actions is not permitted to create or approve pull requests"`)
  - `pr-code-review` will fail when posting review comments (insufficient write access to pull-requests)

## Installation

### 1. Run setup script

```bash
cd scripts/
./setup-factory.sh --repo owner/repo
```

This creates labels, the `[Factory Dashboard]` issue, and checks that required secrets are configured.

### 2. Copy workflows

Copy desired workflow files to your project's `.github/workflows/`:

```bash
# From kit root:
cp workflows/claude-mention.yml /path/to/project/.github/workflows/
cp workflows/pr-code-review.yml /path/to/project/.github/workflows/
# ... etc.

# Or use install.sh:
./install.sh wf-claude-mention --target /path/to/project
```

### 3. Set up CLAUDE.md

Copy `templates/CLAUDE-factory.md` into your project's `CLAUDE.md` and fill in the project-specific sections (build commands, standards, etc.).

### 4. Add secrets

1. Run `claude /install-github-app` locally to generate a `CLAUDE_CODE_OAUTH_TOKEN`.
2. Create a fine-grained PAT (or classic PAT with `public_repo` scope) for `FACTORY_PAT` — see Prerequisites.
3. Navigate to your repo's **Settings → Secrets and variables → Actions**.
4. Add both `CLAUDE_CODE_OAUTH_TOKEN` and `FACTORY_PAT` as repository secrets.

`GITHUB_TOKEN` is provided automatically by GitHub Actions — no manual setup required.

### 5. Test

Verify each layer of the dark factory in order. Each step builds on the previous:

1. **`claude-mention`** — Comment `@claude` on any issue with a simple question. Expect a reply within ~60 seconds.
2. **`issue-triage`** — Open a new issue. Expect labels and a triage comment within ~30 seconds.
3. **`issue-implement`** — Add the `claude:implement` label to an issue. Expect a new branch and PR within 2-5 minutes.
4. **`pr-code-review`** — The PR from step 3 should automatically trigger a code review comment.
5. **Assessment agents** — Go to the **Actions** tab, select an assessment workflow (e.g., `dep-audit`), and click **Run workflow** to trigger manually.

Monitor workflow runs:

```bash
gh run list --repo owner/repo --limit 5
```

## Deployment Checklist

Use this checklist when deploying the dark factory to a new repository:

- [ ] `CLAUDE_CODE_OAUTH_TOKEN` secret added to repo
- [ ] `FACTORY_PAT` secret added to repo (fine-grained PAT with actions/commit-statuses/issues/PRs read/write; classic PAT with `public_repo` scope if label ops fail on public repos)
- [ ] Workflow permissions set to **Read and write** + **Allow GitHub Actions to create and approve pull requests**
- [ ] `setup-factory.sh --repo owner/repo` run (creates labels + Factory Dashboard issue)
- [ ] `CLAUDE.md` created from `templates/CLAUDE-factory.md` and customized
- [ ] Workflow files copied to `.github/workflows/` (including `factory-orchestrator.yml`)
- [ ] Smoke tests passed: mention, triage, implement, review, assessment, orchestrator

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
| Labels | Retry tracking | `autofix:1/2/3` tracks fix attempts on agent PRs |
| Issues | Assessment → Implementation | dep-audit creates issue → issue-implement picks it up |
| PR comments | Review feedback | pr-code-review and pr-docs-check post reviews |
| Draft → Ready | Quality gate | pr-autofix promotes draft PRs after CI passes |
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
| pr-autofix | write | write | write | write |
| factory-orchestrator | read | -- | write | -- |

## Customization

All customization happens in your project's `CLAUDE.md`. The workflows read CLAUDE.md at runtime for:

- **Label taxonomy** -- what labels to apply
- **Build & Test commands** -- how to run tests, lint, format
- **Quality standards** -- max file length, coverage threshold
- **Security standards** -- project-specific security rules
- **Documentation standards** -- what docs are required
- **CI Setup** -- steps needed before running tests (e.g., pixi install, npm install)

See `templates/CLAUDE-factory.md` for the full template.

## Troubleshooting

**"GitHub Actions is not permitted to create or approve pull requests"**
The `issue-implement` or `pr-code-review` workflow fails with this error. Fix: go to **Settings → Actions → General → Workflow permissions** and enable **Read and write permissions** + **Allow GitHub Actions to create and approve pull requests**.

**CI never runs on agent-created PRs (no checks reported)**
The `issue-implement` workflow creates a draft PR, but CI, `pr-code-review`, and `pr-docs-check` never trigger. This is the GITHUB_TOKEN cascade limitation — PR creation events from `GITHUB_TOKEN` are suppressed. Fix: ensure `issue-implement` uses `FACTORY_PAT` (not `GITHUB_TOKEN`) in the "Create PR" step. PAT-triggered events cascade normally. The template already uses `FACTORY_PAT` for this step.

**Auto-fix loop never triggers**
`pr-autofix` triggers on `workflow_run` completion of the CI workflow. If CI never runs (see above), `pr-autofix` never fires. Verify: (1) CI ran on the PR branch, (2) the branch starts with `claude/`, (3) CI conclusion is `failure` (for fix) or `success` (for ready).

**PR Code Review posts no review**
The `pr-code-review` workflow runs but no review comment appears. This is typically the same permissions issue — the workflow needs write access to pull-requests at the repo level, not just in the YAML `permissions:` block.

**Assessment agent hits max turns without completing**
The default `--max-turns` may be too low for projects with many dependencies or large codebases. Increase the value in the workflow YAML (e.g., `--max-turns 30`). The `dep-audit` and `security-scan` workflows ship with 30 turns by default.

**`setup-labels.sh` creates garbled labels**
Older versions of the script used `:` as a delimiter, which conflicted with label names like `claude:implement`. Ensure you're using the latest version of `setup-labels.sh`, which uses `|` as the delimiter.

**Claude can't find CLAUDE.md**
`CLAUDE.md` must be at the repository root. Ensure the checkout step in each workflow succeeds (check for `actions/checkout` errors in the workflow logs).

## Estimated Cost

For a small-to-medium project (~15 PRs/month, ~10 issues/month):

| Category | Est. $/month |
|----------|-------------|
| Reactive agents (reviews, triage, mentions) | $7-15 |
| Assessment agents (6 scheduled) | $2-3 |
| Implementation agent (on-demand) | $5-15 |
| Auto-fix agent (on CI failure) | $2-8 |
| Factory orchestrator (pure shell) | $0 |
| **Total** | **$17-43** |
