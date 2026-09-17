from rank_bm25 import BM25Okapi
from backend.retrieval.vector_store import get_vector_store


class BM25Retriever:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.corpus = []
        self.bm25 = None
        self.doc_metadata = []
        self._build_index()

    def _build_index(self):
        all_docs = self.vector_store.get_all_documents()

        if all_docs['documents']:
            self.corpus = all_docs['documents']
            self.doc_metadata = all_docs['metadatas']
            tokenized_corpus = [doc.split() for doc in self.corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            self.bm25 = None

    def search(self, query, top_k=10):
        if self.bm25 is None or not self.corpus:
            return []

        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)

        scored_docs = [
            (idx, scores[idx])
            for idx in range(len(self.corpus))
        ]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scored_docs[:top_k]:
            results.append({
                "text": self.corpus[idx],
                "metadata": self.doc_metadata[idx],
                "score": float(score)
            })

        return results

    def refresh(self):
        self._build_index()
