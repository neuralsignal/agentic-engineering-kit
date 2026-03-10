---
name: docs-manager
description: >
  Set up and operate a GitHub-based docs repository for a software team.
  Covers the two-flow model (Issues = trackable work, Markdown = permanent records),
  label taxonomy, Obsidian Templater templates, automated issue sync, Claude-powered
  PR review, weekly code->docs sync, and GitHub Pages deployment.
---

# docs-manager

A pattern for running a shared documentation and project-management system for a software team
using a single GitHub repository, GitHub Issues, Obsidian, and Claude-powered automation.

## When to Use This Skill

Use this skill when:
- A team needs a shared docs repo with structured project tracking
- You want issues and markdown docs to stay in sync automatically
- You want Claude to triage issues, review doc PRs, and keep docs current
- You want a GitHub Pages site from the same repo

## Prerequisites

- GitHub organisation with Teams or Enterprise plan (required for private GitHub Pages)
- `CLAUDE_CODE_OAUTH_TOKEN` secret (run `claude /install-github-app` in the repo)
- For code->docs sync: a fine-grained PAT with `Contents: Read+Write` and `Pull requests: Read+Write` on the docs repo, stored as `DOCS_WRITE_TOKEN` in each code repo's secrets

## Setup Procedure

### 1. Create the repository

```bash
gh repo create <org>/docs --private --description "Team docs and project management"
```

### 2. Create labels

```bash
# Project labels (one per project -- add as needed)
gh label create "project:my-project" --repo <org>/docs \
  --description "Issues for my-project" --color "#0075ca"
gh label create "project:general" --repo <org>/docs \
  --description "Cross-project issues" --color "#0075ca"

# Type labels
gh label create "type:task"     --repo <org>/docs --color "#e4e669"
gh label create "type:bug"      --repo <org>/docs --color "#d73a4a"
gh label create "type:feature"  --repo <org>/docs --color "#a2eeef"
gh label create "type:question" --repo <org>/docs --color "#d876e3"

# Status labels
gh label create "status:triage"      --repo <org>/docs --color "#ededed"
gh label create "status:in-progress" --repo <org>/docs --color "#0075ca"
gh label create "status:blocked"     --repo <org>/docs --color "#e11d48"
gh label create "status:done"        --repo <org>/docs --color "#0e8a16"

# Priority labels
gh label create "priority:1" --repo <org>/docs --color "#b60205"
gh label create "priority:2" --repo <org>/docs --color "#fbca04"
gh label create "priority:3" --repo <org>/docs --color "#c5def5"

# Sync control
gh label create "sync-to-docs" --repo <org>/docs --color "#5319e7"
```

### 3. Create folder structure

```bash
mkdir -p sops shared/rules shared/skills shared/agents templates
mkdir -p sync/issues/open sync/issues/closed sync/projects
```

For each project:
```bash
mkdir -p projects/<name>/decisions projects/<name>/meetings projects/<name>/status
```

### 4. Create CLAUDE.md

Copy the template below and fill in your org/project values. This file is the single
source of truth for label taxonomy, project index, and agentic rules.

See `references/` for SOP files to place under `sops/`.

### 5. Install workflows

Copy from `workflows/` in this skill:
- `issue-sync.yml` -> `.github/workflows/`
- `project-sync.yml` -> `.github/workflows/`
- `docs-review.yml` -> `.github/workflows/`
- `code-sync-weekly.yml` -> `.github/workflows/` (optional, for multi-repo orgs)

Also install from the kit's `workflows/` directory:
- `issue-triage.yml` -> `.github/workflows/`
- `claude-mention.yml` -> `.github/workflows/`

### 6. Add CLAUDE_CODE_OAUTH_TOKEN

```bash
cd <docs-repo>
claude /install-github-app
```

Add the displayed token as a repo/org secret named `CLAUDE_CODE_OAUTH_TOKEN`.

### 7. Create GitHub Project board

1. Go to `github.com/orgs/<org>/projects/new`
2. Name it `Team Board` (or per-project boards)
3. Link the docs repo
4. Configure columns: `Backlog`, `In Progress`, `In Review`, `Done`
5. Add custom fields: `Priority` (single select: 1, 2, 3), `DRI` (text)

### 8. Enable GitHub Pages (Teams/Enterprise only for private repos)

Settings -> Pages -> Source: **GitHub Actions**

Install `docs-deploy.yml` from the kit's `workflows/` directory, adapted for your
content paths. For a content-only repo (no Python package), remove `pip install -e .`
and `mkdocstrings`. See `skills/docs-site/SKILL.md` for the Python-package variant.

---

## The Two-Flow Model

