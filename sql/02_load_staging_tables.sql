-- Sample rows to visually inspect
SELECT * FROM stg_order_revenue LIMIT 10;
SELECT * FROM stg_orders LIMIT 5;
SELECT * FROM stg_customers LIMIT 5;


-- Revenue sanity (min/max/total)
SELECT 
  COUNT(*) AS rows,
  SUM(order_revenue)      AS total_revenue,
  MIN(order_revenue)      AS min_order_revenue,
  MAX(order_revenue)      AS max_order_revenue,
  AVG(order_revenue)      AS avg_order_revenue
FROM stg_order_revenue;
