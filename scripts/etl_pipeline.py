import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, event

# Resolve absolute paths relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
DB_DIR = os.path.join(PROJECT_ROOT, "data", "db")
DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "sql", "schema.sql")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
PLOTS_DIR = os.path.join(REPORTS_DIR, "plots")

# Ensure target directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Define clean helper functions
def clean_numeric(val):
    if pd.isnull(val):
        return np.nan
    val_str = str(val).replace(",", "").replace("%", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan

def clean_int(val):
    if pd.isnull(val):
        return np.nan
    val_str = str(val).replace(",", "").strip()
    try:
        return int(float(val_str))
    except ValueError:
        return np.nan

def run_ingestion():
    print("=== [1/4] Starting Data Ingestion Verification ===")
    if not os.path.exists(RAW_DIR):
        print(f"Error: Raw directory not found at {RAW_DIR}")
        return False
    csv_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV datasets in raw data folder.")
    for idx, f in enumerate(sorted(csv_files), 1):
        print(f"  [{idx}] {f} ({os.path.getsize(os.path.join(RAW_DIR, f)) / 1024:.1f} KB)")
    print("Ingestion verification completed successfully.\n")
    return True

def run_cleaning():
    print("=== [2/4] Starting Data Cleaning and Processing ===")
    
    # 1. 01_fund_master.csv
    print("  Processing 01_fund_master.csv...")
    df_fund = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"))
    df_fund['launch_date'] = pd.to_datetime(df_fund['launch_date']).dt.strftime('%Y-%m-%d')
    for col in ['expense_ratio_pct', 'exit_load_pct', 'min_sip_amount', 'min_lumpsum_amount']:
        df_fund[col] = df_fund[col].apply(clean_numeric)
    df_fund['amfi_code'] = df_fund['amfi_code'].apply(clean_int)
    str_cols = ['fund_house', 'scheme_name', 'category', 'sub_category', 'plan', 'benchmark', 'fund_manager', 'risk_category', 'sebi_category_code']
    for col in str_cols:
        df_fund[col] = df_fund[col].astype(str).str.strip()
    df_fund.to_csv(os.path.join(PROCESSED_DIR, "01_fund_master.csv"), index=False)
    
    # 2. 02_nav_history.csv
    print("  Processing 02_nav_history.csv...")
    df_nav = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav['amfi_code'] = df_nav['amfi_code'].apply(clean_int)
    df_nav['nav'] = df_nav['nav'].apply(clean_numeric)
    df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])
    
    full_date_range = pd.date_range(start='2022-01-03', end='2026-05-29', freq='D')
    cleaned_nav_dfs = []
    for amfi_code, group in df_nav.groupby('amfi_code'):
        group_reindexed = group.set_index('date').reindex(full_date_range)
        group_reindexed['amfi_code'] = amfi_code
        group_reindexed['nav'] = group_reindexed['nav'].ffill().bfill()
        group_reindexed = group_reindexed.reset_index().rename(columns={'index': 'date'})
        cleaned_nav_dfs.append(group_reindexed)
        
    df_nav_clean = pd.concat(cleaned_nav_dfs, ignore_index=True)
    df_nav_clean['date'] = df_nav_clean['date'].dt.strftime('%Y-%m-%d')
    df_nav_clean['amfi_code'] = df_nav_clean['amfi_code'].astype(int)
    df_nav_clean = df_nav_clean[df_nav_clean['nav'] > 0]
    df_nav_clean.to_csv(os.path.join(PROCESSED_DIR, "02_nav_history.csv"), index=False)
    
    # 3. 03_aum_by_fund_house.csv
    print("  Processing 03_aum_by_fund_house.csv...")
    df_aum = pd.read_csv(os.path.join(RAW_DIR, "03_aum_by_fund_house.csv"))
    df_aum['date'] = pd.to_datetime(df_aum['date']).dt.strftime('%Y-%m-%d')
    df_aum['fund_house'] = df_aum['fund_house'].astype(str).str.strip()
    df_aum['aum_lakh_crore'] = df_aum['aum_lakh_crore'].apply(clean_numeric)
    df_aum['aum_crore'] = df_aum['aum_crore'].apply(clean_numeric)
    df_aum['num_schemes'] = df_aum['num_schemes'].apply(clean_int)
    df_aum.to_csv(os.path.join(PROCESSED_DIR, "03_aum_by_fund_house.csv"), index=False)
    
    # 4. 04_monthly_sip_inflows.csv
    print("  Processing 04_monthly_sip_inflows.csv...")
    df_sip = pd.read_csv(os.path.join(RAW_DIR, "04_monthly_sip_inflows.csv"))
    df_sip['month'] = pd.to_datetime(df_sip['month'], format='%Y-%m').dt.strftime('%Y-%m')
    for col in ['sip_inflow_crore', 'active_sip_accounts_crore', 'new_sip_accounts_lakh', 'sip_aum_lakh_crore', 'yoy_growth_pct']:
        df_sip[col] = df_sip[col].apply(clean_numeric)
    df_sip.to_csv(os.path.join(PROCESSED_DIR, "04_monthly_sip_inflows.csv"), index=False)
    
    # 5. 05_category_inflows.csv
    print("  Processing 05_category_inflows.csv...")
    df_cat = pd.read_csv(os.path.join(RAW_DIR, "05_category_inflows.csv"))
    df_cat['month'] = pd.to_datetime(df_cat['month'], format='%Y-%m').dt.strftime('%Y-%m')
    df_cat['category'] = df_cat['category'].astype(str).str.strip()
    df_cat['net_inflow_crore'] = df_cat['net_inflow_crore'].apply(clean_numeric)
    df_cat.to_csv(os.path.join(PROCESSED_DIR, "05_category_inflows.csv"), index=False)
    
    # 6. 06_industry_folio_count.csv
    print("  Processing 06_industry_folio_count.csv...")
    df_folio = pd.read_csv(os.path.join(RAW_DIR, "06_industry_folio_count.csv"))
    df_folio['month'] = pd.to_datetime(df_folio['month'], format='%Y-%m').dt.strftime('%Y-%m')
    for col in ['total_folios_crore', 'equity_folios_crore', 'debt_folios_crore', 'hybrid_folios_crore', 'others_folios_crore']:
        df_folio[col] = df_folio[col].apply(clean_numeric)
    df_folio.to_csv(os.path.join(PROCESSED_DIR, "06_industry_folio_count.csv"), index=False)
    
    # 7. 07_scheme_performance.csv
    print("  Processing 07_scheme_performance.csv...")
    df_perf = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))
    df_perf['amfi_code'] = df_perf['amfi_code'].apply(clean_int)
    numeric_cols = [
        'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct',
        'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct',
        'max_drawdown_pct', 'aum_crore', 'expense_ratio_pct'
    ]
    for col in numeric_cols:
        df_perf[col] = df_perf[col].apply(clean_numeric).fillna(0.0)
    for col in ['scheme_name', 'fund_house', 'category', 'plan', 'risk_grade']:
        df_perf[col] = df_perf[col].astype(str).str.strip()
    df_perf['morningstar_rating'] = df_perf['morningstar_rating'].apply(clean_int)
    df_perf.to_csv(os.path.join(PROCESSED_DIR, "07_scheme_performance.csv"), index=False)
    
    # 8. 08_investor_transactions.csv
    print("  Processing 08_investor_transactions.csv...")
    df_tx = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date']).dt.strftime('%Y-%m-%d')
    df_tx['amfi_code'] = df_tx['amfi_code'].apply(clean_int)
    df_tx['amount_inr'] = df_tx['amount_inr'].apply(clean_numeric)
    df_tx['transaction_type'] = df_tx['transaction_type'].astype(str).str.strip()
    type_map = {'sip': 'SIP', 'lumpsum': 'Lumpsum', 'redemption': 'Redemption'}
    df_tx['transaction_type'] = df_tx['transaction_type'].map(lambda x: type_map.get(x.lower(), x))
    df_tx = df_tx[df_tx['amount_inr'] > 0]
    df_tx['kyc_status'] = df_tx['kyc_status'].astype(str).str.strip()
    kyc_map = {'verified': 'Verified', 'pending': 'Pending'}
    df_tx['kyc_status'] = df_tx['kyc_status'].map(lambda x: kyc_map.get(x.lower(), x))
    df_tx.loc[~df_tx['kyc_status'].isin(['Verified', 'Pending']), 'kyc_status'] = 'Pending'
    for col in ['investor_id', 'state', 'city', 'city_tier', 'age_group', 'gender', 'payment_mode']:
        df_tx[col] = df_tx[col].astype(str).str.strip()
    df_tx['annual_income_lakh'] = df_tx['annual_income_lakh'].apply(clean_numeric)
    df_tx.to_csv(os.path.join(PROCESSED_DIR, "08_investor_transactions.csv"), index=False)
    
    # 9. 09_portfolio_holdings.csv
    print("  Processing 09_portfolio_holdings.csv...")
    df_holdings = pd.read_csv(os.path.join(RAW_DIR, "09_portfolio_holdings.csv"))
    df_holdings['amfi_code'] = df_holdings['amfi_code'].apply(clean_int)
    df_holdings['portfolio_date'] = pd.to_datetime(df_holdings['portfolio_date']).dt.strftime('%Y-%m-%d')
    for col in ['weight_pct', 'market_value_cr', 'current_price_inr']:
        df_holdings[col] = df_holdings[col].apply(clean_numeric)
    for col in ['stock_symbol', 'stock_name', 'sector']:
        df_holdings[col] = df_holdings[col].astype(str).str.strip()
    df_holdings.to_csv(os.path.join(PROCESSED_DIR, "09_portfolio_holdings.csv"), index=False)
    
    # 10. 10_benchmark_indices.csv
    print("  Processing 10_benchmark_indices.csv...")
    df_bench = pd.read_csv(os.path.join(RAW_DIR, "10_benchmark_indices.csv"))
    df_bench['date'] = pd.to_datetime(df_bench['date']).dt.strftime('%Y-%m-%d')
    df_bench['index_name'] = df_bench['index_name'].astype(str).str.strip()
    df_bench['close_value'] = df_bench['close_value'].apply(clean_numeric)
    df_bench.to_csv(os.path.join(PROCESSED_DIR, "10_benchmark_indices.csv"), index=False)
    
    print("Data cleaning completed successfully.\n")
    return True

