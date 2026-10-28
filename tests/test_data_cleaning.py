"""
Unit Tests for Data Cleaning Module (src/clean_data.py)
-------------------------------------------------------
Verifies data cleaning operations using known test cases.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.clean_data import (
    clean_text_labels,
    standardize_dates,
    deduplicate_records,
    flag_and_filter_invalid_records,
    calculate_and_reconcile_sales,
)


@pytest.fixture
def sample_raw_df():
    """Create a controlled mini-dataframe with known anomalies."""
    return pd.DataFrame({
        "Order ID": ["ORD-001", "ORD-001", "ORD-001", "ORD-002", "ORD-003", "ORD-004"],
        "Order Date": ["2024-01-15", "2024-01-15", "15/01/2024", "2024-02-10", "2024-02-15", "2024-03-01"],
        "Product ID": ["PROD-01", "PROD-02", "PROD-01", "PROD-03", "PROD-04", "PROD-05"],
        "Product Name": ["Item A", "Item B", "Item A", "Item C", "Item D", "Item E"],
        "Category": ["  electronics ", "ELECTRONICS", "Electronics", "Fashion", "  home & kitchen  ", "Books"],
        "Region": [" north ", "NORTH", "North", "South", "east", "west"],
        "Quantity": [2, 1, 2, -1, 3, 4],
        "Unit Price": [100.0, 50.0, 100.0, 200.0, 0.0, 25.0],
        "Sales Amount": [np.nan, 50.0, 200.0, -200.0, 0.0, 120.0],  # Item E: 4*25=100, but recorded as 120 (discrepancy)
    })


def test_text_normalization(sample_raw_df):
    """Test that whitespace is trimmed and text is standardized to Title Case."""
    audit = []
    cleaned = clean_text_labels(sample_raw_df, audit)

    # Categories should be cleanly normalized
    assert set(cleaned["Category"].unique()) == {"Electronics", "Fashion", "Home & Kitchen", "Books"}
    # Regions should be title-cased and trimmed
    assert set(cleaned["Region"].unique()) == {"North", "South", "East", "West"}
    assert len(audit) == 2


def test_standardize_dates(sample_raw_df):
    """Test date parsing handles mixed ISO and DD/MM/YYYY formats."""
    audit = []
    cleaned = standardize_dates(sample_raw_df, audit)
    # Check that all dates are valid date objects
    for d in cleaned["Order Date"]:
        assert hasattr(d, "year")
        assert d.year == 2024


def test_deduplication_preserves_multi_item_orders(sample_raw_df):
    """
    Test duplicate detection:
    Row 0 and Row 2 have identical Order ID ('ORD-001') AND Product ID ('PROD-01') -> Duplicate!
    Row 1 has Order ID 'ORD-001' and Product ID 'PROD-02' -> Valid multi-item basket, MUST BE KEPT!
    """
    audit = []
    cleaned = deduplicate_records(sample_raw_df, audit)

    assert len(cleaned) == 5  # One duplicate row removed
    # Ensure ORD-001 still has 2 distinct products
    ord_1_items = cleaned[cleaned["Order ID"] == "ORD-001"]
    assert len(ord_1_items) == 2
    assert set(ord_1_items["Product ID"]) == {"PROD-01", "PROD-02"}


def test_flag_and_quarantine_invalid_records(sample_raw_df):
    """Test detection and quarantine of negative quantity and zero price."""
    audit = []
    valid, flagged = flag_and_filter_invalid_records(sample_raw_df, audit)

    # ORD-002 has Quantity = -1 (invalid)
    # ORD-003 has Unit Price = 0.0 (invalid)
    assert len(flagged) == 2
    flagged_orders = set(flagged["Order ID"])
    assert "ORD-002" in flagged_orders
    assert "ORD-003" in flagged_orders

    # Valid records must not contain negative quantities or zero prices
    assert (valid["Quantity"] > 0).all()
    assert (valid["Unit Price"] > 0).all()


def test_sales_amount_calculation_and_reconciliation(sample_raw_df):
    """Test that missing Sales Amount is imputed and incorrect amounts are reconciled."""
    audit = []
    # Drop invalid rows first to test reconciliation on valid rows
    valid_rows, _ = flag_and_filter_invalid_records(sample_raw_df, audit)
    reconciled = calculate_and_reconcile_sales(valid_rows, audit)

    # First row had NaN Sales Amount -> 2 * 100.0 = 200.0
    first_row = reconciled[reconciled["Order ID"] == "ORD-001"].iloc[0]
    assert first_row["Sales Amount"] == 200.0

    # Last row had 4 * 25.0 = 100.0 (originally recorded as 120.0) -> Reconciled to 100.0
    last_row = reconciled[reconciled["Order ID"] == "ORD-004"].iloc[0]
    assert last_row["Sales Amount"] == 100.0
