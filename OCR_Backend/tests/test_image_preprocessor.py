"""
Unit tests for image preprocessor (deskewing, contrast enhancement, noise reduction).
"""

import pytest
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import io

from image_preprocessor import (
    bytes_to_cv2,
    cv2_to_bytes,
    deskew_image,
    enhance_contrast_and_denoise,
    preprocess_document_image,
)


@pytest.fixture
def sample_image_bytes():
    """Generates a clean test image with text bytes."""
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), "INCOME CERTIFICATE 180000", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_bytes_to_cv2_and_back(sample_image_bytes):
    cv_img = bytes_to_cv2(sample_image_bytes)
    assert cv_img is not None
    assert isinstance(cv_img, np.ndarray)
    assert cv_img.shape[0] > 0 and cv_img.shape[1] > 0

    reconstructed_bytes = cv2_to_bytes(cv_img, ".png")
    assert reconstructed_bytes is not None
    assert len(reconstructed_bytes) > 0


def test_deskew_image_straight_image(sample_image_bytes):
    cv_img = bytes_to_cv2(sample_image_bytes)
    deskewed = deskew_image(cv_img)
    assert deskewed is not None
    assert deskewed.shape == cv_img.shape


def test_enhance_contrast_and_denoise(sample_image_bytes):
    cv_img = bytes_to_cv2(sample_image_bytes)
    enhanced = enhance_contrast_and_denoise(cv_img)
    assert enhanced is not None
    assert enhanced.shape == cv_img.shape


def test_preprocess_document_image_returns_valid_bytes(sample_image_bytes):
    processed = preprocess_document_image(sample_image_bytes)
    assert processed is not None
    assert isinstance(processed, bytes)
    assert len(processed) > 0


def test_preprocess_document_image_handles_invalid_bytes():
    invalid_bytes = b"NOT_AN_IMAGE_DATA"
    res = preprocess_document_image(invalid_bytes)
    assert res == invalid_bytes
