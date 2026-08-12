"""Type coercion from raw scraped text fields into typed columns."""

import re

import pandas as pd

from data_pipeline.config import GBP_TO_INR

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_price(price_text):
    """Return a float GBP amount, or None if no number could be found."""
    match = re.search(r"\d+\.?\d*", price_text)
    if match is None:
        return None
    return float(match.group())


def parse_rating(rating_word):
    """Return an int 1-5, or None if the word isn't one we recognize."""
    return RATING_WORDS.get(rating_word)


def parse_availability(availability_text):
    """Return True if the text indicates the book is in stock."""
    return "in stock" in availability_text.lower()


def clean_books(raw_books):
    """
    Convert a list of raw scraped book dicts into a typed DataFrame with
    columns: title, price_gbp, price_inr, rating, in_stock, category.

    Rows whose price or rating text cannot be parsed are dropped rather
    than imputed -- see cleaning.py's module docstring / README for why.
    """
    rows = []
    for book in raw_books:
        price_gbp = parse_price(book["price_text"])
        rating = parse_rating(book["rating_word"])

        if price_gbp is None or rating is None:
            continue

        rows.append({
            "title": book["title"],
            "price_gbp": price_gbp,
            "price_inr": round(price_gbp * GBP_TO_INR, 2),
            "rating": rating,
            "in_stock": parse_availability(book["availability_text"]),
            "category": book["category"],
        })

    df = pd.DataFrame(rows)
    df["rating"] = df["rating"].astype(int)
    df["in_stock"] = df["in_stock"].astype(bool)
    return df


if __name__ == "__main__":
    from data_pipeline.scraper import scrape_all_categories

    raw_books = scrape_all_categories()
    df = clean_books(raw_books)

    print(f"Cleaned rows: {len(df)} (from {len(raw_books)} scraped)")
    print(df.dtypes)
    print(df.head())
