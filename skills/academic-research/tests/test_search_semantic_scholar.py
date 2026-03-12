"""Tests for search_semantic_scholar.py — paper_to_dict and _s2_request."""

from unittest.mock import MagicMock, patch

import pytest
import requests

import search_semantic_scholar as sss


# --- paper_to_dict ---


class TestPaperToDict:
    def test_full_response(self):
        """Complete S2 API response dict — all fields populated."""
        raw = {
            "paperId": "abc123",
            "title": "Deep Learning for Retinal OCT",
            "authors": [{"name": "Smith J"}, {"name": "Jones A"}],
            "year": 2024,
            "venue": "Nature Medicine",
            "journal": {"name": "Nature Medicine"},
            "publicationDate": "2024-06-15",
            "abstract": "We present a deep learning model...",
            "citationCount": 42,
            "referenceCount": 30,
            "externalIds": {"DOI": "10.1038/s41591-024-0001", "PubMed": "38000001"},
            "openAccessPdf": {"url": "https://example.com/paper.pdf"},
            "fieldsOfStudy": ["Medicine", "Computer Science"],
        }
        result = sss.paper_to_dict(raw)

        assert result["title"] == "Deep Learning for Retinal OCT"
        assert result["authors"] == ["Smith J", "Jones A"]
        assert result["year"] == 2024
        assert result["journal"] == "Nature Medicine"
        assert result["doi"] == "10.1038/s41591-024-0001"
        assert result["pubmed_id"] == "38000001"
        assert result["semantic_scholar_id"] == "abc123"
        assert result["abstract"] == "We present a deep learning model..."
        assert result["citation_count"] == 42
        assert result["reference_count"] == 30
        assert result["open_access_pdf"] == "https://example.com/paper.pdf"
        assert result["fields_of_study"] == ["Medicine", "Computer Science"]
        assert result["source"] == "SemanticScholar"

    def test_missing_fields(self):
        """Minimal dict — only paperId and title present."""
        raw = {"paperId": "xyz", "title": "Minimal Paper"}
        result = sss.paper_to_dict(raw)

        assert result["title"] == "Minimal Paper"
        assert result["authors"] == []
        assert result["year"] is None
        assert result["journal"] == ""
        assert result["doi"] == ""
        assert result["pubmed_id"] == ""
        assert result["semantic_scholar_id"] == "xyz"
        assert result["abstract"] == ""
        assert result["citation_count"] == 0
        assert result["reference_count"] == 0
        assert result["open_access_pdf"] is None
        assert result["fields_of_study"] == []

    def test_null_fields(self):
        """Explicit None values for optional fields."""
        raw = {
            "paperId": "n1",
            "title": "Null Test",
            "authors": None,
            "year": None,
            "venue": None,
            "journal": None,
            "abstract": None,
            "citationCount": None,
            "referenceCount": None,
            "externalIds": None,
            "openAccessPdf": None,
            "fieldsOfStudy": None,
        }
        result = sss.paper_to_dict(raw)

        assert result["authors"] == []
        assert result["year"] is None
        assert result["journal"] == ""
        assert result["doi"] == ""
        assert result["pubmed_id"] == ""
        assert result["open_access_pdf"] is None
        assert result["fields_of_study"] == []
        assert result["citation_count"] == 0
        assert result["reference_count"] == 0


# --- _s2_request ---


class TestS2Request:
    def test_429_rate_limit(self):
        """HTTP 429 exits with code 1 and prints rate limit message."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429

        with patch("search_semantic_scholar.requests.get", return_value=mock_resp):
            with pytest.raises(SystemExit) as exc_info:
                sss._s2_request("/paper/search", {"query": "test"}, api_key=None)
            assert exc_info.value.code == 1

    def test_404_not_found(self):
        """HTTP 404 exits with code 1."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404

        with patch("search_semantic_scholar.requests.get", return_value=mock_resp):
            with pytest.raises(SystemExit) as exc_info:
                sss._s2_request("/paper/BADID", {}, api_key=None)
            assert exc_info.value.code == 1

    def test_500_server_error(self):
        """HTTP 500 exits with code 1."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500

        with patch("search_semantic_scholar.requests.get", return_value=mock_resp):
            with pytest.raises(SystemExit) as exc_info:
                sss._s2_request("/paper/search", {}, api_key=None)
            assert exc_info.value.code == 1

    def test_timeout(self):
        """requests.exceptions.Timeout propagates."""
        with patch(
            "search_semantic_scholar.requests.get",
            side_effect=requests.exceptions.Timeout("timed out"),
        ):
            with pytest.raises(requests.exceptions.Timeout):
                sss._s2_request("/paper/search", {}, api_key=None)

    def test_success(self):
        """HTTP 200 returns parsed JSON."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": [{"paperId": "abc"}]}

        with patch("search_semantic_scholar.requests.get", return_value=mock_resp):
            result = sss._s2_request("/paper/search", {"query": "test"}, api_key=None)

        assert result == {"data": [{"paperId": "abc"}]}

    def test_api_key_header(self):
        """x-api-key header sent when key is present, absent when not."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}

        with patch("search_semantic_scholar.requests.get", return_value=mock_resp) as mock_get:
            # With API key
            sss._s2_request("/paper/search", {}, api_key="my-secret-key")
            call_kwargs = mock_get.call_args
            assert call_kwargs.kwargs["headers"] == {"x-api-key": "my-secret-key"}

            mock_get.reset_mock()

            # Without API key
            sss._s2_request("/paper/search", {}, api_key=None)
            call_kwargs = mock_get.call_args
            assert call_kwargs.kwargs["headers"] == {}


# --- year filter formatting ---


class TestYearFilter:
    def test_both_years(self):
        assert sss._format_year_filter(2020, 2024) == "2020-2024"

    def test_start_only(self):
        assert sss._format_year_filter(2020, None) == "2020-"

    def test_end_only(self):
        assert sss._format_year_filter(None, 2024) == "-2024"

    def test_neither(self):
        assert sss._format_year_filter(None, None) is None
