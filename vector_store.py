# vector_store.py

import faiss
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np

    
def flatten_sections(sections_dict, parent_key=""):
        flat = {}
        for k, v in sections_dict.items():
            full_key = f"{parent_key}/{k}" if parent_key else k
            if isinstance(v, dict):
                flat.update(flatten_sections(v, full_key))  # Recursive call
            elif isinstance(v, str):
                flat[full_key] = v.strip()
        return flat

class VectorStore:
    def __init__(self, embedding_model="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(embedding_model)
        self.paper_indexes = {}  # key: paper_id, value: (faiss.Index, text_chunks)


    def build_index(self, paper_id, sections):
        text_chunks = []
        meta = []

        flat_sections = flatten_sections(sections)

        for section_title, content in flat_sections.items():
            if isinstance(content, str) and content.strip():
                text_chunks.append(f"{section_title}\n{content}")
                meta.append((paper_id, section_title))

        if not text_chunks:
            return

        embeddings = self.model.encode(text_chunks, show_progress_bar=False)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))
        self.paper_indexes[paper_id] = (index, text_chunks, meta)
    
    def query(self, query_text, paper, top_k=1):
        paper_id = "temp"
        sections = paper["sections"]

        # Flatten sections first
        flat_sections = flatten_sections(sections)

        # Rebuild index for this query
        self.build_index(paper_id, flat_sections)

        index, text_chunks, meta = self.paper_indexes[paper_id]

        query_embedding = self.model.encode([query_text])[0].reshape(1, -1)

        distances, indices = index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(text_chunks):
                section_name = meta[idx][1]
                content = text_chunks[idx]
                results.append({
                    "section": section_name,
                    "content": content
                })

        return results

