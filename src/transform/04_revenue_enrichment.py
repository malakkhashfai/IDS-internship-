from pathlib import Path
import pandas as pd
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ORDERS_PATH = PROCESSED_DIR / "orders_clean.csv"
ORDER_ITEMS_PATH = RAW_DIR / "olist_order_items_dataset.csv"
PRODUCTS_PATH = PROCESSED_DIR / "products_cleaned.csv"
ENRICHED_PATH = PROCESSED_DIR / "enriched_orders.csv"
CATEGORY_INSIGHTS_PATH = PROCESSED_DIR / "category_revenue_insights.csv"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def compute_order_revenue(order_items: pd.DataFrame) -> pd.DataFrame:
    required = {"order_id", "price", "freight_value", "order_item_id"}
    if not required.issubset(order_items.columns):
        missing = required - set(order_items.columns)
        raise KeyError(f"Missing required columns in order_items: {missing}")

    revenue = (
        order_items
        .groupby("order_id", as_index=False)
        .agg(
            order_revenue=("price", "sum"),
            total_freight=("freight_value", "sum"),
            items_count=("order_item_id", "count"),
            average_item_price=("price", "mean"),
        )
    )
    return revenue


def compute_order_product_metrics(order_items_products: pd.DataFrame) -> pd.DataFrame:
    required = {
        "order_id",
        "product_category_name",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    }
    if not required.issubset(order_items_products.columns):
        missing = required - set(order_items_products.columns)
        raise KeyError(f"Missing required columns after join (order_items+products): {missing}")

    df = order_items_products.copy()

    # item volume (cm3)
    df["item_volume_cm3"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]

    metrics = (
        df.groupby("order_id", as_index=False)
        .agg(
            distinct_categories=("product_category_name", "nunique"),
            average_product_weight=("product_weight_g", "mean"),
            total_volume_cm3=("item_volume_cm3", "sum"),
        )
    )
    return metrics


def compute_category_revenue_insights(order_items_products: pd.DataFrame) -> pd.DataFrame:
    required = {"product_category_name", "price", "order_item_id"}
    if not required.issubset(order_items_products.columns):
        missing = required - set(order_items_products.columns)
        raise KeyError(f"Missing required columns for category insights: {missing}")

    category = (
        order_items_products
        .groupby("product_category_name", as_index=False)
        .agg(
            category_revenue=("price", "sum"),
            items_sold=("order_item_id", "count"),
            average_price=("price", "mean"),
        )
        .sort_values("category_revenue", ascending=False)
    )

    total = float(category["category_revenue"].sum()) if len(category) else 0.0
    category["revenue_share_%"] = (category["category_revenue"] / total * 100) if total > 0 else 0.0

    return category


def compute_abnormal_flags(order_items_products: pd.DataFrame) -> pd.DataFrame:
    """
    Detect abnormal product sizes/weights (simple + clear):
      - invalid if weight <= 0 OR any dimension <= 0
      - outlier if weight > 99th percentile OR volume > 99th percentile
    Return order-level flags:
      - abnormal_items_count
      - has_abnormal_item
    """
    df = order_items_products.copy()

    df["item_volume_cm3"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]

    # invalid values
    invalid = (
        (df["product_weight_g"] <= 0)
        | (df["product_length_cm"] <= 0)
        | (df["product_height_cm"] <= 0)
        | (df["product_width_cm"] <= 0)
        | (df["item_volume_cm3"] <= 0)
    )

    # outliers (99th percentile)
    w_p99 = df["product_weight_g"].quantile(0.99)
    v_p99 = df["item_volume_cm3"].quantile(0.99)

    outlier = (df["product_weight_g"] > w_p99) | (df["item_volume_cm3"] > v_p99)

    df["is_abnormal_item"] = invalid | outlier

    abnormal_orders = (
        df.groupby("order_id", as_index=False)
        .agg(
            abnormal_items_count=("is_abnormal_item", "sum"),
        )
    )
    abnormal_orders["has_abnormal_item"] = abnormal_orders["abnormal_items_count"] > 0

    total_abnormal_items = int(df["is_abnormal_item"].sum())
    total_orders_with_abnormal = int(abnormal_orders["has_abnormal_item"].sum())

    logging.info("Abnormal items detected: %d", total_abnormal_items)
    logging.info("Orders with abnormal item(s): %d", total_orders_with_abnormal)

    return abnormal_orders


