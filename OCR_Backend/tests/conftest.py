"""
conftest.py
------------
Shared pytest fixtures. We generate small sample files on the fly
(instead of committing binary sample files to the repo) so tests are
self-contained and don't depend on any external test-data files.
"""

import io
import sys
import os

import pytest
from PIL import Image, ImageDraw

# Allow tests to import main.py / ocr_service.py / validators.py which live
# one directory up (in the OCR_Backend module root, not inside tests/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402
from main import app as fastapi_app  # noqa: E402


@pytest.fixture
def client():
    """A FastAPI test client for hitting the API endpoints in tests."""
    with TestClient(fastapi_app) as test_client:
        yield test_client


def _make_text_image_bytes(text="HELLO WORLD", fmt="PNG"):
    """Create a simple white image with black text drawn on it, so
    Tesseract has something real to recognize."""
    image = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), text, fill="black")
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def sample_png_bytes():
    return _make_text_image_bytes(fmt="PNG")


@pytest.fixture
def sample_jpg_bytes():
    return _make_text_image_bytes(fmt="JPEG")


@pytest.fixture
def sample_text_pdf_bytes():
    """A real text-based PDF (has an actual text layer), built with
    reportlab, so we can test the 'digital PDF' extraction path."""
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    pdf_canvas.drawString(100, 750, "HELLO WORLD FROM A TEXT PDF")
    pdf_canvas.save()
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def sample_scanned_pdf_bytes():
    """A PDF made from a plain image (no text layer at all), to test the
    OCR-fallback path for scanned documents."""
    image = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "SCANNED PDF TEXT", fill="black")
    buffer = io.BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def corrupted_pdf_bytes():
    """Bytes that look like they might be a PDF but are not valid."""
    return b"%PDF-1.4 this is not a real pdf, just garbage bytes"


@pytest.fixture
def corrupted_image_bytes():
    """Bytes with an image-like extension but invalid image content."""
    return b"this is definitely not a valid jpg file"


@pytest.fixture
def blank_image_bytes():
    """A completely blank image - valid file, but no text to extract."""
    image = Image.new("RGB", (200, 200), color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()
