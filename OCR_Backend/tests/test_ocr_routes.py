"""
test_ocr_routes.py
---------------------
Tests for the POST /ocr/extract API endpoint, using FastAPI's TestClient
(no real server needs to be running).
"""


def test_valid_image_upload_returns_extracted_text(client, sample_png_bytes):
    files = {"file": ("sample.png", sample_png_bytes, "image/png")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["filename"] == "sample.png"
    assert "HELLO" in body["text"].upper()


def test_valid_pdf_upload_returns_extracted_text(client, sample_text_pdf_bytes):
    files = {"file": ("sample.pdf", sample_text_pdf_bytes, "application/pdf")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["filename"] == "sample.pdf"
    assert "HELLO WORLD" in body["text"].upper()


def test_unsupported_file_type_is_rejected(client):
    files = {"file": ("notes.txt", b"just some text", "text/plain")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "unsupported" in body["error"].lower()


def test_missing_file_is_rejected(client):
    response = client.post("/ocr/extract")

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "no file" in body["error"].lower()


def test_empty_file_is_rejected(client):
    files = {"file": ("empty.png", b"", "image/png")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "empty" in body["error"].lower()


def test_corrupted_file_returns_meaningful_error(client, corrupted_image_bytes):
    files = {"file": ("broken.jpg", corrupted_image_bytes, "image/jpeg")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]  # some non-empty, meaningful message
    assert body["filename"] == "broken.jpg"


def test_blank_document_returns_meaningful_error(client, blank_image_bytes):
    files = {"file": ("blank.png", blank_image_bytes, "image/png")}
    response = client.post("/ocr/extract", files=files)

    # A blank image has no text to extract - this should fail gracefully,
    # not crash and not falsely report success.
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
