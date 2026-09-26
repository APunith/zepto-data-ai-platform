# Module 1 — Data Engineering Pipeline (/data_pipeline)

## 1. Overview
This module extracts book catalog data from `books.toscrape.com`, cleans and transforms raw text attributes, converts currency from GBP to INR using a fixed exchange rate (1 GBP = 105.50 INR), builds an normalized SQLite relational database schema, and validates analytical query logic using both SQL clauses and equivalent `pandas` dataframe operations.

---

## 2. Key Features & Implementation Details

* **Robust Web Scraping**:
  * Utilizes `requests` with standard browser `User-Agent` headers to bypass request filtering.
  * Paginates through multiple catalog pages to ingest 100 items (surpassing the minimum requirement of 60 records).
  * Implements defensive error handling and fallbacks for missing price, rating, or stock status fields.

* **Data Cleaning & Transformation**:
  * Strips currency symbols and non-ASCII artifacts from raw price strings.
  * Maps text ratings (`One`, `Two`, `Three`, `Four`, `Five`) to numerical integer values (`1–5`).
  * Converts stock status strings into binary flags (`1` for In stock, `0` for Out of stock).
  * Computes `price_inr` using the fixed exchange rate: `price_inr = round(price_gbp * 105.50, 2)`.

* **Relational SQLite Schema**:
  * Enforces foreign key constraints (`PRAGMA foreign_keys = ON;`).
  * Constructs normalized tables:
    * `categories` (`category_id` PRIMARY KEY, `category_name` UNIQUE)
    * `books` (`book_id` PRIMARY KEY, `category_id` FOREIGN KEY, `title`, `price_gbp`, `price_inr`, `rating`, `in_stock`)

* **Query Execution & Equivalence Verification**:
  * Runs complex SQL queries using `JOIN`, `WHERE`, `ORDER BY`, `LIMIT`, `BETWEEN`, and `DISTINCT`.
  * Replicates relational join logic in Python using `pd.merge()` on in-memory DataFrames to verify data consistency across both querying paradigms.

---

## 3. Setup & Execution

**Run the Pipeline**
```bash
python data_pipeline/pipeline.py
```