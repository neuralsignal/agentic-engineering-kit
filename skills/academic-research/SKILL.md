---
name: academic-research
description: Scripts for academic literature review — search PubMed, Semantic Scholar, and Zotero; scaffold paper knowledge notes from metadata JSON; download and extract PDFs; export BibTeX from existing paper notes.
---

# Academic Research

Scripts for academic literature workflows. Search is performed directly via Python API clients (no MCP servers needed). These scripts handle search, knowledge base integration (note creation), PDF download/extraction, and BibTeX export.

## Locations

| Item | Path |
|------|------|
| Scripts | `skills/academic-research/scripts/` |
| Paper template | `skills/academic-research/references/template-paper.md` |
| Paper notes | `<NOTES_DIR>/YYYYMMDD_paper_*.md` |
| Literature reviews | `<NOTES_DIR>/YYYYMMDD_litreview_*.md` |

`<NOTES_DIR>` is the directory you pass to `--output-dir` / `--notes-dir`. Choose any location in your project (e.g., `notes/`, `docs/papers/`). Create it before first use.

## Running Scripts

All scripts run via pixi:

```bash
cd skills/academic-research && pixi run python scripts/<SCRIPT> <ARGS>
```

## Script Reference

### `search_pubmed.py`

Search PubMed via NCBI E-utilities. Auth: `NCBI_EMAIL` required; optional `NCBI_API_KEY` from env.

```bash
# Search by query
cd skills/academic-research && pixi run python scripts/search_pubmed.py \
    --query "retinal OCT segmentation" --limit 10

# With date range
cd skills/academic-research && pixi run python scripts/search_pubmed.py \
    --query "EHR foundation models" --limit 20 --year-start 2022 --year-end 2025

# Fetch a specific paper
cd skills/academic-research && pixi run python scripts/search_pubmed.py \
    --pmid 38000001 --limit 1

# Fetch with PubMed Central full text (if available)
cd skills/academic-research && pixi run python scripts/search_pubmed.py \
    --pmid 38000001 --limit 1 --fulltext
```

Arguments:
- `--query` or `--pmid` (mutually exclusive, one required)
- `--limit` (required): max results for `--query`
- `--year-start` / `--year-end` (optional): publication year filter
- `--fulltext` (optional, with `--pmid` only): attempt PMC full-text fetch

Output: JSON array (for `--query`) or single JSON object (for `--pmid`) to stdout.

### `search_semantic_scholar.py`

Search papers, look up by DOI/ID, get citations/references. Auth: optional `SEMANTIC_SCHOLAR_API_KEY` (warns if missing).

```bash
# Search by query
cd skills/academic-research && pixi run python scripts/search_semantic_scholar.py \
    --query "OMOP CDM clinical NLP" --limit 10

# With year filter
cd skills/academic-research && pixi run python scripts/search_semantic_scholar.py \
    --query "diabetic retinopathy deep learning" --limit 15 --year-start 2021

# Look up a specific paper (DOI, PMID, or S2 paper ID)
cd skills/academic-research && pixi run python scripts/search_semantic_scholar.py \
    --paper-id "DOI:10.1038/s41591-024-xxxx" --limit 1

# Get a paper with its citation graph
cd skills/academic-research && pixi run python scripts/search_semantic_scholar.py \
    --paper-id "DOI:10.1038/s41591-024-xxxx" --limit 1 --include-citations --include-references

# Look up an author
cd skills/academic-research && pixi run python scripts/search_semantic_scholar.py \
    --author-id 1234567 --limit 1
```

Arguments:
- `--query`, `--paper-id`, or `--author-id` (mutually exclusive, one required)
- `--limit` (required): max results for `--query`
- `--year-start` / `--year-end` (optional): publication year filter (with `--query`)
- `--include-citations` (optional, with `--paper-id`): include up to 20 citing papers
- `--include-references` (optional, with `--paper-id`): include up to 20 referenced papers

Output: JSON to stdout.

### `search_zotero.py`

Search, browse, or list the Zotero cloud library. Auth: `ZOTERO_API_KEY` + `ZOTERO_USER_ID` (required).

