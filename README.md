# Zepto Data & AI Platform

An end-to-end data engineering, analytics, and AI service platform featuring web scraping pipelines, machine learning models, and a local Retrieval-Augmented Generation (RAG) support assistant.

---

##  Repository Structure

```text
zepto-data-ai-platform/
├── .gitignore
├── README.md
├── requirements.txt
├── analytics/
│   ├── models/
│   ├── visualizations/
│   ├── analytics_pipeline.py
│   ├── README.md
│   └── requirements.txt
├── data_pipeline/
│   ├── pipeline.py
│   ├── zepto_catalog.db
│   ├── README.md
│   └── requirements.txt
└── support_assistant/
    ├── docs/
    │   ├── doc_01.txt
    │   ├── doc_02.txt
    │   ├── doc_03.txt
    │   ├── doc_04.txt
    │   ├── doc_05.txt
    │   ├── doc_06.txt
    │   ├── doc_07.txt
    │   └── doc_08.txt
    ├── Dockerfile
    ├── rag_service.py
    ├── README.md
    └── requirements.txt
```
## Setup & Execution Guide
### 1. Install Dependencies
Install all project requirements using the consolidated root requirements file:
```bash
pip install -r requirements.txt
```
## Module Execution Steps
### Module 1 — Data Pipeline (/data_pipeline)
Run the web scraper and database ingestion pipeline:
```bash
python data_pipeline/pipeline.py
```
### Module 2 — Analytics Pipeline (/analytics)
Run the data profiling, feature engineering, and model training pipeline:
```bash
python analytics/analytics_pipeline.py
```
### Module 3 — Support Assistant (/support_assistant)
Start the FastAPI server locally:
```bash
python -m uvicorn support_assistant.rag_service:app --reload --port 7860
```
Open http://127.0.0.1:7860/docs in your browser to test the POST /ask endpoint.

## Docker Deployment (Support Assistant)
Build and run the Support Assistant container locally:
```bash
# Build Docker image
docker build -t zepto-support-assistant support_assistant/

# Run container
docker run -p 7860:7860 zepto-support-assistant
```
