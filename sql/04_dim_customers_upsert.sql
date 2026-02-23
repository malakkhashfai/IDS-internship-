-- ============================================================
-- 04_dim_customers_upsert.sql
-- Populate dim_customers from stg_customers (idempotent)
--
-- Business Rule:
-- Deduplicate on customer_unique_id.
-- Keep the most recent record by created_at (DESC NULLS LAST).
-- ============================================================

BEGIN;
SET search_path = public;

WITH dedup AS (
  SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    created_at
  FROM (
    SELECT
      c.*,
      ROW_NUMBER() OVER (
        PARTITION BY c.customer_unique_id
        ORDER BY c.created_at DESC NULLS LAST, c.customer_id
      ) AS rn
    FROM stg_customers c
    WHERE c.customer_unique_id IS NOT NULL
  ) x
  WHERE rn = 1
)

INSERT INTO dim_customers (
  customer_id,
  customer_unique_id,
  customer_zip_code_prefix,
  customer_city,
  customer_state,
  created_at
)
SELECT
  customer_id,
  customer_unique_id,
  customer_zip_code_prefix,
  customer_city,
  customer_state,
  created_at
FROM dedup

ON CONFLICT (customer_unique_id)
DO UPDATE SET
  customer_id              = EXCLUDED.customer_id,
  customer_zip_code_prefix = EXCLUDED.customer_zip_code_prefix,
  customer_city            = EXCLUDED.customer_city,
  customer_state           = EXCLUDED.customer_state,
  created_at               = EXCLUDED.created_at;

COMMIT;

-- ============================================================
-- VALIDATIONS 
-- ============================================================

-- 1) Count 
SELECT 'dim_customers' AS table_name, COUNT(*) AS row_count
FROM dim_customers;

-- 2) No duplicate customer_unique_id (should return 0 rows)
SELECT customer_unique_id, COUNT(*) AS cnt
FROM dim_customers
GROUP BY customer_unique_id
HAVING COUNT(*) > 1;

-- 3) Null key check (should return 0)
SELECT COUNT(*) AS null_unique_ids
FROM dim_customers
WHERE customer_unique_id IS NULL;

-- 4) Sample rows 
SELECT *
FROM dim_customers
ORDER BY customer_sk
LIMIT 10;