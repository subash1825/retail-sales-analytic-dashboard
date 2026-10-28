"""
Unit Tests for Sales Metrics Module (src/analyze_sales.py)
----------------------------------------------------------
Verifies mathematical correctness of all 15 required business metrics
against an analytically computed, deterministic ground-truth test dataset.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analyze_sales import compute_metrics


@pytest.fixture
def ground_truth_df():
    """
    Deterministic known mini-dataset:
    Order 1 (Jan): 2 units of P1 (price 100) = 200, 1 unit of P2 (price 50) = 50. Total = 250.
    Order 2 (Feb): 1 unit of P3 (price 300) = 300. Total = 300.
    Order 3 (Feb): 3 units of P4 (price 400) = 1200. Total = 1200.
    Order 4 (Mar): 2 units of P5 (price 500) = 1000. Total = 1000.
    Order 5 (Mar): 5 units of P6 (price 50) = 250. Total = 250.
    Order 6 (Mar): 1 unit of P1 (price 100) = 100. Total = 100.

    Total Orders: 6 unique orders
    Total Items: 7 rows
    Total Quantity: 2 + 1 + 1 + 3 + 2 + 5 + 1 = 15 units
    Total Revenue: 200 + 50 + 300 + 1200 + 1000 + 250 + 100 = 3100.00
    Average Order Value: 3100.00 / 6 = 516.67

    Product Totals:
    - P1: Qty 3, Rev 300
    - P2: Qty 1, Rev 50
    - P3: Qty 1, Rev 300
    - P4: Qty 3, Rev 1200
    - P5: Qty 2, Rev 1000
    - P6: Qty 5, Rev 250

    Top 5 by Revenue:
    1. P4 (1200)
    2. P5 (1000)
    3. P1 (300) [tied with P3]
    4. P3 (300)
    5. P6 (250)

    Top 5 by Quantity:
    1. P6 (5 units)
    2. P1 (3 units) [tied with P4]
    3. P4 (3 units)
    4. P5 (2 units)
    5. P2 / P3 (1 unit each)

    Monthly Totals:
    - 2024-01: 250.00
    - 2024-02: 1500.00 -> MoM Growth: ((1500 - 250) / 250) * 100 = +500.00%
    - 2024-03: 1350.00 -> MoM Growth: ((1350 - 1500) / 1500) * 100 = -10.00%
    Best Month: 2024-02 (1500.00)
    Lowest Month: 2024-01 (250.00)
    """
    data = [
        {"Order ID": "O1", "Order Date": "2024-01-10", "Product ID": "P1", "Product Name": "Keyboard", "Category": "Tech", "Region": "North", "Quantity": 2, "Unit Price": 100.0, "Sales Amount": 200.0},
        {"Order ID": "O1", "Order Date": "2024-01-10", "Product ID": "P2", "Product Name": "Mouse", "Category": "Tech", "Region": "North", "Quantity": 1, "Unit Price": 50.0, "Sales Amount": 50.0},
        {"Order ID": "O2", "Order Date": "2024-02-05", "Product ID": "P3", "Product Name": "Desk Lamp", "Category": "Home", "Region": "South", "Quantity": 1, "Unit Price": 300.0, "Sales Amount": 300.0},
        {"Order ID": "O3", "Order Date": "2024-02-18", "Product ID": "P4", "Product Name": "Air Fryer", "Category": "Home", "Region": "West", "Quantity": 3, "Unit Price": 400.0, "Sales Amount": 1200.0},
        {"Order ID": "O4", "Order Date": "2024-03-01", "Product ID": "P5", "Product Name": "Vacuum", "Category": "Home", "Region": "East", "Quantity": 2, "Unit Price": 500.0, "Sales Amount": 1000.0},
        {"Order ID": "O5", "Order Date": "2024-03-12", "Product ID": "P6", "Product Name": "T-Shirt", "Category": "Apparel", "Region": "Central", "Quantity": 5, "Unit Price": 50.0, "Sales Amount": 250.0},
        {"Order ID": "O6", "Order Date": "2024-03-25", "Product ID": "P1", "Product Name": "Keyboard", "Category": "Tech", "Region": "North", "Quantity": 1, "Unit Price": 100.0, "Sales Amount": 100.0},
    ]
    return pd.DataFrame(data)


def test_core_kpis(ground_truth_df):
    """Verify primary KPI calculations."""
    m = compute_metrics(ground_truth_df)

    assert m["total_sales_revenue"] == 3100.0
    assert m["unique_orders_count"] == 6
    assert m["average_order_value"] == 516.67
    assert m["total_quantity_sold"] == 15
    assert m["unique_products_count"] == 6


def test_product_rankings(ground_truth_df):
    """Verify top product ranking calculations."""
    m = compute_metrics(ground_truth_df)

    # Highest revenue product
    assert m["highest_revenue_product"]["product_id"] == "P4"
    assert m["highest_revenue_product"]["revenue"] == 1200.0

    # Top 5 products by revenue
    top_5_rev = m["top_5_products_by_revenue"]
    assert len(top_5_rev) == 5
    assert top_5_rev[0]["Product ID"] == "P4"
    assert top_5_rev[0]["total_revenue"] == 1200.0
    assert top_5_rev[1]["Product ID"] == "P5"
    assert top_5_rev[1]["total_revenue"] == 1000.0

    # Top 5 products by quantity
    top_5_qty = m["top_5_products_by_quantity"]
    assert len(top_5_qty) == 5
    assert top_5_qty[0]["Product ID"] == "P6"
    assert top_5_qty[0]["total_quantity"] == 5


def test_monthly_aggregations_and_mom(ground_truth_df):
    """Verify monthly aggregation, MoM percentage changes, and peak/lowest months."""
    m = compute_metrics(ground_truth_df)

    monthly = m["monthly_revenue_trend"]
    assert len(monthly) == 3

    assert monthly[0]["Year_Month"] == "2024-01"
    assert monthly[0]["monthly_revenue"] == 250.0
    assert monthly[0]["mom_change_pct"] == 0.0

    assert monthly[1]["Year_Month"] == "2024-02"
    assert monthly[1]["monthly_revenue"] == 1500.0
    assert monthly[1]["mom_change_pct"] == 500.0

    assert monthly[2]["Year_Month"] == "2024-03"
    assert monthly[2]["monthly_revenue"] == 1350.0
    assert monthly[2]["mom_change_pct"] == -10.0

    # Best and lowest performing months
    assert m["best_performing_month"]["year_month"] == "2024-02"
    assert m["best_performing_month"]["revenue"] == 1500.0

    assert m["lowest_performing_month"]["year_month"] == "2024-01"
    assert m["lowest_performing_month"]["revenue"] == 250.0


def test_regional_and_category_breakdowns(ground_truth_df):
    """Verify regional order counts, revenues, and category revenue contributions."""
    m = compute_metrics(ground_truth_df)

    # Regional: North had 2 orders (O1 and O6) with 200+50+100 = 350 revenue
    north = [r for r in m["sales_by_region"] if r["region"] == "North"][0]
    assert north["order_count"] == 2
    assert north["revenue"] == 350.0

    # Category: Home had P3 (300) + P4 (1200) + P5 (1000) = 2500 revenue
    home = [c for c in m["sales_by_category"] if c["category"] == "Home"][0]
    assert home["revenue"] == 2500.0
    assert home["revenue_contribution_pct"] == pytest.approx((2500.0 / 3100.0) * 100, abs=0.05)
