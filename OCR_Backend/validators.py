"""
validators.py
--------------
Small, standalone helper functions to validate an uploaded file
BEFORE we try to run OCR on it.

Deliberately framework-agnostic: it works on a plain filename + raw
bytes, not on a Flask/FastAPI-specific upload object. That keeps it
reusable and easy to unit test on its own.
"""

# Extensions we accept for this module (lowercase, without the dot)
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

# Simple size cap so someone can't upload a huge file and hang the server.
# 10 MB is more than enough for a scanned government document.
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def get_file_extension(filename: str) -> str:
    """Return the lowercase extension of a filename, without the dot.
    Example: 'Aadhar.PDF' -> 'pdf'. Returns '' if there is no extension.
    """
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def is_allowed_extension(filename: str) -> bool:
    """Check if the file's extension is one we support."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def validate_upload(filename, file_bytes):
    """
    Validate an uploaded file.

    Args:
        filename: the original filename sent by the client (or None/"" if
                   no file was sent at all).
        file_bytes: the raw file content as bytes (or None if no file
                     was sent at all).

    Checks, in order:
      1. A file was actually sent (filename + bytes present)
      2. The extension is allowed (pdf/jpg/jpeg/png)
      3. The file is not empty and not larger than MAX_FILE_SIZE_MB

    Returns:
        (is_valid: bool, error_message: str or None)
    """
    if not filename:
        return False, "No file was uploaded. Please attach a file."

    if not is_allowed_extension(filename):
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return False, f"Unsupported file type. Allowed types: {allowed}."

    if file_bytes is None or len(file_bytes) == 0:
        return False, "The uploaded file is empty."

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return False, f"File is too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB."

    return True, None
