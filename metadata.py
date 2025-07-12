# metadata.py

import fitz  # PyMuPDF
import re

def extract_metadata(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text()

    lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
    
    # Heuristic: First non-empty line with > 4 words is often the title
    title = ""
    for line in lines:
        if len(line.split()) >= 5:
            title = line
            break

    # Heuristic: Look for typical author patterns (comma-separated, names with initials)
    author_pattern = re.compile(r"([A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+)?)")
    author_candidates = [line for line in lines if ',' in line and author_pattern.search(line)]

    authors = []
    if author_candidates:
        candidate_line = author_candidates[0]
        authors = [a.strip() for a in candidate_line.split(',') if len(a.strip()) > 2]

    # DOI (optional)
    doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', first_page_text, re.I)
    doi = doi_match.group(1) if doi_match else None

    return {
        "title": title.strip() if title else None,
        "authors": authors,
        "doi": doi
    }
