"""
Data Cleaning and Validation Pipeline for Retail Sales Analysis
---------------------------------------------------------------
This module implements an auditable, transparent data cleaning process
for retail transaction datasets.

Key Pipeline Stages:
1. Multi-format ingestion (CSV, XLSX).
2. Schema & column presence verification.
3. Whitespace stripping, title-casing, and label normalization.
4. Robust multi-format date parsing (YYYY-MM-DD, DD/MM/YYYY).
5. Exact and logical duplicate identification without dropping valid multi-item orders.
6. Detection of invalid negative quantities and zero unit prices with flagged quarantine.
7. Recalculation of missing Sales Amount and reconciliation of mismatched values.
8. Generation of a formal Data Quality Report (Markdown).
9. Output generation for CSV, Excel, and Date Dimension.
"""

import os
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


REQUIRED_COLUMNS = [
    "Order ID",
    "Order Date",
    "Product ID",
    "Product Name",
    "Category",
    "Region",
    "Quantity",
    "Unit Price",
    "Sales Amount",
]


def load_raw_data(file_path: str) -> pd.DataFrame:
    """Load raw dataset from CSV or Excel file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found at: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Expected .csv or .xlsx")


def validate_schema(df: pd.DataFrame, required_columns: List[str] = REQUIRED_COLUMNS) -> None:
    """Ensure all required columns are present in the dataset."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Schema validation failed. Missing required columns: {missing}")


def clean_text_labels(df: pd.DataFrame, audit_log: List[Dict]) -> pd.DataFrame:
    """Strip whitespace and normalize casing for categorical text columns."""
    df_clean = df.copy()

    for col in ["Category", "Region"]:
        if col in df_clean.columns:
            original_uniques = df_clean[col].dropna().unique().tolist()
            # Convert to string, strip surrounding whitespaces, and apply title case
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
            new_uniques = df_clean[col].unique().tolist()

            changed_count = (df[col].astype(str) != df_clean[col]).sum()
            audit_log.append({
                "step": f"Normalize {col} Labels",
                "records_affected": int(changed_count),
                "details": f"Stripped whitespace and standardized to Title Case. Unique values consolidated from {len(original_uniques)} to {len(new_uniques)}."
            })

    # Also clean product names and IDs
    for col in ["Order ID", "Product ID", "Product Name"]:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()

    return df_clean


def standardize_dates(df: pd.DataFrame, audit_log: List[Dict]) -> pd.DataFrame:
    """Convert mixed string date representations into standard YYYY-MM-DD datetime."""
    df_clean = df.copy()
    # Try multiple format parsing (dayfirst=True handles DD/MM/YYYY correctly)
    parsed_dates = pd.to_datetime(df_clean["Order Date"], format="mixed", dayfirst=True, errors="coerce")

    invalid_date_count = int(parsed_dates.isna().sum())
    audit_log.append({
        "step": "Date Standardization",
        "records_affected": len(df_clean) - invalid_date_count,
        "details": f"Standardized dates to ISO 8601 (YYYY-MM-DD). Identified {invalid_date_count} unparseable dates."
    })

    df_clean["Order Date"] = parsed_dates.dt.date
    return df_clean


def deduplicate_records(df: pd.DataFrame, audit_log: List[Dict]) -> pd.DataFrame:
    """
    Remove identical duplicate line items.
    Preserves multi-item orders where Order ID is identical but Product ID differs.
    """
    initial_count = len(df)
    # Exact duplicate line items (same Order ID and same Product ID)
    exact_duplicates = df.duplicated(subset=["Order ID", "Product ID"], keep="first")
    dup_count = int(exact_duplicates.sum())

    df_clean = df[~exact_duplicates].copy()

    audit_log.append({
        "step": "Deduplicate Line Items",
        "records_affected": dup_count,
        "details": f"Removed {dup_count} exact duplicate order line items (matching Order ID + Product ID). Multi-product orders with unique line items were strictly preserved."
    })

    return df_clean


