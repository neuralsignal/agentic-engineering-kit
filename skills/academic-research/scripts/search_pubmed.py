#!/usr/bin/env python3
"""Search PubMed via NCBI E-utilities (Bio.Entrez).

Usage:
    pixi run python scripts/search_pubmed.py --query "EHR foundation models" --limit 10 [--year-start Y] [--year-end Y]
    pixi run python scripts/search_pubmed.py --pmid 38000001 [--fulltext]

Required env vars:
    NCBI_EMAIL      Contact email sent to NCBI

Optional env vars:
    NCBI_API_KEY    NCBI API key — lifts rate limit from 3 to 10 req/sec

Output: JSON to stdout. Warnings to stderr.
"""

import argparse
import json
import os
import sys
import time

from Bio import Entrez, Medline


def _require_env(name: str) -> str:
    """Read a required env var or crash with a clear message."""
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: {name} not set. Add it to .env and restart.", file=sys.stderr)
        sys.exit(1)
    return val


def configure_entrez() -> None:
    Entrez.email = _require_env("NCBI_EMAIL")
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        Entrez.api_key = api_key


def _rate_limit_sleep() -> None:
    """Sleep based on whether an API key is configured (10 req/sec vs 3 req/sec)."""
    if Entrez.api_key:
        time.sleep(0.1)
    else:
        time.sleep(0.35)


def _parse_medline_record(record: dict) -> dict:
    pmid = record.get("PMID", "")
    title = record.get("TI", "")
    abstract = record.get("AB", "")
    journal = record.get("JT", "") or record.get("TA", "")
    date_pub = record.get("DP", "")
    year = date_pub[:4] if date_pub else None

    raw_authors = record.get("AU", [])
    authors = list(raw_authors)

    doi = ""
    for aid in record.get("AID", []):
        if aid.endswith("[doi]"):
            doi = aid.replace(" [doi]", "").strip()
            break

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "doi": doi,
        "pubmed_id": pmid,
        "abstract": abstract,
        "mesh_terms": list(record.get("MH", [])),
        "keywords": list(record.get("OT", [])),
        "source": "PubMed",
    }


def search_pubmed(
    query: str,
    limit: int,
    year_start: int | None,
    year_end: int | None,
) -> list[dict]:
    date_range = ""
    if year_start or year_end:
        lo = str(year_start) if year_start else "1900"
        hi = str(year_end) if year_end else "3000"
        date_range = f" AND {lo}:{hi}[pdat]"

    full_query = f"{query}{date_range}"
    print(f"PubMed query: {full_query}", file=sys.stderr)

    handle = Entrez.esearch(db="pubmed", term=full_query, retmax=limit, usehistory="y")
    search_results = Entrez.read(handle)
    handle.close()

    ids = search_results.get("IdList", [])
    print(f"Found {search_results.get('Count', 0)} total; retrieving {len(ids)}", file=sys.stderr)

    if not ids:
        return []

    _rate_limit_sleep()
    handle = Entrez.efetch(db="pubmed", id=ids, rettype="medline", retmode="text")
    records = list(Medline.parse(handle))
    handle.close()

    return [_parse_medline_record(r) for r in records]


def fetch_by_pmid(pmid: str, fulltext: bool) -> dict:
    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="text")
    records = list(Medline.parse(handle))
    handle.close()

    if not records:
        print(f"No record found for PMID {pmid}", file=sys.stderr)
        sys.exit(1)

    paper = _parse_medline_record(records[0])

    if fulltext:
        _rate_limit_sleep()
        handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
        link_results = Entrez.read(handle)
        handle.close()

        pmc_ids: list[str] = []
        for linkset in link_results:
            for db_links in linkset.get("LinkSetDb", []):
                if db_links.get("DbTo") == "pmc":
                    pmc_ids = [lnk["Id"] for lnk in db_links.get("Link", [])]
                    break

        if pmc_ids:
            pmc_id = pmc_ids[0]
            _rate_limit_sleep()
            handle = Entrez.efetch(db="pmc", id=pmc_id, rettype="xml", retmode="xml")
            xml_content = handle.read()
            handle.close()
            paper["pmc_id"] = pmc_id
            paper["pmc_xml_length"] = len(xml_content)
            print(
                f"Full text available in PMC (PMC{pmc_id}, {len(xml_content)} bytes XML)",
                file=sys.stderr,
            )
        else:
            print(f"PMID {pmid} is not in PMC — full text unavailable", file=sys.stderr)

    return paper


def main() -> None:
    configure_entrez()

    parser = argparse.ArgumentParser(description="Search PubMed via NCBI E-utilities")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="PubMed search query string")
    group.add_argument("--pmid", help="Fetch a specific paper by PubMed ID")

    parser.add_argument("--limit", type=int, required=True, help="Max results for --query")
    parser.add_argument("--year-start", type=int, help="Filter: earliest publication year")
    parser.add_argument("--year-end", type=int, help="Filter: latest publication year")
    parser.add_argument(
        "--fulltext",
        action="store_true",
        help="Try to fetch PubMed Central full text (only with --pmid)",
    )

    args = parser.parse_args()

    if args.query:
        papers = search_pubmed(args.query, args.limit, args.year_start, args.year_end)
        print(json.dumps(papers, ensure_ascii=False, indent=2))
    elif args.pmid:
        paper = fetch_by_pmid(args.pmid, args.fulltext)
        print(json.dumps(paper, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
