from sentence_transformers import util
import torch


class Reranker:
    def __init__(self):
        from backend.ingestion.embedder import get_embedder
        self.embedder = get_embedder()

    def rerank(self, query, documents, top_k=5):
        if not documents:
            return []

        query_embedding = self.embedder.embed(query)
        query_embedding = torch.tensor([query_embedding])

        doc_texts = [doc['text'] for doc in documents]
        doc_embeddings = self.embedder.embed_batch(doc_texts)
        doc_embeddings = torch.tensor(doc_embeddings)

        cos_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

        scored_docs = [
            (i, float(cos_scores[i]))
            for i in range(len(documents))
        ]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        reranked = []
        for idx, score in scored_docs[:top_k]:
            doc = documents[idx].copy()
            doc['rerank_score'] = score
            reranked.append(doc)

        return reranked
