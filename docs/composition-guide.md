# Composition Guide

Three approaches for integrating the Agentic Engineering Kit into your project. Choose based on your team's workflow and update preferences.

## Approach 1: Git Subtree (Recommended for Teams)

Git subtree embeds the kit's code directly into your repository. All contributors get it automatically on `git clone` -- no extra initialization steps needed.

### Initial Setup

```bash
git subtree add --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git main --squash
```

This creates a `.agentic-kit/` directory in your project with the full kit contents. The `--squash` flag combines the kit's history into a single commit for a cleaner log.

### Updating

Pull in upstream changes:

```bash
git subtree pull --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git main --squash
```

To pin to a specific version instead of `main`:

```bash
git subtree add --prefix=.agentic-kit \
  https://github.com/neuralsignal/agentic-engineering-kit.git v0.1.0 --squash
```

### Using Kit Components with Subtree

After adding the subtree, you can either:

**Option A: Symlink individual files** from `.agentic-kit/` to where they need to be:

```bash
# Symlink the constitution to project root
ln -s .agentic-kit/CONSTITUTION.md CONSTITUTION.md

# Symlink specific rules
ln -s ../.agentic-kit/rules/planning-protocol.md rules/planning-protocol.md
```

**Option B: Use the install script** to copy components out of the subtree:

```bash
.agentic-kit/install.sh constitution --target .
.agentic-kit/install.sh --all --target . --setup-platform cursor --setup-platform claude
```

**Option C: Point your agent config** at the subtree directory directly. For example, in `CLAUDE.md`:

```markdown
See `.agentic-kit/CONSTITUTION.md` for the engineering constitution.
```

### Pros and Cons

| Pros | Cons |
|------|------|
| Self-contained -- works for all contributors | Adds files to your repo's history |
| No extra tooling or init steps | Subtree merges can be complex on updates |
| Version-pinnable via git tags | Requires git subtree knowledge |
| Full offline access | |

## Approach 2: Manual Copy (Simplest)

Download individual files directly into your project. No git plumbing required.

### Using curl

```bash
# Download the constitution
curl -O https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/CONSTITUTION.md

# Download a specific rule (future)
mkdir -p rules
curl -o rules/planning-protocol.md \
  https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/main/rules/planning-protocol.md

# Pin to a version
curl -O https://raw.githubusercontent.com/neuralsignal/agentic-engineering-kit/v0.1.0/CONSTITUTION.md
```

### From a Local Clone

```bash
git clone https://github.com/neuralsignal/agentic-engineering-kit.git /tmp/aek
cp /tmp/aek/CONSTITUTION.md ~/my-project/
cp -r /tmp/aek/rules/planning-protocol.md ~/my-project/rules/
rm -rf /tmp/aek
```

### Pros and Cons

| Pros | Cons |
|------|------|
| Zero setup, zero dependencies | No automatic updates |
| Full control over what you include | Must manually check for new versions |
| No git history bloat | Easy to diverge from upstream |

## Approach 3: Install Script (Selective + Platform Setup)

The install script combines selective component installation with platform-specific directory structure setup.

### Prerequisites

Clone the kit repo (or add it as a subtree):

```bash
git clone https://github.com/neuralsignal/agentic-engineering-kit.git
```

### Usage

```bash
cd agentic-engineering-kit

# List available components
./install.sh --list

# Install specific components
./install.sh constitution --target ~/my-project

# Install everything
./install.sh --all --target ~/my-project

# Set up platform symlinks (works with any name)
./install.sh --setup-platform cursor --target ~/my-project
./install.sh --setup-platform claude --target ~/my-project

# Combine: install + platform setup
./install.sh constitution --target ~/my-project --setup-platform cursor

# Preview without making changes
./install.sh --all --target ~/my-project --dry-run

# Overwrite existing files
./install.sh constitution --target ~/my-project --force
```

### What `--setup-platform` Does

Creates a `.<name>/` directory with symlinks to the canonical locations:

```
my-project/
├── rules/                           <- canonical
├── skills/                          <- canonical
├── agents/                          <- canonical
└── .<name>/
    ├── rules/   --symlink-->  rules/
    ├── skills/  --symlink-->  skills/
    └── agents/  --symlink-->  agents/
```

Works with any platform name -- `cursor`, `claude`, or anything else.

### Pros and Cons

| Pros | Cons |
|------|------|
| Selective installation | Requires cloning the kit repo first |
| Platform setup automation | Bash dependency (macOS/Linux/WSL) |
| Dry-run mode for safety | |
| Overwrite protection | |

## Which Approach to Choose

| Scenario | Recommended Approach |
|----------|---------------------|
| Team project, want version-locked kit | Git subtree |
| Quick personal project, grab one file | Manual copy (curl) |
| Evaluating the kit, want to try things | Install script |
| CI/CD pipeline needs specific components | Manual copy (curl with pinned version) |
| Monorepo with multiple projects | Git subtree at repo root, symlinks per project |
