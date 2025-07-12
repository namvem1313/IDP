# document_store.py

import os
import json

class DocumentStore:
    def __init__(self, data_dir="data/papers"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.documents = {}  # key: paper_id, value: dict
        self.load_all()

    def load_all(self):
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.data_dir, filename)
                paper_id = os.path.splitext(filename)[0]
                try:
                    with open(path, "r") as f:
                        self.documents[paper_id] = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to load JSON for {filename}: {e}")

    def list_papers(self):
        """Return list of available paper IDs and titles."""
        return [
            {"id": pid, "title": doc.get("title", "Untitled")}
            for pid, doc in self.documents.items()
        ]

    def get_paper(self, paper_id):
        """Return full paper data."""
        return self.documents.get(paper_id)

    def get_section(self, paper_id, section_name):
        paper = self.get_paper(paper_id)
        if not paper or "sections" not in paper:
            return None

        for sec, content in paper["sections"].items():
            if section_name.strip().lower() in sec.strip().lower():
                return content
        return None

    def search_papers(self, keyword):
        """Return papers containing a keyword in title or abstract."""
        results = []
        for pid, doc in self.documents.items():
            title = doc.get("title", "").lower()
            abstract = doc.get("abstract", "").lower()
            if keyword.lower() in title or keyword.lower() in abstract:
                results.append({"id": pid, "title": doc.get("title")})
        return results
