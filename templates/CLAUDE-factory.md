# CLAUDE-factory.md -- Dark Factory Template

Copy the sections below into your project's `CLAUDE.md` to enable the dark factory workflows.
Fill in the placeholders (`<...>`) with project-specific values.

---

## Dark Factory Agent Context

### Label Taxonomy

| Label | Purpose |
|-------|---------|
| `type:bug` | Bug report |
| `type:feat` | Feature request |
| `type:chore` | Maintenance / improvement |
| `priority:1` | Urgent -- implement immediately |
| `priority:2` | Normal (default) |
| `priority:3` | Backlog |
| `claude:implement` | Trigger Claude to implement this issue |
| `status:triaged` | Issue has been triaged |
| `status:in-progress` | Claude is working on this |
| `status:pr-created` | PR created, awaiting review |
| `status:pr-draft` | Draft PR created, CI pending |
| `status:blocked` | Implementation blocked (see comments) |
| `autofix:1` | First auto-fix attempt |
| `autofix:2` | Second auto-fix attempt |
| `autofix:3` | Third (final) auto-fix attempt |
| `source:dep-audit` | Created by dependency audit agent |
| `source:security-scan` | Created by security scan agent |
| `source:code-quality` | Created by code quality agent |
| `source:test-coverage` | Created by test coverage agent |
| `source:docs-freshness` | Created by docs freshness agent |
| `source:workflow-upgrade` | Created by workflow upgrade agent |

### Build & Test

- Package manager: `<pixi|pip|npm|cargo|...>`
- Install command: `<pixi install|npm install|...>`
- Test command: `<pixi run test|npm test|pytest|...>`
- Lint command: `<pixi run lint|npm run lint|...>`
- Format command: `<pixi run format|npm run format|...>`
- Coverage command: `<pixi run test-cov|npm run coverage|...>`
- Coverage threshold: 80%

### Dependency Tooling

- Audit command: `<pip audit|npm audit|cargo audit|...>`
- Lockfile: `<pixi.lock|package-lock.json|Cargo.lock|...>`
- Update command: `<pixi update|npm update|cargo update|...>`

### Security Standards

- No hardcoded secrets or tokens in source
- Input validation at all system boundaries
- <project-specific security notes>

### Documentation Standards

- README.md documents all CLI commands and configuration options
- CHANGELOG.md updated for every user-facing change
- All public functions require docstrings and type hints
- <project-specific doc standards>

### Code Quality Standards

- Maximum file length: 300 lines
- All functions have type hints
- <project-specific quality standards>

### CI Setup

Steps needed before agent workflows can run tests:

```
<e.g., pixi install, npm install, apt-get install ..., etc.>
```
