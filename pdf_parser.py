# process_pdf.py

import os
import json
from text_extractor import extract_text_and_structure
from metadata import extract_metadata
from figure_extractor import extract_figures
from table_extractor import extract_tables

def process_pdf(pdf_path, output_dir="data/papers"):
    paper_id = os.path.splitext(os.path.basename(pdf_path))[0]

    print(f"📄 Processing {paper_id}...")

    # Step 1: Extract Metadata (title, authors, doi)
    metadata = extract_metadata(pdf_path)

    # Step 2: Extract Sections (Introduction, Methods, etc.)
    sections = extract_text_and_structure(pdf_path)

    # Step 3: Extract Figures and Captions
    figures = extract_figures(pdf_path)

    # Step 4: Extract Tables
    tables = extract_tables(pdf_path)

    # Step 5: Construct structured output
    paper_data = {
        "paper_id": paper_id,
        "title": metadata.get("title"),
        "authors": metadata.get("authors"),
        "doi": metadata.get("doi"),
        "sections": sections,
        "figures": figures,
        "tables": tables,
    }

    return paper_data
