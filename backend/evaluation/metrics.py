import sqlite3
import json
from datetime import datetime
from rouge_score import rouge_scorer
from backend.config import EVAL_LOG_DB


def init_eval_db():
    conn = sqlite3.connect(EVAL_LOG_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            question TEXT,
            answer TEXT,
            retrieved_docs TEXT,
            sources TEXT,
            hit_rate REAL,
            citation_correctness REAL,
            groundedness REAL,
            refusal_accuracy INTEGER,
            latency REAL,
            injection_flagged INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def calculate_hit_rate(retrieved_docs, expected_source):
    if not retrieved_docs or not expected_source:
        return 0.0

    hit = any(expected_source.lower() in doc['metadata']['source'].lower()
              for doc in retrieved_docs)
    return 1.0 if hit else 0.0


def calculate_citation_correctness(answer, sources):
    if not sources:
        return 0.0

    citation_count = 0
    for source in sources:
        if source.lower() in answer.lower():
            citation_count += 1

    return (citation_count / len(sources)) if sources else 0.0


def calculate_groundedness(answer, context_passages):
    if not context_passages or not answer:
        return 0.0

    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)

    context_text = " ".join([p['text'] for p in context_passages])

    scores = scorer.score(context_text, answer)
    return scores['rouge1'].fmeasure


def check_refusal_accuracy(answer, expected_type):
    if expected_type == "unanswerable":
        refusal_keywords = [
            "insufficient evidence",
            "not found",
            "cannot answer",
            "not covered",
            "not available"
        ]
        return 1 if any(keyword.lower() in answer.lower() for keyword in refusal_keywords) else 0
    return 1


def log_evaluation(question, answer, retrieved_docs, sources, latency, expected_type=None, injection_flagged=False):
    init_eval_db()

    hit_rate = calculate_hit_rate(retrieved_docs, sources[0] if sources else None)
    citation_correctness = calculate_citation_correctness(answer, sources)
    groundedness = calculate_groundedness(answer, retrieved_docs)
    refusal_accuracy = check_refusal_accuracy(answer, expected_type) if expected_type else 1

    conn = sqlite3.connect(EVAL_LOG_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO evaluations
        (question, answer, retrieved_docs, sources, hit_rate, citation_correctness,
         groundedness, refusal_accuracy, latency, injection_flagged)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        question,
        answer,
        json.dumps([{k: v for k, v in doc.items() if k != 'text'} for doc in retrieved_docs]),
        json.dumps(sources),
        hit_rate,
        citation_correctness,
        groundedness,
        refusal_accuracy,
        latency,
        1 if injection_flagged else 0
    ))
    conn.commit()
    conn.close()

    return {
        "hit_rate": hit_rate,
        "citation_correctness": citation_correctness,
        "groundedness": groundedness,
        "refusal_accuracy": refusal_accuracy,
        "injection_flagged": injection_flagged
    }


def get_eval_logs():
    init_eval_db()
    conn = sqlite3.connect(EVAL_LOG_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM evaluations ORDER BY timestamp DESC')
    logs = cursor.fetchall()
    conn.close()

    results = []
    for log in logs:
        results.append({
            "id": log[0],
            "timestamp": log[1],
            "question": log[2],
            "answer": log[3],
            "hit_rate": log[5],
            "citation_correctness": log[6],
            "groundedness": log[7],
            "refusal_accuracy": log[8],
            "latency": log[9],
            "injection_flagged": log[10]
        })

    return results


def clear_eval_logs():
    init_eval_db()
    conn = sqlite3.connect(EVAL_LOG_DB)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM evaluations')
    conn.commit()
    conn.close()
