"""
Step 3 - Answer the business questions and save charts to images/.

Reads from the SQLite database built by load_to_sqlite.py, so the charts use
exactly the same numbers as the SQL in sql/analysis_queries.sql.
"""
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "superstore.db"
IMG = ROOT / "images"

# Colors: one hue for "profit/gain", a second for "loss"; recessive grey ink
GAIN = "#2a78d6"
LOSS = "#eb6834"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "font.size": 10,
    "grid.color": GRID,
})


def query(conn, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=150)
    plt.close(fig)
    print(f"saved images/{name}")


def margin_by_market(conn) -> None:
    df = query(conn, """
        SELECT market, SUM(sales) AS sales,
               100.0 * SUM(profit) / SUM(sales) AS margin
        FROM orders GROUP BY market ORDER BY margin
    """)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(df["market"], df["margin"], color=GAIN, height=0.6)
    for y, (m, s) in enumerate(zip(df["margin"], df["sales"])):
        ax.text(m + 0.6, y, f"{m:.1f}%  (${s/1000:,.0f}K sales)", va="center", color=INK_2, fontsize=9)
    ax.set_title("Profit margin by market")
    ax.set_xlabel("Profit margin (%)")
    ax.set_xlim(0, df["margin"].max() * 1.45)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    save(fig, "margin_by_market.png")


def profit_by_subcategory(conn) -> None:
    df = query(conn, """
        SELECT sub_category, SUM(profit) AS profit
        FROM orders GROUP BY sub_category ORDER BY profit
    """)
    colors = [LOSS if p < 0 else GAIN for p in df["profit"]]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.barh(df["sub_category"], df["profit"], color=colors, height=0.65)
    ax.axvline(0, color=INK_2, linewidth=1)
    for y, p in enumerate(df["profit"]):
        if p < 0:
            ax.text(p - 120, y, f"-${abs(p):,.0f}", va="center", ha="right", color=INK, fontsize=9)
    ax.set_title("Total profit by sub-category (orange = losing money)")
    ax.set_xlabel("Profit (USD)")
    ax.set_xlim(df["profit"].min() * 1.6, df["profit"].max() * 1.1)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    save(fig, "profit_by_subcategory.png")


def discount_impact(conn) -> None:
    df = query(conn, """
        SELECT CASE WHEN discount = 0 THEN '0%'
                    WHEN discount <= 0.2 THEN '1-20%'
                    WHEN discount <= 0.4 THEN '21-40%'
                    ELSE '40%+' END AS band,
               AVG(profit_margin) * 100 AS margin,
               100.0 * SUM(is_loss) / COUNT(*) AS loss_pct,
               COUNT(*) AS n
        FROM orders GROUP BY band ORDER BY MIN(discount)
    """)
    colors = [LOSS if m < 0 else GAIN for m in df["margin"]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(df["band"], df["margin"], color=colors, width=0.55)
    ax.axhline(0, color=INK_2, linewidth=1)
    for x, (m, lp, n) in enumerate(zip(df["margin"], df["loss_pct"], df["n"])):
        offset = 4 if m >= 0 else -4
        ax.text(x, m + offset, f"{m:.0f}% margin\n{lp:.0f}% of lines lose money",
                ha="center", va="bottom" if m >= 0 else "top", color=INK, fontsize=9)
    ax.set_title("Average profit margin by discount level")
    ax.set_xlabel("Discount given")
    ax.set_ylabel("Average profit margin (%)")
    ax.set_ylim(df["margin"].min() * 1.45, df["margin"].max() * 2.0)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    save(fig, "discount_impact.png")


def quarterly_sales(conn) -> None:
    df = query(conn, "SELECT order_date, sales FROM orders")
    df["order_date"] = pd.to_datetime(df["order_date"])
    q = df.set_index("order_date")["sales"].resample("QE").sum()
    labels = [f"{d.year} Q{d.quarter}" for d in q.index]
    x = range(len(q))
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(x, q.values / 1000, color=GAIN, linewidth=2, marker="o", markersize=5)
    ax.set_xticks(list(x)[::2], labels[::2])
    ax.set_title("Quarterly sales, 2011-2014")
    ax.set_ylabel("Sales (USD, thousands)")
    ax.set_ylim(0, q.max() / 1000 * 1.2)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    peak = int(q.values.argmax())
    ax.annotate(f"Peak: ${q.max()/1000:,.1f}K ({labels[peak]})", (peak, q.max() / 1000),
                textcoords="offset points", xytext=(-10, 10), ha="right", color=INK, fontsize=9)
    save(fig, "quarterly_sales.png")


def main() -> None:
    IMG.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as conn:
        margin_by_market(conn)
        profit_by_subcategory(conn)
        discount_impact(conn)
        quarterly_sales(conn)


if __name__ == "__main__":
    main()
