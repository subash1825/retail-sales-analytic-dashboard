"""
Sales Analysis and Visualization Module
---------------------------------------
Computes all 15 required business metrics from the cleaned retail transaction dataset,
generates publication-quality charts using Matplotlib, and exports a metrics summary JSON
to maintain mathematical consistency across Python, SQL, Excel, and Power BI.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Ensure safe UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Configure visual aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10


def compute_metrics(df: pd.DataFrame) -> dict:
    """Compute the 15 required retail business metrics."""
    # Ensure datetime parsing for monthly aggregations
    df_work = df.copy()
    df_work["Order Date"] = pd.to_datetime(df_work["Order Date"])
    df_work["Year_Month"] = df_work["Order Date"].dt.strftime("%Y-%m")
    df_work["Month_Name"] = df_work["Order Date"].dt.strftime("%b %Y")

    # 1. Total sales revenue
    total_sales = float(round(df_work["Sales Amount"].sum(), 2))

    # 2. Number of unique orders
    unique_orders = int(df_work["Order ID"].nunique())

    # 3. Average order value (Total revenue / Number of unique orders)
    avg_order_value = float(round(total_sales / unique_orders, 2)) if unique_orders > 0 else 0.0

    # 4. Total quantity sold
    total_quantity = int(df_work["Quantity"].sum())

    # 5. Number of unique products
    unique_products = int(df_work["Product ID"].nunique())

    # Product-level aggregations
    prod_agg = df_work.groupby(["Product ID", "Product Name"]).agg(
        total_revenue=("Sales Amount", "sum"),
        total_quantity=("Quantity", "sum")
    ).reset_index()

    # 6. Highest-revenue product
    top_revenue_row = prod_agg.sort_values(by="total_revenue", ascending=False).iloc[0]
    highest_revenue_product = {
        "product_id": top_revenue_row["Product ID"],
        "product_name": top_revenue_row["Product Name"],
        "revenue": float(round(top_revenue_row["total_revenue"], 2))
    }

    # 7. Top five products by revenue
    top_5_by_revenue = (
        prod_agg.sort_values(by="total_revenue", ascending=False)
        .head(5)[["Product ID", "Product Name", "total_revenue"]]
        .to_dict(orient="records")
    )
    for p in top_5_by_revenue:
        p["total_revenue"] = float(round(p["total_revenue"], 2))

    # 8. Top five products by quantity sold
    top_5_by_quantity = (
        prod_agg.sort_values(by="total_quantity", ascending=False)
        .head(5)[["Product ID", "Product Name", "total_quantity"]]
        .to_dict(orient="records")
    )
    for p in top_5_by_quantity:
        p["total_quantity"] = int(p["total_quantity"])

    # Monthly aggregations
    monthly_df = df_work.groupby("Year_Month").agg(
        monthly_revenue=("Sales Amount", "sum"),
        order_count=("Order ID", "nunique"),
        quantity_sold=("Quantity", "sum")
    ).reset_index().sort_values(by="Year_Month")

    # 10. Month-over-month revenue change (%)
    monthly_df["mom_change_pct"] = (
        monthly_df["monthly_revenue"].pct_change() * 100
    ).round(2).fillna(0.0)

    # 9. Monthly revenue dictionary
    monthly_revenue = monthly_df.to_dict(orient="records")
    for m in monthly_revenue:
        m["monthly_revenue"] = float(round(m["monthly_revenue"], 2))

    # 15. Best-performing and lowest-performing months
    best_month_row = monthly_df.sort_values(by="monthly_revenue", ascending=False).iloc[0]
    lowest_month_row = monthly_df.sort_values(by="monthly_revenue", ascending=True).iloc[0]

    best_month = {
        "year_month": best_month_row["Year_Month"],
        "revenue": float(round(best_month_row["monthly_revenue"], 2))
    }
    lowest_month = {
        "year_month": lowest_month_row["Year_Month"],
        "revenue": float(round(lowest_month_row["monthly_revenue"], 2))
    }

    # Regional analysis
    reg_agg = df_work.groupby("Region").agg(
        revenue=("Sales Amount", "sum"),
        order_count=("Order ID", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False)

    # 11. Revenue by region & 13. Order counts by region
    regional_sales = []
    for _, row in reg_agg.iterrows():
        regional_sales.append({
            "region": row["Region"],
            "revenue": float(round(row["revenue"], 2)),
            "order_count": int(row["order_count"]),
            "revenue_share_pct": float(round((row["revenue"] / total_sales) * 100, 2))
        })

    # Category analysis
    cat_agg = df_work.groupby("Category").agg(
        revenue=("Sales Amount", "sum"),
        quantity=("Quantity", "sum")
    ).reset_index().sort_values(by="revenue", ascending=False)

    # 12. Revenue by category & 14. Revenue contribution by category
    category_sales = []
    for _, row in cat_agg.iterrows():
        category_sales.append({
            "category": row["Category"],
            "revenue": float(round(row["revenue"], 2)),
            "quantity": int(row["quantity"]),
            "revenue_contribution_pct": float(round((row["revenue"] / total_sales) * 100, 2))
        })

    return {
        "total_sales_revenue": total_sales,
        "unique_orders_count": unique_orders,
        "average_order_value": avg_order_value,
        "total_quantity_sold": total_quantity,
        "unique_products_count": unique_products,
        "highest_revenue_product": highest_revenue_product,
        "top_5_products_by_revenue": top_5_by_revenue,
        "top_5_products_by_quantity": top_5_by_quantity,
        "monthly_revenue_trend": monthly_revenue,
        "best_performing_month": best_month,
        "lowest_performing_month": lowest_month,
        "sales_by_region": regional_sales,
        "sales_by_category": category_sales,
    }


def generate_visualizations(df: pd.DataFrame, metrics: dict, output_dir: str):
    """Generate high-resolution PNG charts for README, documentation, and reports."""
    os.makedirs(output_dir, exist_ok=True)
    brand_blue = "#1f77b4"
    brand_teal = "#0e7490"
    brand_coral = "#e11d48"
    palette = ["#0284c7", "#0d9488", "#f59e0b", "#6366f1", "#ec4899"]

    # -------------------------------------------------------------
    # 1. Monthly Revenue Trend with MoM Change
    # -------------------------------------------------------------
    months = [m["Year_Month"] for m in metrics["monthly_revenue_trend"]]
    revs = [m["monthly_revenue"] / 100000.0 for m in metrics["monthly_revenue_trend"]]  # in Lakhs INR
    mom = [m["mom_change_pct"] for m in metrics["monthly_revenue_trend"]]

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=300)
    line1 = ax1.plot(months, revs, color=brand_teal, marker="o", linewidth=2.5, markersize=6, label="Revenue (₹ Lakhs)")
    ax1.set_ylabel("Revenue (₹ Lakhs)", color=brand_teal, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=brand_teal)
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, rotation=45, ha="right")
    ax1.set_title("Monthly Sales Revenue & Month-over-Month Growth (2024)", fontsize=13, fontweight="bold", pad=12)

    # Annotate peak and lowest months
    best_idx = months.index(metrics["best_performing_month"]["year_month"])
    ax1.annotate(f"Peak: ₹{metrics['best_performing_month']['revenue']/100000:.2f}L",
                 (best_idx, revs[best_idx]),
                 textcoords="offset points", xytext=(-20, 15),
                 arrowprops=dict(arrowstyle="->", color=brand_coral, lw=1.5),
                 fontweight="bold", color=brand_coral)

    # MoM percentage bar chart on twin axis
    ax2 = ax1.twinx()
    bars = ax2.bar(months, mom, alpha=0.25, color="#64748b", width=0.4, label="MoM Change (%)")
    ax2.set_ylabel("MoM Growth Rate (%)", color="#475569", fontweight="bold")
    ax2.grid(False)

    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "monthly_sales_trend.png")
    plt.savefig(chart1_path)
    plt.close()

    # -------------------------------------------------------------
    # 2. Top 5 Products by Revenue
    # -------------------------------------------------------------
    top_prods = metrics["top_5_products_by_revenue"]
    p_names = [p["Product Name"] for p in reversed(top_prods)]
    p_revs = [p["total_revenue"] / 1000.0 for p in reversed(top_prods)]  # in Thousands INR

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    bars = ax.barh(p_names, p_revs, color="#0284c7", height=0.6)
    ax.set_xlabel("Total Sales Revenue (₹ in Thousands)", fontweight="bold")
    ax.set_title("Top 5 Products by Revenue (INR)", fontsize=13, fontweight="bold", pad=12)

    # Direct data labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 15, bar.get_y() + bar.get_height() / 2, f"₹{width:,.1f}K",
                va="center", ha="left", fontsize=9, fontweight="bold", color="#1e293b")

    ax.set_xlim(0, max(p_revs) * 1.18)
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "top_5_products_revenue.png")
    plt.savefig(chart2_path)
    plt.close()

    # -------------------------------------------------------------
    # 3. Revenue by Region & Order Counts
    # -------------------------------------------------------------
    reg_data = metrics["sales_by_region"]
    regions = [r["region"] for r in reg_data]
    reg_revs = [r["revenue"] / 100000.0 for r in reg_data]
    reg_orders = [r["order_count"] for r in reg_data]

    fig, (ax_reg1, ax_reg2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Bar chart for revenue
    ax_reg1.bar(regions, reg_revs, color=palette[:len(regions)], width=0.55)
    ax_reg1.set_ylabel("Revenue (₹ Lakhs)", fontweight="bold")
    ax_reg1.set_title("Sales Revenue by Region", fontsize=11, fontweight="bold")
    for i, v in enumerate(reg_revs):
        ax_reg1.text(i, v + 0.1, f"₹{v:.1f}L", ha="center", fontweight="bold", fontsize=9)

    # Donut chart for order distribution
    ax_reg2.pie(reg_orders, labels=regions, autopct="%1.1f%%", startangle=140,
                colors=palette[:len(regions)], wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
    ax_reg2.set_title("Order Volume Share by Region", fontsize=11, fontweight="bold")

    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "regional_sales_breakdown.png")
    plt.savefig(chart3_path)
    plt.close()

    # -------------------------------------------------------------
    # 4. Revenue by Product Category & Contribution %
    # -------------------------------------------------------------
    cat_data = metrics["sales_by_category"]
    cats = [c["category"] for c in cat_data]
    cat_revs = [c["revenue"] / 100000.0 for c in cat_data]
    shares = [c["revenue_contribution_pct"] for c in cat_data]

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    bars = ax.bar(cats, cat_revs, color="#4338ca", width=0.5)
    ax.set_ylabel("Revenue (₹ Lakhs)", fontweight="bold")
    ax.set_title("Product Category Revenue & Sales Contribution (%)", fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(axis="x", rotation=15)

    for bar, share in zip(bars, shares):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, f"₹{yval:.1f}L\n({share}%)",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1e1b4b")

    ax.set_ylim(0, max(cat_revs) * 1.25)
    plt.tight_layout()
    chart4_path = os.path.join(output_dir, "category_sales_contribution.png")
    plt.savefig(chart4_path)
    plt.close()

    # -------------------------------------------------------------
    # 5. Executive KPI Summary Card
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 2.5), dpi=300)
    ax.axis("off")

    cards = [
        ("TOTAL REVENUE", f"₹{metrics['total_sales_revenue']:,.2f}", "#0284c7"),
        ("UNIQUE ORDERS", f"{metrics['unique_orders_count']:,}", "#059669"),
        ("AVG ORDER VALUE", f"₹{metrics['average_order_value']:,.2f}", "#7c3aed"),
        ("TOTAL UNITS SOLD", f"{metrics['total_quantity_sold']:,}", "#ea580c")
    ]

    card_width = 0.22
    card_spacing = 0.03
    start_x = 0.02

    for i, (label, val, color) in enumerate(cards):
        x = start_x + i * (card_width + card_spacing)
        rect = plt.Rectangle((x, 0.1), card_width, 0.8,
                             facecolor="#f8fafc", edgecolor="#cbd5e1",
                             linewidth=1.5, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + card_width / 2, 0.65, label, transform=ax.transAxes,
                ha="center", va="center", fontsize=9, fontweight="bold", color="#64748b")
        ax.text(x + card_width / 2, 0.35, val, transform=ax.transAxes,
                ha="center", va="center", fontsize=12, fontweight="bold", color=color)

    plt.tight_layout()
    chart5_path = os.path.join(output_dir, "executive_kpi_summary.png")
    plt.savefig(chart5_path)
    plt.close()

    print(f"[SUCCESS] Generated 5 analytical visualization charts in: {output_dir}")


def run_sales_analysis(cleaned_csv_path: str, metrics_json_path: str, screenshots_dir: str):
    """Execute complete analysis and export figures and JSON."""
    df = pd.read_csv(cleaned_csv_path)
    metrics = compute_metrics(df)

    os.makedirs(os.path.dirname(metrics_json_path), exist_ok=True)
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    generate_visualizations(df, metrics, screenshots_dir)

    # Also copy figures to reports/figures
    reports_fig_dir = os.path.join(os.path.dirname(os.path.dirname(metrics_json_path)), "reports", "figures")
    generate_visualizations(df, metrics, reports_fig_dir)

    print("\n=======================================================")
    print("           RETAIL SALES ANALYTICS SUMMARY              ")
    print("=======================================================")
    print(f"Total Sales Revenue:      ₹{metrics['total_sales_revenue']:,.2f}")
    print(f"Unique Orders Count:      {metrics['unique_orders_count']:,}")
    print(f"Average Order Value:      ₹{metrics['average_order_value']:,.2f}")
    print(f"Total Quantity Sold:      {metrics['total_quantity_sold']:,} units")
    print(f"Unique Products Count:    {metrics['unique_products_count']}")
    print(f"Highest-Revenue Product:  {metrics['highest_revenue_product']['product_name']} (₹{metrics['highest_revenue_product']['revenue']:,.2f})")
    print(f"Best Performing Month:    {metrics['best_performing_month']['year_month']} (₹{metrics['best_performing_month']['revenue']:,.2f})")
    print(f"Lowest Performing Month:  {metrics['lowest_performing_month']['year_month']} (₹{metrics['lowest_performing_month']['revenue']:,.2f})")
    print("=======================================================\n")

    return metrics


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_csv = os.path.join(base_dir, "data", "processed", "retail_sales_cleaned.csv")
    metrics_json = os.path.join(base_dir, "reports", "metrics_summary.json")
    screenshots = os.path.join(base_dir, "screenshots")

    run_sales_analysis(cleaned_csv, metrics_json, screenshots)
