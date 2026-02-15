"""
Products Cleaning Script - Olist Dataset

Responsibilities:
- Clean column names
- Clean product categories
- Handle missing values safely
- Check duplicates (product_id)
- Validate numeric columns (weight, length, height, width, etc.)
- Save cleaned output to data/processed/products_cleaned.parquet
  (fallback to CSV if parquet engine is missing)
- Print simple summaries (rows before/after, issues found)

"""

import os
import pandas as pd

RAW_PATH = "data/raw/olist_products_dataset.csv"
OUTPUT_PATH = "data/processed/products_cleaned.csv"


# Load Data
def load_data(path=RAW_PATH):
    print("📥 Loading products dataset...")
    df = pd.read_csv(path)
    print(f"Rows loaded: {len(df):,}")
    print("Columns:", df.columns.tolist())
    return df


# Clean Column Names + Fix Known Typos
def clean_columns(df):
    print("\n Cleaning column names...")
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Fix common misspellings in Olist dataset (if present)
    rename_map = {
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    return df


# Category Cleaning
def clean_category(df):
    print("\n Cleaning product_category_name...")
    df = df.copy()

    if "product_category_name" in df.columns:
        s = df["product_category_name"].astype("string").str.strip().str.lower()

        # Normalize: spaces/hyphens -> underscore, remove weird chars, collapse underscores
        s = s.str.replace(r"[\s\-]+", "_", regex=True)
        s = s.str.replace(r"[^a-z0-9_]+", "", regex=True)
        s = s.str.replace(r"_+", "_", regex=True).str.strip("_")

        df["product_category_name"] = s.fillna("unknown")
        df.loc[df["product_category_name"].eq(""), "product_category_name"] = "unknown"

    return df


# Fix Types + Numeric Validation
def fix_types_and_validate_numeric(df):
    print("\n Fixing data types + validating numeric columns...")
    df = df.copy()

    # product_id as string
    if "product_id" in df.columns:
        df["product_id"] = df["product_id"].astype("string").str.strip()

    numeric_cols = [
        "product_name_length",
        "product_description_length",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    present_numeric = [c for c in numeric_cols if c in df.columns]

    # Convert to numeric
    for c in present_numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Missing summary BEFORE fill
    missing_before = df.isna().sum()
    missing_nonzero = {k: int(v) for k, v in missing_before.items() if int(v) > 0}
    print("Missing values BEFORE fill (nonzero only):", missing_nonzero if missing_nonzero else "{}")

    # Fill numeric missing with median (simple & stable)
    fill_values = {}
    for c in present_numeric:
        med = df[c].median(skipna=True)
        if pd.isna(med):
            med = 0.0
        fill_values[c] = float(med)
        df[c] = df[c].fillna(med)

    print("Fill values used (median):", fill_values)

    # Clip negatives to 0 (weight/dimensions shouldn't be negative)
    issues = []
    for c in present_numeric:
        neg = int((df[c] < 0).sum())
        if neg > 0:
            issues.append(f"{c}: {neg} negative values clipped to 0")
            df.loc[df[c] < 0, c] = 0

    # photos qty should be integer-like (nullable int)
    if "product_photos_qty" in df.columns:
        df["product_photos_qty"] = df["product_photos_qty"].round().astype("Int64")

    if issues:
        print("⚠️ Issues found:", issues)

    return df


# Validate product_id (no missing IDs)
def validate_product_id(df):
    print("\n Validating product_id...")
    df = df.copy()

    if "product_id" not in df.columns:
        print("⚠️ WARNING: product_id column not found!")
        return df

    before = len(df)
    null_count = int(df["product_id"].isna().sum())

    if null_count > 0:
        print(f"⚠️ {null_count:,} null product_id found. Dropping these rows.")
        df = df[df["product_id"].notna()]

    after = len(df)
    print(f"Rows after product_id validation: {after:,} (dropped {before-after:,})")
    return df


# Check & Remove Duplicates
def check_duplicates(df):
    print("\n Checking duplicates...")
    df = df.copy()

    exact_dups = int(df.duplicated().sum())
    dup_product_id = int(df.duplicated(subset=["product_id"]).sum()) if "product_id" in df.columns else 0

    print(f"Duplicate product_id: {dup_product_id}")
    print(f"Exact duplicate rows: {exact_dups}")

    before = len(df)

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Remove duplicates by product_id (primary key)
    if "product_id" in df.columns:
        df = df.drop_duplicates(subset=["product_id"], keep="first")

    after = len(df)
    print(f"Rows after deduplication: {after:,} (dropped {before-after:,})")
    return df


# Save Output
def save_data(df):
    print("\n Saving cleaned dataset...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False)
    print("✅ Saved as CSV successfully!")

# Main Pipeline
def main():
    df = load_data()
    print(f"\nRows BEFORE cleaning: {len(df):,}")

    df = clean_columns(df)
    df = clean_category(df)
    df = fix_types_and_validate_numeric(df)

    df = validate_product_id(df)   # validate before dedup
    df = check_duplicates(df)

    # final quick missing check
    missing_after = {k: int(v) for k, v in df.isna().sum().items() if int(v) > 0}
    print("\nMissing values AFTER cleaning (nonzero only):", missing_after if missing_after else "{}")

    print(f"\nRows AFTER cleaning: {len(df):,}")
    save_data(df)

    print("\n✅ Products cleaning completed successfully!")


if __name__ == "__main__":
    main()
