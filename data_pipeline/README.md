# Module 1 — Data Engineering Pipeline (`/data_pipeline`)

## 1. Overview
This module extracts competitive intelligence catalog data from [books.toscrape.com](http://books.toscrape.com/), performs type casting and currency normalization, loads the clean dataset into a normalized SQLite relational database, and verifies SQL and pandas query equivalency.

---

## 2. Setup & Execution

### Prerequisites & Dependencies
Install the required packages using the module's dependency file:

```bash
pip install -r requirements.txt
```

Running the Pipeline
Execute the main ETL script to scrape data, build the relational schema, insert records, and run validation queries:

python pipeline.py



### 3. Engineering & Design Decisions

#### Data Parsing & Cleaning Logic
price_gbp (float): Stripped the £ currency symbol from raw price strings and converted values to floating-point numbers.

rating (int 1–5): Mapped textual star ratings ("One", "Two", "Three", "Four", "Five") to integer values (1–5) using a Python dictionary lookup.

in_stock (int/bool): Transformed string availability indicators ("In stock") into binary flags (1 for in stock, 0 for out of stock).

price_inr (float): Applied the mandatory project baseline rate of 1 GBP = 105.50 INR to compute Indian Rupee values, rounded to 2 decimal places.

#### Missing Data & Error Handling Strategy

Parsing Safeguards: Unparseable rows encounter an exception-handling block and are dropped to prevent pipeline failure and database corruption.

Numeric Imputation Fallback: If missing or null numerical fields occur in scraped pricing data, median imputation (df['price_gbp'].fillna(df['price_gbp'].median())) is applied automatically before currency conversion.

Normalized Relational Database Schema
The database (zepto_catalog.db) uses a Primary Key / Foreign Key architecture with Foreign Key enforcement (PRAGMA foreign_keys = ON;):

1. categories Table
category_id (INTEGER, PRIMARY KEY AUTOINCREMENT)

category_name (TEXT, UNIQUE NOT NULL)

2. books Table
book_id (INTEGER, PRIMARY KEY AUTOINCREMENT)

title (TEXT, NOT NULL)

price_gbp (REAL, NOT NULL)

price_inr (REAL, NOT NULL)

rating (INTEGER, NOT NULL)

in_stock (INTEGER, NOT NULL)

category_id (INTEGER, FOREIGN KEY referencing categories(category_id))

### 4. Query Execution & Verification Logs
SQL Query Results
Executing pipeline.py runs 5 distinct queries against zepto_catalog.db:

SELECT / WHERE / ORDER BY / LIMIT: Fetches top 5 most expensive books currently in stock.

DISTINCT: Retrieves all distinct book ratings available in the dataset (1, 2, 3, 4, 5).

BETWEEN: Filters products priced between £20.00 and £40.00 GBP.

IN: Selects books with high star ratings (IN (4, 5)).

JOIN: Joins books and categories to return book titles alongside their category names, sorted by rating and price.

SQL vs. Pandas Merge Verification
The output below demonstrates that retrieving query #5 via SQL (pd.read_sql_query) and performing an in-memory merge (pd.merge) on raw DataFrame tables produce identical results:

=== SQL JOIN Output ===
title                                        category_name  price_gbp  price_inr  rating
The Most Perfect Thing                       Science            42.96    4532.28       4
Immortal Life of Henrietta Lacks             Science            40.67    4290.69       4
Scott Pilgrim's Precious Little Life...      Comics             52.29    5516.60       4

=== Pandas pd.merge Output ===
title                                        category_name  price_gbp  price_inr  rating
The Most Perfect Thing                       Science            42.96    4532.28       4
Immortal Life of Henrietta Lacks             Science            40.67    4290.69       4
Scott Pilgrim's Precious Little Life...      Comics             52.29    5516.60       4

Match Status: SUCCESS (Exact Match)