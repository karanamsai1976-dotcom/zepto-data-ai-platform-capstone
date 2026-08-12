"""SQLite schema and data loading for the data_pipeline module."""

import sqlite3

from data_pipeline.config import DB_PATH

CREATE_CATEGORIES_TABLE = """
CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL
);
"""

CREATE_BOOKS_TABLE = """
CREATE TABLE books (
    book_id     INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    price_gbp   REAL,
    price_inr   REAL,
    rating      INTEGER,
    in_stock    INTEGER,
    category_id INTEGER REFERENCES categories(category_id)
);
"""


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_schema(conn):
    """
    Drop and recreate both tables so every pipeline run starts from a
    clean slate -- this is what makes the loader idempotent: re-running
    it never duplicates rows, because nothing is ever appended to
    existing data.
    """
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute("DROP TABLE IF EXISTS categories")
    cursor.execute(CREATE_CATEGORIES_TABLE)
    cursor.execute(CREATE_BOOKS_TABLE)
    conn.commit()


def load_books(conn, df):
    """Insert a cleaned books DataFrame into the categories/books tables."""
    cursor = conn.cursor()

    category_ids = {}
    for category_name in sorted(df["category"].unique()):
        cursor.execute(
            "INSERT INTO categories (category_name) VALUES (?)",
            (category_name,),
        )
        category_ids[category_name] = cursor.lastrowid

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                row["price_gbp"],
                row["price_inr"],
                row["rating"],
                int(row["in_stock"]),
                category_ids[row["category"]],
            ),
        )

    conn.commit()
