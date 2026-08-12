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


## Acceptance Criteria — Proof

Verified against the actual committed `data_pipeline/books.db` and a fresh run of
every script, not assumed. Commands are reproducible by anyone who clones the repo.

### 1. End-to-end run, no manual copy-pasting, >= 60 rows / >= 3 categories

`python -m data_pipeline.run_pipeline` performs scrape -> clean -> load as a single
automated command. Real output from a run:

```
Scraping books.toscrape.com ...
Scraped 474 raw rows
Cleaned to 474 rows
Loaded 474 books across 9 categories
```

Run twice in a row, the counts were identical both times (474 / 9), confirming the
loader is idempotent (drop-and-recreate on every run, never appends).

### 2. Typed columns and the fixed 105.50 rate

`cleaning.py` produces `price_gbp` (float64), `price_inr` (float64), `rating`
(int64), and `in_stock` (bool). Verified against the committed database:

```
row_count: 474 (need >= 60)               -> 474
cat_count: 9 (need >= 3)                  -> 9
rows with rating outside 1..5: 0 (need 0) -> 0
orphan category_id rows: 0 (need 0)       -> 0
```

`price_inr` correctness was checked with `ROUND(price_gbp * 105.50, 2)` in SQL and
initially showed 5 apparent mismatches out of 474. Investigation showed all 5 are
exact `.625`/`.125` third-decimal ties (e.g. `11.75 * 105.50 = 1239.625`), where
SQLite `ROUND()` (rounds half away from zero) and Python `round()` (rounds half to
even) legitimately disagree. Re-checked all 5 directly against Python `round()`,
which is what `cleaning.py` actually uses -- all 5 matched the stored `price_inr`
exactly. `price_inr` is correct for all 474 rows.

The exact rate, `GBP_TO_INR = 105.50`, is stated above in this README and in
`data_pipeline/config.py`.

### 3. Database file and regenerating script, two-table PK/FK schema

`data_pipeline/books.db` is committed (49 KB), and `database.py` + `run_pipeline.py`
regenerate it from scratch on every run. Schema (see above) is `categories` and
`books` related by `books.category_id -> categories.category_id`. Verified with:

```
PRAGMA foreign_key_list(books) -> [(0, 0, "categories", "category_id", "category_id", "NO ACTION", "NO ACTION", "NONE")]
```

### 4. >= 5 SQL queries, all required clauses, >= 1 JOIN, with real output

`queries.py` defines 5 named queries. Clause coverage: `WHERE`/`ORDER BY`/`LIMIT`
(query 1), `DISTINCT` (query 2), `BETWEEN` (query 3), `IN` and `JOIN` (query 4),
`JOIN` with aggregation (query 5) -- two queries use `JOIN`. Full query text and
real printed output for all 5: see [`query_outputs.md`](query_outputs.md).

### 5. pd.read_sql vs pd.merge, side by side, matching

`pandas_validation.py` prints the SQL-JOIN result and the pandas-merge result side
by side (both are the identical 9-row average-price-per-category table) and asserts
equality with `pd.testing.assert_frame_equal`. Real output ended with:

```
SQL JOIN and pandas merge results match exactly.
```

with no `AssertionError`.

### 6. README documents install/run and cleaning decisions

See the "How to run" and "Cleaning decision: drop vs. impute" sections above in
this same file.

### 7. Feature branch, >= 2 commits, merged to main

The `data-pipeline` branch carries 7 commits and was merged into `main` via a real
merge commit (two parents, not a fast-forward or squash):

```
git log --graph --all --oneline --decorate
*   ee28393 Merge pull request #1 from .../data-pipeline
|\
| * a6fb904 Add data_pipeline module README
| * e1045a8 Add pandas validation proving SQL and pandas JOIN results agree
| * 6fc6d13 Add SQL queries and their real output to query_outputs.md
| * 1f4bd7e Add SQLite schema, loader, and end-to-end run_pipeline script
| * cbfea4b Add HTML fixture for offline parser tests
| * 8781383 Add cleaning module and offline parser tests with HTML fixture
| * 728220d Add data_pipeline scraper and config
|/
* ac80a73 Add project scaffold: .gitignore, requirements.txt, README stub
```
