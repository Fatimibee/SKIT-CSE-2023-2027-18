"""
test_ocr_service.py
---------------------
Unit tests for ocr_service.py directly (no HTTP layer involved).
These test the core OCR and QR scanning logic in isolation.
"""

import sys
import os
import io

import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_service import (  # noqa: E402
    extract_text_from_image,
    extract_text_from_pdf,
    extract_qr_codes_from_image,
    process_document,
    OCRError,
)


def test_extract_text_from_image_returns_text(sample_png_bytes):
    text = extract_text_from_image(sample_png_bytes)
    assert "HELLO" in text.upper()


def test_extract_text_from_corrupted_image_raises_ocr_error(corrupted_image_bytes):
    with pytest.raises(OCRError):
        extract_text_from_image(corrupted_image_bytes)


def test_extract_text_from_text_based_pdf(sample_text_pdf_bytes):
    text = extract_text_from_pdf(sample_text_pdf_bytes)
    assert "HELLO WORLD FROM A TEXT PDF" in text.upper()


def test_extract_text_from_scanned_pdf_uses_ocr_fallback(sample_scanned_pdf_bytes):
    text = extract_text_from_pdf(sample_scanned_pdf_bytes)
    assert "SCANNED" in text.upper()


def test_extract_text_from_corrupted_pdf_raises_ocr_error(corrupted_pdf_bytes):
    with pytest.raises(OCRError):
        extract_text_from_pdf(corrupted_pdf_bytes)


def test_extract_qr_codes_from_image_detects_qr(sample_qr_image_bytes):
    image = Image.open(io.BytesIO(sample_qr_image_bytes))
    qr_data = extract_qr_codes_from_image(image)
    assert len(qr_data) > 0
    assert "GOVT_SCHEME_USER_DEMO_DATA" in qr_data[0]


def test_process_document_routes_image_correctly(sample_png_bytes):
    result = process_document("sample.png", sample_png_bytes)
    assert "text" in result
    assert "qr_data" in result
    assert "HELLO" in result["text"].upper()


def test_process_document_extracts_qr_from_image(sample_qr_image_bytes):
    result = process_document("qr_card.png", sample_qr_image_bytes)
    assert "qr_data" in result
    assert len(result["qr_data"]) > 0
    assert "GOVT_SCHEME_USER_DEMO_DATA" in result["qr_data"][0]


def test_process_document_routes_pdf_correctly(sample_text_pdf_bytes):
    result = process_document("sample.pdf", sample_text_pdf_bytes)
    assert "text" in result
    assert "qr_data" in result
    assert "HELLO" in result["text"].upper()


def test_process_document_unsupported_extension_raises_ocr_error(sample_png_bytes):
    with pytest.raises(OCRError):
        # Reusing image bytes but with a filename this function shouldn't accept
        process_document("sample.gif", sample_png_bytes)
