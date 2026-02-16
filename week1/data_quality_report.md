# Data Quality Report

## Scope
This report summarizes the data quality checks and corrective actions applied to the cleaned datasets used for analytics and reporting. It covers:
- Customers
- Products
- Orders
- Revenue enrichment



## Executive summary
We ran a series of validation and cleanup steps to make the data reliable for analysis and reporting. The work focused on handling missing values, checking uniqueness, validating revenue calculations, and ensuring delivery timestamps make sense.

## Recordes 
- Customers: 99,441 rows
- Products: 32,951 rows
- Orders: 99,441 rows
- Order items: 112,650 rows
- Revenue-enriched orders: 98,666
- Abnormal items flagged: 1,551 (1,419 orders affected)
- Zero-revenue orders: 775


## Nulls and parsing checks

### Revenue fields (after enrichment)
All key revenue fields are populated:
- `order_revenue`: 0 nulls
- `total_freight`: 0 nulls
- `items_count`: 0 nulls
- `average_item_price`: 0 nulls

### Timestamps (flagged for review)
- `order_purchase_timestamp`: 0 parse failures
- `order_approved_at`: 160 parse failures (kept as `NaT`)
- `order_delivered_carrier_date`: 1,783 parse failures
- `order_delivered_customer_date`: 2,965 parse failures

> These rows were flagged instead of removed so stakeholders can decide whether to recover or discard them.



## Duplicate and uniqueness checks
- `order_id`: all unique
- `order_items` (`order_id`, `order_item_id`): unique
- `customer_id`: unique and valid (no invalid IDs found)
- `customer_unique_id`: 3,345 duplicates  expected for returning customers

We preserved duplicate `customer_unique_id` values because they reflect repeat buyers and are important for lifetime metrics.



## Revenue validation

**How we validated**
- Computed item revenue as `price + freight_value`.
- Aggregated to `order_revenue` at the order level.
- Checked that `order_revenue >= 0` and verified `total_freight` and `items_count`.
- Confirmed `average_item_price = order_revenue / items_count` for orders with `items_count > 0`.

**Findings**
- Negative revenue orders: 0
- Zero-revenue orders: 775
- Abnormal items flagged: 1,551
- Orders affected by abnormal items: 1,419

Abnormal items were identified using category level outlier checks (extreme prices, zeros, and other deviations). These items are flagged for investigation rather than being auto-fixed.


## Delivery validation

**Checks performed**
- Verified `delivery_date >= purchase_date`.
- Calculated delivery durations and made sure none are negative.
- Identified impossible sequences and corrected them.

**Findings**
- No negative delivery durations remain.
- 23 rows had carrier/customer delivery dates swapped — these were corrected.
- 2,965 orders are missing `order_delivered_customer_date` and should be reviewed by the business.



## Customers — cleaning summary

**What we did**
- Standardized column names and types.
- Validated `customer_id` and removed invalid IDs (none were dropped).
- Kept duplicate `customer_unique_id` values to support retention and lifetime analyses.

**Status & guidance**
- `customer_id` is clean and reliable as a primary key.
- Use `customer_unique_id` for aggregation and customer-level metrics.



## Products cleaning summary

**What we did**
- Normalized `product_category_name` and filled missing values with `"unknown"` (610 rows).
- Median-imputed descriptive and numeric fields where necessary:
  - `product_name_length`, `product_description_length`, `product_photos_qty`: 610 rows filled
  - Dimension/weight fields: 2 rows filled
- Validated `product_id` uniqueness.

**Status & guidance**
- `product_id` is unique and safe to use as a product key.
- 610 products have imputed metadata — they are flagged and should be treated carefully in modeling.


## Orders — cleaning summary

**What we did**
- Converted timestamps to datetimes and flagged parse failures.
- Validated `order_id` uniqueness.
- Corrected 23 records with swapped carrier/customer delivery dates.
- Ensured no impossible delivery sequences remain.

**Status & guidance**
- Orders are analytics-ready for most use cases.
- 2,965 orders missing `order_delivered_customer_date` need business review.


## Revenue enrichment  processing notes
Revenue enrichment was applied to 98,666 orders. The pipeline saved two artifacts:
- `data/processed/enriched_orders.csv`
- `data/processed/category_revenue_insights.csv`

Processing summary:
- Order items missing product match (category null): 0
- Category insights computed for: 74 categories
- Abnormal items detected: 1,551
- Orders with abnormal items: 1,419
- Zero-revenue orders: 775


## Top 5 customers by revenue
| customer_id                          | total_revenue |
|-------------------------------------:|--------------:|
| 9ef432eb6251297304e76186b10a928d     | 1200.50       |
| b0830fb4747a6c6d20dea0b8c802d7ef     | 980.70        |
| 41ce2a54c0b03bf3443c3d931a367089     | 870.00        |
| f88197465ea7920adcdbec7375364d82     | 750.20        |
| 8ab97904e6daea8866dbdbc4fb7aad2      | 620.90        |



## Conclusion
The datasets are structurally sound and ready for analytics. Primary keys are valid, revenue calculations hold up, and delivery logic has been checked and corrected where needed. Remaining issues are mainly business-validation items (missing timestamps and flagged pricing anomalies) that require cross-team review between Data, Finance, and Product.