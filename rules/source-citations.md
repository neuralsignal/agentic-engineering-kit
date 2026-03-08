---
description: Source citation conventions for knowledge docs and notes
alwaysApply: true
---

# Source Citations

Rules for citing external sources in knowledge base documents.

## Inline Citations

For any external pricing number, capability claim, or vendor assessment, add an inline hyperlink immediately after the claim:

```markdown
Glean minimum is ~$60K/year ([source](https://docs.glean.com/...))
```

Use the format `([source](URL))` for a compact inline citation.

## Sources Section

Any document with 3 or more external references must have a `## Sources` section at the bottom (or immediately before a Relations section if one exists).

Format:
```markdown
## Sources

- [Brief description of what the source covers](URL)
- [Brief description](URL)
```

When exact vendor pricing pages are unavailable, note estimates explicitly:
```markdown
- top.legal pricing: estimated ~€20–50/user/month (DACH SME segment); no public pricing page as of 2026-03
```

## Internal Sources

For claims based on other notes in the knowledge base, use either a wikilink or a standard markdown link:

```markdown
Per [[vendor-landscape]], Glean costs ~$60K/year minimum.
Per [vendor landscape](notes/vendor-landscape.md), Glean costs ~$60K/year minimum.
```

## Scope

Apply to:
- Pricing numbers (per-user costs, annual minimums, infra costs)
- Capability claims ("covers all data sources", "cloud-only")
- Data residency statements (which cloud, which region)
- Tool assessments in ADRs and vendor landscape docs
- Architecture decision rationale that cites external facts

## Existing Docs

Backfill source citations at the next substantive edit of an existing document. New documents: apply from creation.

## What NOT to Cite

- Internal architecture decisions derived from analysis (no source needed — state the reasoning)
- Facts already well-established in the doc's own analysis
- Phase plan dates and cost estimates derived from internal decisions
