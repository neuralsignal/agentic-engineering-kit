# Creating a New Rule

Rules are markdown files that provide always-available or contextually loaded guidance to AI coding agents. They are auto-loaded by the platform -- no manual inclusion needed.

## Architecture

Rules live in `rules/` at your project root. Platform-specific directories are symlinks pointing to this canonical location:

```
rules/                                   <- canonical (single source of truth)
.<platform-name>/rules/  --symlink-->    rules/
```

Use the install script to create the symlinks: `./install.sh --setup-platform <name>`.

## File Format

Rules are `.md` files with YAML frontmatter. To support multiple platforms from a single file, use the dual-field format:

### Always-apply rule

Loaded every session, regardless of which files are open.

```yaml
---
description: Short description for the rule picker
alwaysApply: true
---
```

- Cursor reads `alwaysApply: true`
- Claude Code loads all rules without a `paths` field unconditionally

### File-scoped rule

Loaded only when matching files are open or being edited.

```yaml
---
description: Short description for the rule picker
globs: "src/api/**"
alwaysApply: false
paths:
  - "src/api/**"
---
```

- Cursor reads `globs` for pattern matching
- Claude Code reads `paths` for pattern matching
- Use the same glob patterns in both fields
- Each platform ignores the other's field

### Frontmatter Fields

| Field | Used By | Type | Purpose |
|-------|---------|------|---------|
| `description` | Cursor | string | Shown in rule picker; used for auto-apply decisions |
| `alwaysApply` | Cursor | boolean | If true, included in every session |
| `globs` | Cursor | string | File pattern for auto-attachment |
| `paths` | Claude Code | list | File patterns for conditional loading |

## Content Guidelines

- Keep rules under 500 lines. Shorter is better -- agents deprioritize bloated rule files.
- One concern per rule file. Do not create monolithic rule files covering multiple topics.
- Use descriptive, kebab-case filenames (e.g., `git-commit-conventions.md`, `data-validation.md`).
- Write actionable instructions, not aspirational guidelines. "Do X" is better than "Consider doing X."
- Include concrete examples where helpful.
- Do not duplicate content from the constitution. Reference it instead.

## Step-by-Step

### 1. Create the file

```bash
touch rules/my-new-rule.md
```

### 2. Add frontmatter

Choose always-apply or file-scoped format (see above). Every rule must have a `description`.

### 3. Write rule content

Markdown body after the frontmatter. Structure with headings as needed.

### 4. Register in catalog (if contributing to this kit)

Add an entry to `catalog.yaml`:

```yaml
  - id: my-new-rule
    type: rule
    path: rules/my-new-rule.md
    name: My New Rule
    description: What this rule does in one sentence.
    category: engineering
    platforms: [generic]
    dependencies: []
    install_target: rules
```

## Minimal Rule Template

```markdown
---
description: <One-sentence description>
alwaysApply: true
---

# <Rule Name>

<Rule content here. Be specific and actionable.>
```
