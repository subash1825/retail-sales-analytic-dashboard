# Data Quality & Cleaning Audit Report

## 1. Executive Summary

- **Initial Raw Records Ingested:** 1,507
- **Final Cleaned Records Ready for Analysis:** 1,500
- **Records Quarantined for Review:** 2
- **Data Completeness Rate:** 99.54%

## 2. Cleaning Audit Trail

| Step # | Pipeline Stage | Records Affected | Action Description |
| :---: | :--- | :---: | :--- |
| 1 | Normalize Category Labels | 121 | Stripped whitespace and standardized to Title Case. Unique values consolidated from 20 to 5. |
| 2 | Normalize Region Labels | 121 | Stripped whitespace and standardized to Title Case. Unique values consolidated from 20 to 5. |
| 3 | Date Standardization | 1507 | Standardized dates to ISO 8601 (YYYY-MM-DD). Identified 0 unparseable dates. |
| 4 | Deduplicate Line Items | 5 | Removed 5 exact duplicate order line items (matching Order ID + Product ID). Multi-product orders with unique line items were strictly preserved. |
| 5 | Identify & Quarantine Invalid Records | 2 | Quarantined 2 rows with non-positive quantities, zero/negative unit prices, or null values for auditor review. |
| 6 | Impute Missing Sales Amounts | 35 | Computed 35 missing Sales Amount values as Quantity * Unit Price. |
| 7 | Reconcile Sales Amount Discrepancies | 12 | Corrected 12 recorded sales amount values where recorded amount diverged from Quantity * Unit Price. |

## 3. Quarantined Records Review

The following records were removed from analytical aggregations due to business rule violations:

| Order ID | Product ID | Quantity | Unit Price | Flagged Reason |
| :--- | :--- | :---: | :---: | :--- |
| ORD-ERR-001 | PROD-EL-004 | -2 | ₹3499.00 | Invalid Quantity (-2) |
| ORD-ERR-002 | PROD-FA-001 | 1 | ₹0.00 | Invalid Unit Price (0.0) |

## 4. Handling Rules & Assumptions

1. **Multi-Item Orders:** In retail transactions, multiple rows sharing identical `Order ID` are valid because customers purchase multiple products. Deduplication was strictly restricted to rows matching both `Order ID` AND `Product ID`.
2. **Missing Sales Amount:** Imputed via `Sales Amount = Quantity * Unit Price` without record loss.
3. **Discrepancy Correction:** Reconciled source recording inaccuracies against verified SKU price and quantity.
4. **Label Harmonization:** Trimmed whitespace and converted Region and Category to Title Case to prevent duplicate grouping in SQL and Power BI.
