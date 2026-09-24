import os
import glob
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Zepto Support Assistant Service", version="1.0.0")

MOCK_LLM = os.getenv("MOCK_LLM", "1") == "1"
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
corpus_docs = []

def load_corpus():
    global corpus_docs
    corpus_docs = []
    doc_files = glob.glob(os.path.join(DOCS_DIR, "*.txt"))
    for file_path in sorted(doc_files):
        filename = os.path.basename(file_path)
        doc_id = os.path.splitext(filename)[0]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            corpus_docs.append({"doc_id": doc_id, "content": content})

load_corpus()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float

def classify_intent_heuristic(query: str) -> str:
    keywords = ["delivery", "return", "refund", "membership", "tracking", "cancel", "gift card", "support hours"]
    query_lower = query.lower()
    for kw in keywords:
        if kw in query_lower:
            return "policy_question"
    return "general_question"

@app.post("/ask", response_model=QueryResponse)
def ask_support(req: QueryRequest):
    """Query support assistant with RAG context grounding."""
    intent = classify_intent_heuristic(req.query)

    if intent == "general_question":
        return QueryResponse(
            answer="I can only answer questions about Zepto policies right now.",
            sources=[],
            confidence=1.0
        )

    if not corpus_docs:
        load_corpus()

    best_doc = None
    max_matches = -1
    query_words = set(req.query.lower().split())

    for doc in corpus_docs:
        content_words = set(doc["content"].lower().split())
        overlap = len(query_words.intersection(content_words))
        if overlap > max_matches:
            max_matches = overlap
            best_doc = doc

    if not best_doc:
        best_doc = corpus_docs[0]

    snippet = best_doc["content"][:200]
    answer = f"Based on the retrieved context: {snippet}..."

    return QueryResponse(
        answer=answer,
        sources=[best_doc["doc_id"]],
        confidence=1.0
    )