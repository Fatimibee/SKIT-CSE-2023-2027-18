"""
Unit tests for batch document processing and multi-document endpoints.
"""

import pytest
import io
from PIL import Image, ImageDraw

from ocr_service import process_batch_documents, OCRError


def create_mock_cert_image(text_line: str) -> bytes:
    img = Image.new("RGB", (500, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text_line, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_process_batch_documents_success():
    img1 = create_mock_cert_image("Name: Disha Toshniwal\nDOB: 12/05/2002")
    img2 = create_mock_cert_image("Annual Income: Rs 1,80,000\nCategory: General")

    files_data = [
        ("aadhaar.png", img1),
        ("income_cert.png", img2),
    ]

    res = process_batch_documents(files_data)
    assert res["status"] == "success"
    assert res["total_documents"] == 2
    assert "combined_extracted_fields" in res
    assert "documents" in res
    assert len(res["documents"]) == 2


def test_process_batch_documents_empty_raises_error():
    with pytest.raises(OCRError):
        process_batch_documents([])
