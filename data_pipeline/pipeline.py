import sqlite3
from typing import Dict, List
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/"
GBP_TO_INR_RATE = 105.50
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def scrape_books(max_pages: int = 5) -> List[Dict]:
    """Scrape product details across paginated listing pages."""
    scraped_data = []

    for page in range(1, max_pages + 1):
        url = (
            f"{BASE_URL}catalogue/page-{page}.html"
            if page > 1
            else f"{BASE_URL}index.html"
            )
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("article", class_="product_pod")

        for article in articles:
            title = article.h3.a["title"]
            price_text = article.find("p", class_="price_color").text
            rating_text = article.p["class"][1]
            availability_text = article.find(
                "p", class_="instock availability").text.strip()

            detail_rel_path = article.h3.a["href"].replace("catalogue/", "")
            detail_url = f"{BASE_URL}catalogue/{detail_rel_path}"
            cat_response = requests.get(detail_url, timeout=10)

            category = "Unknown"
            if cat_response.status_code == 200:
                cat_soup = BeautifulSoup(cat_response.content, "html.parser")
                breadcrumb = cat_soup.find("ul", class_="breadcrumb")
                if breadcrumb:
                    category = breadcrumb.find_all("li")[2].text.strip()

            scraped_data.append
            (
                {
                    "title": title,
                    "price_raw": price_text,
                    "rating_raw": rating_text,
                    "availability_raw": availability_text,
                    "category": category,
                }
            )

    return scraped_data


def clean_data(raw_records: List[Dict]) -> pd.DataFrame:
    """Clean scraped fields into typed columns and compute INR price."""
    cleaned_records = []

    for item in raw_records:
        try:
            price_gbp = float
            (
                "".join(c for c in item["price_raw"] if c.isdigit() or c == ".")
            )
            rating = RATING_MAP.get(item["rating_raw"], 0)
            in_stock = 1 if "In stock" in item["availability_raw"] else 0
            price_inr = round(price_gbp * GBP_TO_INR_RATE, 2)

            cleaned_records.append
            (
                {
                    "title": item["title"],
                    "price_gbp": price_gbp,
                    "price_inr": price_inr,
                    "rating": rating,
                    "in_stock": in_stock,
                    "category_name": item["category"],
                }
            )
        except (ValueError, KeyError):
            continue

    df = pd.DataFrame(cleaned_records)

    if df["price_gbp"].isnull().any():
        df["price_gbp"] = df["price_gbp"].fillna(df["price_gbp"].median())
        df["price_inr"] = df["price_gbp"] * GBP_TO_INR_RATE

    return df


def setup_database(db_path: str = "zepto_catalog.db"):
    """Initialize SQLite relational schema with PK/FK constraints."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute
    ("""
        CREATE TABLE IF NOT EXISTS categories 
        (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute
    ("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER REFERENCES categories(category_id)
        );
    """)

    conn.commit()
    conn.close()


def load_data_to_db(df: pd.DataFrame, db_path: str = "zepto_catalog.db"):
    """Populate normalized relational tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for cat in df["category_name"].unique():
        cursor.execute
        (
            "INSERT OR IGNORE INTO categories (category_name) VALUES (?);",
            (cat,),
        )
    conn.commit()

    cat_df = pd.read_sql_query
    (
        "SELECT category_id, category_name FROM categories;", conn
    )
    df_merged = df.merge(cat_df, on="category_name")

    for _, row in df_merged.iterrows():
        cursor.execute
        (
            """
            INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?);
        """,
            (
                row["title"],
                row["price_gbp"],
                row["price_inr"],
                row["rating"],
                row["in_stock"],
                row["category_id"],
            ),
        )

    conn.commit()
    conn.close()


def run_pipeline():
    print("Step 1: Scraping product data...")
    raw_data = scrape_books(max_pages=5)
    print(f"Scraped {len(raw_data)} total items.")

    print("Step 2: Cleaning data and converting currency...")
    df_clean = clean_data(raw_data)
    print(f"Cleaned {len(df_clean)} valid rows.")

    print("Step 3: Setting up SQLite schema...")
    setup_database("data_pipeline/zepto_catalog.db")

    print("Step 4: Inserting data into SQLite...")
    load_data_to_db(df_clean, "data_pipeline/zepto_catalog.db")
    print("Successfully created and populated zepto_catalog.db!")


if __name__ == "__main__":
    run_pipeline()