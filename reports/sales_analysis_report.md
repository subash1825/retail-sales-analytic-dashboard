# Business Analysis & Performance Report: Retail Sales Analytics

**Organization:** Apex Retail India (Simulated Case Study)  
**Author:** Senior Data Analyst & BI Developer  
**Currency:** Indian Rupee (INR - ₹)  
**Analysis Period:** January 1, 2024 – December 31, 2024  
**Report Version:** 1.0 (Production Verified)

---

## 1. Executive Summary & Project Objective

The objective of this project is to provide the executive leadership team of a multi-category Indian retailer with actionable commercial intelligence regarding revenue growth, order volume trends, regional distribution, basket dynamics, and product catalog performance.

Through a unified analytical pipeline combining **Python (Pandas, NumPy)**, **SQL (SQLite)**, **Microsoft Excel**, and **Power BI**, this report translates raw operational transaction logs into strategic insights.

### High-Level KPI Summary (Actual Computed Totals)

| Business Metric | Value (INR / Units) | Benchmark & Context |
| :--- | :--- | :--- |
| **Gross Sales Revenue** | **₹9,047,972.00** | Net of data validation reconciliations across 12 calendar months |
| **Total Completed Orders** | **906** | Unique order baskets across 5 territories |
| **Average Order Value (AOV)** | **₹9,986.72** | High basket efficiency driven by multi-item premium appliances |
| **Total Units Moved** | **2,528 units** | Spanning 25 catalog SKUs |
| **Active Catalog SKUs** | **25 Products** | Distributed over 5 major consumer retail categories |
| **Peak Revenue Month** | **May 2024 (₹1,014,454.00)** | Summer home-cooling and appliance surge (105 orders) |
| **Lowest Revenue Month** | **January 2024 (₹422,399.00)** | Post-holiday demand contraction (39 orders) |

> [!NOTE]
> **Data Provenance & Disclaimer:**
> The transaction records utilized in this analysis were programmatically generated to model Indian consumer retail behavior with realistic noise, price points, and seasonal shifts. This report demonstrates senior analytical rigor, data cleansing, SQL modeling, and dashboard construction; conclusions do not represent actual corporate disclosures of an existing legal entity.

---

## 2. Dataset Description & Cleaning Methodology

### 2.1 Ingestion & Baseline Attributes
- **Raw Transaction Rows Ingested:** 1,507 records
- **Valid Analytical Rows:** 1,500 line items (99.54% data retention)
- **Quarantined Records:** 2 records flagged and isolated for auditor review (`ORD-ERR-001` with negative quantity `-2`, and `ORD-ERR-002` with invalid `₹0.00` price).

### 2.2 Data Cleaning Audit Summary
1. **Categorical Normalization:** Corrected 121 whitespace and casing inconsistencies (`" electronics "`, `"ELECTRONICS"` -> `"Electronics"`). Consolidated fragmented variations into 5 standard categories and 5 regions.
2. **Date Standardization:** Standardized mixed date strings (`DD/MM/YYYY` and `YYYY-MM-DD`) into uniform ISO-8601 timestamps (`YYYY-MM-DD`).
3. **Deduplication Logic:** Removed 5 exact duplicate lines (where `Order ID` + `Product ID` were identical). Valid multi-item orders sharing an `Order ID` across different products were strictly preserved.
4. **Revenue Reconciliation:** Imputed 35 missing `Sales Amount` values via formula `Quantity * Unit Price`, and corrected 12 clerical arithmetic recording discrepancies.

