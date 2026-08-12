"""Named SQL queries against books.db. Each covers specific SQL clauses
required by the assignment: SELECT/WHERE, ORDER BY, LIMIT, DISTINCT,
IN/BETWEEN, and JOIN."""

# WHERE + ORDER BY + LIMIT: the 5 cheapest in-stock books.
CHEAPEST_IN_STOCK = """
SELECT title, price_gbp
FROM books
WHERE in_stock = 1
ORDER BY price_gbp ASC
LIMIT 5;
"""

# DISTINCT: every distinct star rating actually present in the data.
DISTINCT_RATINGS = """
SELECT DISTINCT rating
FROM books
ORDER BY rating;
"""

# BETWEEN: books priced between £20 and £30 (GBP).
MID_PRICED_BOOKS = """
SELECT title, price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 30
ORDER BY price_gbp ASC;
"""

# IN: books from a specific subset of categories.
BOOKS_IN_SELECTED_CATEGORIES = """
SELECT b.title, c.category_name
FROM books b
JOIN categories c ON b.category_id = c.category_id
WHERE c.category_name IN ('Fiction', 'Mystery', 'Fantasy')
ORDER BY c.category_name, b.title
LIMIT 10;
"""

# JOIN + aggregation: average price per category, across both tables.
AVG_PRICE_PER_CATEGORY = """
SELECT c.category_name, COUNT(*) AS book_count, ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp
FROM books b
JOIN categories c ON b.category_id = c.category_id
GROUP BY c.category_name
ORDER BY avg_price_gbp DESC;
"""

ALL_QUERIES = {
    "Cheapest in-stock books (WHERE, ORDER BY, LIMIT)": CHEAPEST_IN_STOCK,
    "Distinct star ratings present (DISTINCT)": DISTINCT_RATINGS,
    "Books priced £20-£30 (BETWEEN)": MID_PRICED_BOOKS,
    "Books in selected categories (IN, JOIN)": BOOKS_IN_SELECTED_CATEGORIES,
    "Average price per category (JOIN, aggregation)": AVG_PRICE_PER_CATEGORY,
}


if __name__ == "__main__":
    from data_pipeline.database import get_connection

    conn = get_connection()
    for name, query in ALL_QUERIES.items():
        print(f"\n=== {name} ===")
        print(query.strip())
        print("--- output ---")
        for row in conn.execute(query).fetchall():
            print(row)
    conn.close()
