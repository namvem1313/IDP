# query_engine.py

from document_store import DocumentStore
from vector_store import VectorStore
import re
from transformers import pipeline

    
def flatten_sections(sections_dict, parent_key=""):
        flat = {}
        for k, v in sections_dict.items():
            full_key = f"{parent_key}/{k}" if parent_key else k
            if isinstance(v, dict):
                flat.update(flatten_sections(v, full_key))  # Recursive call
            elif isinstance(v, str):
                flat[full_key] = v.strip()
        return flat

class QueryEngine:
    def __init__(self):
        self.store = DocumentStore()
        self.vector = VectorStore()
        self.summarizer = None

    def llm_answer(self, prompt):
        try:
            self.summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn", 
            device=-1)
            MAX_INPUT_CHARS = 3000
            prompt = prompt[:MAX_INPUT_CHARS]
            result = self.summarizer(prompt, max_length=3000, min_length=50, do_sample=False)
            print(result)
            return result[0]["summary_text"]
        except Exception as e:
            return f"⚠️ LLM error: {str(e)}"

    def lookup(self, paper_id, section_name):
        content = self.store.get_section(paper_id, section_name)
        return content if content else f"⚠️ Section '{section_name}' not found in paper '{paper_id}'."

    def _split_text(self, text, max_tokens=500):
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_tokens):
            chunk = " ".join(words[i:i+max_tokens])
            chunks.append(chunk)
        return chunks

    def summarize_paper(self, paper_id):
        paper = self.store.get_paper(paper_id)
        paper["full_text"] = paper.get("title", "") + "\n\n"
        paper["full_text"] += "\n\n".join(
            section["text"] if isinstance(section, dict) and "text" in section
            else section if isinstance(section, str)
            else ""
            for section in paper.get("sections", {}).values()
        )
        print(f"DEBUG: Paper keys: {list(paper.keys()) if paper else 'No paper found'}")
        if not paper or "full_text" not in paper:
            return "⚠️ No content available to summarize."

        full_text = paper["full_text"]
        chunks = self._split_text(full_text, max_tokens=1000)

        summaries = []
        for chunk in chunks:
            try:
                self.summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn", 
            device=-1)
                output = self.summarizer(chunk, max_length=150, min_length=40, do_sample=False)
                summaries.append(output[0]["summary_text"])
            except Exception as e:
                summaries.append(f"⚠️ Chunk failed: {e}")

        return "\n\n".join(summaries)

    def extract_metrics(self, paper_id, metrics):
        paper = self.store.get_paper(paper_id)
        if not paper or "sections" not in paper:
            return f"⚠️ No content available for paper '{paper_id}'."

        # Extract section texts safely
        section_texts = [
            section["text"] for section in paper["sections"].values()
            if isinstance(section, dict) and "text" in section
        ]

        full_text = "\n".join(section_texts)

        results = {}
        for metric in metrics:
            pattern = rf"{metric}\s*[:=]?\s*([\d\.]+)"
            match = re.findall(pattern, full_text, flags=re.IGNORECASE)
            results[metric] = match if match else "Not found"

        return results


    def compare_sections(self, paper_id1, section1, paper_id2, section2):
        paper1 = self.store.get_paper(paper_id1)
        paper2 = self.store.get_paper(paper_id2)

        def get_section(paper, section_key):
            try:
                # Handle nested keys like "sections/abstract"
                parts = section_key.split("/")
                content = paper
                for part in parts:
                    content = content.get(part, {})
                if isinstance(content, str):
                    return content.strip()
                return str(content) if content else ""
            except Exception as e:
                return f"⚠️ Error accessing section '{section_key}': {str(e)}"

        content1 = get_section(paper1, section1)
        content2 = get_section(paper2, section2)

        prompt = f"""Compare the following two research paper sections and highlight similarities and differences.

            --- Paper 1 ({section1}) ---
            {content1[:3000]}

            --- Paper 2 ({section2}) ---
            {content2[:3000]}

            Your response should include:
            - What Paper 1 says
            - What Paper 2 says
            - Key similarities
            - Key differences
            - Optional: Conclusion on which paper is more detailed or impactful, if relevant."""

        return self.llm_answer(prompt)

    def ask_question(self, paper_id, question):
        paper = self.store.get_paper(paper_id)
        if not paper:
            return "⚠️ Paper not found."
        
        hits = self.vector.query(query_text=question, paper=paper, top_k=3)

        if not hits:
            return "⚠️ No relevant information found in the paper."

        context = "\n---\n".join([h["content"] for h in hits])
        prompt = f"""Given the following paper content:\n{context}\n\nAnswer the question:\n{question}"""

        return self.llm_answer(prompt)


    def search_across_papers(self, query_text, top_k=1):
        results = []
        for paper_id, paper_data in self.store.documents.items():
            if "sections" not in paper_data:
                continue

            # 🔽 fix nested structure
            sections = paper_data["sections"]
            if "sections" in sections:
                sections = sections["sections"]

            flat_sections = flatten_sections(sections)
            self.vector.build_index(paper_id, flat_sections)

            hits = self.vector.query(query_text=query_text, paper=paper_data, top_k=top_k)
            for hit in hits:
                results.append({
                    "paper_id": paper_id,
                    "section": hit["section"],
                    "content": hit["content"]
                })
        return results
