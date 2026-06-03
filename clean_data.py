import os
import glob
import pandas as pd
import numpy as np

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

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(script_dir, "data", "raw")
    processed_dir = os.path.join(script_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    print("=== Start Data Cleaning Process ===\n")
    
    # ---------------------------------------------------------
    # 1. 01_fund_master.csv
    # ---------------------------------------------------------
    print("Cleaning 01_fund_master.csv...")
    df_fund = pd.read_csv(os.path.join(raw_dir, "01_fund_master.csv"))
    df_fund['launch_date'] = pd.to_datetime(df_fund['launch_date']).dt.strftime('%Y-%m-%d')
    for col in ['expense_ratio_pct', 'exit_load_pct', 'min_sip_amount', 'min_lumpsum_amount']:
        df_fund[col] = df_fund[col].apply(clean_numeric)
    df_fund['amfi_code'] = df_fund['amfi_code'].apply(clean_int)
    # Strip string fields
    str_cols = ['fund_house', 'scheme_name', 'category', 'sub_category', 'plan', 'benchmark', 'fund_manager', 'risk_category', 'sebi_category_code']
    for col in str_cols:
        df_fund[col] = df_fund[col].astype(str).str.strip()
    df_fund.to_csv(os.path.join(processed_dir, "01_fund_master.csv"), index=False)
    print(f"-> Saved {df_fund.shape[0]} rows to processed/01_fund_master.csv\n")
    
    # ---------------------------------------------------------
    # 2. 02_nav_history.csv
    # ---------------------------------------------------------
    print("Cleaning and reindexing 02_nav_history.csv...")
    df_nav = pd.read_csv(os.path.join(raw_dir, "02_nav_history.csv"))
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav['amfi_code'] = df_nav['amfi_code'].apply(clean_int)
    df_nav['nav'] = df_nav['nav'].apply(clean_numeric)
    
    # Remove duplicates on amfi_code + date
    df_nav = df_nav.drop_duplicates(subset=['amfi_code', 'date'])
    
    # Reindex for holidays/weekends and forward fill
    # All 40 funds start on 2022-01-03 and end on 2026-05-29
    full_date_range = pd.date_range(start='2022-01-03', end='2026-05-29', freq='D')
    
    cleaned_nav_dfs = []
    for amfi_code, group in df_nav.groupby('amfi_code'):
        # Set date index, reindex to full daily range
        group_reindexed = group.set_index('date').reindex(full_date_range)
        group_reindexed['amfi_code'] = amfi_code
        # Forward fill first, then backward fill in case there are leading NaNs (unlikely here but safe)
        group_reindexed['nav'] = group_reindexed['nav'].ffill().bfill()
        group_reindexed = group_reindexed.reset_index().rename(columns={'index': 'date'})
        cleaned_nav_dfs.append(group_reindexed)
        
    df_nav_clean = pd.concat(cleaned_nav_dfs, ignore_index=True)
    df_nav_clean['date'] = df_nav_clean['date'].dt.strftime('%Y-%m-%d')
    df_nav_clean['amfi_code'] = df_nav_clean['amfi_code'].astype(int)
    
    # Validate NAV > 0
    invalid_navs = df_nav_clean[df_nav_clean['nav'] <= 0]
    if not invalid_navs.empty:
        print(f"Warning: Found {len(invalid_navs)} rows with NAV <= 0. Dropping...")
        df_nav_clean = df_nav_clean[df_nav_clean['nav'] > 0]
        
    df_nav_clean.to_csv(os.path.join(processed_dir, "02_nav_history.csv"), index=False)
    print(f"-> Reindexed and saved {df_nav_clean.shape[0]} rows to processed/02_nav_history.csv (original had {df_nav.shape[0]} rows)\n")
    
    # ---------------------------------------------------------
    # 3. 03_aum_by_fund_house.csv
    # ---------------------------------------------------------
    print("Cleaning 03_aum_by_fund_house.csv...")
    df_aum = pd.read_csv(os.path.join(raw_dir, "03_aum_by_fund_house.csv"))
    df_aum['date'] = pd.to_datetime(df_aum['date']).dt.strftime('%Y-%m-%d')
    df_aum['fund_house'] = df_aum['fund_house'].astype(str).str.strip()
    df_aum['aum_lakh_crore'] = df_aum['aum_lakh_crore'].apply(clean_numeric)
    df_aum['aum_crore'] = df_aum['aum_crore'].apply(clean_numeric)
    df_aum['num_schemes'] = df_aum['num_schemes'].apply(clean_int)
    df_aum.to_csv(os.path.join(processed_dir, "03_aum_by_fund_house.csv"), index=False)
    print(f"-> Saved {df_aum.shape[0]} rows to processed/03_aum_by_fund_house.csv\n")
    
    # ---------------------------------------------------------
    # 4. 04_monthly_sip_inflows.csv
    # ---------------------------------------------------------
    print("Cleaning 04_monthly_sip_inflows.csv...")
    df_sip = pd.read_csv(os.path.join(raw_dir, "04_monthly_sip_inflows.csv"))
    # Standardise month format to YYYY-MM
    df_sip['month'] = pd.to_datetime(df_sip['month'], format='%Y-%m').dt.strftime('%Y-%m')
    for col in ['sip_inflow_crore', 'active_sip_accounts_crore', 'new_sip_accounts_lakh', 'sip_aum_lakh_crore', 'yoy_growth_pct']:
        df_sip[col] = df_sip[col].apply(clean_numeric)
    df_sip.to_csv(os.path.join(processed_dir, "04_monthly_sip_inflows.csv"), index=False)
    print(f"-> Saved {df_sip.shape[0]} rows to processed/04_monthly_sip_inflows.csv\n")
    
    # ---------------------------------------------------------
    # 5. 05_category_inflows.csv
    # ---------------------------------------------------------
    print("Cleaning 05_category_inflows.csv...")
    df_cat = pd.read_csv(os.path.join(raw_dir, "05_category_inflows.csv"))
    df_cat['month'] = pd.to_datetime(df_cat['month'], format='%Y-%m').dt.strftime('%Y-%m')
    df_cat['category'] = df_cat['category'].astype(str).str.strip()
    df_cat['net_inflow_crore'] = df_cat['net_inflow_crore'].apply(clean_numeric)
    df_cat.to_csv(os.path.join(processed_dir, "05_category_inflows.csv"), index=False)
    print(f"-> Saved {df_cat.shape[0]} rows to processed/05_category_inflows.csv\n")
    
    # ---------------------------------------------------------
    # 6. 06_industry_folio_count.csv
    # ---------------------------------------------------------
    print("Cleaning 06_industry_folio_count.csv...")
    df_folio = pd.read_csv(os.path.join(raw_dir, "06_industry_folio_count.csv"))
    df_folio['month'] = pd.to_datetime(df_folio['month'], format='%Y-%m').dt.strftime('%Y-%m')
    for col in ['total_folios_crore', 'equity_folios_crore', 'debt_folios_crore', 'hybrid_folios_crore', 'others_folios_crore']:
        df_folio[col] = df_folio[col].apply(clean_numeric)
    df_folio.to_csv(os.path.join(processed_dir, "06_industry_folio_count.csv"), index=False)
    print(f"-> Saved {df_folio.shape[0]} rows to processed/06_industry_folio_count.csv\n")
    
    # ---------------------------------------------------------
    # 7. 07_scheme_performance.csv
    # ---------------------------------------------------------
    print("Cleaning and validating 07_scheme_performance.csv...")
    df_perf = pd.read_csv(os.path.join(raw_dir, "07_scheme_performance.csv"))
    df_perf['amfi_code'] = df_perf['amfi_code'].apply(clean_int)
    
    # Validate returns and metrics are numeric
    numeric_cols = [
        'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct',
        'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct',
        'max_drawdown_pct', 'aum_crore', 'expense_ratio_pct'
    ]
    for col in numeric_cols:
        df_perf[col] = df_perf[col].apply(clean_numeric)
        if df_perf[col].isnull().any():
            print(f"  Warning: Found null values in {col}. Filling with 0.0")
            df_perf[col] = df_perf[col].fillna(0.0)
            
    # Check expense_ratio_pct range (0.1% - 2.5%)
    out_of_range_expense = df_perf[(df_perf['expense_ratio_pct'] < 0.1) | (df_perf['expense_ratio_pct'] > 2.5)]
    if not out_of_range_expense.empty:
        print(f"  Warning: Found {len(out_of_range_expense)} schemes with expense_ratio_pct outside [0.1%, 2.5%]:")
        for _, row in out_of_range_expense.iterrows():
            print(f"    - {row['scheme_name']}: {row['expense_ratio_pct']}%")
            
    # Flag return anomalies (e.g. > 50% or < -50%)
    for col in ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']:
        anomalous_returns = df_perf[df_perf[col].abs() > 50.0]
        if not anomalous_returns.empty:
            print(f"  Anomaly Flag: High return in {col}:")
            for _, row in anomalous_returns.iterrows():
                print(f"    - {row['scheme_name']}: {row[col]}%")
                
    # Clean string fields
    for col in ['scheme_name', 'fund_house', 'category', 'plan', 'risk_grade']:
        df_perf[col] = df_perf[col].astype(str).str.strip()
    df_perf['morningstar_rating'] = df_perf['morningstar_rating'].apply(clean_int)
    
    df_perf.to_csv(os.path.join(processed_dir, "07_scheme_performance.csv"), index=False)
    print(f"-> Saved {df_perf.shape[0]} rows to processed/07_scheme_performance.csv\n")
    
    # ---------------------------------------------------------
    # 8. 08_investor_transactions.csv
    # ---------------------------------------------------------
    print("Cleaning and validating 08_investor_transactions.csv...")
    df_tx = pd.read_csv(os.path.join(raw_dir, "08_investor_transactions.csv"))
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date']).dt.strftime('%Y-%m-%d')
    df_tx['amfi_code'] = df_tx['amfi_code'].apply(clean_int)
    df_tx['amount_inr'] = df_tx['amount_inr'].apply(clean_numeric)
    
    # Standardise transaction_type
    df_tx['transaction_type'] = df_tx['transaction_type'].astype(str).str.strip()
    type_map = {'sip': 'SIP', 'lumpsum': 'Lumpsum', 'redemption': 'Redemption'}
    df_tx['transaction_type'] = df_tx['transaction_type'].map(lambda x: type_map.get(x.lower(), x))
    
    # Validate amount > 0
    invalid_amounts = df_tx[df_tx['amount_inr'] <= 0]
    if not invalid_amounts.empty:
        print(f"  Warning: Found {len(invalid_amounts)} transactions with amount <= 0. Dropping them...")
        df_tx = df_tx[df_tx['amount_inr'] > 0]
        
    # Standardise KYC status
    df_tx['kyc_status'] = df_tx['kyc_status'].astype(str).str.strip()
    kyc_map = {'verified': 'Verified', 'pending': 'Pending'}
    df_tx['kyc_status'] = df_tx['kyc_status'].map(lambda x: kyc_map.get(x.lower(), x))
    
    # Validate KYC enum values
    invalid_kyc = df_tx[~df_tx['kyc_status'].isin(['Verified', 'Pending'])]
    if not invalid_kyc.empty:
        print(f"  Warning: Found {len(invalid_kyc)} transactions with invalid kyc_status. Defaulting to Pending...")
        df_tx.loc[~df_tx['kyc_status'].isin(['Verified', 'Pending']), 'kyc_status'] = 'Pending'
        
    # Clean other string fields
    for col in ['investor_id', 'state', 'city', 'city_tier', 'age_group', 'gender', 'payment_mode']:
        df_tx[col] = df_tx[col].astype(str).str.strip()
    df_tx['annual_income_lakh'] = df_tx['annual_income_lakh'].apply(clean_numeric)
    
    df_tx.to_csv(os.path.join(processed_dir, "08_investor_transactions.csv"), index=False)
    print(f"-> Saved {df_tx.shape[0]} rows to processed/08_investor_transactions.csv\n")
    
    # ---------------------------------------------------------
    # 9. 09_portfolio_holdings.csv
    # ---------------------------------------------------------
    print("Cleaning 09_portfolio_holdings.csv...")
    df_holdings = pd.read_csv(os.path.join(raw_dir, "09_portfolio_holdings.csv"))
    df_holdings['amfi_code'] = df_holdings['amfi_code'].apply(clean_int)
    df_holdings['portfolio_date'] = pd.to_datetime(df_holdings['portfolio_date']).dt.strftime('%Y-%m-%d')
    for col in ['weight_pct', 'market_value_cr', 'current_price_inr']:
        df_holdings[col] = df_holdings[col].apply(clean_numeric)
    for col in ['stock_symbol', 'stock_name', 'sector']:
        df_holdings[col] = df_holdings[col].astype(str).str.strip()
    df_holdings.to_csv(os.path.join(processed_dir, "09_portfolio_holdings.csv"), index=False)
    print(f"-> Saved {df_holdings.shape[0]} rows to processed/09_portfolio_holdings.csv\n")
    
    # ---------------------------------------------------------
    # 10. 10_benchmark_indices.csv
    # ---------------------------------------------------------
    print("Cleaning 10_benchmark_indices.csv...")
    df_bench = pd.read_csv(os.path.join(raw_dir, "10_benchmark_indices.csv"))
    df_bench['date'] = pd.to_datetime(df_bench['date']).dt.strftime('%Y-%m-%d')
    df_bench['index_name'] = df_bench['index_name'].astype(str).str.strip()
    df_bench['close_value'] = df_bench['close_value'].apply(clean_numeric)
    df_bench.to_csv(os.path.join(processed_dir, "10_benchmark_indices.csv"), index=False)
    print(f"-> Saved {df_bench.shape[0]} rows to processed/10_benchmark_indices.csv\n")
    
    print("=== Data Cleaning Process Completed Successfully ===")

if __name__ == "__main__":
    main()
