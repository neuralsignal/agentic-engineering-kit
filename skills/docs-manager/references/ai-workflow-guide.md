# AI Workflow Guide

How to use the Claude-powered workflows in your docs repo.

## Installed Workflows

After running the setup procedure in `SKILL.md`, you have these Claude workflows active:

| Workflow | File | When it runs |
|---|---|---|
| Issue triage | `issue-triage.yml` | On every new issue opened |
| Mention handler | `claude-mention.yml` | On `@claude` in any issue/PR comment |
| Docs review | `docs-review.yml` | On PRs touching `projects/` or `sops/` |
| Issue sync | `issue-sync.yml` | On label/close events + weekly |
| Project sync | `project-sync.yml` | Daily at 02:00 UTC |
| Code sync | `code-sync-weekly.yml` | Weekly Monday 06:00 UTC |

---

## Issue Auto-Triage

**Trigger:** Every new issue opened.

**What happens:**
1. Claude reads `CLAUDE.md` for the label taxonomy and project list.
2. Applies `type:*`, `priority:*`, and `status:triage` labels.
3. Posts a triage comment explaining the classification and suggested next steps.

**What you need to do:**
- Review the triage comment.
- Assign a `project:*` label if the auto-triage missed it.
- Change `status:triage` to `status:in-progress` when someone picks it up.

---

## @claude Mention Handler

**Trigger:** Any comment containing `@claude` on an issue or PR.

**Supported commands:**

```
@claude <free-form question>
```
Claude answers using `CLAUDE.md`, `projects/`, `sops/`, and the full issue/PR context.

```
@claude extract-actions
```
On a PR adding a meeting note, Claude reads the Action Items section and creates
GitHub Issues for each action item, pre-labelled with the correct project and type.

```
@claude draft a status update for <project>
```
Claude reads open issues and recent activity for the project and generates a status
update draft as a PR comment. You can then paste it into a new file.

```
@claude summarise open issues for <project>
```
Claude lists and groups the open issues for a project, summarising status and blockers.

```
@claude review this doc
```
On a PR, Claude reviews changed docs files for: frontmatter compliance, naming
conventions, broken internal links, and content quality.

---

## Docs Review Workflow

**Trigger:** Pull requests that touch `projects/**/*.md` or `sops/**/*.md`.

**What Claude checks:**
- YAML frontmatter present and has required fields for the doc type
- File name follows `YYYYMMDD_<slug>.md` convention (for meeting notes, decisions, status)
- No wikilinks or internal vault syntax (the repo is not an Obsidian vault)
- Action Items section present in meeting notes
- Decision records have a `status:` field (accepted/superseded/archived)

**What Claude does not check:**
- Grammar or writing quality
- Whether the content is accurate

---

## Issue Sync Workflow

**Trigger:**
- When `sync-to-docs` label is applied to an issue (immediate)
- When an issue is closed (immediate)
- Weekly Sunday 03:00 UTC (full resync)

**Output:** `sync/issues/open/<number>_<slug>.md` and `sync/issues/closed/<number>_<slug>.md`

**Format of synced files:**

```markdown
---
issue: 42
title: "Fix login redirect bug"
state: open
labels: [type:bug, project:api, priority:1, status:in-progress]
assignees: [alice]
created: 2026-03-10
updated: 2026-03-11
url: https://github.com/org/docs/issues/42
---

# Fix login redirect bug

<issue body>

---
*Last synced: 2026-03-11T08:00:00Z*
```

These files are auto-generated. **Do not edit them manually.**

---

## Project Sync Workflow

**Trigger:** Daily at 02:00 UTC.

**Output:** `sync/projects/<board-slug>.md`

**Format:** Kanban-style markdown table showing all items grouped by column.
Useful for searching project state in Obsidian.

**Requirements:** `ORG_PROJECTS_TOKEN` secret with `read:org` and `read:project` scopes.

---

## Code Sync Workflow

**Trigger:** Weekly Monday 06:00 UTC, manual dispatch.

**What it does:**
1. For each registered code repo (listed in `CLAUDE.md` under `## Code Repositories`),
   fetches the latest git activity (merged PRs, tags, commit summary).
2. Compares against `projects/<name>/architecture.md` and status files.
3. Creates a PR with suggested updates to architecture docs or a new status file
   if significant changes were detected.

**Requirements:**
- `DOCS_WRITE_TOKEN` secret with `Contents: Read+Write` and `Pull requests: Read+Write`
  on this docs repo. Store it in the docs repo's secrets.
- Each code repo must list the docs repo in `CLAUDE.md` under `## Docs Repository`.

---

## Keeping CLAUDE.md Current

The workflows rely on `CLAUDE.md` as their context file. Keep it updated:

- **Add a project:** Add a row to the project index table and create the label.
- **Add a code repo:** Add an entry under `## Code Repositories`.
- **Change a label:** Update the taxonomy section; re-run triage on affected issues manually.
- **Change a SOP:** Update `sops/` and note the change in CLAUDE.md if it affects agent behaviour.
