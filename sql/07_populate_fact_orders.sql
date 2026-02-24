-- ============================================================
-- 07_populate_fact_orders.sql
-- Populate fact_orders with business logic (idempotent)
-- ============================================================

-- Insert or update facts at order grain
INSERT INTO fact_orders (
  order_id,
  customer_sk,
  purchase_date_sk,
  order_status,
  order_purchase_timestamp,
  order_delivered_customer_date,
  order_estimated_delivery_date,
  order_revenue,
  total_freight,
  delivery_days,
  is_delayed
)
SELECT
  r.order_id,
  dc.customer_sk,
  dd.date_sk,
  o.order_status,
  o.order_purchase_timestamp,
  o.order_delivered_customer_date,
  -- If you do not have an estimated delivery in staging, keep NULL.
  -- If you have a column, replace the NULL with that column (e.g. o.order_estimated_delivery_date).
  NULL::timestamp AS order_estimated_delivery_date,
  r.order_revenue,
  r.total_freight,
  CASE
    WHEN o.order_delivered_customer_date IS NOT NULL AND o.order_purchase_timestamp IS NOT NULL
      THEN (o.order_delivered_customer_date::date - o.order_purchase_timestamp::date)
    ELSE NULL
  END AS delivery_days,
  CASE
    WHEN o.order_delivered_customer_date IS NOT NULL AND NULL IS NOT NULL -- no estimated date available
      THEN (o.order_delivered_customer_date::date > (NULL::date))
    ELSE NULL
  END AS is_delayed
FROM stg_order_revenue r
JOIN stg_orders o ON r.order_id = o.order_id
-- map orders' customer to dim_customers: prefer matching by customer_id first; if your pipeline uses customer_unique_id instead, change join accordingly
LEFT JOIN dim_customers dc ON o.customer_id = dc.customer_id
LEFT JOIN dim_date dd ON o.order_purchase_timestamp::date = dd.full_date
-- only insert rows where we have a matching dim_customer and a date (if you want to accept missing date, remove dd condition)
WHERE dc.customer_sk IS NOT NULL
-- Idempotent upsert: update values if order already exists
ON CONFLICT (order_id) DO UPDATE SET
  customer_sk = EXCLUDED.customer_sk,
  purchase_date_sk = EXCLUDED.purchase_date_sk,
  order_status = EXCLUDED.order_status,
  order_purchase_timestamp = EXCLUDED.order_purchase_timestamp,
  order_delivered_customer_date = EXCLUDED.order_delivered_customer_date,
  order_estimated_delivery_date = EXCLUDED.order_estimated_delivery_date,
  order_revenue = EXCLUDED.order_revenue,
  total_freight = EXCLUDED.total_freight,
  delivery_days = EXCLUDED.delivery_days,
  is_delayed = EXCLUDED.is_delayed;