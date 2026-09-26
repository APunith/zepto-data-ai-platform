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
## 4. Verified Pipeline Execution Output

```text
Step 1: Scraped 100 total items.
Step 2: Cleaned 100 records successfully.
Step 3: Database schema initialized and populated.
```

### Step 4: SQL Queries Execution
**SQL Join Query Result (Top 5 Rated >= 4):**
```text
                                          title  price_gbp  price_inr  rating category_name
0  The Death of Humanity: and the Case for Life      58.11    6130.60       4    Philosophy
1  The Death of Humanity: and the Case for Life      58.11    6130.60       4       General
2                           The Past Never Ends      56.50    5960.75       4       Mystery
3                           The Past Never Ends      56.50    5960.75       4       General
4         Sapiens: A Brief History of Humankind      54.23    5721.26       5       History
```

**Pandas `pd.merge()` Equivalence Check:**
```text
                                          title  price_gbp  price_inr  rating category_name
0  The Death of Humanity: and the Case for Life      58.11    6130.60       4       General
1  The Death of Humanity: and the Case for Life      58.11    6130.60       4    Philosophy
2                           The Past Never Ends      56.50    5960.75       4       Mystery
3                           The Past Never Ends      56.50    5960.75       4       General
4         Sapiens: A Brief History of Humankind      54.23    5721.26       5       History
```