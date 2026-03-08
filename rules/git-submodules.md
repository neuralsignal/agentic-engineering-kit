---
description: When and how to use git submodules
alwaysApply: false
---

# Git Submodules

Submodules are reserved for specific cases where you need to pin an external repo at a specific commit. Prefer package manager dependencies or editable installs for almost everything else.

## Decision Framework

| Situation | Correct approach |
|-----------|-----------------|
| Shared code across projects | Shared packages directory + editable install |
| External library | Package manager dependency |
| External tool or CLI | Package manager or system install |
| External repo to pin at specific commit, read-only | **Submodule** |
| External repo you want to modify | Fork it, submodule the fork |
| Large binary data or models | Git LFS or a download script |

## Directory Convention

All submodules live under `external/<repo-name>/`. Never place submodules inside `skills/`, `packages/`, `agents/`, or `rules/`.

```
external/
  <repo-name>/    <- submodule root
```

## Add a Submodule

```bash
git submodule add <url> external/<repo-name>
git submodule update --init --recursive
git add .gitmodules external/<repo-name>
git commit -m "chore: add <repo-name> as submodule"
```

## Clone with Submodules

```bash
git clone --recurse-submodules <url>
# or if already cloned without --recurse-submodules:
git submodule update --init --recursive
```

## Update a Submodule to a Newer Commit

Always pin to a SHA or tag, never to a branch name. A branch pointer drifts; a SHA is permanent.

```bash
cd external/<repo-name>
git fetch
git checkout <commit-sha-or-tag>
cd ../..
git add external/<repo-name>
git commit -m "chore: update <repo-name> to <sha-short>"
```

Push order matters — submodule remote first, then parent:

```bash
cd external/<repo-name> && git push && cd ../..
git push
```

## Remove a Submodule

Four steps required. All four must complete or git state is left inconsistent.

```bash
git submodule deinit -f external/<repo-name>
git rm -f external/<repo-name>
rm -rf .git/modules/external/<repo-name>
git commit -m "chore: remove <repo-name> submodule"
```

Verify `.gitmodules` no longer contains the entry after `git rm`.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Detached HEAD inside submodule | Expected — create a branch explicitly if you need to commit inside the submodule |
| Pushed parent but not submodule | Always push the submodule first |
| `git status` shows submodule modified with no apparent changes | Run `git submodule update --init external/<name>` |
| Forgot `--recursive` on nested submodules | Always pass `--recursive` to `update --init` |
| Cloned without `--recurse-submodules` | Run `git submodule update --init --recursive` |
