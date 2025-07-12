# Intelligent Document Processing Agent

This project implements a deep learning-powered agent that ingests academic PDFs, extracts structured content, and enables intelligent querying via a local LLM — all through a clean Streamlit UI.

# Intelligent Document Processing (IDP) for Academic Papers

A lightweight pipeline and Streamlit-based interface to extract, analyze, query, and compare academic research papers in PDF format.
---

## Features

✅ **Multi-PDF Upload** with consistent file naming  
✅ **Accurate Parsing** into structured sections (title, abstract, body, references)  
✅ **Semantic Search & QA** using local embedding models  
✅ **Section-Based Comparison** across two research papers  
✅ **Optional Summarization** and LLM-based responses  
✅ **Offline / Private Deployment** 

---

## Project Structure

IDP/
├── app.py # Streamlit app UI
├── document_store.py # Stores and loads parsed paper data
├── vector_store.py # Embedding & FAISS-based search
├── query_engine.py # Semantic search, QA, section comparison
├── extract/
│ └── pdf_parser.py 
├── data/
│ └── papers/ # JSON files for parsed PDFs
└── README.md


---

## How to Run

### 1. Setup Environment
```bash
git clone https://github.com/yourusername/IDP.git
cd IDP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch the App

streamlit run app.py

### 3. Usage Workflow

Upload PDFs
Upload one or more academic papers. Each paper is parsed and saved as a structured .json.

Ask Questions
Select a paper and ask research-specific questions. Results are generated via embedding-based search + LLM.

Compare Papers
Choose two papers and select corresponding sections (e.g., Introduction, Results) to compare them side by side.

### 4. Dependencies

streamlit
faiss
sentence-transformers
PyMuPDF or pdfminer.six (parser)
transformers (for local summarization)
torch, numpy, json

### 5. Next Steps

Local OCR-based support for scanned papers
Table & figure extraction + caption linking
Auto-validation of section splits and metadata
SQLite-based persistent vector store
Optional Docker / Kubernetes setup for scale

