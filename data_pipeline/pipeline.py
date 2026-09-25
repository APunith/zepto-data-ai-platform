import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://books.toscrape.com/"
GBP_TO_INR_RATE = 105.50
DB_PATH = os.path.join(os.path.dirname(__file__), "zepto_catalog.db")

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def scrape_books(pages_to_scrape: int = 5) -> list[dict]:
    """Scrape book details across multiple catalogue pages."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    raw_books = []

    for page in range(1, pages_to_scrape + 1):
        url = f"{BASE_URL}catalogue/page-{page}.html" if page > 1 else BASE_URL
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}: Status code {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            book_nodes = soup.find_all("article", class_="product_pod")

            for book in book_nodes:
                title = book.h3.a["title"] if book.h3 and book.h3.a and "title" in book.h3.a.attrs else "Unknown"
                
                price_text = book.find("p", class_="price_color")
                price_val = price_text.text.strip() if price_text else ""

                rating_node = book.find("p", class_="star-rating")
                rating_class = [c for c in rating_node.get("class", []) if c != "star-rating"] if rating_node else []
                rating_str = rating_class[0] if rating_class else "One"

                availability_node = book.find("p", class_="instock availability")
                availability_str = availability_node.text.strip() if availability_node else "Out of stock"

                
                category = "General"

                raw_books.append({
                    "title": title,
                    "price_text": price_val,
                    "star_rating": rating_str,
                    "availability": availability_str,
                    "category": category
                })
        except Exception as e:
            print(f"Error scraping page {page}: {e}")

    print(f"Step 1: Scraped {len(raw_books)} total items.")
    return raw_books


def clean_data(raw_records: list[dict]) -> pd.DataFrame:
    """Clean scraped fields into proper types with guard rails against empty datasets."""
    if not raw_records:
        print("Warning: No raw records scraped. Returning empty DataFrame schema.")
        return pd.DataFrame(columns=["title", "price_gbp", "rating", "in_stock", "category", "price_inr"])

    cleaned_records = []
    for item in raw_records:
        # 1. Clean Price
        price_str = item.get("price_text", "").replace("£", "").replace("Â", "").strip()
        try:
            price_gbp = float(price_str)
        except ValueError:
            price_gbp = None

        # 2. Map Rating
        rating = RATING_MAP.get(item.get("star_rating"), 1)

        # 3. Parse Availability
        in_stock = "In stock" in item.get("availability", "")

        cleaned_records.append({
            "title": item["title"],
            "price_gbp": price_gbp,
            "rating": rating,
            "in_stock": int(in_stock),
            "category": item["category"]
        })

    df = pd.DataFrame(cleaned_records)


    if "price_gbp" in df.columns and df["price_gbp"].isnull().any():
        df["price_gbp"] = df["price_gbp"].fillna(df["price_gbp"].median())


    df["price_inr"] = (df["price_gbp"] * GBP_TO_INR_RATE).round(2)

    print(f"Step 2: Cleaned {len(df)} records successfully.")
    return df


def setup_database(df: pd.DataFrame, db_path: str = DB_PATH):
    """Setup relational SQLite schema with PK/FK constraint and populate data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price_gbp REAL NOT NULL,
        price_inr REAL NOT NULL,
        rating INTEGER NOT NULL,
        in_stock INTEGER NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );
    """)


    categories = df["category"].unique()
    for cat in categories:
        cursor.execute("INSERT OR IGNORE INTO categories (category_name) VALUES (?)", (cat,))
    conn.commit()


    cursor.execute("SELECT category_name, category_id FROM categories;")
    cat_map = dict(cursor.fetchall())


    for _, row in df.iterrows():
        cat_id = cat_map.get(row["category"])
        cursor.execute("""
        INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (row["title"], row["price_gbp"], row["price_inr"], row["rating"], row["in_stock"], cat_id))

    conn.commit()
    print("Step 3: Database schema initialized and populated.")
    return conn


def execute_queries_and_verify(conn: sqlite3.Connection):
    """Execute required SQL queries and verify against pandas operations."""
    print("\n--- Step 4: SQL Queries Execution ---")


    q1 = """
    SELECT b.title, b.price_gbp, b.price_inr, b.rating, c.category_name
    FROM books b
    JOIN categories c ON b.category_id = c.category_id
    WHERE b.rating >= 4
    ORDER BY b.price_gbp DESC
    LIMIT 5;
    """
    df_sql_join = pd.read_sql(q1, conn)
    print("SQL Join Query Result (Top 5 Rated >= 4):")
    print(df_sql_join)


    q2 = "SELECT title, price_inr FROM books WHERE price_inr BETWEEN 1000 AND 3000 LIMIT 5;"
    print("\nBooks priced between 1000 and 3000 INR:")
    print(pd.read_sql(q2, conn))


    q3 = "SELECT DISTINCT rating FROM books ORDER BY rating ASC;"
    print("\nDistinct Star Ratings:")
    print(pd.read_sql(q3, conn))


    df_books = pd.read_sql("SELECT * FROM books", conn)
    df_cats = pd.read_sql("SELECT * FROM categories", conn)

    df_pd_join = pd.merge(df_books, df_cats, on="category_id")
    df_pd_filtered = (
        df_pd_join[df_pd_join["rating"] >= 4]
        .sort_values(by="price_gbp", ascending=False)
        [["title", "price_gbp", "price_inr", "rating", "category_name"]]
        .head(5)
        .reset_index(drop=True)
    )

    print("\n--- Pandas pd.merge Equivalence Check ---")
    print(df_pd_filtered)


def run_pipeline():
    """Run full Module 1 end-to-end data engineering pipeline."""
    raw_data = scrape_books(pages_to_scrape=5)
    df_clean = clean_data(raw_data)

    if not df_clean.empty:
        conn = setup_database(df_clean)
        execute_queries_and_verify(conn)
        conn.close()
    else:
        print("Pipeline aborted due to empty dataset.")


if __name__ == "__main__":
    run_pipeline()