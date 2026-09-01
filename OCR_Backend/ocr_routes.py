"""
ocr_routes.py
--------------
The web-facing layer only: receives the HTTP request, validates it,
calls into ocr_service.py to do the real work, and formats the JSON
response. No OCR logic should live in this file.

Exposes:
    POST /ocr/extract   (multipart/form-data, field name = "file")
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

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
