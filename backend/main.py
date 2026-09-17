from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from pathlib import Path

from backend.config import DATA_PATH, CHROMA_DB_PATH
from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_text
from backend.retrieval.vector_store import get_vector_store
from backend.retrieval.hybrid import HybridRetriever
from backend.retrieval.reranker import Reranker
from backend.generation.generator import get_generator
from backend.security.injection_guard import sanitize_passages, flag_injection_attempt
from backend.evaluation.metrics import log_evaluation, get_eval_logs, clear_eval_logs, init_eval_db
from backend.evaluation.dataset import get_eval_dataset

app = FastAPI(title="RAG Research Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_eval_db()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list
    context_passages: list
    latency: float
    metrics: dict
    injection_flagged: bool


@app.on_event("startup")
async def startup_event():
    Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
    Path(CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)

    vector_store = get_vector_store()
    existing_docs = vector_store.get_all_documents()

    if not existing_docs['documents']:
        ingest_existing_documents()


def ingest_existing_documents():
    vector_store = get_vector_store()
    data_path = Path(DATA_PATH)

    if not data_path.exists():
        return

    for file_path in data_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.md']:
            try:
                text, metadata, _ = load_document(str(file_path))
                chunks = chunk_text(text)

                vector_store.add_documents(
                    chunks=chunks,
                    source_name=metadata['source'],
                    page_num=1
                )
                print(f"Ingested: {metadata['source']}")
            except Exception as e:
                print(f"Error ingesting {file_path}: {e}")


@app.post("/upload", responses={200: {"description": "File uploaded successfully"}})
async def upload_document(file: UploadFile = File(...)):
    try:
        upload_path = Path(DATA_PATH) / file.filename
        with open(upload_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        text, metadata, _ = load_document(str(upload_path))
        chunks = chunk_text(text)

        vector_store = get_vector_store()
        vector_store.add_documents(
            chunks=chunks,
            source_name=metadata['source'],
            page_num=1
        )

        retriever = HybridRetriever()
        retriever.refresh()

        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks),
            "total_pages": metadata.get('total_pages', 1)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        injection_flagged = flag_injection_attempt(request.question)

        retriever = HybridRetriever()
        retrieved = retriever.search(request.question, top_k=10)

        reranker = Reranker()
        reranked = reranker.rerank(request.question, retrieved, top_k=5)

        clean_passages, flagged = sanitize_passages(reranked)

        if not clean_passages and flagged:
            return QueryResponse(
                answer="Insufficient evidence in the documents to answer this question.",
                sources=[],
                context_passages=[],
                latency=0.0,
                metrics={},
                injection_flagged=True
            )

        generator = get_generator()
        result = generator.generate(clean_passages, request.question)

        metrics = log_evaluation(
            question=request.question,
            answer=result['answer'],
            retrieved_docs=reranked,
            sources=result['sources'],
            latency=result['latency'],
            injection_flagged=injection_flagged
        )

        return QueryResponse(
            answer=result['answer'],
            sources=result['sources'],
            context_passages=reranked,
            latency=result['latency'],
            metrics=metrics,
            injection_flagged=injection_flagged
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def get_documents():
    try:
        vector_store = get_vector_store()
        all_docs = vector_store.get_all_documents()

        documents = {}
        for doc, metadata in zip(all_docs['documents'], all_docs['metadatas']):
            source = metadata['source']
            if source not in documents:
                documents[source] = {
                    "source": source,
                    "chunks": 0
                }
            documents[source]['chunks'] += 1

        return {
            "documents": list(documents.values()),
            "total_documents": len(documents),
            "total_chunks": len(all_docs['documents'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluations")
async def get_evaluations():
    try:
        logs = get_eval_logs()
        return {"evaluations": logs, "total": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluations/clear")
async def clear_evaluations():
    try:
        clear_eval_logs()
        return {"status": "success", "message": "Evaluation logs cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/eval-dataset")
async def get_evaluation_dataset():
    return {"dataset": get_eval_dataset(), "total": len(get_eval_dataset())}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RAG Research Assistant API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
