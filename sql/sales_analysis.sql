-- =============================================================================
-- RETAIL SALES ANALYSIS - SQL BUSINESS INTELLIGENCE QUERIES
-- Project: Retail Sales Analysis Dashboard
-- Database Engine: SQLite (also ANSI SQL compliant for PostgreSQL/MySQL/Snowflake)
-- Target Table: retail_sales
-- Schema:
--   id           INTEGER PRIMARY KEY AUTOINCREMENT
--   order_id     TEXT
--   order_date   TEXT (YYYY-MM-DD)
--   product_id   TEXT
--   product_name TEXT
--   category     TEXT
--   region       TEXT
--   quantity     INTEGER
--   unit_price   REAL
--   sales_amount REAL
-- =============================================================================

-- =============================================================================
-- 1. OVERALL EXECUTIVE KPIS
-- Metrics: Total Revenue (INR), Unique Orders, Average Order Value (AOV), Total Quantity Sold
-- =============================================================================
SELECT 
    ROUND(SUM(sales_amount), 2) AS total_revenue_inr,
    COUNT(DISTINCT order_id) AS total_unique_orders,
    ROUND(SUM(sales_amount) * 1.0 / COUNT(DISTINCT order_id), 2) AS average_order_value_inr,
    SUM(quantity) AS total_quantity_sold
FROM retail_sales;

-- =============================================================================
-- 2. TOP 5 PRODUCTS BY TOTAL REVENUE
-- Ranking products based on cumulative sales contribution (INR)
-- =============================================================================
SELECT 
    product_id,
    product_name,
    category,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales_amount), 2) AS total_revenue_inr
FROM retail_sales
GROUP BY product_id, product_name, category
ORDER BY total_revenue_inr DESC
LIMIT 5;

-- =============================================================================
-- 3. TOP 5 PRODUCTS BY QUANTITY SOLD
-- High-velocity volume drivers in terms of total units moved
-- =============================================================================
SELECT 
    product_id,
    product_name,
    category,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales_amount), 2) AS total_revenue_inr
FROM retail_sales
GROUP BY product_id, product_name, category
ORDER BY total_units_sold DESC
LIMIT 5;

-- =============================================================================
-- 4. MONTHLY REVENUE AND ORDER VOLUME TREND
-- Chronological monthly aggregation of revenue, distinct orders, and unit sales
-- =============================================================================
SELECT 
    strftime('%Y-%m', order_date) AS sales_month,
    COUNT(DISTINCT order_id) AS monthly_orders,
    SUM(quantity) AS monthly_quantity_sold,
    ROUND(SUM(sales_amount), 2) AS monthly_revenue_inr,
    ROUND(SUM(sales_amount) * 1.0 / COUNT(DISTINCT order_id), 2) AS monthly_aov_inr
FROM retail_sales
GROUP BY strftime('%Y-%m', order_date)
ORDER BY sales_month ASC;

-- =============================================================================
-- 5. MONTH-OVER-MONTH (MoM) REVENUE GROWTH COMPARISON
-- Utilizes Window Function LAG() to calculate percentage growth month-over-month
-- =============================================================================
WITH MonthlyAggregations AS (
    SELECT 
        strftime('%Y-%m', order_date) AS sales_month,
        ROUND(SUM(sales_amount), 2) AS current_month_revenue
    FROM retail_sales
    GROUP BY strftime('%Y-%m', order_date)
)
SELECT 
    sales_month,
    current_month_revenue,
    LAG(current_month_revenue, 1) OVER (ORDER BY sales_month) AS prior_month_revenue,
    ROUND(
        (current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY sales_month)) * 100.0 / 
        LAG(current_month_revenue, 1) OVER (ORDER BY sales_month), 
        2
    ) AS mom_growth_rate_pct
FROM MonthlyAggregations
ORDER BY sales_month ASC;

-- =============================================================================
-- 6. REGIONAL PERFORMANCE BREAKDOWN
-- Revenue, unique order count, and average spend per region
-- =============================================================================
SELECT 
    region,
    COUNT(DISTINCT order_id) AS total_unique_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales_amount), 2) AS total_revenue_inr,
    ROUND(SUM(sales_amount) * 1.0 / COUNT(DISTINCT order_id), 2) AS regional_aov_inr,
    ROUND(
        (SUM(sales_amount) * 100.0) / (SELECT SUM(sales_amount) FROM retail_sales),
        2
    ) AS revenue_share_pct
FROM retail_sales
GROUP BY region
ORDER BY total_revenue_inr DESC;

-- =============================================================================
-- 7. PRODUCT CATEGORY SALES & CONTRIBUTION ANALYSIS
-- Category revenue, unit sales, and proportional revenue contribution (%)
-- =============================================================================
SELECT 
    category,
    COUNT(DISTINCT order_id) AS distinct_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales_amount), 2) AS total_revenue_inr,
    ROUND(
        (SUM(sales_amount) * 100.0) / (SELECT SUM(sales_amount) FROM retail_sales),
        2
    ) AS category_revenue_contribution_pct
FROM retail_sales
GROUP BY category
ORDER BY total_revenue_inr DESC;

-- =============================================================================
-- 8. BEST-PERFORMING AND LOWEST-PERFORMING MONTHS
-- Identifies peak performance and trough periods for inventory & staffing planning
-- =============================================================================
WITH MonthlySales AS (
    SELECT 
        strftime('%Y-%m', order_date) AS sales_month,
        ROUND(SUM(sales_amount), 2) AS monthly_revenue
    FROM retail_sales
    GROUP BY strftime('%Y-%m', order_date)
)
SELECT 
    'Best Performing Month' AS performance_category,
    sales_month,
    monthly_revenue
FROM MonthlySales
WHERE monthly_revenue = (SELECT MAX(monthly_revenue) FROM MonthlySales)

UNION ALL

SELECT 
    'Lowest Performing Month' AS performance_category,
    sales_month,
    monthly_revenue
FROM MonthlySales
WHERE monthly_revenue = (SELECT MIN(monthly_revenue) FROM MonthlySales);

-- =============================================================================
-- 9. REGIONAL ORDER COUNTS AND BASKET METRICS
-- Demonstrates order density and average line items per order by region
-- =============================================================================
SELECT 
    region,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(*) AS total_line_items,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_items_per_order
FROM retail_sales
GROUP BY region
ORDER BY distinct_orders DESC;
