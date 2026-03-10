---
type: status-update
date: <% tp.date.now("YYYY-MM-DD") %>
project: <project-slug>
---

# <Project Name> Status — <% tp.date.now("YYYY-MM-DD") %>

**Project:** <project-slug>
**Period:** <YYYY-MM-DD> to <YYYY-MM-DD>
**Author:** <name>

---

## Summary

One paragraph: what phase are we in, what is the overall health, what is the
main focus right now?

## Completed This Period

- <What was shipped or finished>

## In Progress

- <What is actively being worked on> — <owner> — expected <date>

## Blocked

- <What is stuck> — blocked by <what> — needs <who or what to unblock>

## Upcoming

- <What starts next period>

## Metrics (if applicable)

| Metric | This period | Prior period | Target |
|---|---|---|---|
| <metric> | | | |

## Issues

Open: [project:<name> is:open](https://github.com/<org>/docs/issues?q=label%3Aproject%3A<name>+is%3Aopen)

Closed this period: [project:<name> closed:>YYYY-MM-DD](https://github.com/<org>/docs/issues?q=label%3Aproject%3A<name>+closed%3A%3EYYYY-MM-DD)

## Notes

Any context, risks, or decisions that did not fit above.