def run_db_loading():
    print("=== [3/4] Starting SQLite Database Creation and Loading ===")
    if not os.path.exists(SCHEMA_PATH):
        print(f"Error: schema.sql not found at {SCHEMA_PATH}")
        return False
        
    # Read and execute DDL script
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
        
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    conn.close()
    print("  SQLite database schema DDL executed successfully.")
    
    # Establish SQLAlchemy connection to load dataframes
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()
        
    # 1. Generate dim_date table
    print("  Generating dim_date dimension table...")
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
    df_date.to_sql("dim_date", con=engine, if_exists="append", index=False)
    
    table_load_order = [
        {"file": "01_fund_master.csv", "table": "dim_fund"},
        {"file": "04_monthly_sip_inflows.csv", "table": "fact_monthly_sip_inflows"},
        {"file": "05_category_inflows.csv", "table": "fact_category_inflows"},
        {"file": "06_industry_folio_count.csv", "table": "fact_industry_folio_count"},
        {"file": "02_nav_history.csv", "table": "fact_nav"},
        {"file": "03_aum_by_fund_house.csv", "table": "fact_aum"},
        {"file": "07_scheme_performance.csv", "table": "fact_performance"},
        {"file": "08_investor_transactions.csv", "table": "fact_transactions"},
        {"file": "09_portfolio_holdings.csv", "table": "fact_portfolio_holdings"},
        {"file": "10_benchmark_indices.csv", "table": "fact_benchmark_indices"}
    ]
    
    # Load parent tables first, then children, matching foreign keys
    df_fund_master = pd.read_csv(os.path.join(PROCESSED_DIR, "01_fund_master.csv"))
    valid_amfi_codes = set(df_fund_master["amfi_code"].unique())
    valid_dates = set(df_date["date"].unique())
    
    for item in table_load_order:
        file_name = item["file"]
        table_name = item["table"]
        csv_path = os.path.join(PROCESSED_DIR, file_name)
        
        df = pd.read_csv(csv_path)
        if "amfi_code" in df.columns:
            df = df[df["amfi_code"].isin(valid_amfi_codes)]
        date_cols = [c for c in ["date", "transaction_date", "portfolio_date"] if c in df.columns]
        for dc in date_cols:
            df = df[df[dc].isin(valid_dates)]
            
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        print(f"  Loaded {df.shape[0]} rows into SQLite '{table_name}' table.")
        
    print("Database loading completed successfully.\n")
    return True