```bash
# Search the library
cd skills/academic-research && pixi run python scripts/search_zotero.py \
    --query "retinal segmentation" --limit 20

# List all collections
cd skills/academic-research && pixi run python scripts/search_zotero.py \
    --list-collections

# Browse all items in a collection (no query needed)
cd skills/academic-research && pixi run python scripts/search_zotero.py \
    --browse --collection-id ABC12345 --limit 20

# Browse entire library without a query
cd skills/academic-research && pixi run python scripts/search_zotero.py \
    --browse --limit 20

# Search within a specific collection
cd skills/academic-research && pixi run python scripts/search_zotero.py \
    --query "foundation models" --collection-id ABC12345 --limit 10
```

Arguments:
- `--query`, `--list-collections`, or `--browse` (mutually exclusive, one required)
- `--collection-id` (optional): restrict item fetch to this collection key
- `--limit` (optional, default 20): max results

Output: JSON array to stdout.

### `download_pdf.py`

Download a paper's PDF from open access sources and optionally extract text. Auth: `UNPAYWALL_EMAIL` env var (required only when Unpaywall fallback is needed); `ZOTERO_API_KEY` + `ZOTERO_USER_ID` when `--zotero-key` is used.

PDF source resolution order (first hit wins): (1) `open_access_pdf` URL from stdin JSON, (2) arXiv direct URL if `arxiv_id` present, (3) Unpaywall API via DOI, (4) PMC OA Web Service via `pmc_id`.

JSON fields that trigger each source:
- `open_access_pdf` (string URL or `{"url": "..."}`) -> direct download
- `arxiv_id` or `externalIds.ArXiv` -> arXiv PDF
- `doi` or `externalIds.DOI` -> Unpaywall lookup
- `pmc_id` or `externalIds.PubMedCentral` -> PMC OA Web Service API

```bash
# From Semantic Scholar / PubMed search output (pipe a single paper object)
cd skills/academic-research && echo '<paper JSON>' | pixi run python scripts/download_pdf.py \
    --output /tmp/papers/ --extract-text

# Direct URL
cd skills/academic-research && pixi run python scripts/download_pdf.py \
    --url https://arxiv.org/pdf/2401.xxxxx \
    --output /tmp/papers/ --filename mypaper --extract-text

# Direct DOI (Unpaywall lookup — requires UNPAYWALL_EMAIL)
cd skills/academic-research && pixi run python scripts/download_pdf.py \
    --doi 10.1038/s41591-024-xxxx \
    --output /tmp/papers/ --extract-text

# Download and attach to a Zotero item
cd skills/academic-research && echo '<paper JSON>' | pixi run python scripts/download_pdf.py \
    --output /tmp/papers/ --extract-text --zotero-key ABC12345
```

Arguments:
- `--url URL`, `--doi DOI`, or stdin JSON (mutually exclusive source modes)
- `--output DIR` (required): directory to save PDF (and optional text)
- `--filename SLUG` (optional): base name without extension; default = slugified title
- `--extract-text` (flag): extract text via pypdf, write `{slug}.txt` alongside PDF
- `--zotero-key KEY` (optional): attach downloaded PDF to this Zotero item

Output JSON to stdout: `{"pdf_path": "...", "text_path": "...", "source": "...", "page_count": N, "text_length": N}`

### `zotero_write.py`

All write operations against the Zotero cloud API. Auth: `ZOTERO_API_KEY` + `ZOTERO_USER_ID` (required).

```bash
# Add papers from search JSON array (pipe from search_*.py)
cd skills/academic-research && pixi run python scripts/search_semantic_scholar.py \
    --query "retinal AI" --limit 5 \
  | pixi run python scripts/zotero_write.py \
      --add-items --collection-id ABC12345

# Create a new top-level collection
cd skills/academic-research && pixi run python scripts/zotero_write.py \
    --create-collection "My Research Topic"

# Create a nested collection under a parent
cd skills/academic-research && pixi run python scripts/zotero_write.py \
    --create-collection "Benchmark Datasets" --parent-id XYZ67890

# Move an item to a collection
cd skills/academic-research && pixi run python scripts/zotero_write.py \
    --move-item ITEM_KEY --to-collection COLLECTION_KEY
```

Arguments:
- `--add-items`, `--create-collection NAME`, or `--move-item ITEM_KEY` (mutually exclusive, one required)
- `--collection-id` (with `--add-items`): place new items in this collection
- `--parent-id` (with `--create-collection`): nest under this collection key
- `--to-collection` (with `--move-item`, required): destination collection key

