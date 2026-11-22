"""
Step 1 - Clean the raw Global Superstore export.

The raw file has several real-world data quality problems:
  * an unnamed leftover index column
  * European decimal commas in numeric fields ("45,06" instead of 45.06)
  * dates stored as text in M/D/YY format
  * postal codes stored as floats ("27217.0") and missing outside the US
  * column names with spaces and hyphens

Output: data/processed/superstore_clean.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "global_super_store_orders.tsv"
OUT = ROOT / "data" / "processed" / "superstore_clean.csv"

NUMERIC_COLS = ["sales", "discount", "profit", "shipping_cost"]


def to_snake(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])
    df.columns = [to_snake(c) for c in df.columns]

    # Decimal commas -> floats
    for col in NUMERIC_COLS:
        df[col] = df[col].str.replace(",", ".", regex=False).astype(float)
    df["quantity"] = df["quantity"].astype(int)

    # Text dates -> real dates
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%y")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%y")

    # Postal codes: "27217.0" -> "27217"; leave missing as empty
    df["postal_code"] = (
        df["postal_code"].str.replace(r"\.0$", "", regex=True).fillna("")
    )

    # Trim stray whitespace in text columns
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].str.strip()

    # Derived columns used throughout the analysis
    df["days_to_ship"] = (df["ship_date"] - df["order_date"]).dt.days
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["profit_margin"] = (df["profit"] / df["sales"]).round(4)
    df["is_loss"] = df["profit"] < 0

    return df


def validate(df: pd.DataFrame) -> None:
    assert df["row_id"].is_unique, "row_id should uniquely identify each order line"
    assert (df["sales"] > 0).all(), "every line should have positive sales"
    assert df["discount"].between(0, 1).all(), "discounts should be between 0 and 1"
    assert (df["days_to_ship"] >= 0).all(), "ship date can't be before order date"


def main() -> None:
    raw = pd.read_csv(RAW, sep="\t", dtype=str)
    df = clean(raw)
    validate(df)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Cleaned {len(df):,} rows x {df.shape[1]} columns -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