Full data cleansing lineage is documented in [`reports/data_quality_report.md`](file:///./reports/data_quality_report.md).

---

## 3. Product Performance Analysis

### 3.1 Top 5 Products by Revenue
High-ticket consumer electronics and premium kitchen appliances dominate top-line turnover:

| Rank | Product ID | Product Name | Category | Units Sold | Total Revenue (INR) | Revenue Share |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | `PROD-HK-004` | **Robotic Vacuum Cleaner** | Home & Kitchen | 105 | **₹1,574,895.00** | **17.41%** |
| 2 | `PROD-EL-003` | **Bluetooth Soundbar 120W** | Electronics | 102 | **₹815,898.00** | **9.02%** |
| 3 | `PROD-EL-002` | **Smart Fitness Watch Ultra** | Electronics | 106 | **₹688,894.00** | **7.61%** |
| 4 | `PROD-HK-002` | **Cold Press Slow Juicer** | Home & Kitchen | 77 | **₹654,423.00** | **7.23%** |
| 5 | `PROD-HK-001` | **Stainless Steel Digital Air Fryer**| Home & Kitchen | 96 | **₹508,704.00** | **5.62%** |

*Key Finding:* The **Robotic Vacuum Cleaner** is the single most valuable SKU, contributing over ₹1.57 Million alone (17.4% of total sales).

### 3.2 Top 5 Products by Unit Volume (Velocity Drivers)
While appliances generate high revenue, everyday home and stationery products act as basket-fillers and drive inventory velocity:

| Rank | Product ID | Product Name | Category | Units Sold | Unit Price (INR) | Total Revenue (INR) |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | `PROD-HK-005` | Electric Borosilicate Glass Kettle | Home & Kitchen | **132** | ₹1,599.00 | ₹211,068.00 |
| 2 | `PROD-BS-004` | Minimalist Aluminum Laptop Stand | Books & Stationery | **128** | ₹1,899.00 | ₹243,072.00 |
| 3 | `PROD-BS-002` | Executive Fountain Pen Gift Set | Books & Stationery | **123** | ₹1,499.00 | ₹184,377.00 |
| 4 | `PROD-BS-001` | Python & SQL Data Masterclass | Books & Stationery | **120** | ₹899.00 | ₹107,880.00 |
| 5 | `PROD-BS-005` | Desk LED Task Lamp with Charger | Books & Stationery | **116** | ₹2,299.00 | ₹266,684.00 |

---

## 4. Monthly Sales Trend & Month-over-Month (MoM) Dynamics

Monthly performance exhibits sharp expansion from Q1 through Q3, peaking in late spring and summer before stabilizing:

| Month | Orders | Units Sold | Revenue (INR) | Monthly AOV (INR) | MoM Growth (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **2024-01** | 39 | 101 | ₹422,399.00 | ₹10,830.74 | *Baseline* |
| **2024-02** | 69 | 193 | ₹666,307.00 | ₹9,656.62 | **+57.74%** |
| **2024-03** | 66 | 186 | ₹751,964.00 | ₹11,393.39 | **+12.86%** |
| **2024-04** | 79 | 221 | ₹906,879.00 | ₹11,479.48 | **+20.60%** |
| **2024-05** | 105 | 296 | **₹1,014,454.00** | ₹9,661.47 | **+11.86%** |
| **2024-06** | 94 | 246 | ₹840,204.00 | ₹8,938.34 | -17.18% |
| **2024-07** | 94 | 231 | ₹850,069.00 | ₹9,043.29 | +1.17% |
| **2024-08** | 102 | 294 | ₹963,556.00 | ₹9,446.63 | **+13.35%** |
| **2024-09** | 95 | 276 | ₹945,874.00 | ₹9,956.57 | -1.84% |
| **2024-10** | 83 | 232 | ₹682,918.00 | ₹8,227.93 | -27.80% |
| **2024-11** | 52 | 143 | ₹533,757.00 | ₹10,264.56 | -21.84% |
| **2024-12** | 38 | 109 | ₹469,591.00 | ₹12,357.66 | -12.02% |

### Key Observations:
- **Peak Period:** May 2024 achieved the highest revenue of **₹1,014,454.00** across 105 distinct transactions.
- **Trough Period:** January 2024 had the lowest sales volume of **₹422,399.00**, indicating a post-holiday demand reset.
- **Basket Quality Shift:** Interestingly, December recorded the lowest order volume (38 orders) but the highest Average Order Value (**₹12,357.66**), indicating fewer buyers purchasing higher-ticket premium gifts.

---

## 5. Regional Sales & Order Distribution

Performance across the 5 geographic territories reveals strong concentration in Tier-1 metropolitan markets:

| Region | Unique Orders | Units Sold | Total Revenue (INR) | Regional AOV (INR) | Revenue Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **North** | 255 | 708 | ₹2,655,642.00 | ₹10,414.28 | **29.35%** |
| **South** | 231 | 668 | ₹2,369,532.00 | ₹10,257.71 | **26.19%** |
| **West** | 200 | 533 | ₹1,852,917.00 | ₹9,264.58 | **20.48%** |
| **East** | 150 | 431 | ₹1,514,919.00 | ₹10,099.46 | **16.74%** |
| **Central** | 70 | 188 | ₹654,962.00 | ₹9,356.60 | **7.24%** |

- **North & South Dominance:** Combined, North (29.35%) and South (26.19%) represent **55.54%** of all corporate revenue.
- **Central Region Opportunity:** Central India accounts for only 7.24% of sales and 70 orders, pointing to underdeveloped fulfillment networks or marketing penetration.

---

## 6. Category Performance & Contribution Analysis

| Category | Orders | Units Sold | Total Revenue (INR) | Category Share (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Home & Kitchen** | 260 | 517 | ₹3,398,383.00 | **37.56%** |
| **Electronics** | 280 | 507 | ₹2,523,793.00 | **27.89%** |
| **Fashion & Apparel** | 265 | 482 | ₹1,517,818.00 | **16.78%** |
| **Books & Stationery** | 284 | 564 | ₹848,136.00 | **9.37%** |
| **Beauty & Personal Care** | 253 | 458 | ₹759,842.00 | **8.40%** |

- **Home & Kitchen + Electronics** together represent **65.45%** of company revenue, acting as primary revenue engines.
- **Books & Stationery** leads in order frequency (284 orders) and unit sales (564 units), functioning as the primary customer acquisition funnel.

---

## 7. Evidence-Based Business Recommendations

1. **Protect Supply Chain for Key Revenue Anchors:**
   The *Robotic Vacuum Cleaner* (`PROD-HK-004`) alone represents 17.41% of total top-line revenue. Any stockouts on this SKU would directly impair monthly performance. Implement safety buffer stocks and multi-vendor supplier agreements for this SKU.

2. **Cross-Sell Stationery Funnel to Electronics & Kitchen:**
   *Books & Stationery* attracts the highest customer transaction frequency (284 orders) with modest basket sizes (₹899 – ₹1,899). Implement automated checkout recommendations (e.g., *"Add a study desk lamp or fast-charge power bank for 10% off"*) to lift AOV.

3. **Regional Expansion Campaign in Central India:**
   Central region trails significantly at 7.24% revenue share. Run targeted digital campaigns and partner with regional logistics carriers to offer lower shipping thresholds in Bhopal, Indore, and Raipur.

4. **Capitalize on Year-End High Basket Values:**
   December exhibited an AOV of ₹12,357.66 despite lower order volume. Create bundled luxury gift hampers during Q4 to maximize holiday gift spending.

---

## 8. Dataset Limitations

1. **Absence of Profit Margins (COGS):** The dataset records gross selling price and sales amount, but does not include Cost of Goods Sold (COGS). Recommendations are based on revenue rather than net operating margin.
2. **Returns and Refunds:** The current schema assumes net fulfilled orders without customer return rate tracking.
3. **Customer Identifiers:** Orders track basket transactions rather than persistent Customer Lifetime IDs, limiting customer retention and cohort churn modeling.
