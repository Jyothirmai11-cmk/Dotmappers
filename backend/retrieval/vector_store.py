import chromadb
from backend.config import CHROMA_DB_PATH
from backend.ingestion.embedder import get_embedder


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = get_embedder()

    def add_documents(self, chunks, source_name, page_num=1):
        embeddings = self.embedder.embed_batch(chunks)

        ids = [f"{source_name}_{page_num}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": source_name, "page": page_num, "chunk_id": i}
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    def search(self, query, top_k=10):
        query_embedding = self.embedder.embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })

        return formatted_results

    def get_all_documents(self):
        all_docs = self.collection.get()
        return all_docs

    def clear(self):
        self.client.delete_collection(name="documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )


_vector_store = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
