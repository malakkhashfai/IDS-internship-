-- ============================================================
-- 03_create_dimensions.sql
-- Create dimension tables (DDL) + populate dim_date + validations
-- ============================================================

BEGIN;
SET search_path = public;

-- =========================
-- DIM_CUSTOMERS (DDL)
-- =========================
CREATE TABLE IF NOT EXISTS dim_customers (
  customer_sk              BIGSERIAL PRIMARY KEY,
  customer_id              TEXT,
  customer_unique_id       TEXT NOT NULL UNIQUE,
  customer_zip_code_prefix TEXT,
  customer_city            TEXT,
  customer_state           TEXT,
  created_at               TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_customers_customer_id
  ON dim_customers (customer_id);

-- =========================
-- DIM_PRODUCTS (DDL)
-- =========================
CREATE TABLE IF NOT EXISTS dim_products (
  product_sk                 BIGSERIAL PRIMARY KEY,
  product_id                 TEXT NOT NULL UNIQUE,
  product_category           TEXT NOT NULL DEFAULT 'unknown',
  product_name_lenght        INT,
  product_description_lenght INT,
  product_photos_qty         INT,
  product_weight_g           NUMERIC,
  product_length_cm          NUMERIC,
  product_height_cm          NUMERIC,
  product_width_cm           NUMERIC
);

CREATE INDEX IF NOT EXISTS idx_dim_products_category
  ON dim_products (product_category);

-- =========================
-- DIM_DATE (DDL)
-- =========================
CREATE TABLE IF NOT EXISTS dim_date (
  date_sk        BIGSERIAL PRIMARY KEY,
  full_date      DATE NOT NULL UNIQUE,
  year           INT  NOT NULL,
  quarter        INT  NOT NULL,
  month          INT  NOT NULL,
  month_name     TEXT NOT NULL,
  day            INT  NOT NULL,
  day_of_week    INT  NOT NULL,   -- 1..7 (Mon..Sun)
  day_name       TEXT NOT NULL,
  is_weekend     BOOLEAN NOT NULL
);

-- =========================
-- Populate dim_date (idempotent) using min/max from stg_orders
-- =========================
WITH bounds AS (
  SELECT
    MIN(order_purchase_timestamp)::date AS min_d,
    MAX(order_purchase_timestamp)::date AS max_d
  FROM stg_orders
  WHERE order_purchase_timestamp IS NOT NULL
),
series AS (
  SELECT gs::date AS d
  FROM bounds,
  LATERAL generate_series(bounds.min_d, bounds.max_d, interval '1 day') gs
  WHERE bounds.min_d IS NOT NULL AND bounds.max_d IS NOT NULL
)
INSERT INTO dim_date (
  full_date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend
)
SELECT
  d,
  EXTRACT(YEAR FROM d)::int,
  EXTRACT(QUARTER FROM d)::int,
  EXTRACT(MONTH FROM d)::int,
  TRIM(TO_CHAR(d, 'Month')),
  EXTRACT(DAY FROM d)::int,
  EXTRACT(ISODOW FROM d)::int,
  TRIM(TO_CHAR(d, 'Day')),
  (EXTRACT(ISODOW FROM d)::int IN (6,7))
FROM series
ON CONFLICT (full_date) DO NOTHING;
-- Safety insert: ensure the max stg_orders date exists in dim_date (idempotent)
INSERT INTO dim_date (
  full_date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend
)
SELECT
  mx,
  EXTRACT(YEAR FROM mx)::int,
  EXTRACT(QUARTER FROM mx)::int,
  EXTRACT(MONTH FROM mx)::int,
  TRIM(TO_CHAR(mx, 'Month')),
  EXTRACT(DAY FROM mx)::int,
  EXTRACT(ISODOW FROM mx)::int,
  TRIM(TO_CHAR(mx, 'Day')),
  (EXTRACT(ISODOW FROM mx)::int IN (6,7))
FROM (
  SELECT MAX(order_purchase_timestamp)::date AS mx
  FROM stg_orders
  WHERE order_purchase_timestamp IS NOT NULL
) t
WHERE mx IS NOT NULL
ON CONFLICT (full_date) DO NOTHING;
COMMIT;

-- ============================================================
-- VALIDATIONS - runs every time
-- ============================================================

-- 1) Quick counts 
SELECT 'dim_customers' AS table_name, COUNT(*) AS row_count FROM dim_customers
UNION ALL
SELECT 'dim_products', COUNT(*) FROM dim_products
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date;

-- 2) Date range check (helps confirm dim_date built correctly)
SELECT
  MIN(full_date) AS dim_min_date,
  MAX(full_date) AS dim_max_date,
  COUNT(*)       AS dim_date_cnt
FROM dim_date;

SELECT
  MIN(order_purchase_timestamp)::date AS stg_min_date,
  MAX(order_purchase_timestamp)::date AS stg_max_date
FROM stg_orders
WHERE order_purchase_timestamp IS NOT NULL;

-- 3) Constraints sanity (should be 0 rows)
SELECT *
FROM dim_date
WHERE full_date IS NULL
   OR year IS NULL
   OR month IS NULL
   OR day IS NULL
   OR day_of_week IS NULL;

-- 4) dim_date validations
SELECT
  MIN(order_purchase_timestamp)::date AS stg_min_date,
  MAX(order_purchase_timestamp)::date AS stg_max_date
FROM stg_orders
WHERE order_purchase_timestamp IS NOT NULL;
