"""
run_demo.py
------------
Run a live demonstration of OCR Text Extraction + QR Code Scanning!
"""
import io
import json
from PIL import Image, ImageDraw, ImageOps
import qrcode

from ocr_service import process_document

def main():
    print("=" * 65)
    print(" OCR & QR CODE EXTRACTION MODULE -- LIVE DEMO")
    print("=" * 65)

    # --- Demo 1: QR Code Extraction (e.g. Aadhaar Card QR Code) ---
    print("\n--- [Demo 1] Processing Document containing a QR Code ---")
    qr_payload = json.dumps({
        "name": "Disha Toshniwal",
        "doc_type": "Aadhaar Card",
        "uid": "9257-5466-5700",
        "dob": "15/08/2005",
        "gender": "Female"
    }, indent=2)

    qr_img = qrcode.make(qr_payload)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    qr_bytes = buf.getvalue()

    result_qr = process_document("aadhaar_qr_sample.png", qr_bytes)
    print("  * Filename:", "aadhaar_qr_sample.png")
    print("  * QR Code(s) Found:", len(result_qr["qr_data"]))
    print("  * Extracted QR Payload:")
    print(result_qr["qr_data"][0] if result_qr["qr_data"] else "None")

    # --- Demo 2: Document with both Text and QR Code ---
    print("\n--- [Demo 2] Processing Document with BOTH Heading Text & QR Code ---")
    doc_image = Image.new("RGB", (600, 300), color="white")
    draw = ImageDraw.Draw(doc_image)
    draw.text((20, 20), "GOVERNMENT OF INDIA - INCOME CERTIFICATE", fill="black")
    draw.text((20, 60), "Name: Disha Toshniwal", fill="black")
    draw.text((20, 100), "Annual Income: Rs 150000", fill="black")

    # Paste padded QR code onto document image
    qr_padded = ImageOps.expand(qr_img.resize((150, 150)), border=10, fill="white")
    doc_image.paste(qr_padded, (400, 100))

    buf2 = io.BytesIO()
    doc_image.save(buf2, format="PNG")
    combo_bytes = buf2.getvalue()

    result_combo = process_document("income_certificate.png", combo_bytes)
    print("  * Filename:", "income_certificate.png")
    print("  * Extracted OCR Text:\n", repr(result_combo["text"]))
    print("  * Extracted QR Code Payload:")
    print("   ", result_combo["qr_data"][0] if result_combo["qr_data"] else "None")

    print("\n" + "=" * 65)
    print(" DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()
