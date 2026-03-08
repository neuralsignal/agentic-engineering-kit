# Platform Setup Guide

Most AI coding platforms auto-load rules, skills, and agents from a `.<platform-name>/` directory at the project root. This kit uses a generic symlink pattern that works with any platform.

## Architecture: Canonical Directories + Symlinks

Maintain canonical directories at your project root and symlink them into each platform's expected location:

```
my-project/
├── rules/                               <- single source of truth
├── skills/                              <- single source of truth
├── agents/                              <- single source of truth
├── .<platform-a>/
│   ├── rules/   --symlink-->  rules/
│   ├── skills/  --symlink-->  skills/
│   └── agents/  --symlink-->  agents/
└── .<platform-b>/
    ├── rules/   --symlink-->  rules/
    ├── skills/  --symlink-->  skills/
    └── agents/  --symlink-->  agents/
```

Benefits:
- One copy of each rule, skill, or agent.
- Adding a file to `rules/` makes it instantly visible to all platforms.
- `.<platform>/` directories are gitignored since they only contain symlinks.

## Using the Install Script

The install script accepts any platform name and creates the `.<name>/` symlink structure:

```bash
./install.sh --setup-platform cursor --target ~/my-project
./install.sh --setup-platform claude --target ~/my-project
```

You can set up multiple platforms and combine with component installation:

```bash
./install.sh constitution --target ~/my-project --setup-platform cursor --setup-platform claude
```

## Manual Setup

```bash
mkdir -p .<platform-name>
ln -s ../rules .<platform-name>/rules
ln -s ../skills .<platform-name>/skills
ln -s ../agents .<platform-name>/agents
```

Add to `.gitignore`:

```
.<platform-name>/rules
.<platform-name>/skills
.<platform-name>/agents
```

## Rule Frontmatter

Different platforms read different frontmatter fields. To support multiple platforms from a single rule file, include all relevant fields:

```yaml
---
description: Short description of the rule
alwaysApply: true
globs: "src/api/**"
paths:
  - "src/api/**"
---
```

| Field | Used By | Purpose |
|-------|---------|---------|
| `description` | Cursor, Claude Code | Rule description |
| `alwaysApply` | Cursor, Claude Code | Load every session when true |
| `globs` | Cursor | File pattern for auto-attachment |
| `paths` | Claude Code | File patterns for conditional loading |

Each platform ignores fields it does not recognize. Use the same glob patterns in both `globs` and `paths`.

## Generic / Other Platforms

For platforms without native rule/skill/agent support, the kit's markdown files serve as reference documentation. Copy `CONSTITUTION.md` into your project root and point your AI assistant at it.
