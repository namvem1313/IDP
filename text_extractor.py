# text_extractor.py

import fitz  # PyMuPDF
import re

SECTION_TITLES = [
    "abstract", "introduction", "background", "related work",
    "method", "methodology", "approach", "experiment", "results",
    "discussion", "conclusion", "references", "acknowledgments"
]

def extract_text_and_structure(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Normalize whitespace
    full_text = re.sub(r'\s+', ' ', full_text)
    structured = {"sections": {}}

    # Abstract handling (if exists in first 1–2 pages)
    abstract_match = re.search(r"(abstract)\s*[:\-]?\s*(.*?)\s*(?=\b" + '|'.join(SECTION_TITLES[1:]) + r"\b)", full_text, re.I | re.S)
    if abstract_match:
        structured["abstract"] = abstract_match.group(2).strip()
    
    # Sectional split
    matches = list(re.finditer(r'\b(' + '|'.join(SECTION_TITLES) + r')\b[:\-]?', full_text, re.I))
    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        section_name = matches[i].group().lower().strip(": -")
        structured["sections"][section_name] = full_text[start:end].strip()

    return structured
