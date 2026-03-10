---
name: markdown-convert
description: Convert any Markdown file to PDF or DOCX, stripping Obsidian-specific syntax (wikilinks, embeds, callouts, Relations section) before export.
---

# markdown-convert

General-purpose Markdown → PDF / DOCX converter. Cleans all Obsidian-specific syntax before export so no internal vault references leak into shared documents.

Use this skill for any note, meeting note, goal doc, task doc, memo, or other vault file that needs to be shared externally.

## Setup

### Install dependencies

With pip or uv:

```bash
pip install obsidian-export
```

With pixi (recommended — gets pandoc, tectonic, nodejs from conda-forge):

```toml
[workspace]
channels = ["conda-forge"]
name = "markdown-convert"
platforms = ["linux-64"]
version = "0.1.0"

[dependencies]
python = ">=3.12,<3.15"
pandoc = ">=3.5,<4"
tectonic = ">=0.15,<0.16"
nodejs = ">=20,<22"
librsvg = ">=2.58,<3"

[pypi-dependencies]
obsidian-export = ">=0.9,<1"
pyyaml = ">=6.0,<7"
```

Run `pixi install` after creating the file.

### Install Mermaid CLI (for diagrams)

One-time setup after Node.js is installed:

```bash
npm install --prefix .mmdc @mermaid-js/mermaid-cli
```

This places mmdc at `.mmdc/node_modules/.bin/mmdc`. Update `mmdc_bin` in your config if you install it elsewhere.

### Create config

Copy `skills/markdown-convert/references/config-example.yaml` to `config.yaml` and adjust as needed. All fields are required — there are no defaults.

## Running

Convert a Markdown file using the `obsidian-export` CLI:

```bash
# PDF
obsidian-export convert \
  --input /path/to/note.md \
  --format pdf \
  --output /tmp/note.pdf \
  --profile config.yaml

# DOCX
obsidian-export convert \
  --input /path/to/note.md \
  --format docx \
  --output /tmp/note.docx \
  --profile config.yaml
```

| Argument | Description |
|----------|-------------|
| `--input` | Absolute path to source `.md` file |
| `--format` | `pdf` or `docx` |
| `--output` | Absolute path for output file (parent dirs created automatically) |
| `--profile` | Path to config YAML (relative to CWD or absolute) |

## Pipeline (4 stages)

| Stage | What happens |
|-------|-------------|
| Stage 1: Vault | Parse frontmatter, resolve `![[embed]]` inline, strip Obsidian syntax |
| Stage 2: Preprocess | Escape currency `$`, convert callouts to fenced divs, handle URLs |
| Stage 3: Mermaid | Render ` ```mermaid ` blocks to PNG via mmdc |
| Stage 4: Pandoc | PDF via tectonic XeLaTeX + Lua filters, or DOCX |

## Obsidian Stripping

Applied automatically on every conversion:

| Syntax | Result |
|--------|--------|
| `![[embed]]` | Resolved inline (content inlined); missing embeds → warning block |
| `[[Entity\|Display]]` | Replaced with `Display` |
| `[[Entity]]` | Replaced with `Entity` |
| `> [!note]` callouts | Converted to coloured tcolorbox (PDF) or blockquote (DOCX) |
| `## Relations` section | Removed entirely |
| YAML frontmatter | Removed; `title` used as document title; `tags` → `keywords` |

**Dollar sign safety:** `$25/user/month` renders as a literal dollar sign in the PDF. The `gfm-tex_math_dollars` from_format and Stage 2 escaping both prevent `$` from being interpreted as LaTeX math.

## Mermaid Diagrams

Mermaid code blocks are automatically rendered to PNG before pandoc processes the document. All output formats use PNG at `--scale 3` for high resolution. The raw mermaid source never appears in the output.

If mmdc is not installed, conversion fails with an actionable error message.

## Format Selection

| Use case | Format |
|----------|--------|
| Final sharing (email, upload) | PDF |
| Collaborative editing | DOCX |
| Archive / filing | PDF |
| Handing off for editing | DOCX |

## Dependencies

| Package | Source | Purpose |
|---------|--------|---------|
| `pandoc >=3.5,<4` | conda-forge | Markdown → PDF / DOCX conversion |
| `tectonic >=0.15,<0.16` | conda-forge | XeLaTeX PDF engine (downloads TeX packages on first use) |
| `nodejs >=20,<22` | conda-forge | Runtime for mmdc (Mermaid CLI) |
| `librsvg >=2.58,<3` | conda-forge | SVG rendering support |
| `obsidian-export` | PyPI | Core pipeline library (https://pypi.org/project/obsidian-export/) |
| `@mermaid-js/mermaid-cli` | npm (local) | Mermaid → PNG rendering (installed manually) |

## First-Run Note (tectonic)

Tectonic downloads required TeX packages from the network on first use and caches them locally. Subsequent runs are fully offline. Ensure network access is available the first time you run a PDF conversion on a new machine.

## Custom Styles (Brand Profiles)

The `obsidian-export` library supports custom LaTeX style profiles for branded output. To add a custom profile:

1. Create a style directory: `styles/<name>/`
2. Add a `header.tex` LaTeX preamble template
3. Reference it in a profile config (e.g., `profiles/<name>.yaml`) with `style.name: "<name>"`
4. Pass `--profile profiles/<name>.yaml` to `obsidian-export convert`

See the [obsidian-export documentation](https://pypi.org/project/obsidian-export/) for style authoring details.