def flag_and_filter_invalid_records(df: pd.DataFrame, audit_log: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify and isolate anomalous records (negative quantity, zero price, missing IDs).
    Returns clean dataframe and quarantined dataframe for inspection.
    """
    # Enforce numeric types
    df_clean = df.copy()
    df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce")
    df_clean["Unit Price"] = pd.to_numeric(df_clean["Unit Price"], errors="coerce")
    df_clean["Sales Amount"] = pd.to_numeric(df_clean["Sales Amount"], errors="coerce")

    # Define validation rules
    rule_invalid_qty = (df_clean["Quantity"].isna()) | (df_clean["Quantity"] <= 0)
    rule_invalid_price = (df_clean["Unit Price"].isna()) | (df_clean["Unit Price"] <= 0)
    rule_missing_order_id = df_clean["Order ID"].isna() | (df_clean["Order ID"] == "")

    invalid_mask = rule_invalid_qty | rule_invalid_price | rule_missing_order_id
    flagged_records = df_clean[invalid_mask].copy()

    # Document reasons for flagging
    reasons = []
    for idx, row in flagged_records.iterrows():
        reason_list = []
        if pd.isna(row["Quantity"]) or row["Quantity"] <= 0:
            reason_list.append(f"Invalid Quantity ({row['Quantity']})")
        if pd.isna(row["Unit Price"]) or row["Unit Price"] <= 0:
            reason_list.append(f"Invalid Unit Price ({row['Unit Price']})")
        if pd.isna(row["Order ID"]) or row["Order ID"] == "":
            reason_list.append("Missing Order ID")
        reasons.append("; ".join(reason_list))

    if not flagged_records.empty:
        flagged_records["Flagged_Reason"] = reasons

    valid_records = df_clean[~invalid_mask].copy()
    # Cast Quantity explicitly to int
    valid_records["Quantity"] = valid_records["Quantity"].astype(int)

    audit_log.append({
        "step": "Identify & Quarantine Invalid Records",
        "records_affected": len(flagged_records),
        "details": f"Quarantined {len(flagged_records)} rows with non-positive quantities, zero/negative unit prices, or null values for auditor review."
    })

    return valid_records, flagged_records


def calculate_and_reconcile_sales(df: pd.DataFrame, audit_log: List[Dict]) -> pd.DataFrame:
    """
    Validate and reconcile Sales Amount.
    Formula: Sales Amount = Quantity * Unit Price
    Recalculates missing values and corrects math discrepancies.
    """
    df_clean = df.copy()
    expected_sales = (df_clean["Quantity"] * df_clean["Unit Price"]).round(2)

    # 1. Missing Sales Amount
    missing_sales_mask = df_clean["Sales Amount"].isna()
    missing_count = int(missing_sales_mask.sum())

    # 2. Existing Sales Amount discrepancies (tolerance ₹0.05)
    discrepant_mask = (~missing_sales_mask) & (np.abs(df_clean["Sales Amount"] - expected_sales) > 0.05)
    discrepant_count = int(discrepant_mask.sum())

    # Reconcile all with verified formula
    df_clean["Sales Amount"] = expected_sales

    audit_log.append({
        "step": "Impute Missing Sales Amounts",
        "records_affected": missing_count,
        "details": f"Computed {missing_count} missing Sales Amount values as Quantity * Unit Price."
    })
    audit_log.append({
        "step": "Reconcile Sales Amount Discrepancies",
        "records_affected": discrepant_count,
        "details": f"Corrected {discrepant_count} recorded sales amount values where recorded amount diverged from Quantity * Unit Price."
    })

    return df_clean


def generate_date_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a supporting Date Dimension table for Power BI and time intelligence.
    Includes Date, Year, Month Number, Month Name, Quarter, Month-Year, and Day of Week.
    """
    min_date = pd.to_datetime(df["Order Date"]).min()
    max_date = pd.to_datetime(df["Order Date"]).max()

    date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    dim_date = pd.DataFrame({"Date": date_range})

    dim_date["Year"] = dim_date["Date"].dt.year
    dim_date["Month_Number"] = dim_date["Date"].dt.month
    dim_date["Month_Name"] = dim_date["Date"].dt.strftime("%B")
    dim_date["Month_Short"] = dim_date["Date"].dt.strftime("%b")
    dim_date["Quarter"] = "Q" + dim_date["Date"].dt.quarter.astype(str)
    dim_date["Year_Month"] = dim_date["Date"].dt.strftime("%Y-%m")
    dim_date["Month_Year"] = dim_date["Date"].dt.strftime("%b %Y")
    dim_date["Year_Month_Sort"] = dim_date["Date"].dt.strftime("%Y%m").astype(int)
    dim_date["Day_Of_Week"] = dim_date["Date"].dt.strftime("%A")
    dim_date["Is_Weekend"] = dim_date["Date"].dt.dayofweek.isin([5, 6]).astype(int)

    dim_date["Date"] = dim_date["Date"].dt.date
    return dim_date


def write_data_quality_report(
    audit_log: List[Dict],
    initial_count: int,
    final_count: int,
    flagged_df: pd.DataFrame,
    report_path: str
) -> None:
    """Output comprehensive Data Quality & Audit Report in Markdown."""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Data Quality & Cleaning Audit Report\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Initial Raw Records Ingested:** {initial_count:,}\n")
        f.write(f"- **Final Cleaned Records Ready for Analysis:** {final_count:,}\n")
        f.write(f"- **Records Quarantined for Review:** {len(flagged_df):,}\n")
        f.write(f"- **Data Completeness Rate:** {(final_count / initial_count) * 100:.2f}%\n\n")

        f.write("## 2. Cleaning Audit Trail\n\n")
        f.write("| Step # | Pipeline Stage | Records Affected | Action Description |\n")
        f.write("| :---: | :--- | :---: | :--- |\n")
        for idx, entry in enumerate(audit_log, 1):
            f.write(f"| {idx} | {entry['step']} | {entry['records_affected']} | {entry['details']} |\n")
        f.write("\n")

        f.write("## 3. Quarantined Records Review\n\n")
        if flagged_df.empty:
            f.write("No anomalous records detected. All ingested rows conformed to business validation rules.\n\n")
        else:
            f.write("The following records were removed from analytical aggregations due to business rule violations:\n\n")
            f.write("| Order ID | Product ID | Quantity | Unit Price | Flagged Reason |\n")
            f.write("| :--- | :--- | :---: | :---: | :--- |\n")
            for _, row in flagged_df.iterrows():
                f.write(f"| {row.get('Order ID', 'N/A')} | {row.get('Product ID', 'N/A')} | {row.get('Quantity', 'N/A')} | ₹{row.get('Unit Price', 0):.2f} | {row.get('Flagged_Reason', 'Unknown')} |\n")
            f.write("\n")

        f.write("## 4. Handling Rules & Assumptions\n\n")
        f.write("1. **Multi-Item Orders:** In retail transactions, multiple rows sharing identical `Order ID` are valid because customers purchase multiple products. Deduplication was strictly restricted to rows matching both `Order ID` AND `Product ID`.\n")
        f.write("2. **Missing Sales Amount:** Imputed via `Sales Amount = Quantity * Unit Price` without record loss.\n")
        f.write("3. **Discrepancy Correction:** Reconciled source recording inaccuracies against verified SKU price and quantity.\n")
        f.write("4. **Label Harmonization:** Trimmed whitespace and converted Region and Category to Title Case to prevent duplicate grouping in SQL and Power BI.\n")

    print(f"[SUCCESS] Data quality report written to: {report_path}")


def clean_retail_data(
    input_file: str,
    output_csv: str,
    output_xlsx: str,
    dim_date_csv: str,
    report_path: str
) -> pd.DataFrame:
    """End-to-end data cleaning execution."""
    print(f"Ingesting raw data from: {input_file} ...")
    df_raw = load_raw_data(input_file)
    initial_count = len(df_raw)

    audit_log = []
    validate_schema(df_raw)

    # 1. Text normalization
    df_stage1 = clean_text_labels(df_raw, audit_log)

    # 2. Date parsing
    df_stage2 = standardize_dates(df_stage1, audit_log)

    # 3. Deduplication
    df_stage3 = deduplicate_records(df_stage2, audit_log)

    # 4. Quarantine invalid numerical rows
    df_stage4, flagged_records = flag_and_filter_invalid_records(df_stage3, audit_log)

    # 5. Sales calculation and reconciliation
    df_cleaned = calculate_and_reconcile_sales(df_stage4, audit_log)

    # 6. Generate supporting Date Dimension
    df_dim_date = generate_date_dimension(df_cleaned)

    # 7. Save outputs
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_cleaned.to_csv(output_csv, index=False)
    df_cleaned.to_excel(output_xlsx, index=False, engine="openpyxl")
    df_dim_date.to_csv(dim_date_csv, index=False)

    # 8. Write Audit Report
    write_data_quality_report(audit_log, initial_count, len(df_cleaned), flagged_records, report_path)

    print(f"[SUCCESS] Cleaned dataset saved:")
    print(f"  - CSV:           {output_csv} ({len(df_cleaned)} rows)")
    print(f"  - Excel:         {output_xlsx}")
    print(f"  - Date Dim CSV:  {dim_date_csv} ({len(df_dim_date)} rows)")

    return df_cleaned


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "retail_sales_raw.csv")
    cleaned_csv = os.path.join(base_dir, "data", "processed", "retail_sales_cleaned.csv")
    cleaned_xlsx = os.path.join(base_dir, "data", "processed", "retail_sales_cleaned.xlsx")
    dim_date_csv = os.path.join(base_dir, "data", "processed", "dim_date.csv")
    quality_report = os.path.join(base_dir, "reports", "data_quality_report.md")

    clean_retail_data(raw_path, cleaned_csv, cleaned_xlsx, dim_date_csv, quality_report)
