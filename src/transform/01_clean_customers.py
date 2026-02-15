"""
Customers Cleaning Script - Olist Dataset

Responsibilities:
- Clean column names
- Fix data types
- Handle missing values safely
- Validate ID columns
- Check duplicates
- Save cleaned dataset
- Print clear summaries

"""

import os
import pandas as pd

RAW_PATH = "data/raw/olist_customers_dataset.csv"
OUTPUT_PATH = "data/processed/customers_cleaned.csv"

# Load Data
def load_data(path=RAW_PATH):
    print("📥 Loading customers dataset...")
    df = pd.read_csv(path)
    print(f"Rows loaded: {len(df):,}")
    print("Columns:", df.columns.tolist())
    return df


# Clean Column Names
def clean_columns(df):
    print("\n Cleaning column names...")
    df = df.copy()
    df.columns = df.columns.str.strip()
    return df


# Fix Data Types & Normalize Text
def fix_types(df):
    print("\n Fixing data types...")
    df = df.copy()

    # Convert IDs and text columns to pandas StringDtype
    for col in ["customer_id", "customer_unique_id", "customer_city", "customer_state"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    # Convert zip prefix to numeric (nullable)
    if "customer_zip_code_prefix" in df.columns:
        df["customer_zip_code_prefix"] = pd.to_numeric(
            df["customer_zip_code_prefix"], errors="coerce"
        ).astype("Int64")

    # Normalize city
    if "customer_city" in df.columns:
        df["customer_city"] = (
            df["customer_city"]
            .str.lower()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Normalize state
    if "customer_state" in df.columns:
        df["customer_state"] = df["customer_state"].str.upper().str.strip()

    return df


# Validate ID Columns (IMPORTANT)
def validate_ids(df):
    print("\n Validating ID columns...")
    df = df.copy()

    before = len(df)

    for col in ["customer_id", "customer_unique_id"]:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                print(f"⚠️ {null_count:,} null values found in {col}. Dropping these rows.")
                df = df[df[col].notna()]

    after = len(df)
    print(f"Rows after ID validation: {after:,} (dropped {before-after:,})")
    return df


# Check & Remove Duplicates
def check_duplicates(df):
    print("\n Checking duplicates...")
    df = df.copy()

    dup_id = df.duplicated(subset=["customer_id"]).sum()
    dup_unique = df.duplicated(subset=["customer_unique_id"]).sum()
    dup_pair = df.duplicated(
        subset=["customer_id", "customer_unique_id"]
    ).sum()
    exact_dups = df.duplicated().sum()

    print(f"Duplicate customer_id: {dup_id}")
    print(f"Duplicate customer_unique_id: {dup_unique}")
    print(f"Duplicate pair (customer_id, customer_unique_id): {dup_pair}")
    print(f"Exact duplicate rows: {exact_dups}")

    before = len(df)

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Remove duplicates by customer_id (primary key)
    df = df.drop_duplicates(subset=["customer_id"], keep="first")

    after = len(df)
    print(f"Rows after deduplication: {after:,} (dropped {before-after:,})")

    return df


# Handle Missing Values (Non-key columns only)
def handle_missing(df):
    print("\n Handling missing values...")
    df = df.copy()

    missing = df.isna().sum()
    missing_nonzero = {k: int(v) for k, v in missing.items() if v > 0}
    print("Missing values (nonzero only):", missing_nonzero if missing_nonzero else "{}")

    # Fill only city/state (NOT IDs)
    for col in ["customer_city", "customer_state"]:
        if col in df.columns:
            df[col] = df[col].fillna("unknown")

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
    df = fix_types(df)
    df = validate_ids(df)       # validate first
    df = check_duplicates(df)
    df = handle_missing(df)

    print(f"\nRows AFTER cleaning: {len(df):,}")

    save_data(df)
    print("\n✅ Customers cleaning completed successfully!")


if __name__ == "__main__":
    main()
