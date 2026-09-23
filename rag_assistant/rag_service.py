import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Zepto Support Assistant RAG Service (Local Mode)", version="1.0.0")

# 1. Free Local Embedding Model (Downloads automatically on first run ~90MB)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Local In-Memory Vector Store (No Docker or cloud needed)
qdrant = QdrantClient(":memory:")
COLLECTION_NAME = "zepto_support_docs"

def init_vector_db():
    collections = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in collections:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE) # MiniLM embedding size = 384
        )

init_vector_db()

# Pydantic Schemas
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    retrieved_sources: List[str]

# Utility: Local Embedding Function
def get_embedding(text: str) -> List[float]:
    return embedding_model.encode(text).tolist()

# 1. Ingest Endpoint (Local)
@app.post("/ingest")
def ingest_knowledge_base(file_path: Optional[str] = None):
    if not file_path:
        path1 = "rag_assistant/data/faqs.json"
        path2 = "data/faqs.json"
        file_path = path1 if os.path.exists(path1) else path2

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Data file not found at {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
        
    points = []
    for idx, doc in enumerate(documents):
        combined_text = f"Title: {doc['title']}\nCategory: {doc['category']}\nContent: {doc['content']}"
        vector = get_embedding(combined_text)
        
        points.append(
            PointStruct(
                id=idx + 1,
                vector=vector,
                payload={
                    "doc_id": doc["doc_id"],
                    "category": doc["category"],
                    "title": doc["title"],
                    "text": combined_text
                }
            )
        )
        
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "success", "total_indexed": len(points)}

# 2. Chat Endpoint (Local Grounded Retrieval)
@app.post("/chat", response_model=QueryResponse)
def support_chat(req: QueryRequest):
    """Query support assistant with RAG context grounding."""
    try:
        # 1. Generate query embedding
        query_vector = get_embedding(req.query)

        # 2. Vector Search (using query_points for latest qdrant-client)
        try:
            search_response = qdrant.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=req.top_k,
                score_threshold=0.3
            )
            search_results = search_response.points
        except Exception:
            # Fallback for older qdrant-client versions
            search_results = qdrant.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=req.top_k,
                score_threshold=0.3
            )

        if not search_results:
            return QueryResponse(
                answer="I'm sorry, but I don't have enough information in my knowledge base to answer that.",
                retrieved_sources=[]
            )

        # 3. Aggregate Context
        context_snippets = [hit.payload["text"] for hit in search_results]
        sources = list(set([hit.payload["doc_id"] for hit in search_results]))

        formatted_context = "\n\n".join(context_snippets)
        answer = f"Based on our support documentation:\n\n{formatted_context}"

        return QueryResponse(answer=answer, retrieved_sources=sources)

    except Exception as e:
        # Prevent generic 500 error and print clear error message
        raise HTTPException(status_code=500, detail=f"Chat execution error: {str(e)}")