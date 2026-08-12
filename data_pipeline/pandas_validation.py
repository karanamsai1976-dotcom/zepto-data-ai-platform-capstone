"""Validate that SQL query results and their pandas equivalents agree."""

import pandas as pd

from data_pipeline.database import get_connection
from data_pipeline.queries import CHEAPEST_IN_STOCK, DISTINCT_RATINGS, AVG_PRICE_PER_CATEGORY


def read_sql_examples(conn):
    """Read two query results directly with pd.read_sql."""
    cheapest_df = pd.read_sql(CHEAPEST_IN_STOCK, conn)
    ratings_df = pd.read_sql(DISTINCT_RATINGS, conn)
    return cheapest_df, ratings_df


def sql_join_result(conn):
    """The average-price-per-category result, produced by SQLite's own JOIN."""
    return pd.read_sql(AVG_PRICE_PER_CATEGORY, conn)


def pandas_merge_result(conn):
    """
    Reproduce the same average-price-per-category result using pd.merge on
    in-memory DataFrames -- no SQL JOIN involved.
    """
    books_df = pd.read_sql("SELECT * FROM books", conn)
    categories_df = pd.read_sql("SELECT * FROM categories", conn)

    merged = pd.merge(books_df, categories_df, on="category_id")

    result = (
        merged.groupby("category_name")
        .agg(book_count=("book_id", "count"), avg_price_gbp=("price_gbp", "mean"))
        .reset_index()
    )
    result["avg_price_gbp"] = result["avg_price_gbp"].round(2)
    result = result.sort_values("avg_price_gbp", ascending=False).reset_index(drop=True)
    return result


if __name__ == "__main__":
    conn = get_connection()

    cheapest_df, ratings_df = read_sql_examples(conn)
    print("=== pd.read_sql: cheapest in-stock books ===")
    print(cheapest_df)
    print("\n=== pd.read_sql: distinct ratings ===")
    print(ratings_df)

    sql_result = sql_join_result(conn)
    merge_result = pandas_merge_result(conn)

    print("\n=== SQL JOIN result (via pd.read_sql) ===")
    print(sql_result)
    print("\n=== pandas pd.merge result (no SQL JOIN) ===")
    print(merge_result)

    pd.testing.assert_frame_equal(
        sql_result.reset_index(drop=True),
        merge_result.reset_index(drop=True),
        check_dtype=False,
    )
    print("\nSQL JOIN and pandas merge results match exactly.")

    conn.close()
