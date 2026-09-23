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

### Running the Pipeline
Execute the main ETL script to scrape data, build the relational schema, insert records, and run validation queries:

python pipeline.py



## 3. Engineering & Design Decisions

 ###  1. Data Cleaning & Parsing

 * Price Parsing: Stripped non-numeric currency characters (£) and cast values to float (price_gbp).
 * Star Ratings: Mapped text representations ("One" through "Five") to integer values (1 to 5) using a dictionary mapping.
 * Availability: Processed string flags ("In stock") into boolean integer values (1 for in stock, 0 for out of stock).

 ### 2. Missing Value & Exception Handling Strategy

 * Numeric Fields: Applied median imputation fallback if numeric parsing fails or null values occur.
 * Corrupted/Unparseable Rows: Dropped unparseable rows during iteration to preserve database integrity and prevent execution crashes.

 ### 3. Baseline Currency Conversion Rate

 * Fixed Rate: Computed price_inr = price_gbp * 105.50 using the project's required fixed baseline constant (1 GBP = 105.50 INR).
 
 ### 4. Normalized SQLite Schema (2-Table PK/FK)

 The database (zepto_catalog.db) uses a normalized relational model with Foreign Key enforcement (PRAGMA foreign_keys = ON;):

 * categories: category_id (PRIMARY KEY), category_name (TEXT UNIQUE)
 * books: book_id (PRIMARY KEY), title (TEXT), price_gbp (REAL), price_inr (REAL), rating (INTEGER), in_stock (INTEGER), category_id (FOREIGN KEY  referencing categories(category_id))

## 4. Verification & Output Log

Executing python pipeline.py outputs:

 * 100 total items scraped across 5 paginated pages.
 * Cleaned and stored into zepto_catalog.db.
 * Side-by-side verification confirms that the SQL JOIN query and the in-memory pandas pd.merge() produce identical output datasets.