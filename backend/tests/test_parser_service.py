"""Tests for parser_service (PDF parsing logic)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import patch, MagicMock
from app.services.parser_service import parse_pdf


@pytest.mark.asyncio
async def test_parse_pdf_returns_text_and_sections():
    """parse_pdf should return a non-empty string and a sections dict."""
    sample_text = (
        "Jane Smith\n\n"
        "SKILLS\nPython, FastAPI\n\n"
        "EXPERIENCE\nBackend Engineer at Acme (2022-Present)\n"
    )
    mock_page = MagicMock()
    mock_page.extract_text.return_value = sample_text

    mock_pdf = MagicMock()
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = [mock_page]

    with patch("app.services.parser_service.pdfplumber.open", return_value=mock_pdf):
        text, sections = await parse_pdf(b"fake-pdf-bytes")

    assert "Jane Smith" in text
    assert isinstance(sections, dict)
    assert "skills" in sections
    assert "experience" in sections


@pytest.mark.asyncio
async def test_parse_pdf_raises_on_empty_text():
    """parse_pdf should raise an exception when no text is extracted."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""

    mock_pdf = MagicMock()
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = [mock_page]

    with patch("app.services.parser_service.pdfplumber.open", return_value=mock_pdf):
        with pytest.raises(Exception, match="PDF parsing error"):
            await parse_pdf(b"fake-pdf-bytes")


@pytest.mark.asyncio
async def test_parse_pdf_concatenates_multiple_pages():
    """Text from all pages should be combined."""
    page1 = MagicMock()
    page1.extract_text.return_value = "Page one content\n"
    page2 = MagicMock()
    page2.extract_text.return_value = "Page two content\n"

    mock_pdf = MagicMock()
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = [page1, page2]

    with patch("app.services.parser_service.pdfplumber.open", return_value=mock_pdf):
        text, _ = await parse_pdf(b"fake-pdf-bytes")

    assert "Page one content" in text
    assert "Page two content" in text
