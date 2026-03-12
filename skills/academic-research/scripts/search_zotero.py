#!/usr/bin/env python3
"""Search, browse, or list the Zotero cloud library.

Usage:
    pixi run python scripts/search_zotero.py --query "retinal AI" [--limit N]
    pixi run python scripts/search_zotero.py --list-collections
    pixi run python scripts/search_zotero.py --browse [--collection-id KEY] [--limit N]
    pixi run python scripts/search_zotero.py --query "..." --collection-id KEY [--limit N]

Required env vars:
    ZOTERO_API_KEY    Zotero API key (https://www.zotero.org/settings/keys)
    ZOTERO_USER_ID    Zotero numeric user ID (shown at top of keys page)

Output: JSON to stdout.
"""

import argparse
import json
import os
import sys

from pyzotero import zotero

LITERATURE_TYPES = {
    "journalArticle",
    "conferencePaper",
    "preprint",
    "report",
    "book",
    "bookSection",
    "thesis",
    "manuscript",
}


def _require_env(name: str) -> str:
    """Read a required env var or crash with a clear message."""
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: {name} not set. Add it to .env and restart.", file=sys.stderr)
        sys.exit(1)
    return val


def build_paper_dict(item: dict) -> dict:
    data = item.get("data", {})
    creators = data.get("creators", [])
    authors = []
    for c in creators:
        if "name" in c:
            authors.append(c["name"])
        else:
            last = c.get("lastName", "")
            first = c.get("firstName", "")
            authors.append(f"{last} {first}".strip() if last else first)
    return {
        "title": data.get("title", ""),
        "authors": authors,
        "year": (data.get("date") or "")[:4] or None,
        "journal": data.get("publicationTitle") or data.get("journalAbbreviation") or "",
        "doi": data.get("DOI", ""),
        "url": data.get("url", ""),
        "abstract": data.get("abstractNote", ""),
        "item_type": data.get("itemType", ""),
        "zotero_key": item.get("key", ""),
        "tags": [t.get("tag", "") for t in data.get("tags", [])],
        "source": "Zotero",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Search, browse, or list Zotero library")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="Search query string")
    group.add_argument("--list-collections", action="store_true", help="List all collections")
    group.add_argument(
        "--browse",
        action="store_true",
        help="Browse all items (optionally filtered by --collection-id) without a query",
    )

    parser.add_argument("--collection-id", help="Restrict item fetch to this collection key")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")

    args = parser.parse_args()

    api_key = _require_env("ZOTERO_API_KEY")
    user_id = _require_env("ZOTERO_USER_ID")

    zot = zotero.Zotero(user_id, "user", api_key)

    if args.list_collections:
        collections = zot.collections()
        result = [
            {
                "key": c["key"],
                "name": c["data"]["name"],
                "parent": c["data"].get("parentCollection") or None,
                "num_items": c["meta"].get("numItems", 0),
            }
            for c in collections
        ]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Item search or browse (--query sets q filter; --browse fetches without filter)
    if args.collection_id:
        kwargs: dict = {"limit": args.limit}
        if args.query:
            kwargs["q"] = args.query
        items = zot.collection_items(args.collection_id, **kwargs)
    else:
        kwargs = {"limit": args.limit}
        if args.query:
            kwargs["q"] = args.query
        items = zot.items(**kwargs)

    papers = [
        build_paper_dict(item)
        for item in items
        if item.get("data", {}).get("itemType") in LITERATURE_TYPES
    ]
    print(json.dumps(papers, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
