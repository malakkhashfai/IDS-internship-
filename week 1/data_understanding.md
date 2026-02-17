## Title 
Olist Brazilian E-Commerce — Data Understanding and Initial Findings

# Data Understanding
I opened the dataset from Kaggle and inspected the main CSVs using pandas. I looked at shapes, dtypes, nulls, and whether the primary keys are unique or not. Below you’ll find a short summary of what is clean, what needs fixing, and the quick actions I recommend.

## Purpose
This document summarizes the initial exploration of the Olist Brazilian E-Commerce dataset. It describes table structures, primary keys, relationships, data quality issues found during the first pass and recommended cleaning steps. The goal is to provide a clear handoff so teammates can start their tasks immediately.

## Methodology
I loaded the CSV files from `data/raw/` using Pandas and ran checks for row/column counts, dtypes, null values and primary key uniqueness. 1000 row samples were exported to `docs/samples/` for quicker local development by teammates.

## Dataset overview
- Source: Olist Brazilian E-Commerce (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- Files explored: customers, orders, order_items, products

## Key findings
Primary keys:
- customers → customer_id
- orders → order_id
- products → product_id
- order_items → (order_id + order_item_id)

Relationships:
- orders.customer_id → customers.customer_id
- order_items.order_id → orders.order_id
- order_items.product_id → products.product_id

## Observations & Issues (initial)
- I noticed about 610 rows missing `product_category_name`i will replace these with "unknown" during product cleaning.
- About 2,965 orders are missing a `order_delivered_customer_date`. We will check whether these are cancelled/returned or just late/missing records.
- Price and freight columns appear numeric in `order_items`, but other numeric like fields in other tables are strings/objects we will cast them to numeric types during cleaning.
- No duplicate primary keys were observed during the first pass if we find exceptions during transformation we will handle that.

## customers
- Rows: 99441
- Columns: 5
- Candidate primary key: `('customer_id',)`
  - PK unique?: True (unique rows: 99441 / total: 99441)

- Top null counts (top 10):
  - customer_id: 0
  - customer_unique_id: 0
  - customer_zip_code_prefix: 0
  - customer_city: 0
  - customer_state: 0

- dtypes (first 10):
  - customer_id: object
  - customer_unique_id: object
  - customer_zip_code_prefix: int64
  - customer_city: object
  - customer_state: object

- Sample head (first 5 rows):
```
{'customer_id': '06b8999e2fba1a1fbc88172c00ba8bc7', 'customer_unique_id': '861eff4711a542e4b93843c6dd7febb0', 'customer_zip_code_prefix': 14409, 'customer_city': 'franca', 'customer_state': 'SP'}
{'customer_id': '18955e83d337fd6b2def6b18a428ac77', 'customer_unique_id': '290c77bc529b7ac935b93aa66c333dc3', 'customer_zip_code_prefix': 9790, 'customer_city': 'sao bernardo do campo', 'customer_state': 'SP'}
{'customer_id': '4e7b3e00288586ebd08712fdd0374a03', 'customer_unique_id': '060e732b5b29e8181a18229c7b0b2b5e', 'customer_zip_code_prefix': 1151, 'customer_city': 'sao paulo', 'customer_state': 'SP'}
{'customer_id': 'b2b6027bc5c5109e529d4dc6358b12c3', 'customer_unique_id': '259dac757896d24d7702b9acbbff3f3c', 'customer_zip_code_prefix': 8775, 'customer_city': 'mogi das cruzes', 'customer_state': 'SP'}
{'customer_id': '4f2d8ab171c80ec8364f7c12e35b23ad', 'customer_unique_id': '345ecd01c38d18a9036ed96c73b8d066', 'customer_zip_code_prefix': 13056, 'customer_city': 'campinas', 'customer_state': 'SP'}
```

## orders
- Rows: 99441
- Columns: 8
- Candidate primary key: `('order_id',)`
  - PK unique?: True (unique rows: 99441 / total: 99441)

- Top null counts (top 10):
  - order_delivered_customer_date: 2965
  - order_delivered_carrier_date: 1783
  - order_approved_at: 160
  - order_id: 0
  - customer_id: 0
  - order_status: 0
  - order_purchase_timestamp: 0
  - order_estimated_delivery_date: 0

- dtypes (first 10):
  - order_id: object
  - customer_id: object
  - order_status: object
  - order_purchase_timestamp: object
  - order_approved_at: object
  - order_delivered_carrier_date: object
  - order_delivered_customer_date: object
  - order_estimated_delivery_date: object

- Sample head (first 5 rows):
```
{'order_id': 'e481f51cbdc54678b7cc49136f2d6af7', 'customer_id': '9ef432eb6251297304e76186b10a928d', 'order_status': 'delivered', 'order_purchase_timestamp': '2017-10-02 10:56:33', 'order_approved_at': '2017-10-02 11:07:15', 'order_delivered_carrier_date': '2017-10-04 19:55:00', 'order_delivered_customer_date': '2017-10-10 21:25:13', 'order_estimated_delivery_date': '2017-10-18 00:00:00'}
{'order_id': '53cdb2fc8bc7dce0b6741e2150273451', 'customer_id': 'b0830fb4747a6c6d20dea0b8c802d7ef', 'order_status': 'delivered', 'order_purchase_timestamp': '2018-07-24 20:41:37', 'order_approved_at': '2018-07-26 03:24:27', 'order_delivered_carrier_date': '2018-07-26 14:31:00', 'order_delivered_customer_date': '2018-08-07 15:27:45', 'order_estimated_delivery_date': '2018-08-13 00:00:00'}
{'order_id': '47770eb9100c2d0c44946d9cf07ec65d', 'customer_id': '41ce2a54c0b03bf3443c3d931a367089', 'order_status': 'delivered', 'order_purchase_timestamp': '2018-08-08 08:38:49', 'order_approved_at': '2018-08-08 08:55:23', 'order_delivered_carrier_date': '2018-08-08 13:50:00', 'order_delivered_customer_date': '2018-08-17 18:06:29', 'order_estimated_delivery_date': '2018-09-04 00:00:00'}
{'order_id': '949d5b44dbf5de918fe9c16f97b45f8a', 'customer_id': 'f88197465ea7920adcdbec7375364d82', 'order_status': 'delivered', 'order_purchase_timestamp': '2017-11-18 19:28:06', 'order_approved_at': '2017-11-18 19:45:59', 'order_delivered_carrier_date': '2017-11-22 13:39:59', 'order_delivered_customer_date': '2017-12-02 00:28:42', 'order_estimated_delivery_date': '2017-12-15 00:00:00'}
{'order_id': 'ad21c59c0840e6cb83a9ceb5573f8159', 'customer_id': '8ab97904e6daea8866dbdbc4fb7aad2c', 'order_status': 'delivered', 'order_purchase_timestamp': '2018-02-13 21:18:39', 'order_approved_at': '2018-02-13 22:20:29', 'order_delivered_carrier_date': '2018-02-14 19:46:34', 'order_delivered_customer_date': '2018-02-16 18:17:02', 'order_estimated_delivery_date': '2018-02-26 00:00:00'}
```

## order_items
- Rows: 112650
- Columns: 7
- Candidate primary key: `('order_id', 'order_item_id')`
  - PK unique?: True (unique rows: 112650 / total: 112650)

- Top null counts (top 10):
  - order_id: 0
  - order_item_id: 0
  - product_id: 0
  - seller_id: 0
  - shipping_limit_date: 0
  - price: 0
  - freight_value: 0

- dtypes (first 10):
  - order_id: object
  - order_item_id: int64
  - product_id: object
  - seller_id: object
  - shipping_limit_date: object
  - price: float64
  - freight_value: float64

- Sample head (first 5 rows):
```
{'order_id': '00010242fe8c5a6d1ba2dd792cb16214', 'order_item_id': 1, 'product_id': '4244733e06e7ecb4970a6e2683c13e61', 'seller_id': '48436dade18ac8b2bce089ec2a041202', 'shipping_limit_date': '2017-09-19 09:45:35', 'price': 58.9, 'freight_value': 13.29}
{'order_id': '00018f77f2f0320c557190d7a144bdd3', 'order_item_id': 1, 'product_id': 'e5f2d52b802189ee658865ca93d83a8f', 'seller_id': 'dd7ddc04e1b6c2c614352b383efe2d36', 'shipping_limit_date': '2017-05-03 11:05:13', 'price': 239.9, 'freight_value': 19.93}
{'order_id': '000229ec398224ef6ca0657da4fc703e', 'order_item_id': 1, 'product_id': 'c777355d18b72b67abbeef9df44fd0fd', 'seller_id': '5b51032eddd242adc84c38acab88f23d', 'shipping_limit_date': '2018-01-18 14:48:30', 'price': 199.0, 'freight_value': 17.87}
{'order_id': '00024acbcdf0a6daa1e931b038114c75', 'order_item_id': 1, 'product_id': '7634da152a4610f1595efa32f14722fc', 'seller_id': '9d7a1d34a5052409006425275ba1c2b4', 'shipping_limit_date': '2018-08-15 10:10:18', 'price': 12.99, 'freight_value': 12.79}
{'order_id': '00042b26cf59d7ce69dfabb4e55b4fd9', 'order_item_id': 1, 'product_id': 'ac6c3623068f30de03045865e4e10089', 'seller_id': 'df560393f3a51e74553ab94004ba5c87', 'shipping_limit_date': '2017-02-13 13:57:51', 'price': 199.9, 'freight_value': 18.14}
```

### Cleaning Recommendations
- Convert `shipping_limit_date` to datetime.
- Validate that `price` and `freight_value` are non-negative.
- Prepare for revenue aggregation:
  - Revenue per item = price + freight_value
- Ensure composite key (order_id + order_item_id) remains unique.

## products
- Rows: 32951
- Columns: 9
- Candidate primary key: `('product_id',)`
  - PK unique?: True (unique rows: 32951 / total: 32951)

- Top null counts (top 10):
  - product_category_name: 610
  - product_name_lenght: 610
  - product_description_lenght: 610
  - product_photos_qty: 610
  - product_weight_g: 2
  - product_length_cm: 2
  - product_height_cm: 2
  - product_width_cm: 2
  - product_id: 0

- dtypes (first 10):
  - product_id: object
  - product_category_name: object
  - product_name_lenght: float64
  - product_description_lenght: float64
  - product_photos_qty: float64
  - product_weight_g: float64
  - product_length_cm: float64
  - product_height_cm: float64
  - product_width_cm: float64

- Sample head (first 5 rows):
```
{'product_id': '1e9e8ef04dbcff4541ed26657ea517e5', 'product_category_name': 'perfumaria', 'product_name_lenght': 40.0, 'product_description_lenght': 287.0, 'product_photos_qty': 1.0, 'product_weight_g': 225.0, 'product_length_cm': 16.0, 'product_height_cm': 10.0, 'product_width_cm': 14.0}
{'product_id': '3aa071139cb16b67ca9e5dea641aaa2f', 'product_category_name': 'artes', 'product_name_lenght': 44.0, 'product_description_lenght': 276.0, 'product_photos_qty': 1.0, 'product_weight_g': 1000.0, 'product_length_cm': 30.0, 'product_height_cm': 18.0, 'product_width_cm': 20.0}
{'product_id': '96bd76ec8810374ed1b65e291975717f', 'product_category_name': 'esporte_lazer', 'product_name_lenght': 46.0, 'product_description_lenght': 250.0, 'product_photos_qty': 1.0, 'product_weight_g': 154.0, 'product_length_cm': 18.0, 'product_height_cm': 9.0, 'product_width_cm': 15.0}
{'product_id': 'cef67bcfe19066a932b7673e239eb23d', 'product_category_name': 'bebes', 'product_name_lenght': 27.0, 'product_description_lenght': 261.0, 'product_photos_qty': 1.0, 'product_weight_g': 371.0, 'product_length_cm': 26.0, 'product_height_cm': 4.0, 'product_width_cm': 26.0}
{'product_id': '9dc1a7de274444849c219cff195d0b71', 'product_category_name': 'utilidades_domesticas', 'product_name_lenght': 37.0, 'product_description_lenght': 402.0, 'product_photos_qty': 4.0, 'product_weight_g': 625.0, 'product_length_cm': 20.0, 'product_height_cm': 17.0, 'product_width_cm': 13.0}
```

### Cleaning Recommendations
- Replace missing `product_category_name` with "unknown".
- Convert category names to lowercase with underscores.
- Validate numeric columns (weight, length, height, width).
- Handle missing dimension values (2 rows).

## Validation numbers
orders.customer_id missing in customers: 0
order_items.order_id missing in orders: 0
order_items.product_id missing in products: 0
customers duplicate customer_id: 0
orders duplicate order_id: 0
order_items duplicate composite key: 0
order_items price <=0: 0
order_items freight_value < 0: 0
order_purchase_timestamp parse failures (NaT): 0
order_approved_at parse failures (NaT): 160
order_delivered_customer_date parse failures (NaT): 2965
order_delivered_carrier_date parse failures (NaT): 1783
order_estimated_delivery_date parse failures (NaT): 0

## Referential Integrity Checks
- All `orders.customer_id` values exist in `customers.customer_id`.
- All `order_items.order_id` values exist in `orders.order_id`.
- All `order_items.product_id` values exist in `products.product_id`.

(If mismatches are found, they must be documented and investigated.)

## Summary
The dataset structure is well defined with clear primary keys and relationships.

Key observations:
- No duplicate primary keys were found.
- Orders and order_items contain no missing critical keys.
- Products contain missing category information (610 rows).
- Orders contain missing delivery timestamps (2965 rows).

The dataset is suitable for transformation into analytics-ready tables after cleaning and enrichment.

## Logical Data Model (Pre-Transformation)
customers (1) ────< orders (1) ────< order_items >──── (1) products

- One customer can have many orders.
- One order can have many order items.
- One product can appear in many order items.

