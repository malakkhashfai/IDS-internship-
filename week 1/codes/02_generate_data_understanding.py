# src/ingest/02_generate_data_understanding.py
import os
import pandas as pd

RAW_DIR = "data/raw"
OUT_MD = "docs/data_understanding.md"
FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv"
}

os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)

def load_df(fname):
    path = os.path.join(RAW_DIR, fname)
    return pd.read_csv(path, low_memory=False)

def pk_check(df, key_cols):
    # returns (is_unique, unique_count, total_count)
    if isinstance(key_cols, (list, tuple)):
        unique_count = df.drop_duplicates(subset=key_cols).shape[0]
    else:
        unique_count = df[key_cols].nunique()
    total = df.shape[0]
    is_unique = unique_count == total
    return is_unique, unique_count, total

def basic_summary(df):
    return {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "dtypes": df.dtypes.astype(str).to_dict(),
        "nulls": df.isnull().sum().to_dict(),
        "sample_head": df.head(5).to_dict(orient="records")
    }

summary = {}

for name, fname in FILES.items():
    try:
        df = load_df(fname)
    except FileNotFoundError:
        print(f"Missing {fname} in {RAW_DIR}, skipping.")
        summary[name] = {"error": "file not found"}
        continue

    s = basic_summary(df)

    # candidate PKs
    if name == "customers":
        s["pk"] = ("customer_id",)  # candidate
        s["pk_check"] = pk_check(df, "customer_id")
    elif name == "orders":
        s["pk"] = ("order_id",)
        s["pk_check"] = pk_check(df, "order_id")
    elif name == "order_items":
        s["pk"] = ("order_id", "order_item_id")
        s["pk_check"] = pk_check(df, ["order_id", "order_item_id"])
    elif name == "products":
        s["pk"] = ("product_id",)
        s["pk_check"] = pk_check(df, "product_id")

    summary[name] = s

# --- Write markdown file (skeleton + auto findings)
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# Data Understanding\n\n")
    f.write("Auto-generated summary. Please review and add manual notes below each section.\n\n")

    # Short dataset overview
    f.write("## Dataset overview\n\n")
    f.write("- Source: Olist Brazilian E-Commerce (CSV files in `data/raw/`)\n")
    f.write("- Files explored: customers, orders, order_items, products\n\n")

    # Per-table sections
    for t, s in summary.items():
        f.write(f"## {t}\n\n")
        if "error" in s:
            f.write(f"- **Error**: {s['error']}\n\n")
            continue
        f.write(f"- Rows: {s['rows']}\n")
        f.write(f"- Columns: {s['cols']}\n")
        f.write(f"- Candidate primary key: `{s['pk']}`\n")
        is_unique, unique_count, total = s["pk_check"]
        f.write(f"  - PK unique?: {is_unique} (unique rows: {unique_count} / total: {total})\n")
        # top nulls
        nulls = sorted(s["nulls"].items(), key=lambda x: x[1], reverse=True)[:10]
        f.write("\n- Top null counts (top 10):\n")
        for col, n in nulls:
            f.write(f"  - {col}: {n}\n")
        f.write("\n- dtypes (first 10):\n")
        for col, dt in list(s["dtypes"].items())[:10]:
            f.write(f"  - {col}: {dt}\n")
        f.write("\n- Sample head (first 5 rows):\n")
        f.write("```\n")
        for row in s["sample_head"]:
            f.write(str(row) + "\n")
        f.write("```\n\n")

    # Relationships (manual templated - check these)
    f.write("## Relationships (candidate)\n\n")
    f.write("- `orders.customer_id` → `customers.customer_id`\n")
    f.write("- `order_items.order_id` → `orders.order_id`\n")
    f.write("- `order_items.product_id` → `products.product_id`\n\n")

    # Initial data issues (auto-found hints)
    f.write("## Initial data issues (auto-detected hints)\n\n")
    f.write("- Check columns with many nulls (see top null counts above).\n")
    f.write("- Check dtype mismatches (e.g., numeric stored as object).\n")
    f.write("- Check duplicate keys if PK unique check is False.\n\n")

print("Wrote", OUT_MD)
