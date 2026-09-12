"""
ocr_service.py
---------------
All OCR / text-extraction logic and QR code scanning live here, with NO web-framework code
at all (no FastAPI imports here).

Supported inputs:
- Images (jpg/jpeg/png)          -> OCR directly with pytesseract + QR scanning with OpenCV
- Text-based PDFs (has real text)-> extract text directly (fast, accurate) + QR scanning
- Scanned/image-based PDFs       -> render each page to an image, then OCR + QR scanning

Everything here works on raw bytes (not file paths), so the caller
(ocr_routes.py) never needs to save the upload to disk.
"""

import io
import logging
from typing import List, Dict, Any, Tuple

from PIL import Image, ImageOps, UnidentifiedImageError
import pytesseract
import pypdf
from pdf2image import convert_from_bytes
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError
import cv2
import numpy as np

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


def extract_qr_codes_from_image(image: Image.Image) -> List[str]:
    """Scan a PIL Image for QR codes and return a list of decoded string contents."""
    qr_results = []
    try:
        # Add white padding to ensure a clean quiet zone around QR codes for detection
        padded_img = ImageOps.expand(image.convert("RGB"), border=30, fill="white")
        cv_img = cv2.cvtColor(np.array(padded_img), cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()

        # Method 1: detectAndDecode (robust for single QR codes)
        try:
            single_text, _, _ = detector.detectAndDecode(cv_img)
            if single_text and single_text.strip():
                qr_results.append(single_text.strip())
        except Exception as exc:
            logger.debug("detectAndDecode failed: %s", exc)

        # Method 2: detectAndDecodeMulti (multi QR code detection)
        try:
            retval, decoded_info, _, _ = detector.detectAndDecodeMulti(cv_img)
            if retval and decoded_info:
                for info in decoded_info:
                    if info and str(info).strip():
                        qr_results.append(str(info).strip())
        except Exception as exc:
            logger.debug("detectAndDecodeMulti failed: %s", exc)

    except Exception as exc:
        logger.warning("QR extraction failed on image: %s", exc)

    return list(dict.fromkeys(qr_results))


def extract_text_from_image(file_bytes: bytes) -> str:
    """Run OCR on raw image bytes (jpg/jpeg/png) and return extracted text."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
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


def _extract_text_layer_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
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
        text = ocr_text if ocr_text else text

    if not text:
        raise OCRError(
            "No readable text could be found in this document "
            "(it may be blank, very low quality, or unreadable)."
        )

    return text


def process_document(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Main entry point used by the API route.

    Given a filename and the raw file bytes, returns a dictionary with
    extracted 'text' and 'qr_data' (list of decoded QR code strings).
    Raises OCRError if neither text nor QR codes could be extracted.
    """
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    text = ""
    qr_codes = []

    if extension in ("jpg", "jpeg", "png"):
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.load()
        except UnidentifiedImageError:
            raise OCRError("This does not appear to be a valid image file.")
        except Exception as exc:
            raise OCRError(f"Could not open image file: {exc}")

        try:
            text = pytesseract.image_to_string(image).strip()
        except pytesseract.TesseractError as exc:
            logger.warning("OCR image extraction failed: %s", exc)

        qr_codes = extract_qr_codes_from_image(image)

    elif extension == "pdf":
        try:
            text, page_count = _extract_text_layer_from_pdf(file_bytes)
        except OCRError:
            text = ""
            page_count = 0

        avg_chars_per_page = len(text) / page_count if page_count else 0
        looks_like_a_scan = avg_chars_per_page < MIN_CHARS_PER_PAGE_TO_TRUST_TEXT_LAYER

        # Render PDF pages to scan for QR codes and fallback OCR
        try:
            pages = convert_from_bytes(file_bytes)
            for page_image in pages:
                qrs = extract_qr_codes_from_image(page_image)
                qr_codes.extend(qrs)

            if looks_like_a_scan and pages:
                page_texts = []
                for page_image in pages:
                    try:
                        page_texts.append(pytesseract.image_to_string(page_image))
                    except Exception:
                        pass
                ocr_text = "\n".join(page_texts).strip()
                text = ocr_text if ocr_text else text
        except (PDFPageCountError, PDFSyntaxError) as exc:
            if not text and not qr_codes:
                raise OCRError(f"This PDF could not be read (it may be corrupted): {exc}")
        except Exception as exc:
            logger.warning("Rendering PDF pages for QR/OCR scanning failed: %s", exc)

    else:
        raise OCRError(f"Unsupported file type: .{extension}")

    unique_qr_codes = list(dict.fromkeys(qr_codes))

    if not text and not unique_qr_codes:
        raise OCRError(
            "No text or QR code could be extracted from this document "
            "(it may be blank, very low quality, or unreadable)."
        )

    return {"text": text, "qr_data": unique_qr_codes}
