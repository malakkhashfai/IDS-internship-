from pathlib import Path
import pandas as pd
import logging
from typing import Tuple, Set

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

ORDERS_RAW = RAW_DIR / "olist_orders_dataset.csv"
ORDERS_CLEAN_PATH = PROCESSED_DIR / "orders_clean.csv"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def to_datetime_cols(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)
    return df


def validate_order_status(df: pd.DataFrame) -> Tuple[pd.Series, Set[str]]:
    allowed = {
        "created", "approved", "invoiced", "processing", "shipped", "delivered",
        "canceled", "unavailable"
    }
    counts = df["order_status"].value_counts(dropna=False)
    logging.info("Order status counts:\n%s", counts.to_string())
    unknown = set(df["order_status"].dropna().unique()) - allowed
    if unknown:
        logging.warning("Unknown order_status values found: %s", unknown)
    else:
        logging.info("All order_status values are known.")
    return counts, unknown


def drop_impossible_deliveries(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    if {"order_delivered_customer_date", "order_purchase_timestamp"}.issubset(df.columns):
        mask = (
            df["order_delivered_customer_date"].notna()
            & df["order_purchase_timestamp"].notna()
            & (df["order_delivered_customer_date"] < df["order_purchase_timestamp"])
        )
        n = int(mask.sum())
        logging.info("Impossible deliveries (delivered_customer_date < purchase): %d", n)
        return df.loc[~mask].copy(), n
    return df, 0


def flag_carrier_after_customer(df: pd.DataFrame) -> int:
    if {"order_delivered_carrier_date", "order_delivered_customer_date"}.issubset(df.columns):
        mask = (
            df["order_delivered_carrier_date"].notna()
            & df["order_delivered_customer_date"].notna()
            & (df["order_delivered_carrier_date"] > df["order_delivered_customer_date"])
        )
        n = int(mask.sum())
        logging.warning("Rows where carrier delivery is AFTER customer delivery: %d", n)
        return n
    return 0


def compute_delivery_days(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:
    if {"order_delivered_customer_date", "order_purchase_timestamp"}.issubset(df.columns):
        df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
        neg = int((df["delivery_days"] < 0).sum())
        very_long = int((df["delivery_days"] > 365).sum())
        logging.info("Negative delivery_days: %d; delivery_days > 365: %d", neg, very_long)
        return df, neg, very_long
    df["delivery_days"] = pd.NA
    return df, 0, 0


def main():
    logging.info("Loading orders: %s", ORDERS_RAW)
    orders = pd.read_csv(ORDERS_RAW, low_memory=False)
    logging.info("Initial orders shape: %s", orders.shape)

    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    orders = to_datetime_cols(orders, date_cols)

    status_counts, unknown_status = validate_order_status(orders)

    orders, dropped = drop_impossible_deliveries(orders)
    logging.info("Shape after dropping impossible deliveries: %s", orders.shape)

    carrier_after = flag_carrier_after_customer(orders)

    orders, neg_days, long_days = compute_delivery_days(orders)

    dup_orders = int(orders.duplicated(subset=["order_id"]).sum())
    if dup_orders:
        logging.warning("Duplicate order_id rows in orders table: %d", dup_orders)
        # Optionally remove duplicates keeping the first occurrence:
        orders = orders.drop_duplicates(subset=["order_id"], keep="first")

    orders.to_csv(ORDERS_CLEAN_PATH, index=False)
    logging.info("Saved cleaned orders to: %s", ORDERS_CLEAN_PATH)

    # Summary
    logging.info("----- SUMMARY -----")
    logging.info("Rows processed: %d", len(orders) + dropped)
    logging.info("Rows kept: %d", len(orders))
    logging.info("Rows dropped (impossible deliveries): %d", dropped)
    logging.info("Carrier after customer count: %d", carrier_after)
    logging.info("Negative delivery_days: %d", neg_days)
    logging.info("Very long delivery_days (>365): %d", long_days)
    logging.info("Duplicate order_id (remaining): %d", int(orders.duplicated(subset=['order_id']).sum()))


if __name__ == "__main__":
    main()
