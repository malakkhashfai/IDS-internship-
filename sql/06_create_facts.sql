-- ============================================================
-- 06_create_facts.sql
-- Create fact_orders table (idempotent)
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_orders (
    order_sk BIGSERIAL PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    customer_sk BIGINT NOT NULL REFERENCES dim_customers(customer_sk),
    purchase_date_sk BIGINT REFERENCES dim_date(date_sk),
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    order_revenue NUMERIC,
    total_freight NUMERIC,
    delivery_days INT,
    is_delayed BOOLEAN
);

-- Useful indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer_sk ON fact_orders(customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_orders_purchase_date_sk ON fact_orders(purchase_date_sk);