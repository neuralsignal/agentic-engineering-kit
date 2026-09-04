---
description: Never attribute responsibilities or decisions to specific people unless the user has explicitly confirmed who is responsible.
alwaysApply: true
---

# No Implicit Attributions or Assumptions

Never attribute a responsibility, ownership, or a decision to a named person unless the user has
explicitly stated who is responsible. Do not guess or infer it from role, title, or prior context —
even when it seems obvious.

- **User says they don't know** ("we don't really know", "bad assumption", "remove the name") →
  remove the attribution immediately, replace with vague language: leadership, the relevant team,
  IT, legal counsel.
- **Re-add a specific name or role only on an explicit statement** ("Dana owns the budget
  decision"). Never infer it back from context.
- **Never re-introduce a removed attribution** in later edits or regenerations. Once removed at the
  user's request, the attribution stays unconfirmed until the user re-confirms it.

Wrong: `- [ ] Cloud spend approval *(Dana)*: Confirm budget…` · `- [ ] Data protection review *(Sam)*: …`
Right: `- [ ] Cloud spend approval: Confirm budget…` · `- [ ] Data protection review: Legal counsel to advise…`

Applies to any written output where ownership or responsibility is implied — documents, plans,
decisions-needed sections in executive summaries, task and action-item lists, meeting notes and
follow-ups, decision logs, ADRs, phase plans. When working with organizational knowledge documents,
check whether a named attribution already in the document was explicitly confirmed by the user; if
uncertain, use role- or team-level language instead.
