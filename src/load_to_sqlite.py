"""
Step 2 - Load the cleaned data into a SQLite database.

Creates data/superstore.db with one table, `orders`, defined in sql/schema.sql.
SQLite needs no server, so anyone who clones the repo can run the SQL queries.
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "processed" / "superstore_clean.csv"
DB = ROOT / "data" / "superstore.db"
SCHEMA = ROOT / "sql" / "schema.sql"


def main() -> None:
    df = pd.read_csv(CLEAN, dtype={"postal_code": str})
    df["postal_code"] = df["postal_code"].fillna("")
    df["is_loss"] = df["is_loss"].astype(int)

    DB.unlink(missing_ok=True)
    with sqlite3.connect(DB) as conn:
        conn.executescript(SCHEMA.read_text())
        df.to_sql("orders", conn, if_exists="append", index=False)
        count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"Loaded {count:,} rows into {DB.relative_to(ROOT)} (table: orders)")


if __name__ == "__main__":
    main()
