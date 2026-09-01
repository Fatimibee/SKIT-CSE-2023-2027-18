"""
ocr_service.py
---------------
All OCR / text-extraction logic lives here, with NO web-framework code
at all (no FastAPI imports here).

Keeping this file framework-agnostic means:
- It's easy to unit test without spinning up a web server.
- It could be reused later (e.g. a background job, a CLI script)
  without dragging FastAPI along with it.

Supported inputs:
- Images (jpg/jpeg/png)          -> OCR directly with pytesseract
- Text-based PDFs (has real text)-> extract text directly (fast, accurate)
- Scanned/image-based PDFs       -> render each page to an image, then OCR

Everything here works on raw bytes (not file paths), so the caller
(ocr_routes.py) never needs to save the upload to disk.
"""

import io
import logging

from PIL import Image, UnidentifiedImageError
import pytesseract
import pypdf
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError

logger = logging.getLogger(__name__)

# If a text-based PDF yields fewer than this many characters per page on
# average, we assume it's actually a scan (no real text layer) and fall
# back to OCR instead.
MIN_CHARS_PER_PAGE_TO_TRUST_TEXT_LAYER = 20


class OCRError(Exception):
    """Raised when a document cannot be processed for a known, explainable
    reason (corrupted file, no readable content, etc). ocr_routes.py
    catches this and turns it into a clean JSON error response."""
    pass


def extract_text_from_image(file_bytes: bytes) -> str:
    """Run OCR on raw image bytes (jpg/jpeg/png) and return extracted text."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Force-load pixel data now so a corrupted/truncated image raises
        # an error here, with a clear message, instead of later.
        image.load()
    except UnidentifiedImageError:
        raise OCRError("This does not appear to be a valid image file.")
    except Exception as exc:
        raise OCRError(f"Could not open image file: {exc}")

    try:
        text = pytesseract.image_to_string(image)
    except pytesseract.TesseractError as exc:
        raise OCRError(f"OCR failed on this image: {exc}")

    return text.strip()


def _extract_text_layer_from_pdf(file_bytes: bytes):
    """Try to pull real (already-digital) text out of a PDF using pypdf.
    Returns (text, page_count). Text may be empty if the PDF has no
    text layer (e.g. it's a scanned document saved as PDF).
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except pypdf.errors.PdfReadError as exc:
        raise OCRError(f"This PDF could not be read (it may be corrupted): {exc}")
    except Exception as exc:
        raise OCRError(f"Could not open PDF file: {exc}")

    if len(reader.pages) == 0:
        raise OCRError("This PDF has no pages.")

    if getattr(reader, "is_encrypted", False):
        raise OCRError("This PDF is password-protected and cannot be read.")

    page_texts = []
    for page in reader.pages:
        try:
            page_texts.append(page.extract_text() or "")
        except Exception:
            # A single unreadable page shouldn't kill the whole extraction;
            # just treat that page as having no text and move on.
            page_texts.append("")

    return "\n".join(page_texts).strip(), len(reader.pages)


def _extract_text_via_ocr_from_pdf(file_bytes: bytes) -> str:
    """Fallback path for scanned/image-based PDFs: render each page to an
    image and OCR it, then join the results together."""
    try:
        pages = convert_from_bytes(file_bytes)
    except (PDFPageCountError, PDFSyntaxError) as exc:
        raise OCRError(f"This PDF could not be read (it may be corrupted): {exc}")
    except Exception as exc:
        raise OCRError(f"Could not render PDF pages for OCR: {exc}")

    if not pages:
        raise OCRError("This PDF has no pages that could be rendered.")

    page_texts = []
    for page_image in pages:
        try:
            page_texts.append(pytesseract.image_to_string(page_image))
        except pytesseract.TesseractError as exc:
            logger.warning("OCR failed on a PDF page: %s", exc)
            page_texts.append("")

    return "\n".join(page_texts).strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF, handling both:
      - text-based PDFs (extract the existing text layer directly)
      - scanned/image-based PDFs (OCR each rendered page)
    """
    text, page_count = _extract_text_layer_from_pdf(file_bytes)

    avg_chars_per_page = len(text) / page_count if page_count else 0
    looks_like_a_scan = avg_chars_per_page < MIN_CHARS_PER_PAGE_TO_TRUST_TEXT_LAYER

    if looks_like_a_scan:
        ocr_text = _extract_text_via_ocr_from_pdf(file_bytes)
        # Prefer whichever result actually has content.
        text = ocr_text if ocr_text else text

    if not text:
        raise OCRError(
            "No readable text could be found in this document "
            "(it may be blank, very low quality, or unreadable)."
        )

    return text


def process_document(filename: str, file_bytes: bytes) -> str:
    """
    Main entry point used by the API route.

    Given a filename (to determine the file type) and the raw file bytes,
    returns the extracted text, or raises OCRError with a message safe to
    show to the user.
    """
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension in ("jpg", "jpeg", "png"):
        text = extract_text_from_image(file_bytes)
    elif extension == "pdf":
        text = extract_text_from_pdf(file_bytes)
    else:
        # Should not normally happen because validators.py already checks
        # this, but we guard here too since this function may be reused
        # elsewhere later.
        raise OCRError(f"Unsupported file type: .{extension}")

    if not text:
        raise OCRError(
            "No text could be extracted from this document "
            "(it may be blank or of very low image quality)."
        )

    return text
