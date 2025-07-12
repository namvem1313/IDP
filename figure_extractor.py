# figures.py

import fitz  # PyMuPDF

def extract_figures(pdf_path):
    doc = fitz.open(pdf_path)
    figures = []

    for page_num, page in enumerate(doc):
        images = page.get_images(full=True)
        for i, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            fig = {
                "page": page_num + 1,
                "name": f"figure_{page_num+1}_{i+1}.png",
                "image_bytes": image_bytes
            }
            figures.append(fig)
    
    return figures
