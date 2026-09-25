"""
Image Preprocessing Pipeline for Document OCR & QR Detection.
Provides deskewing, noise reduction, and contrast enhancement
for low-quality mobile scans of identity & income certificates.
"""

import cv2
import numpy as np
from PIL import Image
import io


def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Converts raw image bytes to an OpenCV BGR numpy array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def cv2_to_bytes(cv2_img: np.ndarray, format_ext: str = ".png") -> bytes:
    """Converts an OpenCV BGR image back to raw bytes."""
    is_success, buffer = cv2.imencode(format_ext, cv2_img)
    if not is_success:
        raise ValueError("Failed to encode image to bytes.")
    return buffer.tobytes()


def deskew_image(img: np.ndarray) -> np.ndarray:
    """
    Detects skew angle in document image and auto-rotates it.
    Uses minimum area rectangle bounding box on text contours.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Invert image (text becomes white, background black)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Dilate text blocks to merge lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img

    # Get largest contour assumed to be the main document text block
    largest_contour = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(largest_contour)
    angle = rect[-1]

    # Adjust angle for OpenCV minAreaRect conventions
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Ignore minor skew angles under 0.5 degrees or extreme rotations > 45 degrees
    if abs(angle) < 0.5 or abs(angle) > 45:
        return img

    # Rotate image around center
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


def enhance_contrast_and_denoise(img: np.ndarray) -> np.ndarray:
    """
    Applies CLAHE (Contrast Limited Adaptive Histogram Equalization)
    and mild bilateral filtering for noise reduction on mobile photos.
    """
    # Convert BGR to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to L-channel for adaptive contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Merge channels back
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # Mild denoising while preserving sharp text edges
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=50, sigmaSpace=50)
    return denoised


def preprocess_document_image(image_bytes: bytes) -> bytes:
    """
    Main entry point for image preprocessing pipeline.
    Deskews, enhances contrast, and denoises image bytes.
    Returns enhanced image bytes.
    """
    try:
        cv2_img = bytes_to_cv2(image_bytes)
        if cv2_img is None:
            return image_bytes  # Return original if unparseable by OpenCV

        # Step 1: Deskew (Auto-rotate)
        deskewed = deskew_image(cv2_img)

        # Step 2: Enhance contrast & denoise
        enhanced = enhance_contrast_and_denoise(deskewed)

        return cv2_to_bytes(enhanced, format_ext=".png")
    except Exception:
        # Fallback to raw bytes if any preprocessing error occurs
        return image_bytes
