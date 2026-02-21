# 00_download_dataset.py
import os
from kaggle.api.kaggle_api_extended import KaggleApi

# 1️⃣ Authenticate using your kaggle.json in C:\Users\user\.kaggle\kaggle.json
api = KaggleApi()
api.authenticate()

# 2️⃣ Define dataset and target folder
DATASET = "olistbr/brazilian-ecommerce"  # Kaggle dataset name
TARGET_DIR = os.path.join("data", "raw")

# 3️⃣ Make sure target folder exists
os.makedirs(TARGET_DIR, exist_ok=True)

# 4️⃣ Download and unzip the dataset
print("Downloading dataset...")
api.dataset_download_files(DATASET, path=TARGET_DIR, unzip=True)
print(f"Dataset downloaded and extracted to {TARGET_DIR}")

# 5️⃣ List downloaded files
print("Files in data/raw/:")
for f in os.listdir(TARGET_DIR):
    print("-", f)
