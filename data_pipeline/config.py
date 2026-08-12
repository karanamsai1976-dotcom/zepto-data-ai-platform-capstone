"""Configuration constants for the data_pipeline module."""

# Fixed project-defined GBP-to-INR conversion rate. This is NOT a live market
# rate -- it is an artificial constant for this assignment and must never be
# replaced with a live FX API call.
GBP_TO_INR = 105.50

# We scrape category listing pages (not the "All products" pages) because a
# category page exposes the book's category for free; the "All products"
# listing does not, which would require an extra request per book to recover it.
BASE_URL = "http://books.toscrape.com/catalogue/category/books/{slug}/index.html"

# Category slugs verified from the live site's sidebar navigation. Each slug
# already includes the site's own numeric id suffix (e.g. "fiction_10").
CATEGORY_SLUGS = [
    "fiction_10",
    "mystery_3",
    "historical-fiction_4",
    "sequential-art_5",
    "nonfiction_13",
    "fantasy_19",
    "young-adult_21",
    "romance_8",
    "childrens_11",
]

# Minimum scraping targets required by the assignment spec.
MIN_BOOKS = 60
MIN_CATEGORIES = 3

# Politeness delay between requests, in seconds.
REQUEST_DELAY_SECONDS = 0.5

# SQLite database file path, relative to the repository root.
DB_PATH = "data_pipeline/books.db"