Output JSON varies by mode:
- `--add-items`: `[{"input_index": 0, "zotero_key": "...", "title": "..."}, ...]`
- `--create-collection`: `{"key": "...", "name": "..."}`
- `--move-item`: `{"item_key": "...", "moved_to": "..."}`

### `create_paper_note.py`

Scaffold a paper knowledge note from metadata JSON piped via stdin. Writes to the specified output directory and prints the output filepath.

```bash
# Pipe search output directly to create notes
cd skills/academic-research && pixi run python scripts/search_pubmed.py \
    --query "retinal OCT" --limit 1 \
  | pixi run python scripts/create_paper_note.py \
      --output-dir /path/to/notes \
      --date 20260310

# Or pipe a single paper object
cd skills/academic-research && echo '{
  "title": "Foundation Models for EHR",
  "authors": ["Smith J", "Jones A"],
  "year": 2024,
  "journal": "Nature Medicine",
  "doi": "10.1038/s41591-024-xxxx",
  "pubmed_id": "38000000",
  "semantic_scholar_id": "abc123",
  "source": "PubMed",
  "relevance": "high",
  "tags": ["EHR", "foundation-models"],
  "abstract": "We present..."
}' | pixi run python scripts/create_paper_note.py \
      --output-dir /path/to/notes \
      --date 20260310
```

Arguments:
- `--output-dir` (required): Directory to write the paper note into
- `--date` (required): Date prefix YYYYMMDD for the output filename

Accepts a single JSON object or a JSON array (uses first element; warns if array has multiple items).

Outputs the full path of the created note file. Automatically deduplicates filenames if a note with the same slug already exists.

### `export_bibtex.py`

Scan all `YYYYMMDD_paper_*.md` files in a directory and emit BibTeX to stdout or a file. Only notes with `type: paper` in frontmatter are included.

```bash
# Print to stdout
cd skills/academic-research && pixi run python scripts/export_bibtex.py \
    --notes-dir /path/to/notes

# Write to file
cd skills/academic-research && pixi run python scripts/export_bibtex.py \
    --notes-dir /path/to/notes \
    --output /tmp/papers.bib
```

Arguments:
- `--notes-dir` (required): Directory containing paper note markdown files
- `--output` (optional): Output `.bib` file path. If omitted, prints to stdout.

BibTeX cite keys are automatically deduplicated with `a`, `b`, `c` suffixes when collisions occur.

## Dependencies

| Package | Purpose |
|---------|---------|
| `pyyaml>=6` | Parse YAML frontmatter from paper notes |
| `pyzotero>=1.5.0` | Zotero cloud API client (read + write) |
| `requests>=2.31` | Direct HTTP calls to S2 Academic Graph API v1; PDF download (`download_pdf.py`) |
| `biopython>=1.84` | Bio.Entrez for NCBI E-utilities (PubMed) |
| `pypdf>=4.0` | PDF text extraction (`download_pdf.py`) |

## Composing Scripts

Search output pipes directly to `create_paper_note.py`. For batch note creation from a search:

```bash
# Create notes for each paper in a search result
DATE=$(date +%Y%m%d)
cd skills/academic-research
pixi run python scripts/search_pubmed.py --query "retinal AI" --limit 5 | \
  pixi run python -c "
import json, sys, subprocess
papers = json.load(sys.stdin)
for p in papers:
    result = subprocess.run(
        ['pixi', 'run', 'python', 'scripts/create_paper_note.py',
         '--output-dir', '/path/to/notes', '--date', '$DATE'],
        input=json.dumps(p).encode(),
        capture_output=True
    )
    print(result.stdout.decode().strip())
"
```

Or let the agent handle this with a loop in Bash.

## Gotchas — What Will Hang or Crash

### Things that hang

| Symptom | Cause | Fix |
|---------|-------|-----|
| `search_semantic_scholar.py --query` exits with rate limit error | Unauthenticated requests hit the 100 req/5min S2 limit; script exits immediately with HTTP 429 error | Add `SEMANTIC_SCHOLAR_API_KEY` to `.env` for 10x higher limits (1000 req/5min). |
| `search_pubmed.py` returns HTTP 400 | Invalid or expired `NCBI_API_KEY` in `.env` — NCBI rejects the request entirely rather than falling back | Comment out or remove the bad key from `.env`. Unauthenticated PubMed (3 req/sec) works fine for typical usage. |
| `download_pdf.py` hangs on a URL | Cloudflare or publisher anti-bot blocking the request | Try `--doi` with Unpaywall fallback instead. Some publishers (Elsevier, Wiley) will never serve PDFs to scripts. |

