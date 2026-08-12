"""Offline tests for scraper parsing and cleaning, using a saved HTML fixture."""

from pathlib import Path

from bs4 import BeautifulSoup

from data_pipeline.scraper import parse_book, get_category_name
from data_pipeline.cleaning import parse_price, parse_rating, parse_availability, clean_books

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mystery_category_page.html"


def load_fixture_soup():
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    return BeautifulSoup(html, "lxml")


def test_get_category_name():
    soup = load_fixture_soup()
    assert get_category_name(soup) == "Mystery"


def test_fixture_has_expected_article_count():
    soup = load_fixture_soup()
    articles = soup.select("article.product_pod")
    assert len(articles) == 20


def test_parse_book_extracts_raw_fields():
    soup = load_fixture_soup()
    articles = soup.select("article.product_pod")
    book = parse_book(articles[0], "Mystery")

    assert book["title"] == "Sharp Objects"
    assert book["price_text"] == "£47.82"
    assert book["rating_word"] == "Four"
    assert book["availability_text"] == "In stock"
    assert book["category"] == "Mystery"


def test_parse_price():
    assert parse_price("£47.82") == 47.82
    assert parse_price("not a price") is None


def test_parse_rating():
    assert parse_rating("Four") == 4
    assert parse_rating("One") == 1
    assert parse_rating("Zero") is None


def test_parse_availability():
    assert parse_availability("In stock (19 available)") is True
    assert parse_availability("Out of stock") is False


def test_clean_books_from_fixture():
    soup = load_fixture_soup()
    articles = soup.select("article.product_pod")
    raw_books = [parse_book(a, "Mystery") for a in articles]

    df = clean_books(raw_books)

    assert len(df) == 20
    assert df["rating"].between(1, 5).all()
    assert df["price_gbp"].dtype == "float64"
    assert df["in_stock"].dtype == bool

    # Real first book on this fixture page: Sharp Objects, £47.82, rating Four.
    first_row = df.iloc[0]
    assert first_row["title"] == "Sharp Objects"
    assert first_row["price_gbp"] == 47.82
    assert first_row["rating"] == 4
    assert first_row["price_inr"] == round(47.82 * 105.50, 2)


def test_clean_books_drops_unparseable_rows():
    raw_books = [
        {
            "title": "Good Book",
            "price_text": "£10.00",
            "rating_word": "Three",
            "availability_text": "In stock",
            "category": "Mystery",
        },
        {
            "title": "Bad Price Book",
            "price_text": "no price here",
            "rating_word": "Three",
            "availability_text": "In stock",
            "category": "Mystery",
        },
        {
            "title": "Bad Rating Book",
            "price_text": "£10.00",
            "rating_word": "Zero",
            "availability_text": "In stock",
            "category": "Mystery",
        },
    ]

    df = clean_books(raw_books)

    assert len(df) == 1
    assert df.iloc[0]["title"] == "Good Book"
