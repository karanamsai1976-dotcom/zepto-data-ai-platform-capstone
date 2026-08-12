# Data Pipeline — Zepto Data & AI Platform Capstone

Scrapes [books.toscrape.com](http://books.toscrape.com), a public scraping-practice
site, cleans the results, loads them into a normalized SQLite database, and validates
that SQL and pandas produce identical results for the same question. The catalogue is
books rather than groceries -- the assignment explicitly allows this substitution
because the exercise is about pipeline mechanics (scrape -> clean -> load -> query),
not about the specific product category.

## Why category pages, not "All products"

We scrape from category listing pages (/catalogue/category/books/<slug>/index.html,
with pagination), not the sites "All products" listing. The "All products" pages do
not show a books category on the page itself, so that route would require an extra
request per book just to recover it. Category pages give us category for free and
keep the scrape deterministic.

## The GBP-to-INR rate

GBP_TO_INR = 105.50

This is a fixed, project-defined constant, not a live market rate -- it has no
date reference and needs no lookup. It is what gets graded; a live FX API is an
explicitly optional, ungraded extension that must never replace this constant.

## Cleaning decision: drop vs. impute

Rows whose price or star-rating text cannot be parsed are dropped, not
median-imputed. Fabricating a plausible price or rating for a book we couldnt
actually read off the page would misrepresent the real catalogue -- a books price
isnt naturally centered around some "typical" value the way, say, a persons age
might be, so a median substitute would just be a fictional number inserted into a
database that claims to reflect real listings. In practice this scrape produced 474
raw rows and all 474 parsed cleanly, so the drop path never actually triggered here --
but the guard exists so a genuinely malformed row can never silently corrupt the data.

## Schema

Two tables, related by primary key / foreign key:

    CREATE TABLE categories (
        category_id   INTEGER PRIMARY KEY,
        category_name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE books (
        book_id     INTEGER PRIMARY KEY,
        title       TEXT NOT NULL,
        price_gbp   REAL,
        price_inr   REAL,
        rating      INTEGER,
        in_stock    INTEGER,
        category_id INTEGER REFERENCES categories(category_id)
    );

Splitting category_name into its own table means its stored once per category
instead of once per book, so renaming a category later is a single edit rather than
hundreds, and typos in category text cant silently create phantom categories that
never match on a join.

## Idempotency

database.create_schema() drops and recreates both tables on every run, so
re-running the pipeline never duplicates rows -- nothing is ever appended to existing
data.

## Real results from the last run

- 474 books scraped across 9 categories (target was >=60 books / >=3 categories).
- All 474 rows parsed cleanly; 0 rows dropped.
- PRAGMA foreign_key_list(books) confirms books.category_id correctly references
  categories.category_id.
- pandas_validation.py proves a SQL JOIN and an equivalent pd.merge produce
  identical results for the same question (average price per category).

Full SQL query text and real output for all 5 required queries: see query_outputs.md.

## How to run

From the repository root, with the virtual environment activated:

    python -m data_pipeline.run_pipeline      # scrape -> clean -> load (needs internet)
    pytest data_pipeline/tests -q             # offline parser tests (no internet needed)
    python -m data_pipeline.queries           # run and print all 5 SQL queries
    python -m data_pipeline.pandas_validation # prove SQL JOIN == pandas merge

## Known traps handled

- Mojibake: response.encoding = "utf-8" is set before .text is read, so the
  pound sign decodes correctly instead of becoming garbled.
- Star rating in a CSS class: the rating word ("Three", etc.) is read from the
  second class on <p class="star-rating Three">, not from the elements text.
- Politeness: a time.sleep() delay runs between every request.
- in_stock as a real boolean: SQLite stores it as 0/1, but the pandas
  DataFrame column is cast to dtype bool.