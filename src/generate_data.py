"""
Data Generator for Retail Sales Analysis Dashboard
--------------------------------------------------
Generates a realistic synthetic retail sales dataset for a fictional Indian retailer
('Apex Retail India'). The dataset contains multi-item orders, seasonal patterns,
realistic product catalog prices in INR, and intentional real-world data quality anomalies
(whitespace, inconsistent casing, missing values, duplicates) to demonstrate data cleaning.

Reproducible via fixed random seed (default: 42).
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_retail_dataset(
    num_records: int = 1500,
    random_seed: int = 42,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31"
) -> pd.DataFrame:
    """
    Generate synthetic raw retail sales records with realistic noise and attributes.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    # Product catalog with base unit prices in INR (₹)
    catalog = [
        # Electronics
        ("PROD-EL-001", "Wireless Noise-Canceling Headphones", "Electronics", 4999.0),
        ("PROD-EL-002", "Smart Fitness Watch Ultra", "Electronics", 6499.0),
        ("PROD-EL-003", "Bluetooth Soundbar 120W", "Electronics", 7999.0),
        ("PROD-EL-004", "Mechanical Gaming Keyboard", "Electronics", 3499.0),
        ("PROD-EL-005", "Fast-Charge Power Bank 20000mAh", "Electronics", 1899.0),
        # Home & Kitchen
        ("PROD-HK-001", "Stainless Steel Digital Air Fryer", "Home & Kitchen", 5299.0),
        ("PROD-HK-002", "Cold Press Slow Juicer", "Home & Kitchen", 8499.0),
        ("PROD-HK-003", "Tri-Ply Induction Cookware Set", "Home & Kitchen", 4199.0),
        ("PROD-HK-004", "Robotic Vacuum Cleaner", "Home & Kitchen", 14999.0),
        ("PROD-HK-005", "Electric Borosilicate Glass Kettle", "Home & Kitchen", 1599.0),
        # Fashion & Apparel
        ("PROD-FA-001", "Slim-Fit Stretch Cotton Chinos", "Fashion & Apparel", 1799.0),
        ("PROD-FA-002", "Merino Wool Blend Cardigan", "Fashion & Apparel", 2499.0),
        ("PROD-FA-003", "Pro-Cushion Running Sneakers", "Fashion & Apparel", 3999.0),
        ("PROD-FA-004", "Full-Grain Leather Formal Shoes", "Fashion & Apparel", 4499.0),
        ("PROD-FA-005", "Classic Washed Denim Jacket", "Fashion & Apparel", 2899.0),
        # Beauty & Personal Care
        ("PROD-BP-001", "Vitamin C Brightening Face Serum", "Beauty & Personal Care", 799.0),
        ("PROD-BP-002", "Ceramide Barrier Repair Cream", "Beauty & Personal Care", 649.0),
        ("PROD-BP-003", "Sonic Rechargeable Electric Toothbrush", "Beauty & Personal Care", 2199.0),
        ("PROD-BP-004", "Ionic Salon Hair Dryer", "Beauty & Personal Care", 3199.0),
        ("PROD-BP-005", "Pure Cold-Pressed Moroccan Argan Oil", "Beauty & Personal Care", 1199.0),
        # Books & Stationery
        ("PROD-BS-001", "Python & SQL Data Masterclass", "Books & Stationery", 899.0),
        ("PROD-BS-002", "Executive Fountain Pen Gift Set", "Books & Stationery", 1499.0),
        ("PROD-BS-003", "Dot-Grid Hardbound Leather Journal", "Books & Stationery", 599.0),
        ("PROD-BS-004", "Minimalist Aluminum Laptop Stand", "Books & Stationery", 1899.0),
        ("PROD-BS-005", "Desk LED Task Lamp with Wireless Charger", "Books & Stationery", 2299.0),
    ]

    regions = ["North", "South", "East", "West", "Central"]
    region_weights = [0.28, 0.25, 0.16, 0.22, 0.09]  # Realistic sales density in India

    # Convert start and end dates
    dt_start = datetime.strptime(start_date, "%Y-%m-%d")
    dt_end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (dt_end - dt_start).days

    rows = []
    order_counter = 1001

    while len(rows) < num_records:
        # Multi-item orders: 1 to 4 items per order
        items_in_order = random.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05])[0]
        order_id = f"ORD-{order_counter}"
        order_counter += 1

        # Simulate seasonal boost towards Q4 (Oct-Dec festival season)
        day_offset = int(np.random.beta(a=2.0, b=1.8) * total_days)
        order_date = dt_start + timedelta(days=day_offset)
        order_region = random.choices(regions, weights=region_weights)[0]

        # Sample unique products for this order
        chosen_products = random.sample(catalog, min(items_in_order, len(catalog)))

        for prod_id, prod_name, category, unit_price in chosen_products:
            # Quantity purchased (typically 1-3, occasionally up to 5)
            quantity = random.choices([1, 2, 3, 4, 5], weights=[0.60, 0.23, 0.10, 0.05, 0.02])[0]
            sales_amount = round(quantity * unit_price, 2)

            rows.append({
                "Order ID": order_id,
                "Order Date": order_date.strftime("%Y-%m-%d"),
                "Product ID": prod_id,
                "Product Name": prod_name,
                "Category": category,
                "Region": order_region,
                "Quantity": quantity,
                "Unit Price": unit_price,
                "Sales Amount": sales_amount,
            })

    # Slice to exact requested record count
    df = pd.DataFrame(rows[:num_records])

    # -------------------------------------------------------------
    # INTENTIONAL DATA QUALITY ANOMALIES (for real cleaning demonstration)
    # -------------------------------------------------------------
    # 1. Whitespace and mixed case in Region and Category
    noise_indices = df.sample(frac=0.08, random_state=random_seed).index
    for idx in noise_indices:
        variant = random.choice(["upper", "lower", "spaces"])
        val_cat = df.at[idx, "Category"]
        val_reg = df.at[idx, "Region"]
        if variant == "upper":
            df.at[idx, "Category"] = val_cat.upper()
            df.at[idx, "Region"] = val_reg.upper()
        elif variant == "lower":
            df.at[idx, "Category"] = val_cat.lower()
            df.at[idx, "Region"] = val_reg.lower()
        else:
            df.at[idx, "Category"] = f"  {val_cat}  "
            df.at[idx, "Region"] = f" {val_reg} "

    # 2. Missing Sales Amount (requires calculation: Quantity * Unit Price)
    missing_sales_idx = df.sample(n=35, random_state=random_seed + 1).index
    df.loc[missing_sales_idx, "Sales Amount"] = np.nan

    # 3. Discrepant Sales Amount (e.g. typographical error in source recording)
    discrepant_idx = df.sample(n=12, random_state=random_seed + 2).index
    df.loc[discrepant_idx, "Sales Amount"] = df.loc[discrepant_idx, "Sales Amount"] + 150.0

    # 4. Inconsistent Date Formats (some rows with DD/MM/YYYY instead of YYYY-MM-DD)
    date_alt_idx = df.sample(n=40, random_state=random_seed + 3).index
    for idx in date_alt_idx:
        dt_obj = datetime.strptime(df.at[idx, "Order Date"], "%Y-%m-%d")
        df.at[idx, "Order Date"] = dt_obj.strftime("%d/%m/%Y")

    # 5. Exact duplicate rows (simulate double entry submission)
    dup_sample = df.sample(n=5, random_state=random_seed + 4).copy()
    df = pd.concat([df, dup_sample], ignore_index=True)

    # 6. Flagged edge case records (negative quantity, zero price - must be caught and recorded)
    bad_record_1 = df.iloc[10].copy()
    bad_record_1["Order ID"] = "ORD-ERR-001"
    bad_record_1["Quantity"] = -2
    bad_record_1["Sales Amount"] = -2 * bad_record_1["Unit Price"]

    bad_record_2 = df.iloc[25].copy()
    bad_record_2["Order ID"] = "ORD-ERR-002"
    bad_record_2["Unit Price"] = 0.0
    bad_record_2["Sales Amount"] = 0.0

    df = pd.concat([df, pd.DataFrame([bad_record_1, bad_record_2])], ignore_index=True)

    # Shuffle the dataset to ensure anomalies are realistically interspersed
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)

    return df


def save_datasets(df: pd.DataFrame, base_dir: str):
    """
    Save the raw dataset to both CSV and Excel format.
    """
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    csv_path = os.path.join(raw_dir, "retail_sales_raw.csv")
    xlsx_path = os.path.join(raw_dir, "retail_sales_raw.xlsx")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, engine="openpyxl")

    print(f"[SUCCESS] Generated {len(df)} raw records.")
    print(f"  - CSV output:   {csv_path}")
    print(f"  - Excel output: {xlsx_path}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("Generating synthetic retail sales dataset...")
    df_raw = generate_retail_dataset(num_records=1500, random_seed=42)
    save_datasets(df_raw, current_dir)
