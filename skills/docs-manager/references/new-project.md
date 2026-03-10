# Adding a New Project

Steps to add a new project to the docs repo.

## Checklist

- [ ] Create the project label
- [ ] Create the folder structure
- [ ] Create `projects/<name>/README.md`
- [ ] Update `CLAUDE.md`
- [ ] Create the GitHub Project board item (optional)

---

## Step 1: Create the project label

```bash
gh label create "project:<name>" \
  --repo <org>/docs \
  --description "Issues for <name>" \
  --color "#0075ca"
```

Use a kebab-case slug for `<name>` that matches the folder name exactly.
Example: `project:api-gateway`, `project:mobile-app`, `project:data-pipeline`.

---

## Step 2: Create the folder structure

```bash
mkdir -p projects/<name>/decisions
mkdir -p projects/<name>/meetings
mkdir -p projects/<name>/status
```

---

## Step 3: Create `projects/<name>/README.md`

This is the project index file. Use this template:

```markdown
---
type: project-readme
date: YYYY-MM-DD
project: <name>
status: active
---

# <Project Name>

One-paragraph description of what this project is and what problem it solves.

## Status

Current phase: <phase>
Owner: <team or person>
Links: <Jira board / Notion / Confluence if applicable>

## Key Documents

- [Architecture](architecture.md)
- [Decisions](decisions/)
- [Meeting notes](meetings/)

## Open Issues

Search: [project:<name> is:open](https://github.com/<org>/docs/issues?q=label%3Aproject%3A<name>+is%3Aopen)
```

---

## Step 4: Update CLAUDE.md

Add the project to the project index table:

```markdown
## Projects

| Project | Label | Folder | Owner | Status |
|---|---|---|---|---|
| <Project Name> | `project:<name>` | `projects/<name>/` | <team> | active |
```

And add the label to the label taxonomy section.

---

## Step 5: Create the GitHub Project board item (optional)

If using GitHub Projects v2 for the team board:

```bash
# Add the project as a single-select option in the "Project" custom field
# (do this in the GitHub Projects UI -- no CLI command available)
```

Or create a dedicated board for the project if it warrants separate tracking.

---

## When a Project Is Done

1. Update `projects/<name>/README.md`: set `status: archived` in frontmatter.
2. Remove the label from new issue templates (but keep the label itself -- issues are permanent).
3. Update the project row in `CLAUDE.md` to `status: archived`.
4. Close all open issues for the project (or move to a successor project).

Do not delete the `projects/<name>/` folder. Meeting notes, decisions, and architecture
docs are permanent records.
