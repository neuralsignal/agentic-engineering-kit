# Issue Lifecycle

How an issue moves from creation to closure in the docs repo.

## States

```
opened
  |
  v
status:triage   <-- auto-applied by issue-triage.yml
  |
  v
status:in-progress  <-- set manually when someone picks it up
  |
  +--> status:blocked  <-- set when work cannot proceed
  |         |
  |         v
  |    (unblocked) --> status:in-progress
  |
  v
status:done  <-- set when work is complete, before closing
  |
  v
closed
```

## Label Invariants

Every open issue must have exactly:
- One `project:*` label
- One `type:*` label
- One `priority:*` label
- One `status:*` label

The triage workflow applies these automatically on open. If any are missing, apply them manually.

## Transitions

### Triage -> In Progress

```bash
gh issue edit <number> \
  --remove-label "status:triage" \
  --add-label "status:in-progress" \
  --assignee "<github-username>"
```

### In Progress -> Blocked

```bash
gh issue edit <number> \
  --remove-label "status:in-progress" \
  --add-label "status:blocked"
```

Add a comment explaining the blocker. Tag the person or team who can unblock it.

### Blocked -> In Progress

```bash
gh issue edit <number> \
  --remove-label "status:blocked" \
  --add-label "status:in-progress"
```

Add a comment noting the blocker is resolved.

### In Progress -> Done

```bash
gh issue edit <number> \
  --remove-label "status:in-progress" \
  --add-label "status:done"
gh issue close <number>
```

Or combine:
```bash
gh issue close <number> --comment "Done: <brief description of what was done>"
```

The `issue-sync.yml` workflow moves the synced file from `sync/issues/open/` to
`sync/issues/closed/` on the next run.

## Immediate Sync

To force immediate sync of an issue to a markdown snapshot:

```bash
gh issue edit <number> --add-label "sync-to-docs"
```

This triggers `issue-sync.yml` immediately via the `labeled` event.

## Linking Issues to Documents

When closing an issue that resulted in a document (meeting note, decision, architecture update):

```
Resolved by: <path/to/document.md> (commit <sha>)
```

Add this to the closing comment. It creates a permanent trail between the issue and
the document that resolved it.

## Issue Templates

Place issue templates in `.github/ISSUE_TEMPLATE/` in the docs repo.
Recommended templates:

- `task.yml` -- task with project/type/priority fields
- `bug.yml` -- bug report with steps to reproduce
- `feature.yml` -- feature request with acceptance criteria
- `question.yml` -- question with context

Each template should pre-populate the relevant labels for its type.
See the kit's `templates/` directory for starter templates.
