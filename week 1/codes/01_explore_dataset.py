import os
import pandas as pd

RAW_DIR = "data/raw"
DOCS_DIR = "docs"
SAMPLES_DIR = "docs/samples"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv"
}

def explore_table(name, filename):
    print(f"\nExploring {name}...")

    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)

    print("Shape:", df.shape)
    print("Data types:\n", df.dtypes)
    print("Missing values:\n", df.isnull().sum())
    print("Duplicate rows:", df.duplicated().sum())

    # Primary key check
    if "id" in df.columns[0]:
        print("First column unique?:", df[df.columns[0]].is_unique)

    # Save sample for teammates
    sample_path = os.path.join(SAMPLES_DIR, f"{name}_sample.csv")
    df.head(1000).to_csv(sample_path, index=False)
    print(f"Sample saved to {sample_path}")

    return df

summary_text = "# Data Understanding\n\n"

for name, file in FILES.items():
    df = explore_table(name, file)

    summary_text += f"## {name}\n"
    summary_text += f"- Rows: {df.shape[0]}\n"
    summary_text += f"- Columns: {df.shape[1]}\n"
    summary_text += f"- Duplicate rows: {df.duplicated().sum()}\n\n"

# Save data_understanding.md
with open("docs/data_understanding.md", "w") as f:
    f.write(summary_text)

# Create simple data contract file
with open("docs/data_contract.md", "w") as f:
    f.write("# Data Contract\n\n")
    f.write("Cleaned datasets must be saved in data/processed/\n")
    f.write("- customers_cleaned.parquet\n")
    f.write("- products_cleaned.parquet\n")
    f.write("- orders_cleaned.parquet\n")
    f.write("- orders_enriched.parquet\n")

print("\nDONE ✅ Documentation files created.")
