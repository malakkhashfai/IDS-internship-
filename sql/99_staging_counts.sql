-- one-row-per-check summary (returns text values so they export cleanly)
SELECT 'current_database' AS check_name, current_database()::text AS value
UNION ALL
SELECT 'stg_customers_rows', COUNT(*)::text FROM stg_customers
UNION ALL
SELECT 'stg_products_rows', COUNT(*)::text FROM stg_products
UNION ALL
SELECT 'stg_orders_rows', COUNT(*)::text FROM stg_orders
UNION ALL
SELECT 'stg_order_revenue_rows', COUNT(*)::text FROM stg_order_revenue
UNION ALL
SELECT 'missing_order_id', (SELECT COUNT(*) FROM stg_order_revenue WHERE order_id IS NULL)::text
UNION ALL
SELECT 'duplicate_order_ids_count', (SELECT COUNT(*) FROM (SELECT order_id FROM stg_order_revenue GROUP BY order_id HAVING COUNT(*)>1) t)::text
UNION ALL
SELECT 'revenue_not_in_orders', (SELECT COUNT(*) FROM stg_order_revenue r LEFT JOIN stg_orders o ON r.order_id=o.order_id WHERE o.order_id IS NULL)::text
UNION ALL
SELECT 'orders_with_missing_customer', (SELECT COUNT(*) FROM (SELECT DISTINCT customer_id FROM stg_orders) o LEFT JOIN stg_customers c ON o.customer_id=c.customer_id WHERE c.customer_id IS NULL)::text;