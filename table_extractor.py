# tables.py

import pdfplumber

def extract_tables(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                extracted_tables = page.extract_tables()
                for table_data in extracted_tables:
                    if table_data and len(table_data) > 1:
                        tables.append({
                            "page": page_num,
                            "table": table_data
                        })
            except Exception as e:
                continue  # skip problematic pages

    return tables
