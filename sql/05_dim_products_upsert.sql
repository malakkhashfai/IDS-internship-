-- ============================================================
-- 05_dim_products_upsert.sql
-- Populate dim_products from stg_products (idempotent)
--
-- Business Rules:
-- 1) product_id is the natural key (UNIQUE).
-- 2) product_category: keep lower-case, replace NULL with 'unknown'.
-- 3) Deduplicate on product_id (keep best/latest row if duplicates exist).
-- ============================================================

BEGIN;
SET search_path = public;

-- =========================
-- Upsert into DIM_PRODUCTS
-- =========================
WITH prepared AS (
  SELECT
    p.product_id,
    COALESCE(NULLIF(LOWER(TRIM(p.product_category_name)), ''), 'unknown') AS product_category,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    ROW_NUMBER() OVER (
      PARTITION BY p.product_id
      ORDER BY
        -- prefer rows with category filled
        (p.product_category_name IS NOT NULL) DESC,
        -- prefer rows with more complete measures
        (p.product_weight_g IS NOT NULL) DESC,
        (p.product_length_cm IS NOT NULL) DESC,
        (p.product_height_cm IS NOT NULL) DESC,
        (p.product_width_cm IS NOT NULL) DESC
    ) AS rn
  FROM stg_products p
  WHERE p.product_id IS NOT NULL
),
dedup AS (
  SELECT *
  FROM prepared
  WHERE rn = 1
)
INSERT INTO dim_products (
  product_id,
  product_category,
  product_name_lenght,
  product_description_lenght,
  product_photos_qty,
  product_weight_g,
  product_length_cm,
  product_height_cm,
  product_width_cm
)
SELECT
  product_id,
  product_category,
  product_name_lenght,
  product_description_lenght,
  product_photos_qty,
  product_weight_g,
  product_length_cm,
  product_height_cm,
  product_width_cm
FROM dedup
ON CONFLICT (product_id)
DO UPDATE SET
  product_category           = EXCLUDED.product_category,
  product_name_lenght        = EXCLUDED.product_name_lenght,
  product_description_lenght = EXCLUDED.product_description_lenght,
  product_photos_qty         = EXCLUDED.product_photos_qty,
  product_weight_g           = EXCLUDED.product_weight_g,
  product_length_cm          = EXCLUDED.product_length_cm,
  product_height_cm          = EXCLUDED.product_height_cm,
  product_width_cm           = EXCLUDED.product_width_cm;

COMMIT;

-- ============================================================
-- VALIDATIONS (NOT OPTIONAL)
-- ============================================================

-- 1) Count
SELECT 'dim_products' AS table_name, COUNT(*) AS row_count
FROM dim_products;

-- 2) No duplicate product_id (should return 0 rows)
SELECT product_id, COUNT(*) AS cnt
FROM dim_products
GROUP BY product_id
HAVING COUNT(*) > 1;

-- 3) Null key check (should return 0)
SELECT COUNT(*) AS null_product_ids
FROM dim_products
WHERE product_id IS NULL;

-- 4) product_category must not be NULL (unknown allowed) (should return 0 rows)
SELECT COUNT(*) AS null_categories
FROM dim_products
WHERE product_category IS NULL;

-- 5) Numeric validations (should return 0 rows)
SELECT *
FROM dim_products
WHERE product_weight_g < 0
   OR product_length_cm < 0
   OR product_height_cm < 0
   OR product_width_cm < 0;

-- 6) Sample rows 
SELECT *
FROM dim_products
ORDER BY product_sk
LIMIT 10;