#!/usr/bin/env python3
"""Download a paper's PDF from open access sources and optionally extract text.

PDF source resolution order (first hit wins):
  1. open_access_pdf URL from stdin JSON
  2. arXiv direct URL (if arxiv_id in JSON)
  3. Unpaywall API (if DOI present, requires UNPAYWALL_EMAIL env var)
  4. PMC OA Web Service (if pmc_id in JSON)

Usage:
    # From Semantic Scholar / PubMed search output piped in (single paper object)
    echo '<paper JSON>' | pixi run python scripts/download_pdf.py \
        --output /tmp/papers/ [--extract-text] [--zotero-key KEY]

    # Direct URL
    pixi run python scripts/download_pdf.py \
        --url https://arxiv.org/pdf/2401.xxxxx \
        --output /tmp/papers/ --filename mypaper [--extract-text]

    # Direct DOI (Unpaywall lookup — requires UNPAYWALL_EMAIL)
    pixi run python scripts/download_pdf.py \
        --doi 10.1038/s41591-024-xxxx \
        --output /tmp/papers/ [--extract-text]

Optional env vars:
    UNPAYWALL_EMAIL    Required only when Unpaywall is needed (no other source found)
    ZOTERO_API_KEY     Required only when --zotero-key is used
    ZOTERO_USER_ID     Required only when --zotero-key is used

Output: JSON to stdout with pdf_path, text_path (if extracted), source, page_count, text_length.
Progress and warnings go to stderr.
"""

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


def _require_env(name: str) -> str:
    """Read a required env var or crash with a clear message."""
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: {name} not set. Add it to .env and restart.", file=sys.stderr)
        sys.exit(1)
    return val


def _slug(text: str) -> str:
    """Convert text to a URL/filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text)
    return text[:60].strip("_")


_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def _download_bytes(url: str) -> bytes:
    """Download URL to bytes. Raises on non-200 or non-PDF response."""
    import requests

    session = requests.Session()
    session.headers.update(_HEADERS)
    print(f"  Downloading: {url}", file=sys.stderr)
    resp = session.get(url, timeout=60, allow_redirects=True)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "pdf" not in content_type and not resp.content[:4] == b"%PDF":
        raise ValueError(f"Response is not a PDF (Content-Type: {content_type})")
    return resp.content


def _resolve_unpaywall(doi: str) -> str | None:
    """Look up the best OA PDF URL for a DOI via Unpaywall."""
    import requests

    email = _require_env("UNPAYWALL_EMAIL")
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    print(f"  Unpaywall lookup for DOI: {doi}", file=sys.stderr)
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    best = data.get("best_oa_location") or {}
    return best.get("url_for_pdf") or None


def _resolve_pmc_pdf(pmc_id: str) -> str | None:
    """Look up actual PDF URL via PMC OA Web Service API."""
    import requests

    pmc_id_clean = str(pmc_id).replace("PMC", "")
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_id_clean}"
    print(f"  PMC OA lookup for PMC{pmc_id_clean}", file=sys.stderr)
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    for link in root.iter("link"):
        if link.get("format") == "pdf":
            href = link.get("href", "")
            # Convert FTP URLs to HTTPS
            if href.startswith("ftp://"):
                href = href.replace("ftp://", "https://")
            return href
    return None


def _extract_text(pdf_path: Path) -> str:
    """Extract text from PDF using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    parts = []
    skipped = 0
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
        else:
            skipped += 1
    if skipped:
        print(
            f"  Warning: {skipped}/{len(reader.pages)} pages yielded no text (likely scanned/image pages)",
            file=sys.stderr,
        )
    return "\n\n".join(parts)


def _attach_to_zotero(item_key: str, pdf_path: Path) -> None:
    """Upload a PDF attachment to a Zotero item."""
    from pyzotero import zotero

    api_key = _require_env("ZOTERO_API_KEY")
    user_id = _require_env("ZOTERO_USER_ID")
    zot = zotero.Zotero(user_id, "user", api_key)
    zot.upload_attachments([str(pdf_path)], parentid=item_key)
    print(f"  Attached PDF to Zotero item {item_key}", file=sys.stderr)


