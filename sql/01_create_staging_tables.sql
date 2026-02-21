CREATE DATABASE ecommerce_project;

-- create staging tables for ecommerce_project
SET search_path = public;  -- or ecommerce if you created that schema

CREATE TABLE IF NOT EXISTS stg_customers (
  customer_id               TEXT,
  customer_unique_id        TEXT,
  customer_zip_code_prefix  TEXT,
  customer_city             TEXT,
  customer_state            TEXT,
  created_at                TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stg_products (
  product_id                 TEXT,
  product_category_name      TEXT,
  product_name_lenght        INT,
  product_description_lenght INT,
  product_photos_qty         INT,
  product_weight_g           NUMERIC,
  product_length_cm          NUMERIC,
  product_height_cm          NUMERIC,
  product_width_cm           NUMERIC
);

CREATE TABLE IF NOT EXISTS stg_orders (
  order_id                        TEXT,
  customer_id                     TEXT,
  order_status                    TEXT,
  order_purchase_timestamp        TIMESTAMP,
  order_approved_at               TIMESTAMP,
  order_delivered_carrier_date    TIMESTAMP,
  order_delivered_customer_date   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stg_order_revenue (
  order_id        TEXT PRIMARY KEY,
  order_revenue   NUMERIC,
  total_freight   NUMERIC,
  items_count     INT,
  avg_item_price  NUMERIC
);