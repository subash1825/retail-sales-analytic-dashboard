# Excel Analysis & Validation Guide

This guide provides practical instructions for analyzing the retail sales dataset in **Microsoft Excel**, building dynamic PivotTables and PivotCharts, calculating business metrics with Excel formulas, and reconciling the outputs against Python and SQL results.

---

## 1. Input Datasets

- **Cleaned Dataset:** [`data/processed/retail_sales_cleaned.xlsx`](file:///../data/processed/retail_sales_cleaned.xlsx) (1,500 validated rows)
- **Raw Inspection Dataset:** [`data/raw/retail_sales_raw.xlsx`](file:///../data/raw/retail_sales_raw.xlsx)

---

## 2. Inspecting Raw Data & Applying Filters

1. Open `data/raw/retail_sales_raw.xlsx`.
2. Convert the data range to an official Excel Table by pressing **`Ctrl + T`** (Ensure *"My table has headers"* is checked). Name the table `RawSalesTable`.
3. In the header row, notice the filter dropdowns:
   - Click the filter on **`Category`**: Observe inconsistent casings and spaces (`ELECTRONICS`, `  electronics  `, `Electronics`).
   - Click the filter on **`Quantity`**: Filter for `< 0` to identify quarantined entries like `ORD-ERR-001`.
   - Click the filter on **`Unit Price`**: Filter for `0` to identify zero-price error transactions like `ORD-ERR-002`.
   - Click the filter on **`Sales Amount`**: Notice `(Blanks)` where values were missing.
4. Formula for Sales Amount Imputation in Excel:
   ```excel
   =IF(ISBLANK([@[Sales Amount]]), [@[Quantity]] * [@[Unit Price]], [@[Sales Amount]])
   ```

---

## 3. Core Metric Formulas in Excel

Open `data/processed/retail_sales_cleaned.xlsx`. You can verify key KPIs directly using standard Excel formulas:

| Metric | Target Cell | Excel Formula | Expected Output |
| :--- | :--- | :--- | :--- |
| **Total Revenue** | `K2` | `=SUM(I2:I1501)` | **₹9,047,972.00** |
| **Total Quantity Sold** | `K3` | `=SUM(G2:G1501)` | **2,528** |
| **Unique Orders** | `K4` | `=COUNTA(UNIQUE(A2:A1501))` | **906** |
| **Average Order Value (AOV)** | `K5` | `=K2 / K4` | **₹9,986.72** |
| **Unique Products Count** | `K6` | `=COUNTA(UNIQUE(C2:C1501))` | **25** |

*(Where Column A is Order ID, Column C is Product ID, Column G is Quantity, Column H is Unit Price, Column I is Sales Amount).*

---

## 4. Building Dynamic PivotTables

### PivotTable 1: Monthly Sales Trend & MoM Growth
1. Select any cell inside the cleaned table.
2. Go to **Insert -> PivotTable -> New Worksheet**. Name the worksheet `Monthly_Analysis`.
3. Setup Fields:
   - **Rows:** Drag `Order Date` (Excel will automatically group by Year and Month).
   - **Values:** 
     1. Drag `Sales Amount` -> Summarize by **Sum**. Format as Currency (`₹ #,##0.00`).
     2. Drag `Sales Amount` again -> Right click -> **Show Values As -> % Difference From...** -> Base field: `Order Date` (Month), Base item: `(previous)`. This gives the exact **Month-over-Month (MoM) Growth %**.
     3. Drag `Order ID` -> Summarize by **Distinct Count**.

---

### PivotTable 2: Regional Performance & Revenue Share
1. Insert a new PivotTable on a sheet called `Regional_Analysis`.
2. Setup Fields:
   - **Rows:** `Region`
   - **Values:**
     1. `Sales Amount` (Sum) -> Renamed to "Revenue (INR)".
     2. `Sales Amount` -> Show Values As -> **% of Grand Total**.
     3. `Order ID` (Distinct Count) -> Renamed to "Total Orders".
     4. `Quantity` (Sum) -> Renamed to "Units Sold".
3. Add a **Calculated Field** for Regional AOV:
   - PivotTable Analyze -> Fields, Items & Sets -> **Calculated Field**.
   - Formula: `='Sales Amount' / 'Quantity'` (or order level).

---

### PivotTable 3: Category Breakdown
1. Insert PivotTable on a sheet called `Category_Analysis`.
2. Setup Fields:
   - **Rows:** `Category`
   - **Values:**
     - Sum of `Sales Amount`
     - % of Grand Total
     - Sum of `Quantity`
3. Sort descending by Sum of `Sales Amount`.
4. Insert a **2D Clustered Column Chart** linked to this PivotTable for a clean dashboard tile.

---

### PivotTable 4: Top 5 Products by Revenue
1. Insert PivotTable on a sheet called `Product_Rankings`.
2. Setup Fields:
   - **Rows:** `Product Name`
   - **Values:** Sum of `Sales Amount`, Sum of `Quantity`.
3. Filter for Top 5:
   - Click the row labels filter dropdown -> **Value Filters -> Top 10...**
   - Change `10` to **`5`** -> by **Sum of Sales Amount**.
4. Result:
   1. *Robotic Vacuum Cleaner* (~₹1,574,895.00)
   2. *Bluetooth Soundbar 120W* (~₹815,898.00)
   3. *Smart Fitness Watch Ultra* (~₹688,894.00)
   4. *Cold Press Slow Juicer* (~₹654,423.00)
   5. *Stainless Steel Digital Air Fryer* (~₹508,704.00)

---

## 5. Reconciliation: Excel vs Python vs SQL

To ensure zero human or methodological error, compare your Excel PivotTable totals with Python and SQL:

| Dimension / Metric | Python Calculation | SQLite Query | Excel PivotTable | Variance | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Total Revenue** | ₹9,047,972.00 | ₹9,047,972.00 | ₹9,047,972.00 | ₹0.00 | **MATCH** |
| **Unique Orders** | 906 | 906 | 906 | 0 | **MATCH** |
| **Average Order Value** | ₹9,986.72 | ₹9,986.72 | ₹9,986.72 | ₹0.00 | **MATCH** |
| **Total Units Sold** | 2,528 | 2,528 | 2,528 | 0 | **MATCH** |
| **Peak Month (2024-05)** | ₹1,014,454.00 | ₹1,014,454.00 | ₹1,014,454.00 | ₹0.00 | **MATCH** |
| **Lowest Month (2024-01)**| ₹422,399.00 | ₹422,399.00 | ₹422,399.00 | ₹0.00 | **MATCH** |
| **Top Category Share (Home & Kitchen)** | 37.56% | 37.56% | 37.56% | 0.00% | **MATCH** |

This exact alignment demonstrates rigorous analytical validation across all business tools.
