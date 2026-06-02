# %% [markdown]
# # Day 1: EDA and Data Validation
# This interactive script performs Exploratory Data Analysis (EDA) on `fund_master` 
# and validates mutual fund AMFI codes against `nav_history`.

# %%
import os
import glob
import pandas as pd

# %%
# 1. Locate Datasets
# Support running from either root folder or notebooks folder
raw_dir = os.path.join("..", "data", "raw")
if not os.path.exists(raw_dir):
    raw_dir = os.path.join("data", "raw")

print(f"Searching for datasets in: {os.path.abspath(raw_dir)}")

# Search for fund_master
fund_master_paths = glob.glob(os.path.join(raw_dir, "*fund_master*.csv")) + \
                    glob.glob(os.path.join(raw_dir, "*fundmaster*.csv"))
fund_master_path = fund_master_paths[0] if fund_master_paths else None

# Search for nav_history
nav_history_paths = glob.glob(os.path.join(raw_dir, "*nav_history*.csv")) + \
                    glob.glob(os.path.join(raw_dir, "*navhistory*.csv"))
nav_history_path = nav_history_paths[0] if nav_history_paths else None

print(f"Fund Master path found: {fund_master_path}")
print(f"NAV History path found: {nav_history_path}")

# %% Helper function for robust column matching
def get_column_by_candidates(df, candidates):
    for col in df.columns:
        col_lower = col.lower().replace("_", "").replace(" ", "").replace("-", "")
        for cand in candidates:
            cand_clean = cand.lower().replace("_", "").replace(" ", "").replace("-", "")
            if cand_clean in col_lower:
                return col
    return None

# %%
# 2. EDA of Fund Master (Task 6)
if fund_master_path:
    df_fund = pd.read_csv(fund_master_path)
    print("\n" + "="*50)
    print("--- EXPLORATORY DATA ANALYSIS: FUND MASTER ---")
    print("="*50)
    print(f"Total rows in fund_master: {len(df_fund)}")
    
    # Identify key columns dynamically
    house_col = get_column_by_candidates(df_fund, ["fundhouse", "house", "amc"])
    cat_col = get_column_by_candidates(df_fund, ["category", "type"])
    subcat_col = get_column_by_candidates(df_fund, ["subcategory", "subcat"])
    risk_col = get_column_by_candidates(df_fund, ["risk", "grade", "riskgrade"])
    
    print(f"Matched columns: AMC/House='{house_col}', Category='{cat_col}', Sub-category='{subcat_col}', Risk='{risk_col}'\n")
    
    # Analyze and print unique values
    for col_name, label in [(house_col, "Fund Houses"), (cat_col, "Categories"), (subcat_col, "Sub-categories"), (risk_col, "Risk Grades")]:
        if col_name:
            uniques = df_fund[col_name].dropna().unique()
            print(f"Unique {label} ({len(uniques)}):")
            print(sorted(list(uniques)))
            print("-" * 50)
        else:
            print(f"Could not find matching column for: {label}")
            print("-" * 50)
else:
    print("\n[Warning] fund_master CSV file not found in data/raw/. Skipping EDA.")

# %%
# 3. AMFI Code Validation (Task 7)
if fund_master_path and nav_history_path:
    df_fund = pd.read_csv(fund_master_path)
    df_nav = pd.read_csv(nav_history_path)
    
    print("\n" + "="*50)
    print("--- AMFI CODE VALIDATION ---")
    print("="*50)
    
    # Get AMFI code columns dynamically
    amfi_fund_col = get_column_by_candidates(df_fund, ["amfi", "schemecode", "code"])
    amfi_nav_col = get_column_by_candidates(df_nav, ["amfi", "schemecode", "code"])
    
    if amfi_fund_col and amfi_nav_col:
        # Extract unique codes
        fund_codes = set(df_fund[amfi_fund_col].dropna().unique())
        nav_codes = set(df_nav[amfi_nav_col].dropna().unique())
        
        print(f"Unique AMFI codes in Fund Master: {len(fund_codes)}")
        print(f"Unique AMFI codes in NAV History: {len(nav_codes)}")
        
        # Compare sets
        matched_codes = fund_codes.intersection(nav_codes)
        missing_in_nav = fund_codes - nav_codes
        
        match_percentage = (len(matched_codes) / len(fund_codes)) * 100 if fund_codes else 0
        
        # Prepare validation report text
        report_lines = [
            "==================================================",
            "           DATA QUALITY REPORT: AMFI CODES        ",
            "==================================================",
            f"Fund Master file: {os.path.basename(fund_master_path)}",
            f"NAV History file: {os.path.basename(nav_history_path)}",
            "--------------------------------------------------",
            f"Unique AMFI codes in Fund Master: {len(fund_codes)}",
            f"Unique AMFI codes in NAV History: {len(nav_codes)}",
            "--------------------------------------------------",
            f"Number of codes matched: {len(matched_codes)} ({match_percentage:.2f}%)",
            f"Number of codes in Fund Master missing from NAV History: {len(missing_in_nav)}",
        ]
        
        if missing_in_nav:
            report_lines.append("\nSample of missing AMFI codes (up to 10):")
            report_lines.append(str(list(missing_in_nav)[:10]))
        else:
            report_lines.append("\nSuccess: All codes in Fund Master successfully match with NAV History!")
            
        report_text = "\n".join(report_lines)
        print(report_text)
        
        # Determine reports output folder
        reports_dir = os.path.join("..", "reports")
        if not os.path.exists(reports_dir):
            reports_dir = os.path.join("reports")
            
        os.makedirs(reports_dir, exist_ok=True)
        report_file_path = os.path.join(reports_dir, "data_quality_report.txt")
        
        # Write report to file
        with open(report_file_path, "w") as f:
            f.write(report_text)
        print(f"\nData quality report successfully written to: {report_file_path}")
    else:
        print(f"Could not identify AMFI/scheme code columns automatically.")
        print(f"Found fund master code col: '{amfi_fund_col}', NAV history code col: '{amfi_nav_col}'")
else:
    print("\n[Warning] Both fund_master and nav_history files are required to perform code validation.")
