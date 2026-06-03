import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, event

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "bluestock_mf.db")
    schema_path = os.path.join(script_dir, "schema.sql")
    processed_dir = os.path.join(script_dir, "data", "processed")
    
    print("=== Start SQLite Database Initialization & Data Loading ===\n")
    
    # 1. Execute schema.sql using sqlite3 connection (direct DDL execution)
    print("Executing schema DDL...")
    if not os.path.exists(schema_path):
        print(f"Error: schema.sql not found at {schema_path}")
        return
        
    with open(schema_path, "r") as f:
        schema_sql = f.read()
        
    conn = sqlite3.connect(db_path)
    # Enable foreign keys during schema creation
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    conn.close()
    print("Schema DDL executed successfully. Created tables and indexes.\n")
    
    # 2. Setup SQLAlchemy Engine with SQLite foreign keys enabled on connect
    engine = create_engine(f"sqlite:///{db_path}")
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()
        
    # 3. Generate dim_date DataFrame
    print("Generating dim_date table...")
    date_range = pd.date_range(start="2022-01-01", end="2026-12-31", freq="D")
    df_date = pd.DataFrame({"date": date_range})
    df_date["year"] = df_date["date"].dt.year
    df_date["month"] = df_date["date"].dt.month
    df_date["day"] = df_date["date"].dt.day
    df_date["quarter"] = df_date["date"].dt.quarter
    df_date["day_of_week"] = df_date["date"].dt.dayofweek
    df_date["day_name"] = df_date["date"].dt.strftime("%A")
    df_date["month_name"] = df_date["date"].dt.strftime("%B")
    df_date["is_weekend"] = df_date["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
    df_date["date"] = df_date["date"].dt.strftime("%Y-%m-%d")
    
    # Load dim_date
    df_date.to_sql("dim_date", con=engine, if_exists="append", index=False)
    print(f"Loaded {df_date.shape[0]} rows into dim_date table.\n")
    
    # Define mapping from CSV file name to DB table name
    # We order them carefully to load parent tables before child tables
    table_load_order = [
        # Parent tables
        {"file": "01_fund_master.csv", "table": "dim_fund"},
        {"file": "04_monthly_sip_inflows.csv", "table": "fact_monthly_sip_inflows"},
        {"file": "05_category_inflows.csv", "table": "fact_category_inflows"},
        {"file": "06_industry_folio_count.csv", "table": "fact_industry_folio_count"},
        
        # Child tables
        {"file": "02_nav_history.csv", "table": "fact_nav"},
        {"file": "03_aum_by_fund_house.csv", "table": "fact_aum"},
        {"file": "07_scheme_performance.csv", "table": "fact_performance"},
        {"file": "08_investor_transactions.csv", "table": "fact_transactions"},
        {"file": "09_portfolio_holdings.csv", "table": "fact_portfolio_holdings"},
        {"file": "10_benchmark_indices.csv", "table": "fact_benchmark_indices"}
    ]
    
    # Fetch valid amfi_codes and dates for integrity filtering
    df_fund_master = pd.read_csv(os.path.join(processed_dir, "01_fund_master.csv"))
    valid_amfi_codes = set(df_fund_master["amfi_code"].unique())
    valid_dates = set(df_date["date"].unique())
    
    for item in table_load_order:
        file_name = item["file"]
        table_name = item["table"]
        csv_path = os.path.join(processed_dir, file_name)
        
        print(f"Loading {file_name} into table '{table_name}'...")
        if not os.path.exists(csv_path):
            print(f"Error: Processed file not found: {csv_path}")
            continue
            
        df = pd.read_csv(csv_path)
        source_count = df.shape[0]
        
        # Integrity checks: Filter out rows that violate foreign key constraints (if any)
        # 1. Filter by amfi_code if present
        if "amfi_code" in df.columns:
            invalid_amfi = df[~df["amfi_code"].isin(valid_amfi_codes)]
            if not invalid_amfi.empty:
                print(f"  Warning: Filtering out {len(invalid_amfi)} rows from {file_name} with invalid amfi_code (not present in dim_fund).")
                df = df[df["amfi_code"].isin(valid_amfi_codes)]
                
        # 2. Filter by date/transaction_date/portfolio_date if present
        date_cols = [c for c in ["date", "transaction_date", "portfolio_date"] if c in df.columns]
        for dc in date_cols:
            invalid_d = df[~df[dc].isin(valid_dates)]
            if not invalid_d.empty:
                print(f"  Warning: Filtering out {len(invalid_d)} rows from {file_name} with invalid date '{dc}' (not present in dim_date).")
                df = df[df[dc].isin(valid_dates)]
                
        # Load data to SQLite
        # If loading into fact_transactions, we should drop 'transaction_id' if pandas read it as null
        # or let sqlite generate it automatically by omitting it.
        # But wait, our CSV doesn't have transaction_id, so that's fine.
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        
        # Verify row counts
        db_count = pd.read_sql_query(f"SELECT COUNT(*) FROM {table_name}", con=engine).iloc[0, 0]
        print(f"  Success: Loaded {df.shape[0]} rows (Source had {source_count} rows). DB Table row count = {db_count}")
        
        if db_count != df.shape[0] and table_name != "dim_date":
            # For some tables we might have filtered a few rows
            print(f"  Note: Row counts differ because of integrity filtering (Source: {source_count}, Loaded: {df.shape[0]})")
            
        print("-" * 60)
        
    print("\n=== Database Loading Completed Successfully ===")

if __name__ == "__main__":
    main()
