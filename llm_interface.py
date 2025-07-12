# llm_interface.py

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch


class LocalLLM:
    def __init__(self, model_name="gpt2", max_tokens=256):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self._load_model()

    def _load_model(self):
        print(f"🔍 Loading HuggingFace model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )
        print("✅ LLM loaded.")

    def ask(self, context, question):
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        try:
            output = self.pipeline(
                prompt,
                max_new_tokens=self.max_tokens,
                do_sample=False,
                return_full_text=False
            )[0]["generated_text"]
            return output.strip()
        except Exception as e:
            print(f"⚠️ LLM error: {e}")
            return "[LLM Error]"