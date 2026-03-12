#!/usr/bin/env python3
"""Export BibTeX entries from all paper knowledge notes.

Scans YYYYMMDD_paper_*.md files in the given directory, parses YAML
frontmatter, and emits valid BibTeX to stdout or a file.

Usage:
    pixi run python scripts/export_bibtex.py \
        --notes-dir /path/to/notes

    pixi run python scripts/export_bibtex.py \
        --notes-dir /path/to/notes \
        --output /tmp/papers.bib
"""

import argparse
import re
import sys
from pathlib import Path

import yaml


def parse_frontmatter(text: str) -> dict | None:
    """Extract and parse YAML frontmatter from a markdown file."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm_text = text[3:end].strip()
    return yaml.safe_load(fm_text)


def make_cite_key(authors: list, year: int | str, title: str) -> str:
    first_author = authors[0].split()[-1] if authors else "unknown"
    first_author = re.sub(r"[^a-zA-Z0-9]", "", first_author).lower()
    year_str = str(year) if year else "0000"
    first_word = title.split()[0] if title else "untitled"
    first_word = re.sub(r"[^a-zA-Z0-9]", "", first_word).lower()
    return f"{first_author}{year_str}{first_word}"


def meta_to_bibtex(meta: dict, seen_keys: set) -> str:
    authors = meta.get("authors") or []
    year = meta.get("year", "")
    title = meta.get("title", "")
    journal = meta.get("journal", "")
    doi = meta.get("doi", "")
    pubmed_id = meta.get("pubmed_id", "")

    key = make_cite_key(authors, year, title)

    # Deduplicate cite keys
    if key in seen_keys:
        suffix = 1
        while f"{key}{chr(ord('a') + suffix - 1)}" in seen_keys:
            suffix += 1
        key = f"{key}{chr(ord('a') + suffix - 1)}"
    seen_keys.add(key)

    author_str = " and ".join(authors) if authors else ""
    entry_type = "article" if journal else "misc"

    fields = []
    if author_str:
        fields.append(f"  author = {{{author_str}}}")
    fields.append(f"  title = {{{title}}}")
    if year:
        fields.append(f"  year = {{{year}}}")
    if journal:
        fields.append(f"  journal = {{{journal}}}")
    if doi:
        fields.append(f"  doi = {{{doi}}}")
    if pubmed_id:
        fields.append(f"  pmid = {{{pubmed_id}}}")

    return "@{}{{{},\n{}\n}}".format(entry_type, key, ",\n".join(fields))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export BibTeX from paper knowledge notes."
    )
    parser.add_argument(
        "--notes-dir",
        required=True,
        help="Directory containing paper note markdown files",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="Output .bib file path (default: stdout)",
    )
    args = parser.parse_args()

    notes_dir = Path(args.notes_dir)

    paper_files = sorted(notes_dir.glob("*_paper_*.md"))
    if not paper_files:
        print("# No paper notes found.", file=sys.stderr)

    entries = []
    seen_keys: set = set()
    skipped = 0
    for filepath in paper_files:
        text = filepath.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        if not meta or meta.get("type") != "paper":
            continue
        try:
            entries.append(meta_to_bibtex(meta, seen_keys))
        except Exception as exc:
            print(f"WARNING: skipping {filepath.name}: {exc}", file=sys.stderr)
            skipped += 1

    output = "\n\n".join(entries)
    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output + "\n", encoding="utf-8")
        print(
            f"Wrote {len(entries)} entries to {args.output}"
            + (f" ({skipped} skipped)" if skipped else ""),
            file=sys.stderr,
        )
    else:
        print(output)


if __name__ == "__main__":
    main()
