-- ============================================================
-- 08_validation_queries.sql
-- Validation checks
-- ============================================================

-- 1) Revenue validation (staging vs fact)
SELECT
  (SELECT COALESCE(SUM(order_revenue),0) FROM stg_order_revenue) AS stg_total_revenue,
  (SELECT COALESCE(SUM(order_revenue),0) FROM fact_orders)       AS fact_total_revenue,
  (SELECT COALESCE(SUM(order_revenue),0) FROM fact_orders)
  -
  (SELECT COALESCE(SUM(order_revenue),0) FROM stg_order_revenue) AS diff;

-- 2) Order count validation (staging vs fact)
SELECT
  (SELECT COUNT(DISTINCT order_id) FROM stg_orders) AS stg_orders_cnt,
  (SELECT COUNT(*) FROM fact_orders)                AS fact_orders_cnt,
  (SELECT COUNT(*) FROM stg_order_revenue)         AS stg_order_revenue_cnt;

-- 3) Duplicate primary key check in fact
SELECT order_id, COUNT(*) cnt
FROM fact_orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 4) FK integrity - customers
SELECT COUNT(*) AS bad_customer_fk
FROM fact_orders f
LEFT JOIN dim_customers c ON c.customer_sk = f.customer_sk
WHERE c.customer_sk IS NULL;


-- 5) FK integrity - dates (purchase_date_sk)
SELECT COUNT(*) AS bad_date_fk
FROM fact_orders f
LEFT JOIN dim_date d ON d.date_sk = f.purchase_date_sk
WHERE f.purchase_date_sk IS NOT NULL AND d.date_sk IS NULL;

-- 6) Revenue non-negativity and sanity
SELECT COUNT(*) AS negative_revenue_count FROM fact_orders WHERE order_revenue < 0;
SELECT MIN(order_revenue) AS min_order_revenue, MAX(order_revenue) AS max_order_revenue FROM fact_orders;

-- 7) Orders in staging that did not land in fact (possible missing customer or date)
SELECT r.order_id
FROM stg_order_revenue r
LEFT JOIN fact_orders f ON r.order_id = f.order_id
WHERE f.order_id IS NULL
LIMIT 100;

-- 8) Rows excluded due to missing customer mapping (diagnostic)
-- Shows orders we had in staging that lacked a dim customer mapping at populate time
SELECT o.order_id, o.customer_id
FROM stg_orders o
LEFT JOIN dim_customers dc ON o.customer_id = dc.customer_id
WHERE dc.customer_sk IS NULL
LIMIT 100;

-- 9) Sample of fact_orders (for screenshots)
SELECT * FROM fact_orders ORDER BY order_sk LIMIT 20;