def main():
    logging.info("Loading orders from: %s", ORDERS_PATH)
    orders = pd.read_csv(ORDERS_PATH, low_memory=False)

    logging.info("Loading order items from: %s", ORDER_ITEMS_PATH)
    order_items = pd.read_csv(ORDER_ITEMS_PATH, low_memory=False)

    logging.info("Loading products from: %s", PRODUCTS_PATH)
    products = pd.read_csv(PRODUCTS_PATH, low_memory=False)


    # Revenue metrics (existing)
    revenue = compute_order_revenue(order_items)
    logging.info("Computed revenue metrics for %d orders", len(revenue))

    # Join order_items + products
    join_required = {"order_id", "product_id", "price", "freight_value", "order_item_id"}
    if not join_required.issubset(order_items.columns):
        missing = join_required - set(order_items.columns)
        raise KeyError(f"Missing required columns in order_items for join: {missing}")

    order_items_products = order_items.merge(
        products,
        on="product_id",
        how="left",
        validate="m:1"
    )

    missing_products = int(order_items_products["product_category_name"].isna().sum())
    logging.info("Order items with missing product match (category null): %d", missing_products)

    # Product metrics per order
    product_metrics = compute_order_product_metrics(order_items_products)
    logging.info("Computed product metrics for %d orders", len(product_metrics))

    # Abnormal flags per order
    abnormal_flags = compute_abnormal_flags(order_items_products)

    # Category insights
    category_insights = compute_category_revenue_insights(order_items_products)
    logging.info("Computed category insights for %d categories", len(category_insights))

    # Merge into enriched orders
    enriched = (
        orders
        .merge(revenue, on="order_id", how="left", validate="1:1")
        .merge(product_metrics, on="order_id", how="left", validate="1:1")
        .merge(abnormal_flags, on="order_id", how="left", validate="1:1")
    )

    # Fill numeric nulls with zeros for orders that had no items (if any)
    for col in [
        "order_revenue", "total_freight", "items_count", "average_item_price",
        "distinct_categories", "average_product_weight", "total_volume_cm3",
        "abnormal_items_count"
    ]:
        if col in enriched.columns:
            enriched[col] = enriched[col].fillna(0)

    if "has_abnormal_item" in enriched.columns:
        enriched["has_abnormal_item"] = (
            enriched["has_abnormal_item"]
            .astype("boolean")   # pandas nullable boolean type
            .fillna(False)
        )

    # Validation checks (existing + basic)
    neg_revenue_count = int((enriched["order_revenue"] < 0).sum())
    zero_revenue_count = int((enriched["order_revenue"] == 0).sum())
    duplicates = int(enriched.duplicated(subset=["order_id"]).sum())

    # Weird values: revenue should be > 0 for orders with items_count > 0
    weird_revenue = int(((enriched["items_count"] > 0) & (enriched["order_revenue"] <= 0)).sum())

    logging.info("Negative revenue orders: %d", neg_revenue_count)
    logging.info("Zero revenue orders: %d", zero_revenue_count)
    logging.info("Weird revenue (items>0 but revenue<=0): %d", weird_revenue)
    logging.info("Duplicate orders (post-merge): %d", duplicates)

    enriched.to_csv(ENRICHED_PATH, index=False)
    logging.info("Saved enriched orders to: %s", ENRICHED_PATH)

    category_insights.to_csv(CATEGORY_INSIGHTS_PATH, index=False)
    logging.info("Saved category insights to: %s", CATEGORY_INSIGHTS_PATH)


if __name__ == "__main__":
    main()