def run_metrics():
    print("=== [4/4] Starting Advanced Analytics and Risk Metrics ===")
    
    # Connect and compute
    conn = sqlite3.connect(DB_PATH)
    df_nav = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    
    var_cvar_data = []
    for amfi_code, group in df_nav.groupby('amfi_code'):
        group = group.sort_values('date')
        returns = group['nav'].pct_change().dropna()
        if len(returns) < 30:
            continue
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        var_cvar_data.append({
            'amfi_code': amfi_code,
            'var_95_pct': var_95 * 100,
            'cvar_95_pct': cvar_95 * 100
        })
        
    df_var_cvar = pd.DataFrame(var_cvar_data)
    df_funds = pd.read_sql_query("SELECT amfi_code, scheme_name, category FROM dim_fund", conn)
    df_report = pd.merge(df_funds, df_var_cvar, on='amfi_code')
    df_report.to_csv(os.path.join(REPORTS_DIR, 'var_cvar_report.csv'), index=False)
    
    # Rolling Sharpe chart
    target_funds = [148568, 120842, 118634, 149322, 102886]
    fig, ax = plt.subplots(figsize=(14, 7), facecolor='#f8fafc')
    ax.set_facecolor('#ffffff')
    
    colors = ['#1e3a8a', '#0d8a72', '#e66f50', '#e6ad12', '#475569']
    for idx, amfi in enumerate(target_funds):
        fund_name = df_funds[df_funds['amfi_code'] == amfi]['scheme_name'].values[0].split(' - ')[0]
        fund_nav = df_nav[df_nav['amfi_code'] == amfi].sort_values('date').copy()
        fund_nav['return'] = fund_nav['nav'].pct_change()
        
        rolling_mean = fund_nav['return'].rolling(90).mean()
        rolling_std = fund_nav['return'].rolling(90).std()
        fund_nav['rolling_sharpe'] = (rolling_mean / rolling_std) * np.sqrt(252)
        
        ax.plot(
            fund_nav['date'], fund_nav['rolling_sharpe'],
            label=fund_name, linewidth=2.5, color=colors[idx % len(colors)]
        )
        
    ax.set_title("Rolling 90-day Sharpe Ratio over Time (Top 5 Funds by AUM)", fontsize=14, fontweight='bold', pad=15, color='#1e3a8a')
    ax.set_xlabel("Date", fontsize=11, labelpad=8)
    ax.set_ylabel("Annualised Sharpe Ratio", fontsize=11, labelpad=8)
    ax.tick_params(axis='x', rotation=30)
    ax.grid(True, linestyle='--', alpha=0.3, color='#94a3b8')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    ax.legend(loc='best', fontsize=9.5, frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', framealpha=0.9)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'rolling_sharpe_chart.png'), dpi=150)
    plt.close()
    
    conn.close()
    print("Advanced metrics and Sharpe plots compiled successfully.")
    print("=== [4/4] Advanced Metrics Completed ===\n")
    return True

def main():
    print("=" * 80)
    print("             BLUESTOCK MUTUAL FUND - MASTER ETL PIPELINE")
    print("=" * 80)
    
    if not run_ingestion():
        print("Ingestion verification failed. Exiting.")
        return
    if not run_cleaning():
        print("Data cleaning failed. Exiting.")
        return
    if not run_db_loading():
        print("Database loading failed. Exiting.")
        return
    if not run_metrics():
        print("Metrics computation failed. Exiting.")
        return
        
    print("=" * 80)
    print("   MASTER ETL PIPELINE EXECUTED SUCCESSFULLY - ALL TABLES LOADED")
    print("=" * 80)

if __name__ == "__main__":
    main()
