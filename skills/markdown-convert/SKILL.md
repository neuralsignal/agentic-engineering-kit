---
name: markdown-convert
description: Convert any Markdown file to PDF or DOCX, stripping Obsidian-specific syntax (wikilinks, embeds, callouts, Relations section) before export.
---

# markdown-convert

General-purpose Markdown → PDF / DOCX converter. Cleans all Obsidian-specific syntax before export so no internal vault references leak into shared documents.

Use this skill for any note, meeting note, goal doc, task doc, memo, or other vault file that needs to be shared externally.

## Locations

| Path | Contents |
|------|----------|
| `skills/markdown-convert/` | Skill root |
| `skills/markdown-convert/scripts/convert.py` | CLI entry point (thin wrapper — delegates to obsidian-export) |
| `skills/markdown-convert/scripts/setup_mmdc.py` | One-time mmdc installer |
| `skills/markdown-convert/config.yaml` | All settings (no defaults) |
| `skills/markdown-convert/pixi.toml` | Dependencies |
| `skills/markdown-convert/.mmdc/` | Local mmdc install (gitignored, created by setup_mmdc.py) |

## Running Scripts

```bash
cd skills/markdown-convert && pixi run python scripts/convert.py \
  --input <INPUT> --format <FORMAT> --output <OUTPUT> --config config.yaml
```

Alternatively, use the `obsidian-export` CLI directly:

```bash
cd skills/markdown-convert && pixi run obsidian-export convert \
  --input <INPUT> --format <FORMAT> --output <OUTPUT> --profile config.yaml
```

## One-Time Setup (Mermaid diagrams)

After `pixi install`, install the Mermaid CLI locally:

```bash
cd skills/markdown-convert && pixi run python scripts/setup_mmdc.py
```

This installs `@mermaid-js/mermaid-cli` into `.mmdc/node_modules/` (gitignored).
Only needs to be done once per machine. If mmdc is missing, `convert.py` will
raise a clear error reminding you to run this.

## Mermaid Diagrams

Mermaid code blocks are automatically rendered to PNG before pandoc processes
the document. All output formats use PNG at `--scale 3` for high resolution.

The raw mermaid source never appears in the output. If mmdc is not installed,
conversion fails with an actionable error message.

## Script Reference

### `scripts/setup_mmdc.py`

One-time installer for the Mermaid CLI. Must be run after `pixi install`.

```bash
cd skills/markdown-convert && pixi run python scripts/setup_mmdc.py
```

### `scripts/convert.py`

Converts a Markdown file to PDF or DOCX. All arguments required.

```
convert.py --input <path> --format pdf|docx --output <path> --config <path>
```

| Argument | Description |
|----------|-------------|
| `--input` | Absolute path to source `.md` file |
| `--format` | `pdf` or `docx` |
| `--output` | Absolute path for output file (parent dirs created automatically) |
| `--config` | Path to `config.yaml` (relative to CWD or absolute) |

**Examples:**

```bash
# Convert a note to PDF
cd skills/markdown-convert && pixi run python scripts/convert.py \
  --input /path/to/my_note.md \
  --format pdf \
  --output /tmp/my_note.pdf \
  --config config.yaml

# Convert a note to DOCX
cd skills/markdown-convert && pixi run python scripts/convert.py \
  --input /path/to/my_note.md \
  --format docx \
  --output /tmp/my_note.docx \
  --config config.yaml
```

**Pipeline (4 stages via obsidian-export library):**

| Stage | What happens |
|-------|-------------|
| Stage 1: Vault | Parse frontmatter, resolve `![[embed]]` inline, strip Obsidian syntax |
| Stage 2: Preprocess | Escape currency `$`, convert callouts to fenced divs, handle URLs |
| Stage 3: Mermaid | Render ` ```mermaid ` blocks to PNG via mmdc |
| Stage 4: Pandoc | PDF via tectonic XeLaTeX + Lua filters, or DOCX |

**Obsidian stripping applied automatically:**

| Syntax | Result |
|--------|--------|
| `![[embed]]` | Resolved inline (content inlined); missing embeds → warning block |
| `[[Entity\|Display]]` | Replaced with `Display` |
| `[[Entity]]` | Replaced with `Entity` |
| `> [!note]` callouts | Converted to coloured tcolorbox (PDF) or blockquote (DOCX) |
| `## Relations` section | Removed entirely |
| YAML frontmatter | Removed; `title` used as document title; `tags` → `keywords` |

**Dollar sign safety:** `$25/user/month` renders as a literal dollar sign in the PDF.
The `gfm-tex_math_dollars` from_format and Stage 2 escaping both prevent `$` from
being interpreted as LaTeX math.

## Running Tests

```bash
cd skills/markdown-convert && pixi run pytest
```

## Dependencies

| Package | Source | Purpose |
|---------|--------|---------|
| `pandoc >=3.5,<4` | conda-forge | Markdown → PDF / DOCX conversion |
| `tectonic >=0.15,<0.16` | conda-forge | XeLaTeX PDF engine (downloads TeX packages on first use) |
| `nodejs >=20,<22` | conda-forge | Runtime for mmdc (Mermaid CLI) |
| `librsvg >=2.58,<3` | conda-forge | SVG rendering support |
| `obsidian-export` | PyPI | Core pipeline library (https://pypi.org/project/obsidian-export/) |
| `pyyaml >=6.0,<7` | PyPI (via obsidian-export) | YAML config and frontmatter parsing |
| `click >=8.0,<9` | PyPI (via obsidian-export) | CLI framework |
| `pytest >=8.0,<9` | PyPI | Test runner |
| `hypothesis >=6.0,<7` | PyPI | Property-based testing |
| `@mermaid-js/mermaid-cli` | npm (local) | Mermaid → PNG rendering (installed by setup_mmdc.py) |

## First-Run Note (tectonic)

Tectonic downloads required TeX packages from the network on first use and caches them locally. Subsequent runs are fully offline. Ensure network access is available the first time you run a PDF conversion on a new machine.

## Custom Styles (Brand Profiles)

The `obsidian-export` library supports custom LaTeX style profiles for branded output. To add a custom profile:

1. Create a style directory: `skills/markdown-convert/styles/<name>/`
2. Add a `header.tex` LaTeX preamble template
3. Reference it in a profile config (e.g., `profiles/<name>.yaml`)
4. Pass `--config profiles/<name>.yaml` to `convert.py`

See the [obsidian-export documentation](https://pypi.org/project/obsidian-export/) for style authoring details.
