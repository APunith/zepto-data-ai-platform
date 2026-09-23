# Module 3 — Support Assistant RAG Service (`/rag_assistant`)

## 1. Overview
This module implements a Retrieval-Augmented Generation (RAG) backend service for customer support inquiries. It chunks product FAQs, computes vector embeddings using local SentenceTransformers (`all-MiniLM-L6-v2`), indexes them into an in-memory Qdrant vector collection, and generates context-grounded responses.

---

## 2. Setup & Execution

### Install Dependencies
```bash
pip install -r rag_assistant/requirements.txt
```
## 3. Endpoints
* POST /ingest: Reads rag_assistant/data/faqs.json and indexes 384-dimensional vector embeddings into Qdrant.

* POST /chat: Receives user support queries, performs cosine similarity vector search, and generates grounded context responses.