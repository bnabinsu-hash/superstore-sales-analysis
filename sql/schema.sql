-- Table for cleaned Global Superstore order lines (one row per product in an order)
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    row_id          INTEGER PRIMARY KEY,
    order_id        TEXT    NOT NULL,
    order_date      DATE    NOT NULL,
    ship_date       DATE    NOT NULL,
    ship_mode       TEXT,
    customer_id     TEXT    NOT NULL,
    customer_name   TEXT,
    segment         TEXT,
    city            TEXT,
    state           TEXT,
    country         TEXT,
    postal_code     TEXT,
    market          TEXT,
    region          TEXT,
    product_id      TEXT    NOT NULL,
    category        TEXT,
    sub_category    TEXT,
    product_name    TEXT,
    sales           REAL    NOT NULL,
    quantity        INTEGER NOT NULL,
    discount        REAL,
    profit          REAL,
    shipping_cost   REAL,
    order_priority  TEXT,
    days_to_ship    INTEGER,
    order_year      INTEGER,
    order_month     TEXT,
    profit_margin   REAL,
    is_loss         INTEGER
);

CREATE INDEX idx_orders_market   ON orders (market);
CREATE INDEX idx_orders_category ON orders (category, sub_category);
CREATE INDEX idx_orders_date     ON orders (order_date);
