"""
SQLite Database Loader and Query Runner
---------------------------------------
Loads the cleaned retail sales dataset into a local SQLite database (`retail_sales.db`),
establishes appropriate schema indexes, and executes queries to validate analytical metrics.
"""

import os
import sys
import sqlite3
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load_to_sqlite(csv_path: str, db_path: str) -> None:
    """Load cleaned CSV into SQLite table with snake_case column names and indices."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found at: {csv_path}")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    df = pd.read_csv(csv_path)

    # Rename columns to standard SQL snake_case
    col_mapping = {
        "Order ID": "order_id",
        "Order Date": "order_date",
        "Product ID": "product_id",
        "Product Name": "product_name",
        "Category": "category",
        "Region": "region",
        "Quantity": "quantity",
        "Unit Price": "unit_price",
        "Sales Amount": "sales_amount",
    }
    df_sql = df.rename(columns=col_mapping)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing table if present
    cursor.execute("DROP TABLE IF EXISTS retail_sales;")

    # Explicit DDL with data types and primary key composite consideration
    cursor.execute("""
    CREATE TABLE retail_sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL,
        order_date TEXT NOT NULL,
        product_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        region TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        sales_amount REAL NOT NULL
    );
    """)

    # Insert cleaned records
    df_sql.to_sql("retail_sales", conn, if_exists="append", index=False)

    # Create indexes for high-performance aggregations
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_id ON retail_sales(order_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON retail_sales(order_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON retail_sales(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON retail_sales(region);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_id ON retail_sales(product_id);")

    conn.commit()

    # Verify count
    cursor.execute("SELECT COUNT(*) FROM retail_sales;")
    count = cursor.fetchone()[0]
    conn.close()

    print(f"[SUCCESS] Loaded {count} rows into SQLite database:")
    print(f"  - Database file: {db_path}")
    print(f"  - Table name:    retail_sales")


def execute_sql_file(sql_file_path: str, db_path: str) -> None:
    """Execute all SQL queries from the SQL file and display formatted outputs."""
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL script not found at: {sql_file_path}")

    conn = sqlite3.connect(db_path)

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Separate queries delimited by comments or semicolons
    queries = [q.strip() for q in sql_content.split(";") if q.strip()]

    print(f"\nExecuting {len(queries)} SQL queries against SQLite database...\n")

    for i, q in enumerate(queries, 1):
        # Extract title comment if present (skip separator lines)
        title = f"Query {i}"
        lines = [line.strip() for line in q.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("--") and not line.startswith("-- =="):
                title = line.lstrip("-").strip()
                break

        try:
            df_result = pd.read_sql_query(q, conn)
            print(f"-----------------------------------------------------------------")
            print(f"[{i}] {title}")
            print(f"-----------------------------------------------------------------")
            print(df_result.to_string(index=False))
            print()
        except Exception as e:
            print(f"[ERROR in Query {i} - {title}]: {e}\n")

    conn.close()


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_csv = os.path.join(base_dir, "data", "processed", "retail_sales_cleaned.csv")
    db_file = os.path.join(base_dir, "data", "processed", "retail_sales.db")
    sql_script = os.path.join(base_dir, "sql", "sales_analysis.sql")

    load_to_sqlite(cleaned_csv, db_file)
    if os.path.exists(sql_script):
        execute_sql_file(sql_script, db_file)
