from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def run_ocr_on_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    all_text = []
    for page_num, page in enumerate(pages):
        text = pytesseract.image_to_string(page)
        all_text.append({
            "page": page_num + 1,
            "text": text.strip()
        })
    return all_text
