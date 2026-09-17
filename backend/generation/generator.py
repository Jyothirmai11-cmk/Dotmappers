import google.generativeai as genai
import time
from backend.config import GEMINI_API_KEY, LLM_MODEL
from backend.generation.prompt import format_generation_prompt


genai.configure(api_key=GEMINI_API_KEY)


class Generator:
    def __init__(self):
        self.model = genai.GenerativeModel(LLM_MODEL)

    def generate(self, context_passages, question):
        prompt = format_generation_prompt(context_passages, question)

        start_time = time.time()
        response = self.model.generate_content(prompt)
        latency = time.time() - start_time

        answer = response.text if response else "No response generated."

        result = {
            "answer": answer,
            "sources": list(set([p['metadata']['source'] for p in context_passages])),
            "context_passages": context_passages,
            "latency": latency
        }

        return result


_generator = None


def get_generator():
    global _generator
    if _generator is None:
        _generator = Generator()
    return _generator
