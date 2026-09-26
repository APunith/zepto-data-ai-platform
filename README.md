# Zepto Data & AI Platform

Welcome to the **Zepto Data & AI Platform** repository. This unified platform integrates three core modules designed to support Zepto's data engineering, predictive analytics, and automated AI support workflows:

1. **Module 1 — Data Engineering Pipeline (`/data_pipeline`)**: Scrapes live product catalog data, performs data cleaning and currency conversion, and populates a normalized SQLite relational database verified via SQL and `pandas`.
2. **Module 2 — Analytics Pipeline (`/analytics`)**: Profiles passenger/customer dataset distributions, applies missingness handling rules, evaluates multiple classification models, tunes hyperparameter space via Out-of-Bag (OOB) scoring, and exports a production-ready `joblib` pipeline.
3. **Module 3 — Support Assistant RAG Service (`/support_assistant`)**: Implements an embedded ChromaDB vector store, a LangGraph state router with a deterministic `MOCK_LLM` toggle, and a Pydantic-validated FastAPI service (`POST /ask`) containerized via Docker.

---

### 1. Directory Structure

```text
zepto-data-ai-platform/
├── data_pipeline/
│   ├── pipeline.py
│   ├── zepto_catalog.db
│   ├── requirements.txt
│   └── README.md
├── analytics/
│   ├── analytics_pipeline.py
│   ├── titanic.csv
│   ├── models/
│   │   └── best_pipeline.joblib
│   ├── visualizations/
│   │   └── correlation_heatmap.png
│   ├── requirements.txt
│   └── README.md
├── support_assistant/
│   ├── rag_service.py
│   ├── docs/
│   │   ├── doc_01.txt ... doc_08.txt
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── .gitignore
└── README.md
```
### 2. Environment Setup & Installation
You can set up a unified virtual environment or install dependencies per module as needed:

#### Virtual Environment Creation

```bash
python -m venv .venv
```
#### Install Module Dependencies
```bash
pip install -r data_pipeline/requirements.txt
pip install -r analytics/requirements.txt
pip install -r support_assistant/requirements.txt
```
### 3. Execution Commands
#### Module 1 — Data Pipeline (/data_pipeline)
Run the web scraper, data cleaning, relational SQLite loading, and query verification pipeline:
```bash
python data_pipeline/pipeline.py
```
#### Module 2 — Analytics Pipeline (/analytics)
Run the EDA profiling, model comparison, SMOTE evaluation, hyperparameter tuning, and model artifact export script:
```bash
python analytics/analytics_pipeline.py
```
#### Module 3 — Support Assistant (/support_assistant)
Launch the FastAPI uvicorn server locally on port 7860:
```bash
python -m uvicorn support_assistant.rag_service:app --host 0.0.0.0 --port 7860 --reload
```
* Interactive Swagger UI: Navigate to http://localhost:7860/docs to test POST /ask
#### Docker Deployment
Build and run the containerized FastAPI service:
```bash
docker build -t zepto-support-assistant support_assistant/
docker run -p 7860:7860 zepto-support-assistant
```
### 4. Module Architecture & Design Decisions
#### Module 1 — Data Pipeline
* Scraping Strategy: Applied standard browser HTTP user-agent headers to prevent request filtering while scraping books.toscrape.com. Paginates across catalog pages to extract 100 records (exceeding the 60-item requirement).

* Currency Standardization: Converted price_gbp to price_inr using the fixed exchange rate constant: 1 GBP = 105.50 INR.

* Relational Database Schema: Enforces primary key and foreign key constraints (PRAGMA foreign_keys = ON;) linking categories (category_id) to books (category_id).

* Query Verification: Confirmed query result parity between SQLite JOIN queries and native pandas.merge() DataFrame operations.

#### Module 2 — Analytics Pipeline
* **Missing Value Threshold Rule:**
 * deck (77.22% missing): Exceeded 30% threshold $\rightarrow$ Dropped column.
 * age (19.87% missing): Between 5%–30% threshold $\rightarrow$ Imputed with median.
 * embarked (< 1% missing): Under 5% threshold $\rightarrow$ Removed missing rows.
* **Classification Results (Stratified Split):**
 | Model | Accuracy | Precision | Recall | F1 Score | AUC |
 | :--- | :--- | :--- | :--- | :--- | :--- |
 | **Logistic Regression** | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
 | **Decision Tree** | 0.8090 | 0.8148 | 0.6471 | 0.7213 | 0.8560 |
 | **Random Forest** | **0.8202** | **0.7812** | **0.7353** | **0.7576** | **0.8179** |
**Imbalance & Tuning:** Evaluated SMOTE oversampling on training split only (0.7176 F1 Score). Tuned Random Forest hyperparameters using GridSearchCV with oob_score=True, achieving an Out-of-Bag score of 0.8172.
**Fare Regression Task:** Multivariate Linear Regression achieved an MAE of 21.14, RMSE of 41.75, and $R^2$ of 0.3468.
**Artifact Export:** Exported the complete fitted preprocessor and classifier pipeline to analytics/models/best_pipeline.joblib.
#### Module 3 — Support Assistant RAG Pipeline
* **Document Ingestion:** Ingested 8 official policy documents (doc_01.txt to doc_08.txt). Generated 384-dimensional embeddings using sentence-transformers/all-MiniLM-L6-v2 and indexed them into ChromaDB.

* **LangGraph Orchestration:** Built a StateGraph routing queries via intent classification (classify_intent) to either policy retrieval (retrieve_and_answer) or conversational response (direct_answer).

* **Deterministic Engine:** Features a MOCK_LLM toggle (default 1) to support deterministic, offline evaluation without external API keys.

* **Schema Validation:** Enforces structured Pydantic response models containing answer, sources, and confidence.
### 5. Repository Verification
All features, bug fixes, and documentation updates have been committed and merged into the main branch.
* **Repository URL:** https://github.com/APunith/zepto-data-ai-platform