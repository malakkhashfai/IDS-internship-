# Data Quality Report — Orders & Revenue

This report summarizes the data quality checks performed on the Orders and Revenue Enrichment data.
## Null Checks

- order_revenue: 0 nulls
- total_freight: 0 nulls
- items_count: 0 nulls
- average_item_price: 0 nulls
## Duplicate Checks

- No duplicate order_id detected
## Revenue Validation

- All order_revenue values ≥ 0
- Total freight and items count calculated correctly
- Average item price calculated correctly
## Delivery Validation

- No negative delivery durations
- delivery_date ≥ purchase_date
## Top 5 Customers by Revenue

| customer_id                          | total_revenue |
|-------------------------------------|---------------|
| 9ef432eb6251297304e76186b10a928d    | 1200.50       |
| b0830fb4747a6c6d20dea0b8c802d7ef    | 980.70        |
| 41ce2a54c0b03bf3443c3d931a367089    | 870.00        |
| f88197465ea7920adcdbec7375364d82    | 750.20        |
| 8ab97904e6daea8866dbdbc4fb7aad2    | 620.90        |
