---
type: meeting-note
date: <% tp.date.now("YYYY-MM-DD") %>
project: <project-slug>
attendees:
  - <name>
---

# <% tp.date.now("YYYY-MM-DD") %> — <Meeting Title>

**Project:** <project-slug>
**Attendees:** <names>
**Duration:** <HH:MM>

---

## Context

Why this meeting happened. Link to relevant issue or prior doc if applicable.

## Discussion

Key points discussed, in order.

1.
2.
3.

## Decisions

Document any decisions made. Each decision that has lasting impact should become
a separate decision record in `projects/<name>/decisions/`.

- **Decision:** <what was decided>
  **Rationale:** <why>

## Action Items

Each action item becomes a GitHub Issue. After merging this PR, comment
`@claude extract-actions` to have Claude create the issues automatically.

- [ ] <Action> — <owner> — due <YYYY-MM-DD>
- [ ] <Action> — <owner> — due <YYYY-MM-DD>

## Next Steps

Any follow-up meetings, check-ins, or milestones.
