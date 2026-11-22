-- Business questions answered with SQL against data/superstore.db
-- Run any query with:  sqlite3 data/superstore.db < sql/analysis_queries.sql
-- (or paste one into DB Browser for SQLite / the VS Code SQLite extension)

-- Q1. Overall KPIs
SELECT
    COUNT(DISTINCT order_id)                    AS orders,
    COUNT(DISTINCT customer_id)                 AS customers,
    ROUND(SUM(sales), 2)                        AS total_sales,
    ROUND(SUM(profit), 2)                       AS total_profit,
    ROUND(100.0 * SUM(profit) / SUM(sales), 1)  AS profit_margin_pct
FROM orders;

-- Q2. Sales and profit by market, best first
SELECT
    market,
    ROUND(SUM(sales), 2)                        AS sales,
    ROUND(SUM(profit), 2)                       AS profit,
    ROUND(100.0 * SUM(profit) / SUM(sales), 1)  AS margin_pct
FROM orders
GROUP BY market
ORDER BY sales DESC;

-- Q3. Which sub-categories lose money?
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 2)   AS sales,
    ROUND(SUM(profit), 2)  AS profit,
    ROUND(AVG(discount), 3) AS avg_discount
FROM orders
GROUP BY category, sub_category
ORDER BY profit ASC;

-- Q4. How do discounts affect profitability?
SELECT
    CASE
        WHEN discount = 0     THEN '0%'
        WHEN discount <= 0.2  THEN '1-20%'
        WHEN discount <= 0.4  THEN '21-40%'
        ELSE '40%+'
    END                                          AS discount_band,
    COUNT(*)                                     AS order_lines,
    ROUND(AVG(profit_margin) * 100, 1)           AS avg_margin_pct,
    ROUND(100.0 * SUM(is_loss) / COUNT(*), 1)    AS pct_lines_at_loss
FROM orders
GROUP BY discount_band
ORDER BY MIN(discount);

-- Q5. Year-over-year sales growth (window function)
WITH yearly AS (
    SELECT order_year, SUM(sales) AS sales
    FROM orders
    GROUP BY order_year
)
SELECT
    order_year,
    ROUND(sales, 2)                                                        AS sales,
    ROUND(100.0 * (sales - LAG(sales) OVER (ORDER BY order_year))
          / LAG(sales) OVER (ORDER BY order_year), 1)                      AS yoy_growth_pct
FROM yearly
ORDER BY order_year;

-- Q6. Top 10 customers by profit, with their rank inside their segment
SELECT *
FROM (
    SELECT
        customer_name,
        segment,
        ROUND(SUM(sales), 2)  AS sales,
        ROUND(SUM(profit), 2) AS profit,
        RANK() OVER (PARTITION BY segment ORDER BY SUM(profit) DESC) AS rank_in_segment
    FROM orders
    GROUP BY customer_id, customer_name, segment
)
ORDER BY profit DESC
LIMIT 10;

-- Q7. Average shipping time by ship mode and order priority
SELECT
    ship_mode,
    order_priority,
    COUNT(*)                     AS order_lines,
    ROUND(AVG(days_to_ship), 1)  AS avg_days_to_ship
FROM orders
GROUP BY ship_mode, order_priority
ORDER BY avg_days_to_ship;
