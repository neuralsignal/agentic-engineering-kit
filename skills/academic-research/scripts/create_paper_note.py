#!/usr/bin/env python3
"""Create a paper knowledge note from paper metadata JSON.

Reads paper metadata as JSON from stdin, writes
YYYYMMDD_paper_[slug].md into the specified output directory,
and prints the output filepath to stdout.

Usage:
    echo '{"title": "...", "authors": ["Smith J"], "year": 2024, ...}' | \
        pixi run python scripts/create_paper_note.py \
        --output-dir /path/to/notes \
        --date 20260310

Metadata fields (all optional except title):
    title, authors (list), year (int), journal, doi,
    pubmed_id, semantic_scholar_id, zotero_key, source,
    status, relevance, tags (list), abstract, url
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def make_slug(meta: dict) -> str:
    authors = meta.get("authors", [])
    first_author_last = authors[0].split()[-1] if authors else "unknown"
    year = str(meta.get("year", ""))
    title = meta.get("title", "untitled")
    title_slug = slugify(title)[:20]
    author_slug = slugify(first_author_last)[:15]
    return f"{author_slug}{year}_{title_slug}"


def render_frontmatter(meta: dict) -> str:
    fm = {
        "type": "paper",
        "title": meta.get("title", ""),
        "authors": meta.get("authors", []),
        "year": meta.get("year", None),
        "journal": meta.get("journal", ""),
        "doi": meta.get("doi", ""),
        "pubmed_id": meta.get("pubmed_id", ""),
        "semantic_scholar_id": meta.get("semantic_scholar_id", ""),
        "zotero_key": meta.get("zotero_key", ""),
        "source": meta.get("source", ""),
        "status": meta.get("status", "unread"),
        "relevance": meta.get("relevance", ""),
        "tags": meta.get("tags", []),
    }
    return yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)


def render_body(meta: dict) -> str:
    title = meta.get("title", "Untitled")
    authors = ", ".join(meta.get("authors", []))
    year = meta.get("year", "")
    journal = meta.get("journal", "")
    abstract = meta.get("abstract", "")
    url = meta.get("url", "")
    doi = meta.get("doi", "")

    lines = [f"# {title}", ""]
    lines.append(f"**Authors**: {authors}")
    lines.append(f"**Year**: {year}")
    if journal:
        lines.append(f"**Journal**: {journal}")
    if url:
        lines.append(f"**URL**: {url}")
    elif doi:
        lines.append(f"**DOI**: {doi}")
    lines.append("")

    if abstract:
        lines.append("## Abstract")
        lines.append("")
        lines.append(abstract)
        lines.append("")

    lines.extend([
        "## Annotations",
        "",
        "- [key_finding] ",
        "- [method] ",
        "- [dataset] ",
        "- [relevance_note] ",
        "- [limitations] ",
        "- [follow_up] ",
        "",
        "## Relations",
        "",
        "- relates_to [[goal-slug]]",
        "- part_of [[litreview-note-slug]]",
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a paper knowledge note from JSON metadata via stdin."
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write the paper note into",
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Date prefix YYYYMMDD for the note filename (e.g. 20260310)",
    )
    args = parser.parse_args()

    notes_dir = Path(args.output_dir)
    if not notes_dir.is_dir():
        print(f"ERROR: output directory not found: {notes_dir}", file=sys.stderr)
        sys.exit(1)

    raw = sys.stdin.read().strip()
    if not raw:
        print("ERROR: no JSON metadata provided via stdin", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON on stdin: {exc}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, list):
        if len(data) == 0:
            print("ERROR: empty JSON array on stdin", file=sys.stderr)
            sys.exit(1)
        if len(data) > 1:
            print(f"Warning: received {len(data)} papers, processing first only. Pipe one paper at a time.", file=sys.stderr)
        meta = data[0]
    elif isinstance(data, dict):
        meta = data
    else:
        print("ERROR: expected JSON object or array on stdin", file=sys.stderr)
        sys.exit(1)

    slug = make_slug(meta)
    filename = f"{args.date}_paper_{slug}.md"
    output_path = notes_dir / filename

    # Deduplicate slug collisions
    counter = 1
    while output_path.exists():
        filename = f"{args.date}_paper_{slug}_{counter}.md"
        output_path = notes_dir / filename
        counter += 1

    content = f"---\n{render_frontmatter(meta)}---\n\n{render_body(meta)}\n"
    output_path.write_text(content, encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
