---
description: Citation conventions for external claims in knowledge docs
alwaysApply: true
---

# Source Citations

Cite external sources inline, immediately after the claim, in the compact form `([source](URL))`:

```markdown
Vendor X's minimum is ~$60K/year ([source](https://docs.example.com/pricing))
```

Where no exact vendor page exists, say so in the citation: `estimated ~€20–50/user/month (SME segment); no public pricing page as of 2026-03`.

For claims resting on another note, link internally instead — `Per [[vendor-landscape]], …` or `Per [vendor landscape](notes/vendor-landscape.md), …`.

A document with 3 or more external references also needs a `## Sources` section at the bottom (or immediately before a Relations section, if one exists), one bullet per source:

```markdown
## Sources

- [Brief description of what the source covers](URL)
```

**Cite:** pricing numbers (per-user costs, annual minimums, infra costs) · capability claims ("covers all data sources", "cloud-only") · data residency statements (which cloud, which region) · tool assessments in ADRs and vendor landscape docs · architecture decision rationale that cites external facts.

**Do not cite:** internal architecture decisions derived from analysis (state the reasoning instead) · facts already well-established in the doc's own analysis · phase plan dates and cost estimates derived from internal decisions.

New documents apply this from creation; existing ones are backfilled at their next substantive edit.