def resolve_pdf_url(paper: dict, direct_url: str | None, doi: str | None) -> tuple[str, str]:
    """Return (pdf_url, source_label) for the best available source."""
    # Mode: direct URL
    if direct_url:
        return direct_url, "direct_url"

    # Mode: DOI only (Unpaywall)
    if doi and not paper:
        url = _resolve_unpaywall(doi)
        if url:
            return url, "unpaywall"
        raise RuntimeError(f"No OA PDF found via Unpaywall for DOI: {doi}")

    # Mode: from JSON metadata
    # 1. open_access_pdf from Semantic Scholar
    oa = paper.get("open_access_pdf")
    if isinstance(oa, dict):
        oa_url = oa.get("url")
    else:
        oa_url = oa if isinstance(oa, str) else None
    if oa_url:
        return oa_url, "semantic_scholar_oa"

    # 2. arXiv direct
    arxiv_id = paper.get("arxiv_id") or paper.get("externalIds", {}).get("ArXiv")
    if arxiv_id:
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf", "arxiv"

    # 3. Unpaywall via DOI
    paper_doi = doi or paper.get("doi") or paper.get("externalIds", {}).get("DOI")
    if paper_doi:
        uw_url = _resolve_unpaywall(paper_doi)
        if uw_url:
            return uw_url, "unpaywall"

    # 4. PMC OA Web Service
    pmc_id = paper.get("pmc_id") or paper.get("externalIds", {}).get("PubMedCentral")
    if pmc_id:
        pmc_url = _resolve_pmc_pdf(pmc_id)
        if pmc_url:
            return pmc_url, "pmc"
        print(f"  Warning: PMC{pmc_id} not in OA subset — no PDF available", file=sys.stderr)

    raise RuntimeError("No open-access PDF source found for this paper. Provide --url or --doi, or check open_access_pdf in the JSON.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download an open-access PDF for a paper")
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--url", help="Direct PDF URL to download")
    source_group.add_argument("--doi", help="DOI to resolve via Unpaywall")
    # (stdin is the third option — mutually exclusive is soft; checked below)

    parser.add_argument("--output", required=True, help="Directory to save PDF (and text)")
    parser.add_argument("--filename", help="Base filename slug (without extension). Default: slugified title")
    parser.add_argument("--extract-text", action="store_true", help="Extract text via pypdf and write .txt alongside PDF")
    parser.add_argument("--zotero-key", help="Zotero item key — attach PDF after download")

    args = parser.parse_args()

    # Read JSON from stdin if no --url or --doi
    paper: dict = {}
    if not args.url and not args.doi:
        raw = sys.stdin.read().strip()
        if not raw:
            parser.error("Provide --url, --doi, or pipe paper JSON to stdin")
        paper = json.loads(raw)

    # Resolve PDF URL
    pdf_url, source = resolve_pdf_url(paper, args.url, args.doi)

    # Determine filename slug
    if args.filename:
        slug = _slug(args.filename)
    elif paper.get("title"):
        slug = _slug(paper["title"])
    else:
        # Fall back to last segment of URL
        slug = _slug(pdf_url.split("/")[-1].replace(".pdf", "") or "paper")

    # Download
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{slug}.pdf"

    pdf_bytes = _download_bytes(pdf_url)
    pdf_path.write_bytes(pdf_bytes)
    print(f"  Saved PDF: {pdf_path}", file=sys.stderr)

    # Count pages
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError

        reader = PdfReader(str(pdf_path))
        page_count = len(reader.pages)
    except PdfReadError as exc:
        print(f"  Warning: could not count pages: {exc}", file=sys.stderr)
        page_count = None

    result: dict = {
        "pdf_path": str(pdf_path),
        "source": source,
        "page_count": page_count,
    }

    # Extract text
    if args.extract_text:
        txt_path = output_dir / f"{slug}.txt"
        print(f"  Extracting text...", file=sys.stderr)
        text = _extract_text(pdf_path)
        txt_path.write_text(text, encoding="utf-8")
        print(f"  Saved text: {txt_path}", file=sys.stderr)
        result["text_path"] = str(txt_path)
        result["text_length"] = len(text)

    # Attach to Zotero
    if args.zotero_key:
        _attach_to_zotero(args.zotero_key, pdf_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
