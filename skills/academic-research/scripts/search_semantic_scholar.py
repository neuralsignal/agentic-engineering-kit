#!/usr/bin/env python3
"""Search Semantic Scholar for papers, authors, and citation graphs.

Usage:
    pixi run python scripts/search_semantic_scholar.py --query "OMOP CDM" --limit 10 [--year-start Y] [--year-end Y]
    pixi run python scripts/search_semantic_scholar.py --paper-id "DOI:10.1038/..." [--include-citations] [--include-references]
    pixi run python scripts/search_semantic_scholar.py --author-id 1234567

Optional env vars:
    SEMANTIC_SCHOLAR_API_KEY    API key for higher rate limits (1000 vs 100 req/5 min)

Output: JSON to stdout.
"""

import argparse
import json
import os
import sys

import requests

S2_BASE = "https://api.semanticscholar.org/graph/v1"
TIMEOUT_SECONDS = 15

PAPER_FIELDS = ",".join([
    "paperId",
    "title",
    "authors",
    "year",
    "venue",
    "journal",
    "publicationDate",
    "abstract",
    "citationCount",
    "referenceCount",
    "externalIds",
    "openAccessPdf",
    "fieldsOfStudy",
])

AUTHOR_FIELDS = ",".join([
    "authorId",
    "name",
    "affiliations",
    "paperCount",
    "citationCount",
    "hIndex",
    "papers",
    "papers.paperId",
    "papers.title",
    "papers.authors",
    "papers.year",
    "papers.venue",
    "papers.journal",
    "papers.abstract",
    "papers.citationCount",
    "papers.referenceCount",
    "papers.externalIds",
    "papers.openAccessPdf",
    "papers.fieldsOfStudy",
])


def _s2_request(path: str, params: dict, api_key: str | None) -> dict:
    """Make a request to the S2 Academic Graph API. Exits on 429/404/5xx."""
    headers = {"x-api-key": api_key} if api_key else {}
    resp = requests.get(
        f"{S2_BASE}{path}",
        params=params,
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )
    if resp.status_code == 429:
        print(
            "ERROR: S2 rate limit (HTTP 429). Set SEMANTIC_SCHOLAR_API_KEY for 10x limits.",
            file=sys.stderr,
        )
        sys.exit(1)
    if resp.status_code == 404:
        print(f"ERROR: Not found (HTTP 404): {path}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code >= 500:
        print(
            f"ERROR: S2 server error (HTTP {resp.status_code}). Try again later.",
            file=sys.stderr,
        )
        sys.exit(1)
    resp.raise_for_status()
    return resp.json()


def _format_year_filter(
    year_start: int | None, year_end: int | None
) -> str | None:
    """Format year range for S2 API year parameter."""
    if year_start is None and year_end is None:
        return None
    lo = str(year_start) if year_start else ""
    hi = str(year_end) if year_end else ""
    return f"{lo}-{hi}"


def paper_to_dict(paper: dict) -> dict:
    """Convert an S2 API paper dict to our standard output format."""
    authors = []
    raw_authors = paper.get("authors")
    if raw_authors:
        for a in raw_authors:
            if isinstance(a, dict):
                authors.append(a.get("name", str(a)))
            else:
                authors.append(str(a))

    external_ids = paper.get("externalIds") or {}
    doi = external_ids.get("DOI", "")
    pubmed_id = external_ids.get("PubMed", "")

    journal_info = paper.get("journal")
    journal_name = ""
    if journal_info and isinstance(journal_info, dict):
        journal_name = journal_info.get("name", "") or ""

    pdf_url = None
    open_access = paper.get("openAccessPdf")
    if open_access and isinstance(open_access, dict):
        pdf_url = open_access.get("url")

    return {
        "title": paper.get("title", "") or "",
        "authors": authors,
        "year": paper.get("year"),
        "journal": journal_name or paper.get("venue", "") or "",
        "doi": doi,
        "pubmed_id": pubmed_id,
        "semantic_scholar_id": paper.get("paperId", ""),
        "abstract": paper.get("abstract", "") or "",
        "citation_count": paper.get("citationCount") or 0,
        "reference_count": paper.get("referenceCount") or 0,
        "open_access_pdf": pdf_url,
        "fields_of_study": list(paper.get("fieldsOfStudy") or []),
        "source": "SemanticScholar",
    }


def main() -> None:
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if not api_key:
        print(
            "Warning: SEMANTIC_SCHOLAR_API_KEY not set — using unauthenticated (100 req/5 min)",
            file=sys.stderr,
        )

    parser = argparse.ArgumentParser(description="Search Semantic Scholar")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="Full-text search query")
    group.add_argument(
        "--paper-id", help="Paper ID (DOI:..., PMID:..., or S2 paper ID)"
    )
    group.add_argument("--author-id", help="Semantic Scholar author ID")

    parser.add_argument(
        "--limit", type=int, required=True, help="Max results for --query"
    )
    parser.add_argument(
        "--year-start", type=int, help="Filter: earliest publication year"
    )
    parser.add_argument(
        "--year-end", type=int, help="Filter: latest publication year"
    )
    parser.add_argument(
        "--include-citations",
        action="store_true",
        help="Include citing papers (with --paper-id)",
    )
    parser.add_argument(
        "--include-references",
        action="store_true",
        help="Include referenced papers (with --paper-id)",
    )

    args = parser.parse_args()

    if args.query:
        params: dict = {
            "query": args.query,
            "limit": args.limit,
            "fields": PAPER_FIELDS,
        }
        year_filter = _format_year_filter(args.year_start, args.year_end)
        if year_filter:
            params["year"] = year_filter

        data = _s2_request("/paper/search", params, api_key)
        raw_papers = data.get("data") or []
        papers = [paper_to_dict(p) for p in raw_papers]
        print(json.dumps(papers, ensure_ascii=False, indent=2))

    elif args.paper_id:
        paper_data = _s2_request(
            f"/paper/{args.paper_id}",
            {"fields": PAPER_FIELDS},
            api_key,
        )
        result: dict = {"paper": paper_to_dict(paper_data)}

        if args.include_citations:
            cit_data = _s2_request(
                f"/paper/{args.paper_id}/citations",
                {"fields": PAPER_FIELDS, "limit": 20},
                api_key,
            )
            result["citations"] = [
                paper_to_dict(c["citingPaper"])
                for c in (cit_data.get("data") or [])
            ]

        if args.include_references:
            ref_data = _s2_request(
                f"/paper/{args.paper_id}/references",
                {"fields": PAPER_FIELDS, "limit": 20},
                api_key,
            )
            result["references"] = [
                paper_to_dict(r["citedPaper"])
                for r in (ref_data.get("data") or [])
            ]

        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.author_id:
        author_data = _s2_request(
            f"/author/{args.author_id}",
            {"fields": AUTHOR_FIELDS},
            api_key,
        )
        papers = []
        if author_data.get("papers"):
            for p in author_data["papers"]:
                papers.append(paper_to_dict(p))

        result = {
            "author": {
                "id": author_data.get("authorId", ""),
                "name": author_data.get("name", ""),
                "affiliations": list(author_data.get("affiliations") or []),
                "paper_count": author_data.get("paperCount", 0),
                "citation_count": author_data.get("citationCount", 0),
                "h_index": author_data.get("hIndex", 0),
            },
            "papers": papers,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