| Content type | Lives as | Created via | Lifecycle |
|---|---|---|---|
| Task / feature / bug | GitHub Issue | GitHub UI with template | Open -> triage -> in-progress -> done |
| Question | GitHub Issue | GitHub UI | Open -> answered -> close |
| Meeting note | `projects/<name>/meetings/YYYYMMDD_*.md` | Obsidian Templater | Permanent record |
| Decision record | `projects/<name>/decisions/YYYYMMDD_*.md` | Obsidian Templater | Permanent record |
| Architecture doc | `projects/<name>/architecture.md` | Any editor | Living doc, versioned via git |
| Project status update | `projects/<name>/status/YYYYMMDD_*.md` | Obsidian Templater | Permanent record |

**Decision rule:**
- Use Issues when the item has a lifecycle, needs assignment, or tracks a deliverable
- Use markdown when the content is a permanent record (meeting happened, decision was made)

---

## Label Taxonomy

### Project labels (required on every issue)
- `project:<name>` -- one per project, kebab-case slug
- `project:general` -- cross-project issues

### Type labels (required)
- `type:task`, `type:bug`, `type:feature`, `type:question`

### Status labels (managed by workflow)
- `status:triage` -- newly opened, awaiting classification
- `status:in-progress` -- work active
- `status:blocked` -- cannot proceed
- `status:done` -- complete

### Priority labels (default: `priority:2`)
- `priority:1` -- urgent
- `priority:2` -- normal
- `priority:3` -- low / backlog

### Sync control
- `sync-to-docs` -- triggers immediate issue->markdown sync when applied

---

## YAML Frontmatter Schema

All markdown files under `projects/` require YAML frontmatter:

```yaml
---
type: <meeting-note | decision | architecture | status-update | project-readme>
date: YYYY-MM-DD
project: <project-slug>
status: <active | accepted | superseded | archived>   # decisions, project-readmes
attendees: []                                          # meeting notes only
---
```

Required fields by type:

| Type | Required fields |
|---|---|
| `meeting-note` | `type`, `date`, `project`, `attendees` |
| `decision` | `type`, `date`, `project`, `status` |
| `architecture` | `type`, `date`, `project` |
| `status-update` | `type`, `date`, `project` |
| `project-readme` | `type`, `date`, `project`, `status` |

---

## @claude Commands Reference

| Command | Where | What happens |
|---|---|---|
| `@claude extract-actions` | PR comment on a meeting note PR | Claude reads Action Items section, creates GitHub Issues |
| `@claude <question>` | Any issue or PR comment | Claude answers using CLAUDE.md, projects/, sops/ |
| `@claude draft a status update for <project>` | Issue comment | Claude generates a status update draft |
| `@claude summarise open issues for <project>` | Issue comment | Claude queries and summarises open issues |
| `@claude review this doc` | PR comment | Claude reviews the changed doc for compliance |

---

## Workflows Reference

| Workflow | Trigger | What it does |
|---|---|---|
| `issue-triage.yml` | New issue opened | Auto-labels project, type, priority, status |
| `claude-mention.yml` | `@claude` in any issue/PR comment | Invokes Claude to answer or act |
| `docs-review.yml` | PR touches docs paths | Claude reviews for frontmatter, naming, compliance |
| `issue-sync.yml` | Issue labeled/closed + weekly | Syncs issues to `sync/issues/` markdown snapshots |
| `project-sync.yml` | Daily | Syncs GitHub Project board to `sync/projects/` |
| `code-sync-weekly.yml` | Weekly Monday | Queries registered code repos, updates project docs |

---

## Obsidian Setup

The `sync/` directory makes the docs repo usable as an Obsidian vault: issues and board
state are searchable as text.

Obsidian Templater templates live in `references/templates/` in this skill. Copy them
into the docs repo's `templates/` directory. Configure Templater to use `templates/` as
the template folder.

---

## Gotchas

- **`sync/` is auto-generated** -- never edit files there manually; they are overwritten on next sync run
- **Frontmatter required** -- `docs-review.yml` flags files missing required fields
- **Pages one-time setup** -- after the first workflow push, manually enable GitHub Pages in Settings -> Pages -> Source: GitHub Actions
- **Private Pages requires Teams/Enterprise** -- GitHub Free only supports public Pages sites; private repos on Free plan cannot use Pages
- **`DOCS_WRITE_TOKEN` scope** -- must be a fine-grained PAT with `Contents: Read+Write` and `Pull requests: Read+Write` scoped only to the docs repo; not an org-wide PAT
- **Project board `ORG_PROJECTS_TOKEN`** -- `project-sync.yml` needs `ORG_PROJECTS_TOKEN` with `read:org` and `read:project` scopes to query org-level Projects v2
