from cross_encoder import CrossEncoder


class Reranker:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank(self, query, documents, top_k=5):
        if not documents:
            return []

        doc_texts = [doc['text'] for doc in documents]

        pairs = [[query, doc] for doc in doc_texts]
        scores = self.model.predict(pairs)

        scored_docs = [
            (i, scores[i])
            for i in range(len(documents))
        ]
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        reranked = []
        for idx, score in scored_docs[:top_k]:
            doc = documents[idx].copy()
            doc['rerank_score'] = float(score)
            reranked.append(doc)

        return reranked
