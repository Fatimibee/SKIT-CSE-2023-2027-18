"""
ocr_routes.py
--------------
The web-facing layer only: receives the HTTP request, validates it,
calls into ocr_service.py to do the real work, and formats the JSON
response. No OCR logic should live in this file.

Exposes:
    POST /ocr/extract          -> raw extracted text only
    POST /ocr/extract-fields   -> structured fields + verification

Both take multipart/form-data with the field name "file".
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from document_verifier import verify_extracted_data
from field_extractor import extract_fields
from ocr_service import process_document, OCRError
from validators import validate_upload

logger = logging.getLogger(__name__)

# An APIRouter lets this module be wired into any FastAPI app
# (this standalone one, or later the team's main FastAPI app) with:
#   from ocr_routes import router as ocr_router
#   app.include_router(ocr_router)
router = APIRouter(prefix="/ocr", tags=["OCR"])


def _success_response(filename: str, text: str):
    return {"success": True, "filename": filename, "text": text}


def _error_response(filename: str, error_message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "filename": filename, "error": error_message},
    )


@router.post("/extract")
async def extract(file: Optional[UploadFile] = File(default=None)):
    """
    Accepts a single uploaded document and returns extracted text.

    Request:  multipart/form-data, field "file"
    Response: {"success": true, "filename": "...", "text": "..."}
           or {"success": false, "filename": "...", "error": "..."}
    """
    filename = file.filename if file else None
    file_bytes = await file.read() if file else None

    # --- Step 1: validate the upload itself (type/size/presence) ---
    is_valid, error_message = validate_upload(filename, file_bytes)
    if not is_valid:
        return _error_response(filename or "unknown", error_message, status_code=400)

    # --- Step 2: run OCR / text extraction ---
    try:
        text = process_document(filename, file_bytes)
    except OCRError as exc:
        # A known, explainable failure (corrupted file, no text found, etc).
        # 422 = "Unprocessable Entity": the request was well-formed, but we
        # couldn't do anything useful with the file's content.
        return _error_response(filename, str(exc), status_code=422)
    except Exception:
        # Catch-all so an unexpected bug never crashes the server or leaks
        # a raw traceback - the client always gets clean JSON back.
        logger.exception("Unexpected error while processing '%s'", filename)
        return _error_response(
            filename,
            "An unexpected error occurred while processing the document.",
            status_code=500,
        )

    return _success_response(filename, text)


# ---------------------------------------------------------------------------
# POST /ocr/extract-fields
# ---------------------------------------------------------------------------
# Reuses exactly the same upload validation and OCR pipeline as
# /ocr/extract above, then adds two extra steps on top of the raw text:
#
#   raw OCR text -> field_extractor    -> structured citizen fields
#                -> document_verifier  -> internal validity report
#
# /ocr/extract is deliberately left untouched, so anything already
# calling it keeps working unchanged.
# ---------------------------------------------------------------------------


@router.post("/extract-fields")
async def extract_structured_fields(file: Optional[UploadFile] = File(default=None)):
    """
    Accepts a single uploaded document and returns structured citizen
    information extracted from it, plus an internal verification report.

    Request:  multipart/form-data, field "file"
    Response (success):
        {
          "success": true,
          "filename": "...",
          "document_type": "Income Certificate",
          "extracted_data": { ...the supported fields, null when unknown... },
          "verification": {"is_valid": true, "issues": [], ...},
          "raw_text": "..."
        }
    Response (failure):
        {"success": false, "filename": "...", "error": "..."}

    NOTE: "verification" is local/internal validation only. It does NOT
    check the document against any government database.
    """
    filename = file.filename if file else None
    file_bytes = await file.read() if file else None

    # --- Step 1: validate the upload itself (type/size/presence) ---
    is_valid, error_message = validate_upload(filename, file_bytes)
    if not is_valid:
        return _error_response(filename or "unknown", error_message, status_code=400)

    # --- Step 2: run OCR / text extraction (same service as /extract) ---
    try:
        text = process_document(filename, file_bytes)
    except OCRError as exc:
        return _error_response(filename, str(exc), status_code=422)
    except Exception:
        logger.exception("Unexpected error while processing '%s'", filename)
        return _error_response(
            filename,
            "An unexpected error occurred while processing the document.",
            status_code=500,
        )

    # --- Step 3: structured field extraction + Step 4: verification ---
    # These are pure text-in / dict-out functions, but they are still
    # wrapped so that an unexpected bug in the rules can never take the
    # endpoint down - the caller always gets clean JSON back.
    try:
        extracted_data = extract_fields(text)
        verification = verify_extracted_data(extracted_data, raw_text=text)
    except Exception:
        # Only the filename is logged, never the document's contents.
        logger.exception("Unexpected error while extracting fields from '%s'", filename)
        return _error_response(
            filename,
            "The document was read, but its information could not be processed.",
            status_code=500,
        )

    return {
        "success": True,
        "filename": filename,
        # Surfaced at the top level for convenience, and also kept inside
        # extracted_data so the full field set stays in one place.
        "document_type": extracted_data["document_type"],
        "extracted_data": extracted_data,
        "verification": verification,
        "raw_text": text,
    }
