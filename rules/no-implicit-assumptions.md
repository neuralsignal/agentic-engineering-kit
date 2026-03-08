---
description: Never attribute responsibilities or decisions to specific people unless the user has explicitly confirmed who is responsible.
alwaysApply: true
---

# No Implicit Attributions or Assumptions

Do not attribute responsibilities, ownership, or decisions to specific named people unless the user has explicitly stated who is responsible. This applies to documents, plans, task lists, decision logs, and any other written output.

## Rule

- **Do not guess or assume** who owns a decision, action, or responsibility based on their role, title, or prior context — even if it seems obvious.
- **When the user says they don't know** who is responsible (e.g., "we don't really know", "bad assumption", "remove the name"), immediately remove the attribution and replace with vague language (e.g., "leadership", "the relevant team", "IT", "legal counsel").
- **Only re-add a specific name or role** if the user explicitly states it (e.g., "Stephan owns the budget decision"). Do not infer from context.
- **Do not re-introduce removed attributions** in subsequent edits or regenerations. Once a name is removed at the user's request, treat the attribution as unconfirmed until the user re-confirms it.

## Examples

**Wrong:**
> - [ ] Azure spend approval *(Stephan)*: Confirm budget...
> - [ ] Data protection review *(Moritz)*: ...

**Right (after user says they don't know):**
> - [ ] Azure spend approval: Confirm budget...
> - [ ] Data protection review: Legal counsel to advise...

## Application

This rule applies to:
- Decisions Needed sections in executive summaries
- Task or action item lists
- Meeting notes or follow-up summaries
- Any document where ownership or responsibility is implied

## Scope

When working with organizational knowledge documents (executive summaries, architecture decision records, phase plans), always check whether named attributions in the document have been explicitly confirmed by the user. If uncertain, use role-based or team-level language instead.
