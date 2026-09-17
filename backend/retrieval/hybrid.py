from backend.retrieval.vector_store import get_vector_store
from backend.retrieval.bm25_retriever import BM25Retriever


class HybridRetriever:
    def __init__(self):
        self.vector_store = get_vector_store()
        self.bm25 = BM25Retriever()

    def _normalize_scores(self, results, max_score):
        if max_score == 0:
            return results
        return [(text, meta, score / max_score) for text, meta, score in results]

    def search(self, query, top_k=10):
        semantic_results = self.vector_store.search(query, top_k=top_k)
        bm25_results = self.bm25.search(query, top_k=top_k)

        semantic_scores = {
            f"{r['metadata']['source']}_{r['metadata']['page']}_{r['metadata']['chunk_id']}": (1 - r['distance'])
            for r in semantic_results
        }

        bm25_scores = {
            f"{r['metadata']['source']}_{r['metadata']['page']}_{r['metadata']['chunk_id']}": r['score']
            for r in bm25_results
        }

        max_semantic = max(semantic_scores.values()) if semantic_scores else 1
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1

        all_docs = set(list(semantic_scores.keys()) + list(bm25_scores.keys()))

        fused_scores = {}
        for doc_id in all_docs:
            sem_score = (semantic_scores.get(doc_id, 0) / max_semantic) if max_semantic > 0 else 0
            bm25_score = (bm25_scores.get(doc_id, 0) / max_bm25) if max_bm25 > 0 else 0
            fused_scores[doc_id] = (sem_score + bm25_score) / 2

        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        results_map = {}
        for r in semantic_results:
            key = f"{r['metadata']['source']}_{r['metadata']['page']}_{r['metadata']['chunk_id']}"
            results_map[key] = r

        for r in bm25_results:
            key = f"{r['metadata']['source']}_{r['metadata']['page']}_{r['metadata']['chunk_id']}"
            if key not in results_map:
                results_map[key] = r

        final_results = []
        for doc_id, score in sorted_docs[:top_k]:
            if doc_id in results_map:
                result = results_map[doc_id].copy()
                result['fused_score'] = score
                final_results.append(result)

        return final_results

    def refresh(self):
        self.bm25.refresh()
