# Content Routing: Where Does This Go?

Use this reference to decide where new content belongs in the docs repo.

## Decision Tree

```
Is this about something that will be DONE?
  Yes --> GitHub Issue
  No  --> Markdown file

Is this a record of something that HAPPENED?
  Yes --> Markdown file (permanent record)
  No  --> Could be either; read on

Does it need to be ASSIGNED to someone?
  Yes --> GitHub Issue
  No  --> Markdown file

Does it need STATUS TRACKING (open/closed, in-progress/blocked)?
  Yes --> GitHub Issue
  No  --> Markdown file
```

## Quick Reference Table

| Content | Destination | Example path |
|---|---|---|
| Bug report | Issue | -- |
| Feature request | Issue | -- |
| Task or chore | Issue | -- |
| Question needing answer | Issue | -- |
| Meeting notes | Markdown | `projects/<name>/meetings/YYYYMMDD_topic.md` |
| Decision record | Markdown | `projects/<name>/decisions/YYYYMMDD_topic.md` |
| Architecture overview | Markdown | `projects/<name>/architecture.md` |
| Weekly/monthly status | Markdown | `projects/<name>/status/YYYYMMDD_status.md` |
| SOP / runbook | Markdown | `sops/<topic>.md` |
| Shared rule or standard | Markdown | `shared/rules/<rule>.md` |
| Agent skill | Directory | `shared/skills/<skill>/` |
| Project index | Markdown | `projects/<name>/README.md` |

## Anatomy of `projects/<name>/`

```
projects/<name>/
  README.md          # Project index: overview, links, current phase
  architecture.md    # Technical design decisions (living doc)
  decisions/         # Permanent decision records (ADRs)
    YYYYMMDD_topic.md
  meetings/          # Meeting notes (permanent records)
    YYYYMMDD_topic.md
  status/            # Status updates (permanent records)
    YYYYMMDD_status.md
```

## What Goes in `sops/`

Standard Operating Procedures are reusable process docs that apply across projects.
Not project-specific notes. Examples:

- `sops/incident-response.md` -- how the team handles outages
- `sops/code-review.md` -- code review expectations
- `sops/onboarding.md` -- new team member setup
- `sops/release-process.md` -- how releases are cut

## What Goes in `shared/`

Cross-project reference material used by multiple teams or agents:
- `shared/rules/` -- engineering principles, style guides
- `shared/skills/` -- agent skill files shared across projects
- `shared/agents/` -- agent definition files

## Naming Conventions

- Meeting notes, decisions, status updates: `YYYYMMDD_<slug>.md` (date prefix required)
- Architecture and READMEs: descriptive name without date (these are living docs)
- SOPs: descriptive name (`onboarding.md`, not `20260101_onboarding.md`)
- Issue titles: imperative verb phrase ("Add user authentication", "Fix login redirect")
