#!/usr/bin/env python3
"""Write operations against the Zotero cloud API.

Three mutually exclusive modes:
  --add-items           Read JSON array from stdin, add as Zotero items
  --create-collection   Create a new collection (optionally nested)
  --move-item           Move an item to a collection

Usage:
    # Add papers from search JSON array (stdin)
    echo '<papers JSON array>' | pixi run python scripts/zotero_write.py \
        --add-items [--collection-id KEY]

    # Create a new collection
    pixi run python scripts/zotero_write.py \
        --create-collection "Ophthalmology & Retinal AI" [--parent-id KEY]

    # Move an item to a collection
    pixi run python scripts/zotero_write.py \
        --move-item ITEM_KEY --to-collection COLLECTION_KEY

Required env vars:
    ZOTERO_API_KEY    Zotero API key
    ZOTERO_USER_ID    Zotero numeric user ID

Output: JSON to stdout.
"""

import argparse
import json
import os
import sys

from pyzotero import zotero


def _require_env(name: str) -> str:
    """Read a required env var or crash with a clear message."""
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: {name} not set. Add it to .env and restart.", file=sys.stderr)
        sys.exit(1)
    return val


def _make_zotero_item(zot: zotero.Zotero, paper: dict) -> dict:
    """Map a search-script paper dict onto a Zotero journalArticle template."""
    template = zot.item_template("journalArticle")

    template["title"] = paper.get("title") or ""

    # Authors
    creators = []
    for author in paper.get("authors") or []:
        if "," in author:
            last, first = [p.strip() for p in author.split(",", 1)]
        elif " " in author:
            parts = author.rsplit(" ", 1)
            first, last = parts[0], parts[1]
        else:
            last, first = author, ""
        creators.append({"creatorType": "author", "firstName": first, "lastName": last})
    if creators:
        template["creators"] = creators

    year = paper.get("year")
    if year:
        template["date"] = str(year)

    template["publicationTitle"] = paper.get("journal") or ""
    template["DOI"] = paper.get("doi") or ""
    template["url"] = paper.get("url") or ""
    template["abstractNote"] = paper.get("abstract") or ""

    # Tags
    tags = paper.get("tags") or []
    template["tags"] = [{"tag": t} for t in tags if t]

    return template


def add_items(zot: zotero.Zotero, papers: list[dict], collection_id: str | None) -> None:
    """Add papers to Zotero, optionally placing them in a collection."""
    batch_size = 50
    all_created = []

    for i in range(0, len(papers), batch_size):
        batch = papers[i : i + batch_size]
        items = [_make_zotero_item(zot, p) for p in batch]
        response = zot.create_items(items)

        if not isinstance(response, dict):
            raise RuntimeError(f"Unexpected Zotero API response: {type(response)}: {response!r:.200}")

        # pyzotero returns {"success": {"0": "KEY", ...}, "failed": {...}}
        success = response.get("success", {})
        failed = response.get("failed", {})

        for idx_str, zotero_key in success.items():
            batch_idx = int(idx_str)
            global_idx = i + batch_idx
            paper = papers[global_idx]
            all_created.append({
                "input_index": global_idx,
                "zotero_key": zotero_key,
                "title": paper.get("title", ""),
            })
            print(f"  Created: {zotero_key} — {paper.get('title', '')[:60]}", file=sys.stderr)

        for idx_str, err in failed.items():
            batch_idx = int(idx_str)
            global_idx = i + batch_idx
            print(f"  ERROR: item [{global_idx}] failed: {err}", file=sys.stderr)

    # Add to collection if requested
    if collection_id and all_created:
        # pyzotero expects a list of item dicts with {"key": ..., "version": ...}
        # We need to fetch each created item to get its version
        keys = [item["zotero_key"] for item in all_created]
        print(f"  Adding {len(keys)} items to collection {collection_id}...", file=sys.stderr)
        fetched = [zot.item(k) for k in keys]
        zot.addto_collection(collection_id, fetched)
        print(f"  Added to collection {collection_id}", file=sys.stderr)

    print(json.dumps(all_created, ensure_ascii=False, indent=2))


def create_collection(zot: zotero.Zotero, name: str, parent_id: str | None) -> None:
    """Create a new Zotero collection."""
    payload = [{"name": name, "parentCollection": parent_id or False}]
    response = zot.create_collection(payload)

    if not isinstance(response, dict):
        raise RuntimeError(f"Unexpected Zotero API response: {type(response)}: {response!r:.200}")

    # Response: {"success": {"0": "KEY"}, ...}
    success = response.get("success", {})
    if not success:
        failed = response.get("failed", {})
        raise RuntimeError(f"Collection creation failed: {failed}")

    collection_key = list(success.values())[0]
    result = {"key": collection_key, "name": name}
    if parent_id:
        result["parent_id"] = parent_id
    print(f"  Created collection: {collection_key} — {name}", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def move_item(zot: zotero.Zotero, item_key: str, collection_key: str) -> None:
    """Add an item to a collection (Zotero items can belong to multiple collections)."""
    item = zot.item(item_key)
    data = item.get("data", {})
    existing_collections = data.get("collections", [])

    if collection_key in existing_collections:
        print(f"  Item {item_key} is already in collection {collection_key}", file=sys.stderr)
    else:
        data["collections"] = existing_collections + [collection_key]
        zot.update_item(item)
        print(f"  Moved item {item_key} → collection {collection_key}", file=sys.stderr)

    result = {"item_key": item_key, "moved_to": collection_key}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Write operations against the Zotero API")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--add-items",
        action="store_true",
        help="Read JSON array from stdin and add as Zotero items",
    )
    mode_group.add_argument(
        "--create-collection",
        metavar="NAME",
        help="Create a new collection with this name",
    )
    mode_group.add_argument(
        "--move-item",
        metavar="ITEM_KEY",
        help="Zotero item key to move to a collection",
    )

    parser.add_argument(
        "--collection-id",
        help="Collection key (used with --add-items to place items in a collection)",
    )
    parser.add_argument(
        "--parent-id",
        help="Parent collection key (used with --create-collection for nested collections)",
    )
    parser.add_argument(
        "--to-collection",
        metavar="COLLECTION_KEY",
        help="Destination collection key (used with --move-item)",
    )

    args = parser.parse_args()

    # Validate mode-specific args
    if args.move_item and not args.to_collection:
        parser.error("--move-item requires --to-collection")

    # Auth — fail fast with clear message
    api_key = _require_env("ZOTERO_API_KEY")
    user_id = _require_env("ZOTERO_USER_ID")
    zot = zotero.Zotero(user_id, "user", api_key)

    if args.add_items:
        raw = sys.stdin.read().strip()
        if not raw:
            parser.error("--add-items requires JSON array piped to stdin")
        data = json.loads(raw)
        if isinstance(data, dict):
            # Accept single object too
            data = [data]
        add_items(zot, data, args.collection_id)

    elif args.create_collection:
        create_collection(zot, args.create_collection, args.parent_id)

    elif args.move_item:
        move_item(zot, args.move_item, args.to_collection)


if __name__ == "__main__":
    main()
