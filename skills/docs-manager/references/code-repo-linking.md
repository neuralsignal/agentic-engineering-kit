# Code Repository Linking

How to connect code repositories to the docs repo so the code-sync workflow
can automatically surface changes and update project docs.

## Overview

The `code-sync-weekly.yml` workflow queries registered code repos for recent
activity (merged PRs, new releases, commit summaries) and opens a PR in the
docs repo with suggested documentation updates.

## Setup: Docs Repo

Add a `## Code Repositories` section to `CLAUDE.md` in the docs repo:

```markdown
## Code Repositories

| Project | Repo | Docs folder |
|---|---|---|
| api-gateway | org/api-gateway | projects/api-gateway |
| mobile-app  | org/mobile-app  | projects/mobile-app  |
```

Create a fine-grained PAT:
1. GitHub -> Settings -> Developer settings -> Fine-grained personal access tokens
2. Name: `docs-repo-writer`
3. Resource owner: your org
4. Repository access: **Only selected repositories** -> select the docs repo
5. Permissions: `Contents: Read+Write`, `Pull requests: Read+Write`
6. Add to the docs repo's secrets as `DOCS_WRITE_TOKEN`

## Setup: Each Code Repo

In each code repo's `CLAUDE.md`, add:

```markdown
## Docs Repository

org/docs
```

Add `DOCS_WRITE_TOKEN` to the code repo's secrets (same PAT, scoped to docs repo):

```bash
gh secret set DOCS_WRITE_TOKEN --repo <org>/<code-repo>
```

## What Gets Synced

The weekly sync extracts:

| Signal | Source | Mapped to |
|---|---|---|
| Merged PRs (last 7 days) | `gh pr list --state merged` | Status update or architecture note |
| New releases / tags | `gh release list` | Status update |
| Commit activity summary | `git log --oneline --since=1week` | Status update |
| Open issues with `docs-needed` label | `gh issue list --label docs-needed` | New docs tasks |

## `docs-needed` Label

Add a `docs-needed` label to the code repo:

```bash
gh label create "docs-needed" --repo <org>/<code-repo> \
  --description "This change needs documentation" --color "#0052cc"
```

When a developer opens an issue or PR that requires docs, they apply `docs-needed`.
The weekly sync picks this up and creates a task issue in the docs repo.

## Manual Trigger

To trigger a sync immediately for a specific code repo:

```bash
gh workflow run code-sync-weekly.yml \
  --repo <org>/docs \
  --field repo=<org>/<code-repo>
```

## Deduplication

The workflow skips creating a PR if an open `claude/code-sync` PR already exists.
Merge or close the open PR before the next sync run.

## Disabling Sync for a Repo

Remove the repo from the `## Code Repositories` table in `CLAUDE.md`.
The workflow reads this table on each run.
