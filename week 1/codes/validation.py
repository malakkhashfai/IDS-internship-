import pandas as pd

raw = "data/raw"
customers = pd.read_csv(f"{raw}/olist_customers_dataset.csv")
orders = pd.read_csv(f"{raw}/olist_orders_dataset.csv")
order_items = pd.read_csv(f"{raw}/olist_order_items_dataset.csv")
products = pd.read_csv(f"{raw}/olist_products_dataset.csv")

# 1) Referential integrity counts
missing_orders_customers = orders[~orders['customer_id'].isin(customers['customer_id'])].shape[0]
missing_items_orders = order_items[~order_items['order_id'].isin(orders['order_id'])].shape[0]
missing_items_products = order_items[~order_items['product_id'].isin(products['product_id'])].shape[0]

print("orders.customer_id missing in customers:", missing_orders_customers)
print("order_items.order_id missing in orders:", missing_items_orders)
print("order_items.product_id missing in products:", missing_items_products)

# 2) Duplicate checks
print("customers duplicate customer_id:", customers['customer_id'].duplicated().sum())
print("orders duplicate order_id:", orders['order_id'].duplicated().sum())
print("order_items duplicate composite key:", order_items.duplicated(subset=['order_id','order_item_id']).sum())

# 3) Negative price/freight
print("order_items price <=0:", (order_items['price'] <= 0).sum())
print("order_items freight_value < 0:", (order_items['freight_value'] < 0).sum())

# 4) Date parsing failures example (orders)
for col in ['order_purchase_timestamp','order_approved_at','order_delivered_customer_date','order_delivered_carrier_date','order_estimated_delivery_date']:
    parsed = pd.to_datetime(orders[col], errors='coerce')
    failures = parsed.isna().sum()
    print(f"{col} parse failures (NaT):", failures)
