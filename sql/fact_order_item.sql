CREATE TABLE IF NOT EXISTS stg_order_items (
    order_id      TEXT,
    order_item_id INT,
    product_id    TEXT,
    seller_id     TEXT,
    price         NUMERIC,
    freight_value NUMERIC
);

-- ============================================================
-- 08_create_fact_order_items.sql
-- Create fact_order_items table (idempotent)
-- Grain: one row per order item (an order can have many items)
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_order_items (
    order_item_sk   BIGSERIAL PRIMARY KEY,
    order_id        TEXT NOT NULL REFERENCES fact_orders(order_id),
    product_sk      BIGINT NOT NULL REFERENCES dim_products(product_sk),
    order_item_id   INT,
    price           NUMERIC,
    freight_value   NUMERIC,
    seller_id       TEXT
);

CREATE INDEX IF NOT EXISTS idx_fact_oi_order_id   ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_oi_product_sk ON fact_order_items(product_sk);

-- ============================================================
-- 09_populate_fact_order_items.sql
-- Populate fact_order_items (idempotent via DELETE + INSERT)
-- ============================================================

BEGIN;
SET search_path = public;

-- Idempotent: clear before re-inserting
TRUNCATE TABLE fact_order_items RESTART IDENTITY;

INSERT INTO fact_order_items (
    order_id,
    product_sk,
    order_item_id,
    price,
    freight_value,
    seller_id
)
SELECT
    oi.order_id,
    dp.product_sk,
    oi.order_item_id,
    oi.price,
    oi.freight_value,
    oi.seller_id
FROM stg_order_items oi
-- link to dim_products via product_id
JOIN dim_products dp ON oi.product_id = dp.product_id
-- only keep items whose order exists in fact_orders
JOIN fact_orders fo ON oi.order_id = fo.order_id;

COMMIT;

-- ============================================================
-- VALIDATIONS
-- ============================================================

-- 1) Row count (should be > 0)
SELECT 'fact_order_items' AS table_name, COUNT(*) AS row_count
FROM fact_order_items;

-- 2) Orphan order_ids — orders in items but not in fact_orders (should be 0)
SELECT COUNT(*) AS orphan_orders
FROM fact_order_items foi
LEFT JOIN fact_orders fo ON foi.order_id = fo.order_id
WHERE fo.order_id IS NULL;

-- 3) Orphan product_sk — should be 0 since we INNER JOINed dim_products
SELECT COUNT(*) AS null_product_sk
FROM fact_order_items
WHERE product_sk IS NULL;

-- 4) Revenue sanity: compare sum of item prices vs fact_orders revenue
-- Small differences are ok (cancelled items etc), large gaps are a red flag
SELECT
    ROUND(SUM(foi.price)::NUMERIC, 2)        AS items_total_revenue,
    ROUND(SUM(fo.order_revenue)::NUMERIC, 2) AS orders_total_revenue,
    ROUND(
        ABS(SUM(foi.price) - SUM(fo.order_revenue))::NUMERIC, 2
    )                                         AS difference
FROM fact_order_items foi
JOIN fact_orders fo ON foi.order_id = fo.order_id;

-- 5) Top 10 categories by revenue (quick sanity preview for Power BI)
SELECT
    dp.product_category,
    COUNT(foi.order_item_sk)      AS items_sold,
    ROUND(SUM(foi.price)::NUMERIC, 2) AS total_revenue
FROM fact_order_items foi
JOIN dim_products dp ON foi.product_sk = dp.product_sk
GROUP BY dp.product_category
ORDER BY total_revenue DESC
LIMIT 10;