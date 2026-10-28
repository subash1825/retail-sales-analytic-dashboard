# Dataset Metadata & Provenance Guide

## 1. Primary Dataset Overview (Synthetic Benchmark)

- **Dataset Name:** Apex Retail India Sales Dataset (Synthetic Benchmark)
- **Currency:** Indian Rupee (INR - ₹)
- **Timeframe:** January 1, 2024 to December 31, 2024 (12 Full Calendar Months)
- **Number of Raw Records:** 1,507 sales transactions (multi-item orders)
- **Generator Script:** [`src/generate_data.py`](file:///./src/generate_data.py)
- **Random Seed:** `42` (ensures 100% deterministic reproducibility)

> [!IMPORTANT]
> **Synthetic Data Disclaimer:**
> This dataset was programmatically generated to simulate realistic e-commerce and retail transactions within the Indian market. It reflects multi-item orders, seasonal Q4 festival spikes, category pricing, and real-world data quality anomalies. It does **not** represent actual proprietary transactions of any real-world company.

---

## 2. Schema Specification

The dataset adheres to the following structural schema:

| Column Name | Data Type | Nullable | Example Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Order ID` | String | No | `ORD-1042` | Unique transaction order identifier. Multi-item orders share the same Order ID. |
| `Order Date` | String (Raw) / Date | No | `2024-03-15` or `15/03/2024` | Transaction timestamp. Raw data contains mixed format strings. |
| `Product ID` | String | No | `PROD-EL-001` | Unique Stock Keeping Unit (SKU) identifier. |
| `Product Name` | String | No | `Wireless Noise-Canceling Headphones` | Product description. |
| `Category` | String | No | `Electronics` | Merchandising department (5 total categories). |
| `Region` | String | No | `North` | Operational sales territory (North, South, East, West, Central). |
| `Quantity` | Integer | No | `2` | Number of units purchased in the order line item. |
| `Unit Price` | Float | No | `4999.00` | Selling price per single unit in INR (₹). |
| `Sales Amount` | Float | Yes (Raw) | `9998.00` | Gross revenue for the line item (`Quantity * Unit Price`). |

---

## 3. Product Catalog & Categories

The simulated retailer offers 25 distinct SKUs across 5 core categories:

1. **Electronics (5 SKUs):** Headphones, Smart Watches, Soundbars, Gaming Keyboards, Power Banks (₹1,899 – ₹7,999)
2. **Home & Kitchen (5 SKUs):** Air Fryers, Slow Juicers, Induction Cookware Sets, Robotic Vacuums, Electric Kettles (₹1,599 – ₹14,999)
3. **Fashion & Apparel (5 SKUs):** Stretch Chinos, Cardigans, Running Sneakers, Leather Formal Shoes, Denim Jackets (₹1,799 – ₹4,499)
4. **Beauty & Personal Care (5 SKUs):** Vitamin C Serums, Barrier Creams, Electric Toothbrushes, Hair Dryers, Argan Oils (₹649 – ₹3,199)
5. **Books & Stationery (5 SKUs):** Data Masterclass Books, Fountain Pen Sets, Bullet Journals, Laptop Stands, LED Task Lamps (₹599 – ₹2,299)

---

## 4. Public Dataset Alternative / Plug-and-Play Compatibility

If an evaluator or employer requires running this solution against external public datasets, the cleaning pipeline and analysis modules are designed to accept standard e-commerce schemas.

### Recommended Public Datasets:

1. **Sample Superstore Dataset (Tableau / Kaggle)**
   - **Source:** [Kaggle Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
   - **License:** CC0: Public Domain
   - **Download:** Download `Sample - Superstore.xls` or `.csv`.
   - **Field Mapping:** Map `Order ID` -> `Order ID`, `Order Date` -> `Order Date`, `Category` -> `Category`, `Region` -> `Region`, `Sales` -> `Sales Amount`.

2. **Online Retail II UCI Machine Learning Repository**
   - **Source:** [UCI Machine Learning Repository - Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
   - **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
   - **Description:** Real e-commerce transactions for a UK-based registered gift-ware retailer between 2009 and 2011.
   - **Download Steps:** Download `online_retail_II.xlsx` from UCI, place in `data/raw/`.
