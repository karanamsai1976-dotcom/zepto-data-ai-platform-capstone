"""End-to-end pipeline: scrape -> clean -> load into SQLite. Run with:
python -m data_pipeline.run_pipeline
"""

from data_pipeline.cleaning import clean_books
from data_pipeline.database import create_schema, get_connection, load_books
from data_pipeline.scraper import scrape_all_categories


def run():
    print("Scraping books.toscrape.com ...")
    raw_books = scrape_all_categories()
    print(f"Scraped {len(raw_books)} raw rows")

    df = clean_books(raw_books)
    print(f"Cleaned to {len(df)} rows")

    conn = get_connection()
    try:
        create_schema(conn)
        load_books(conn, df)

        row_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        fk_info = conn.execute("PRAGMA foreign_key_list(books)").fetchall()

        print(f"Loaded {row_count} books across {category_count} categories")
        print(f"Foreign key info: {fk_info}")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
