---
name: docs-site
description: Set up MkDocs + Material documentation with auto-generated API reference for Python packages.
---

# Documentation Site

Set up a hosted documentation site for a Python package using MkDocs, Material for MkDocs theme, and mkdocstrings for auto-generated API reference from docstrings.

## When to Use

- Python package needs a hosted documentation site
- You want auto-generated API reference from docstrings
- You want GitHub Pages deployment with CI/CD

## Prerequisites

- Python 3.12+
- Python package with Google-style docstrings
- GitHub repository with Actions enabled

## Setup Procedure

### 1. Add documentation dependencies

Add to your `pixi.toml` (or `requirements.txt` / `pyproject.toml`):

```toml
[pypi-dependencies]
mkdocs = ">=1.6,<2"
mkdocs-material = ">=9.5,<10"
mkdocstrings = {version = ">=0.27,<1", extras = ["python"]}
```

Or with pip:

```bash
pip install "mkdocs>=1.6,<2" "mkdocs-material>=9.5,<10" "mkdocstrings[python]>=0.27,<1"
```

### 2. Create `mkdocs.yml`

Place at the repo root. Replace placeholders (`<SITE_NAME>`, `<REPO_URL>`, `<PACKAGE_DIR>`) with your project values:

```yaml
site_name: <SITE_NAME>
site_url: https://<GITHUB_ORG>.github.io/<REPO_NAME>/
site_description: <DESCRIPTION>
repo_url: <REPO_URL>
repo_name: <GITHUB_ORG>/<REPO_NAME>

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.sections
    - navigation.expand
    - navigation.top
    - content.code.copy
    - search.suggest
    - search.highlight
  icon:
    repo: fontawesome/brands/github

plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          paths: [.]
          options:
            show_source: true
            show_root_heading: true
            show_symbol_type_heading: true
            members_order: source
            docstring_style: google
            show_signature_annotations: true
            separate_signature: true

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - toc:
      permalink: true
  - attr_list

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - User Guide:
    # Add your user guide pages here
    - Configuration: user-guide/configuration.md
  - API Reference:
    - Public API: reference/api.md
    # Add module reference pages here
  - Changelog: changelog.md
```

### 3. Create `docs/` skeleton

```
docs/
  index.md                    # Project pitch, badges, quick links
  getting-started/
    installation.md            # Install instructions
    quickstart.md              # First usage example
  user-guide/
    configuration.md           # Config reference
  reference/
    api.md                     # ::: your_package
  changelog.md                 # --8<-- "CHANGELOG.md" (snippets include)
```

### 4. Write API reference pages

Each API reference page uses a single mkdocstrings directive:

```markdown
# Module Name

::: your_package.module_name
```

mkdocstrings auto-generates documentation from the module's docstrings, type hints, and function signatures.

### 5. Add `site/` to `.gitignore`

### 6. Install workflows

Copy both workflows to your project's `.github/workflows/`:

- **`docs-deploy.yml`** — builds on every push/PR, deploys to GitHub Pages on push to main
- **`docs-update.yml`** — triggers on source code changes + weekly schedule, uses Claude to detect drift between code and docs, opens a PR with updates

Update the path filters in both workflows to match your package directory (replace the `src/**` TODO lines).

### 7. Enable GitHub Pages

After the first push to `main`, go to:

> **Settings -> Pages -> Source: GitHub Actions**

This is a one-time manual step. The workflow handles everything else.

## Local Development

```bash
# Preview docs with live reload
mkdocs serve
# or with pixi:
pixi run docs-serve

# Build and check for errors
mkdocs build --strict
# or with pixi:
pixi run docs-build
```

## Gotchas

- **mkdocstrings import errors**: mkdocstrings needs to import your package to read docstrings. Run `pip install -e .` (or `pixi install` with editable dep) before building docs.
- **`--strict` failures**: `--strict` treats warnings as errors. Fix all warnings (broken links, missing pages) before deploying.
- **GitHub Pages 404 on first deploy**: After the first successful deploy, you must enable GitHub Pages in repo Settings (Source: GitHub Actions). Without this, the site returns 404.
- **Path filters**: The workflow only triggers on changes to docs/, mkdocs.yml, or source code. If you add new paths to the nav, make sure the path filter in the workflow covers them.
- **Mermaid diagrams in docs**: The Material theme renders Mermaid diagrams natively via `pymdownx.superfences` custom fences. No additional plugins needed.
- **Snippets for changelog**: Use `--8<-- "CHANGELOG.md"` in `docs/changelog.md` to include the root CHANGELOG.md without duplicating it.
- **docs-update loop prevention**: The `docs-update` workflow only triggers on source code changes, NOT on `docs/**` changes. This prevents the workflow from re-triggering itself when it pushes doc updates. It also skips if an open `claude/docs-update` PR already exists.
- **FACTORY_PAT for PR creation**: The `docs-update` workflow uses `FACTORY_PAT` (not `GITHUB_TOKEN`) to create PRs so that downstream workflows (CI, code review) trigger on the PR. See the dark factory README for details on the GITHUB_TOKEN cascade limitation.
