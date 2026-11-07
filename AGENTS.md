# agentic-engineering-kit — agent instructions

Public kit of engineering principles, rules, skills and Claude-powered GitHub workflows that other
projects install. Consumers read `catalog.yaml` and `INTEGRATING.md`; keep both accurate.

## Rules for changes

- Every installable component has an entry in `catalog.yaml`. Add, rename or remove a file → update
  its entry in the same change.
- `CONSTITUTION.md` and `rules/` are synced copies, not edited here first. Change them at the source
  and copy the result over whole.
- Skills follow the Agent Skills spec. Check before pushing:
  `python scripts/validate_skills.py --skills-dir skills` and
  `pytest scripts/test_validate_skills.py -q` (CI runs both).
- `AGENTS.md` is the instruction file the kit tells consumers to create, with `CLAUDE.md` as a
  symlink. Workflow prompts read `AGENTS.md`; keep that name consistent across `workflows/`,
  `templates/` and `skills/docs-manager/`.
- Record user-visible changes in `CHANGELOG.md` under `[Unreleased]`.
- Public repo: no internal names, hosts, or paths.

## Memory

Consolidated repo memory: `.agents/memory/` (written only by the memory dreamer; record new facts
in your inbox — auto-memory for Claude, `~/.agents/inbox/agentic-engineering-kit/` for other
harnesses). Index:

@.agents/memory/MEMORY.md
