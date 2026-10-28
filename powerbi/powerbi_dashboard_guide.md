# Power BI Implementation Guide: Retail Sales Analysis Dashboard

This comprehensive manual provides end-to-end instructions for assembling the **Retail Sales Analysis Dashboard** in **Microsoft Power BI Desktop**.

---

## 1. System Requirements & Prerequisites

- **Tool:** Microsoft Power BI Desktop (Free download from Microsoft Store or powerbi.microsoft.com)
- **Input Data Files:**
  - Fact Table: [`data/processed/retail_sales_cleaned.csv`](file:///../data/processed/retail_sales_cleaned.csv) (or `.xlsx`)
  - Date Dimension: [`data/processed/dim_date.csv`](file:///../data/processed/dim_date.csv)
- **DAX Formulas:** Reference [`powerbi/dax_measures.md`](file:///./dax_measures.md)

---

## 2. Data Ingestion & Power Query Transformation

### Step 2.1: Ingest Fact Table
1. Open **Power BI Desktop**.
2. On the **Home** ribbon, select **Get Data -> Text/CSV** (or **Excel Workbook**).
3. Browse to `retail-sales-analysis-dashboard/data/processed/retail_sales_cleaned.csv` and click **Transform Data**.

### Step 2.2: Verify Data Types in Power Query Editor
Review and ensure each column has the correct explicit data type:
| Column | Target Type | Power Query Type Icon |
| :--- | :--- | :--- |
| `Order ID` | Text | `ABC` |
| `Order Date` | Date | Calendar Icon |
| `Product ID` | Text | `ABC` |
| `Product Name` | Text | `ABC` |
| `Category` | Text | `ABC` |
| `Region` | Text | `ABC` |
| `Quantity` | Whole Number | `123` |
| `Unit Price` | Fixed Decimal Number / Currency | `$ / Decimal` |
| `Sales Amount` | Fixed Decimal Number / Currency | `$ / Decimal` |

### Step 2.3: Ingest Date Dimension
1. In Power Query, click **New Source -> Text/CSV**.
2. Select `data/processed/dim_date.csv`.
3. Set `Date` column to **Date** type, `Year` and `Month_Number` to **Whole Number**, and strings to **Text**.
4. Click **Close & Apply** on the top-left ribbon.

---

## 3. Data Modeling & Relationship Configuration

1. In Power BI Desktop, click on the **Model View** icon (left-hand sidebar, third icon).
2. Establish the relationship between the Fact table and Date Dimension:
   - Drag `dim_date[Date]` onto `retail_sales_cleaned[Order Date]`.
   - **Cardinality:** `1 to Many (1:*)` (One in `dim_date`, Many in `retail_sales_cleaned`).
   - **Cross Filter Direction:** `Single` (`dim_date` filters `retail_sales_cleaned`).
   - Ensure the checkbox **"Make this relationship active"** is checked.
3. Fix Calendar Chronological Sorting:
   - Switch to **Data View** (second icon on left sidebar).
   - Select the `dim_date` table.
   - Click on the column header `Month_Year` (or `Month_Name`).
   - In the top ribbon, click **Sort by Column** -> choose **`Year_Month_Sort`** (or `Month_Number`).
   - *This ensures charts display `Jan 2024 -> Feb 2024 -> ... -> Dec 2024` rather than alphabetical sorting.*

---

## 4. DAX Measure Creation

Create a dedicated measure table:
1. On the **Home** ribbon, click **Enter Data**.
2. Name table: `_Measures`. Click **Load**.
3. Select `_Measures`, right click and choose **New Measure** to enter the DAX formulas below (detailed explanations in [`dax_measures.md`](file:///./dax_measures.md)):

```dax
Total Sales = SUM ( 'retail_sales_cleaned'[Sales Amount] )
```
*Format: Set to Currency, Symbol: English (India) ₹, Decimal places: 2.*

```dax
Total Orders = DISTINCTCOUNT ( 'retail_sales_cleaned'[Order ID] )
```
*Format: Whole Number, comma separated.*

```dax
Average Order Value = DIVIDE ( [Total Sales], [Total Orders], 0 )
```
*Format: Currency, Symbol: English (India) ₹.*

```dax
Total Quantity = SUM ( 'retail_sales_cleaned'[Quantity] )
```
*Format: Whole Number.*

```dax
Sales PM = CALCULATE ( [Total Sales], PREVIOUSMONTH ( 'dim_date'[Date] ) )
```

```dax
MoM Growth % = DIVIDE ( [Total Sales] - [Sales PM], [Sales PM], BLANK () )
```
*Format: Percentage `0.00%`.*

---

## 5. Dashboard Layout & Visual Construction

Set Canvas size: In **Format Page**, set Canvas Settings to **16:9** (1280 x 720 px or 1920 x 1080 px).

### Visual 1: Executive KPI Cards (Top Banner)
Create 4 **Card (New)** or classic **Card** visuals arranged across the top:
1. **Total Sales:** Field = `[Total Sales]` (Value: ₹9.05M / ₹9,047,972)
2. **Total Orders:** Field = `[Total Orders]` (Value: 906)
3. **Average Order Value:** Field = `[Average Order Value]` (Value: ₹9,986.72)
4. **Total Units Sold:** Field = `[Total Quantity]` (Value: 2,528)
*Styling:* White background, 1px border with slight shadow (`#e2e8f0`), bold dark navy titles (`#1e293b`).

---

### Visual 2: Monthly Sales Trend (Line Chart)
- **Visual Type:** **Line Chart**
- **X-Axis:** `dim_date[Month_Year]`
- **Y-Axis:** `[Total Sales]`
- **Tooltips:** `[Total Orders]`, `[MoM Growth %]`
- **Formatting:** Line color `#0e7490` (Teal), Stroke width `3px`, enable **Data Markers**, enable **Data Labels**.
- **Title:** "Monthly Sales Revenue Trend (INR)"

---

### Visual 3: Top 5 Products by Revenue (Clustered Bar Chart)
- **Visual Type:** **Clustered Bar Chart** (Horizontal)
- **Y-Axis:** `retail_sales_cleaned[Product Name]`
- **X-Axis:** `[Total Sales]`
- **Filter pane configuration:**
  - Select this visual -> Open **Filters Pane** -> Under `Product Name` filter type, choose **Top N**.
  - Show items: **Top 5**.
  - By value: Drag `[Total Sales]` into the field.
  - Click **Apply Filter**.
- **Formatting:** Bar color `#0284c7`, Data Labels = ON, Title: "Top 5 Products by Revenue".

---

### Visual 4: Regional Sales Performance (Donut & Column Chart)
- **Visual Type:** **Donut Chart**
- **Legend:** `retail_sales_cleaned[Region]`
- **Values:** `[Total Sales]`
- **Details:** Data labels showing "Category, percent of total".
- **Title:** "Regional Revenue Distribution (%)"

---

### Visual 5: Category Revenue Breakdown (Column Chart)
- **Visual Type:** **Clustered Column Chart**
- **X-Axis:** `retail_sales_cleaned[Category]`
- **Y-Axis:** `[Total Sales]`
- **Tooltips:** `[Total Quantity]`, `[% of Total Category Sales]`
- **Formatting:** Bar color `#4338ca` (Indigo), Data Labels = ON.
- **Title:** "Sales Revenue by Product Category"

---

### Visual 6: Interactive Slicers Pane (Left or Top Filter Bar)
Add 4 interactive slicer controls:
1. **Date Range Slicer:** Field = `dim_date[Date]` (Style: **Between** slider).
2. **Region Slicer:** Field = `retail_sales_cleaned[Region]` (Style: **Tile** or **Dropdown**).
3. **Category Slicer:** Field = `retail_sales_cleaned[Category]` (Style: **Dropdown** with multiselect).
4. **Product Slicer:** Field = `retail_sales_cleaned[Product Name]` (Style: **Dropdown** with Search enabled).

---

## 6. Testing & Interactive Filter Verification Checklist

Once built, verify cross-filtering interactivity:
- [ ] **Date Slider Test:** Drag the start date to `2024-06-01`. All KPI cards, charts, and product rankings must update dynamically.
- [ ] **Region Filter Test:** Click **"North"** on the Region slicer.
  - KPI Total Sales should update to ~₹2,655,642.
  - Category chart shows category distribution specifically for North region.
- [ ] **Category Filter Test:** Select **"Electronics"**.
  - Top 5 products chart adjusts to show only top electronics items (e.g. Bluetooth Soundbar, Smart Fitness Watch Ultra).
- [ ] **Cross-Chart Highlighting:** Clicking "Home & Kitchen" in the category column chart highlights related portions in the regional donut chart.
- [ ] **Clear Filters:** Verify that resetting slicers restores the grand total revenue to **₹9,047,972.00**.

---

## 7. Publishing & Portfolio Hosting

1. Save the workbook as `retail_sales_dashboard.pbix`.
2. To publish to Power BI Service (Cloud):
   - Click **Home -> Publish -> My Workspace**.
   - Generate a viewable web link or capture high-resolution screenshots for GitHub repository and LinkedIn showcase.
