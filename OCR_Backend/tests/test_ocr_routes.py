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
    assert "text" in body
    assert "qr_data" in body
    assert "HELLO" in body["text"].upper()


def test_valid_qr_image_upload_returns_qr_data(client, sample_qr_image_bytes):
    files = {"file": ("qr_card.png", sample_qr_image_bytes, "image/png")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["filename"] == "qr_card.png"
    assert "qr_data" in body
    assert len(body["qr_data"]) > 0
    assert "GOVT_SCHEME_USER_DEMO_DATA" in body["qr_data"][0]


def test_valid_pdf_upload_returns_extracted_text(client, sample_text_pdf_bytes):
    files = {"file": ("sample.pdf", sample_text_pdf_bytes, "application/pdf")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["filename"] == "sample.pdf"
    assert "text" in body
    assert "qr_data" in body
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

    # A blank image has no text or QR code to extract - this should fail gracefully,
    # not crash and not falsely report success.
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False


# ===========================================================================
# POST /ocr/extract-fields  (structured extraction + verification)
#
# The tests above must keep passing untouched - /ocr/extract is unchanged.
# ===========================================================================


def test_extract_fields_returns_structured_data(
    client, sample_income_certificate_pdf_bytes
):
    files = {
        "file": (
            "income_certificate.pdf",
            sample_income_certificate_pdf_bytes,
            "application/pdf",
        )
    }
    response = client.post("/ocr/extract-fields", files=files)

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["filename"] == "income_certificate.pdf"
    assert body["document_type"] == "Income Certificate"

    data = body["extracted_data"]
    assert data["name"] == "Rahul Sharma"
    assert data["date_of_birth"] == "12/05/2002"
    assert data["gender"] == "Male"
    assert data["category"] == "OBC"
    assert data["annual_income"] == 180000
    assert data["state"] == "Rajasthan"
    assert data["district"] == "Jaipur"
    assert data["document_type"] == "Income Certificate"

    assert body["verification"]["is_valid"] is True
    assert body["verification"]["issues"] == []

    # The raw OCR text is still returned, so nothing is lost.
    assert "INCOME CERTIFICATE" in body["raw_text"].upper()


def test_extract_fields_response_has_all_expected_keys(
    client, sample_income_certificate_pdf_bytes
):
    files = {"file": ("doc.pdf", sample_income_certificate_pdf_bytes, "application/pdf")}
    body = client.post("/ocr/extract-fields", files=files).json()

    assert set(body.keys()) == {
        "success", "filename", "document_type",
        "extracted_data", "verification", "raw_text", "qr_data",
    }
    assert set(body["extracted_data"].keys()) == {
        "name", "date_of_birth", "age", "gender", "category",
        "annual_income", "state", "district", "address", "document_type",
    }
    assert set(body["verification"].keys()) == {
        "is_valid", "issues", "missing_fields", "extracted_fields",
    }


def test_extract_fields_returns_null_for_fields_not_in_the_document(
    client, sample_png_bytes
):
    # This image only contains "HELLO WORLD" - there are no citizen
    # fields in it at all, so everything must come back as null rather
    # than invented.
    files = {"file": ("hello.png", sample_png_bytes, "image/png")}
    response = client.post("/ocr/extract-fields", files=files)

    assert response.status_code == 200
    body = response.json()
    data = body["extracted_data"]

    assert data["date_of_birth"] is None
    assert data["annual_income"] is None
    assert data["category"] is None
    assert data["document_type"] == "Unknown"
    # Missing information must not be reported as invalid information.
    assert body["verification"]["is_valid"] is True


def test_extract_fields_rejects_unsupported_file_type(client):
    files = {"file": ("notes.txt", b"just some text", "text/plain")}
    response = client.post("/ocr/extract-fields", files=files)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "unsupported" in body["error"].lower()


def test_extract_fields_rejects_missing_file(client):
    response = client.post("/ocr/extract-fields")

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "no file" in body["error"].lower()


def test_extract_fields_rejects_empty_file(client):
    files = {"file": ("empty.png", b"", "image/png")}
    response = client.post("/ocr/extract-fields", files=files)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "empty" in body["error"].lower()


def test_extract_fields_corrupted_file_returns_meaningful_error(
    client, corrupted_image_bytes
):
    files = {"file": ("broken.jpg", corrupted_image_bytes, "image/jpeg")}
    response = client.post("/ocr/extract-fields", files=files)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]
    assert body["filename"] == "broken.jpg"


def test_extract_fields_blank_document_returns_meaningful_error(
    client, blank_image_bytes
):
    files = {"file": ("blank.png", blank_image_bytes, "image/png")}
    response = client.post("/ocr/extract-fields", files=files)

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_extract_still_returns_only_raw_text(
    client, sample_income_certificate_pdf_bytes
):
    # Backward compatibility: the original endpoint must be unchanged and
    # must NOT start returning the new structured fields.
    files = {"file": ("doc.pdf", sample_income_certificate_pdf_bytes, "application/pdf")}
    response = client.post("/ocr/extract", files=files)

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"success", "filename", "text", "qr_data"}
    assert "extracted_data" not in body