### Things that crash

| Symptom | Cause | Fix |
|---------|-------|-----|
| `requests.exceptions.Timeout` from `search_semantic_scholar.py` | S2 API did not respond within 15 seconds | Retry once. If persistent, S2 API may be down — try again later. |
| `ERROR: NCBI_EMAIL not set` | `.env` not sourced before running the script | Source `.env` first: `set -a && source .env && set +a`, or ensure the calling agent/shell loads it. |
| `ERROR: ZOTERO_API_KEY not set` | Same — env var missing | Add to `.env`. Required for all Zotero scripts. |
| `Response is not a PDF` | Publisher returned an HTML paywall page instead of a PDF | The paper is not open access. Do not retry — try a different source (Unpaywall, arXiv) or inform the user. |
| `No open-access PDF source found` | None of the 4 resolution paths (OA URL, arXiv, Unpaywall, PMC) found a PDF | The paper is paywalled. Provide `--url` if you have a direct link, otherwise skip. |
| `argparse: error: --limit is required` | `--limit` was not passed to `search_pubmed.py` or `search_semantic_scholar.py` | Always pass `--limit N` explicitly. There is no default. |

### Things that silently produce wrong results

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pipe sends empty stdin to the Python script | Bash syntax `echo '...' \| cd dir && pixi run ...` — the pipe goes to `cd`, not to pixi | Always `cd` BEFORE the pipe: `cd dir && echo '...' \| pixi run ...` |
| `.env` line N: `$'\r': command not found` | `.env` has Windows `\r\n` line endings | Run `sed -i 's/\r$//' .env` |
| `create_paper_note.py` crashes with `AttributeError: 'list' object has no attribute 'get'` | Search output (JSON array) piped directly without extracting a single object | The script now handles arrays (uses first element + warns), but for clarity pipe one paper at a time. |
| PDF text extraction returns very short text | Scanned/image-only pages yield no extractable text | Check stderr — the script warns about blank pages. Consider OCR tooling for scanned PDFs. |
| BibTeX has duplicate cite keys | Two papers with same first-author + year + first-title-word | Auto-deduplicated with `a`, `b`, `c` suffixes. No action needed. |

### Environment requirements

| Variable | Required? | What breaks without it |
|----------|-----------|----------------------|
| `NCBI_EMAIL` | **Yes** | `search_pubmed.py` crashes immediately |
| `NCBI_API_KEY` | No | 3 req/sec instead of 10. **Remove if expired** — an invalid key causes HTTP 400. |
| `SEMANTIC_SCHOLAR_API_KEY` | No (but recommended) | `--query` exits with HTTP 429 when unauthenticated limit exceeded. `--paper-id` lookups still work. |
| `UNPAYWALL_EMAIL` | Only when Unpaywall path triggers | Crashes only if no other OA source found and DOI lookup is attempted |
| `ZOTERO_API_KEY` + `ZOTERO_USER_ID` | For Zotero scripts only | `search_zotero.py`, `zotero_write.py`, `download_pdf.py --zotero-key` crash |

### General notes

- All scripts send progress/warnings to **stderr** and clean JSON to **stdout**. Safe for piping.
- `create_paper_note.py` auto-deduplicates filenames — if `YYYYMMDD_paper_slug.md` exists, it creates `..._slug_1.md`.
- `--date` must be exactly 8 digits in `YYYYMMDD` format. No validation enforced — bad dates create oddly named files.
- `export_bibtex.py` only includes notes with `type: paper` in frontmatter. Notes missing this field are silently skipped.
- `zotero_write.py --add-items` accepts both a JSON array and a single object on stdin.
- Zotero collection keys are opaque strings — use `--list-collections` to discover them.
- PDF source resolution checks `open_access_pdf`, `arxiv_id`, `doi`, `pmc_id` fields in that order. The first hit wins.
- `download_pdf.py` validates responses are actual PDFs (checks `Content-Type` header and `%PDF` magic bytes).
