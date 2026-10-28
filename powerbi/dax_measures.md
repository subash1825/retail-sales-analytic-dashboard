# Power BI DAX Measures & Data Model Reference

This reference catalog provides production-ready Data Analysis Expressions (DAX) measures developed for the **Retail Sales Analysis Dashboard** in Power BI Desktop.

---

## 1. Table Architecture & Measure Organization

Best practice in Power BI is to create a dedicated empty table to house all business measures (often called `_Measures` or `Key Metrics`).

### Step to create the `_Measures` table:
1. In Power BI Desktop, click **Enter Data** in the Home ribbon.
2. Name the table `_Measures` and column `Column1`. Click **Load**.
3. Create your measures inside this table.
4. Once your first measure is created, right-click `Column1` and select **Hide** or **Delete**. Power BI will give `_Measures` a calculator icon at the top of your Fields pane.

---

## 2. Core Business Measures (DAX)

### Measure 1: Total Sales Revenue (`[Total Sales]`)
Calculates the aggregate gross revenue across all sales transactions.
```dax
Total Sales = 
SUM ( 'retail_sales'[Sales Amount] )
```
- **Data Type:** Currency
- **Format String:** `₹ #,##0.00` (or English - India `₹`)
- **Visuals:** KPI Card, Line Chart Y-axis, Bar Chart values

---

### Measure 2: Distinct Order Count (`[Total Orders]`)
Calculates the unique number of customer transactions.
```dax
Total Orders = 
DISTINCTCOUNT ( 'retail_sales'[Order ID] )
```
- **Data Type:** Whole Number
- **Format String:** `#,##0`
- **Visuals:** KPI Card, Tooltips, Regional Order comparisons
- *Note:* Do not use `COUNTROWS` because multiple line items can share the same Order ID in multi-product shopping carts.

---

### Measure 3: Average Order Value (`[Average Order Value]`)
Calculates the average revenue generated per unique customer order. Uses `DIVIDE` to safely handle division by zero.
```dax
Average Order Value = 
DIVIDE (
    [Total Sales],
    [Total Orders],
    0
)
```
- **Data Type:** Currency
- **Format String:** `₹ #,##0.00`
- **Visuals:** KPI Card, Regional drill-down tables

---

### Measure 4: Total Units Sold (`[Total Quantity]`)
Calculates total physical inventory units purchased.
```dax
Total Quantity = 
SUM ( 'retail_sales'[Quantity] )
```
- **Data Type:** Whole Number
- **Format String:** `#,##0`
- **Visuals:** KPI Card, Volume analysis

---

## 3. Time Intelligence Measures (DAX)

These measures leverage the Date Dimension table (`dim_date`) connected via an active 1-to-Many relationship on `dim_date[Date] -> retail_sales[Order Date]`.

### Measure 5: Prior Month Sales (`[Sales PM]`)
Calculates revenue for the previous month based on current filter context.
```dax
Sales PM = 
CALCULATE (
    [Total Sales],
    PREVIOUSMONTH ( 'dim_date'[Date] )
)
```

---

### Measure 6: Month-over-Month Sales Growth (`[MoM Sales Growth]`)
Calculates the absolute variance between current month and prior month revenue.
```dax
MoM Sales Growth = 
VAR CurrentSales = [Total Sales]
VAR PreviousSales = [Sales PM]
RETURN
IF (
    ISBLANK ( PreviousSales ),
    BLANK (),
    CurrentSales - PreviousSales
)
```

---

### Measure 7: Month-over-Month Growth Rate % (`[MoM Growth %]`)
Calculates percentage change in revenue month-over-month.
```dax
MoM Growth % = 
DIVIDE (
    [MoM Sales Growth],
    [Sales PM],
    BLANK ()
)
```
- **Data Type:** Percentage
- **Format String:** `+0.00%;-0.00%;0.00%`

---

## 4. Advanced Ranking & Category Contribution Measures

### Measure 8: Category Sales Contribution % (`[% of Total Category Sales]`)
Calculates category revenue share relative to overall total regardless of category filters.
```dax
% of Total Category Sales = 
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALL ( 'retail_sales'[Category] ) ),
    0
)
```
- **Format:** `0.00%`

---

### Measure 9: Top 5 Products by Revenue Dynamic Title (`[Top 5 Title]`)
Dynamic visual title that updates based on active category selections.
```dax
Top 5 Title = 
VAR SelectedCat = SELECTEDVALUE ( 'retail_sales'[Category], "All Categories" )
RETURN
"Top 5 Products by Sales Revenue (" & SelectedCat & ")"
```

---

## 5. Standalone DAX Calendar Table (Optional Alternative)

If you prefer generating the Calendar Table dynamically in DAX rather than importing `dim_date.csv`:
```dax
dim_date = 
ADDCOLUMNS (
    CALENDAR ( DATE ( 2024, 1, 1 ), DATE ( 2024, 12, 31 ) ),
    "Year", YEAR ( [Date] ),
    "Month Number", MONTH ( [Date] ),
    "Month Name", FORMAT ( [Date], "MMMM" ),
    "Month Short", FORMAT ( [Date], "MMM" ),
    "Month Year", FORMAT ( [Date], "MMM YYYY" ),
    "Year Month Sort", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "Day of Week", FORMAT ( [Date], "dddd" )
)
```
> **Sorting Rule:** Always select column `'dim_date'[Month Year]`, go to **Column Tools -> Sort by Column**, and select **`Year Month Sort`**. This guarantees January through December display in chronological calendar order rather than alphabetical order.
