## Module 3 — Support Assistant RAG Service (/support_assistant)

### 1. Overview
This module implements a Retrieval-Augmented Generation (RAG) backend service for Zepto customer support inquiries. It loads and chunks 8 core policy documents (`doc_01.txt` to `doc_08.txt`), computes 384-dimensional vector embeddings using local SentenceTransformers (`all-MiniLM-L6-v2`), indexes them into ChromaDB, and generates context-grounded responses using a LangGraph state graph with a deterministic `MOCK_LLM` toggle.

### 2. Setup & Execution

**Install Dependencies**
```bash
pip install -r support_assistant/requirements.txt
```
**Run Service via Uvicorn**
```bash
python -m uvicorn support_assistant.rag_service:app --host 0.0.0.0 --port 7860 --reload
```
### 3. Endpoints
* **POST /ask:** Accepts a JSON body {"query": "<your question>"}.
* **Routes queries through a LangGraph** StateGraph **(** classify_intent -> retrieve_and_answer **or** direct_answer **).**
* **Returns a structured JSON response enforcing schema validation with** answer **(string),** sources **(list of document IDs), and** confidence **(float).**