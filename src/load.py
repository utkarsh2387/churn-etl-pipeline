"""
Load stage of the churn ETL pipeline.

Writes the cleaned, flagged DataFrame to a local SQLite warehouse.
Swap the connection string for Postgres/BigQuery/Snowflake later
without changing the interface.
"""

import sqlite3
import pandas as pd
from pathlib import Path


def load(
    df: pd.DataFrame,
    db_path: str = "data/churn_warehouse.db",
    table: str = "customers_clean",
) -> None:
    """
    Write the transformed DataFrame to a SQLite table.

    Args:
        df: cleaned, transformed DataFrame.
        db_path: path to the SQLite database file (created if missing).
        table: destination table name (replaced on each run).
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table, conn, if_exists="replace", index=False)
    finally:
        conn.close()

    print(f"[LOAD] Wrote {len(df)} rows to table '{table}' in {db_path}")


if __name__ == "__main__":
    from extract import extract
    from transform import transform

    raw = extract()
    transformed = transform(raw)
    load(transformed)
