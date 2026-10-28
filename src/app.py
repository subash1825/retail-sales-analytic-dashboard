"""
Supplementary Interactive Streamlit Dashboard
----------------------------------------------
NOTE: This is an OPTIONAL supplementary interactive demonstration dashboard
to allow quick local testing and browser-based exploration. It does NOT replace
the primary Microsoft Power BI Desktop implementation.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# Page configuration
st.set_page_config(
    page_title="Retail Sales Analytics Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished aesthetics
st.markdown("""
<style>
    .metric-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "processed", "retail_sales_cleaned.csv")
    df = pd.read_csv(csv_path)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df, base_dir


df_full, base_dir = load_data()

# App Header
st.title("📊 Retail Sales Analysis Explorer")
st.caption("Supplementary Interactive Demonstration App | Portfolio Project for Data Analyst & BI Roles")
st.info("💡 **Note:** This web interface is a supplementary demonstration tool. The official Power BI Desktop implementation guide is located in `powerbi/powerbi_dashboard_guide.md`.")

# Sidebar Filters
st.sidebar.header("🔍 Interactive Slicers")

min_date = df_full["Order Date"].min().date()
max_date = df_full["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

all_regions = sorted(df_full["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Filter by Region", options=all_regions, default=all_regions)

all_categories = sorted(df_full["Category"].unique().tolist())
selected_categories = st.sidebar.multiselect("Filter by Category", options=all_categories, default=all_categories)

# Apply Filters
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = df_full[
        (df_full["Order Date"].dt.date >= start_d) &
        (df_full["Order Date"].dt.date <= end_d) &
        (df_full["Region"].isin(selected_regions)) &
        (df_full["Category"].isin(selected_categories))
    ]
else:
    filtered_df = df_full[
        (df_full["Region"].isin(selected_regions)) &
        (df_full["Category"].isin(selected_categories))
    ]

# Metrics
total_sales = filtered_df["Sales Amount"].sum()
unique_orders = filtered_df["Order ID"].nunique()
aov = total_sales / unique_orders if unique_orders > 0 else 0.0
total_qty = filtered_df["Quantity"].sum()

# Display KPI Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.markdown(f"""<div class="metric-box"><div class="metric-label">Total Revenue (INR)</div><div class="metric-value">₹{total_sales:,.2f}</div></div>""", unsafe_allow_html=True)
kpi2.markdown(f"""<div class="metric-box"><div class="metric-label">Unique Orders</div><div class="metric-value">{unique_orders:,}</div></div>""", unsafe_allow_html=True)
kpi3.markdown(f"""<div class="metric-box"><div class="metric-label">Average Order Value</div><div class="metric-value">₹{aov:,.2f}</div></div>""", unsafe_allow_html=True)
kpi4.markdown(f"""<div class="metric-box"><div class="metric-label">Total Units Sold</div><div class="metric-value">{total_qty:,}</div></div>""", unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📈 Visual Dashboards", "🗄️ SQL Query Explorer", "📋 Cleaned Dataset Viewer"])

with tab1:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Monthly Revenue Trend")
        df_monthly = filtered_df.copy()
        df_monthly["YearMonth"] = df_monthly["Order Date"].dt.strftime("%Y-%m")
        monthly_sales = df_monthly.groupby("YearMonth")["Sales Amount"].sum().reset_index()

        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
        ax.plot(monthly_sales["YearMonth"], monthly_sales["Sales Amount"] / 100000.0, marker="o", color="#0e7490", lw=2)
        ax.set_ylabel("Revenue (₹ Lakhs)")
        ax.set_xticks(range(len(monthly_sales["YearMonth"])))
        ax.set_xticklabels(monthly_sales["YearMonth"], rotation=45, ha="right", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.subheader("Top 5 Products by Revenue")
        top_prods = filtered_df.groupby("Product Name")["Sales Amount"].sum().reset_index()
        top_5 = top_prods.sort_values(by="Sales Amount", ascending=False).head(5)

        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
        ax.barh(top_5["Product Name"].iloc[::-1], top_5["Sales Amount"].iloc[::-1] / 1000.0, color="#0284c7")
        ax.set_xlabel("Revenue (₹ Thousands)")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)
        plt.close()

    col_cat, col_reg = st.columns(2)

    with col_cat:
        st.subheader("Sales by Category")
        cat_sales = filtered_df.groupby("Category")["Sales Amount"].sum().reset_index().sort_values(by="Sales Amount", ascending=False)
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
        ax.bar(cat_sales["Category"], cat_sales["Sales Amount"] / 100000.0, color="#4338ca")
        ax.set_ylabel("Revenue (₹ Lakhs)")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig)
        plt.close()

    with col_reg:
        st.subheader("Regional Revenue Share")
        reg_sales = filtered_df.groupby("Region")["Sales Amount"].sum().reset_index().sort_values(by="Sales Amount", ascending=False)
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
        ax.pie(reg_sales["Sales Amount"], labels=reg_sales["Region"], autopct="%1.1f%%", startangle=140,
               colors=["#0284c7", "#0d9488", "#f59e0b", "#6366f1", "#ec4899"])
        st.pyplot(fig)
        plt.close()

with tab2:
    st.subheader("Interactive SQLite Query Runner")
    st.write("Execute live SQL queries against the local `retail_sales.db` SQLite database.")

    db_path = os.path.join(base_dir, "data", "processed", "retail_sales.db")
    sample_queries = {
        "Executive KPIs": "SELECT ROUND(SUM(sales_amount),2) AS total_revenue, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales_amount)*1.0/COUNT(DISTINCT order_id),2) AS aov, SUM(quantity) AS units FROM retail_sales;",
        "Top 5 Products by Revenue": "SELECT product_id, product_name, category, SUM(quantity) AS units, ROUND(SUM(sales_amount),2) AS revenue FROM retail_sales GROUP BY product_id ORDER BY revenue DESC LIMIT 5;",
        "Monthly Sales Trend": "SELECT strftime('%Y-%m', order_date) AS month, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales_amount),2) AS revenue FROM retail_sales GROUP BY month ORDER BY month;",
        "Sales by Region": "SELECT region, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales_amount),2) AS revenue, ROUND(SUM(sales_amount)*100.0/(SELECT SUM(sales_amount) FROM retail_sales),2) AS share_pct FROM retail_sales GROUP BY region ORDER BY revenue DESC;",
        "Sales by Category": "SELECT category, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales_amount),2) AS revenue, ROUND(SUM(sales_amount)*100.0/(SELECT SUM(sales_amount) FROM retail_sales),2) AS share_pct FROM retail_sales GROUP BY category ORDER BY revenue DESC;"
    }

    selected_query_name = st.selectbox("Select Pre-configured SQL Query", list(sample_queries.keys()))
    query_text = st.text_area("SQL Query Editor", value=sample_queries[selected_query_name], height=100)

    if st.button("Run SQL Query", type="primary"):
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            try:
                res_df = pd.read_sql_query(query_text, conn)
                st.dataframe(res_df, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")
            finally:
                conn.close()
        else:
            st.warning("Database not found. Please run `python src/load_database.py` first.")

with tab3:
    st.subheader("Filtered Cleaned Transactions")
    st.write(f"Displaying {len(filtered_df):,} records:")
    st.dataframe(filtered_df, use_container_width=True)
