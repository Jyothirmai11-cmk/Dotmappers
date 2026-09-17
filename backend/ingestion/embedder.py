from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def embed(self, text):
        return self.model.encode(text, convert_to_tensor=False).tolist()

    def embed_batch(self, texts):
        return self.model.encode(texts, convert_to_tensor=False).tolist()


_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder
