"""Scraper for books.toscrape.com category listing pages."""

import time

import requests
from bs4 import BeautifulSoup

from data_pipeline import config


def fetch_page(url):
    response = requests.get(url)
    # Must be set explicitly before reading .text, or the £ symbol in
    # prices gets mis-decoded into "Â£" (mojibake).
    response.encoding = "utf-8"
    return response.text


def get_category_name(soup):
    return soup.select_one("ul.breadcrumb li.active").get_text(strip=True)


def parse_book(article, category_name):
    title = article.h3.a["title"]
    price_text = article.select_one("p.price_color").get_text(strip=True)

    # The star rating lives in the second CSS class of this tag, e.g.
    # <p class="star-rating Three">, not in the element's text.
    rating_word = article.select_one("p.star-rating")["class"][1]

    availability_text = article.select_one("p.instock.availability").get_text(strip=True)

    return {
        "title": title,
        "price_text": price_text,
        "rating_word": rating_word,
        "availability_text": availability_text,
        "category": category_name,
    }


def scrape_category(slug):
    """Scrape every page of one category, following pagination."""
    url = config.BASE_URL.format(slug=slug)
    books = []
    category_name = None

    while url is not None:
        html = fetch_page(url)
        soup = BeautifulSoup(html, "lxml")

        if category_name is None:
            category_name = get_category_name(soup)

        for article in soup.select("article.product_pod"):
            books.append(parse_book(article, category_name))

        next_link = soup.select_one("li.next a")
        if next_link is not None:
            url = url.rsplit("/", 1)[0] + "/" + next_link["href"]
        else:
            url = None

        time.sleep(config.REQUEST_DELAY_SECONDS)

    return books


def scrape_all_categories():
    """Scrape every configured category and return one combined list of book dicts."""
    all_books = []
    for slug in config.CATEGORY_SLUGS:
        all_books.extend(scrape_category(slug))
    return all_books


if __name__ == "__main__":
    import pandas as pd

    books = scrape_all_categories()
    df = pd.DataFrame(books)

    print(f"Rows scraped: {len(df)}")
    print(f"Distinct categories: {df['category'].nunique()} -> {sorted(df['category'].unique())}")
    print(df.head())
