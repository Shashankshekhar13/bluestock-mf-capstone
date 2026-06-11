import os
import sys
import sqlite3
import argparse
import pandas as pd

def get_db_path():
    db_path = 'data/db/bluestock_mf.db'
    if not os.path.exists(db_path):
        db_path = '../data/db/bluestock_mf.db'
    if not os.path.exists(db_path):
        db_path = 'bluestock_mf.db'
    if not os.path.exists(db_path):
        db_path = '../bluestock_mf.db'
    return db_path

def recommend_funds(risk_appetite):
    risk_appetite = risk_appetite.strip().lower()
    
    # Map risk appetite to database risk_grade values
    if risk_appetite == 'low':
        grades = ["Low"]
    elif risk_appetite == 'moderate':
        grades = ["Moderate", "Moderately High"]
    elif risk_appetite == 'high':
        grades = ["High", "Very High"]
    else:
        print(f"Error: Invalid risk appetite '{risk_appetite}'. Must be Low, Moderate, or High.")
        return None
        
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}.")
        return None
        
    conn = sqlite3.connect(db_path)
    
    # Query DIM_FUND and FACT_PERFORMANCE
    query = """
        SELECT p.amfi_code, f.scheme_name, f.category, p.sharpe_ratio, p.risk_grade, p.aum_crore
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        WHERE p.risk_grade IN ({})
        ORDER BY p.sharpe_ratio DESC
        LIMIT 3
    """.format(','.join('?' for _ in grades))
    
    df = pd.read_sql_query(query, conn, params=grades)
    conn.close()
    
    return df

# ANSI Color Codes
C_BLUE = "\033[1;34m"
C_CYAN = "\033[1;36m"
C_GREEN = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

def init_ansi():
    # Enable ANSI escape codes on Windows console
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # 7 = ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def main():
    init_ansi()
    
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund - Fund Recommender Engine")
    parser.add_argument(
        '-r', '--risk', 
        choices=['low', 'moderate', 'high', 'Low', 'Moderate', 'High'],
        help="Investor risk appetite (Low / Moderate / High)"
    )
    
    args = parser.parse_args()
    
    risk_appetite = args.risk
    if not risk_appetite:
        print(f"{C_BLUE}=" * 65)
        print(f"       {C_BOLD}{C_CYAN}BLUESTOCK MUTUAL FUND - RECOMMENDATION ENGINE{C_RESET}")
        print(f"{C_BLUE}=" * 65 + C_RESET)
        try:
            risk_appetite = input(f"{C_BOLD}{C_YELLOW}Enter your Risk Appetite (Low / Moderate / High): {C_RESET}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
            
    df_recs = recommend_funds(risk_appetite)
    
    if df_recs is not None and not df_recs.empty:
        appetite_upper = risk_appetite.strip().upper()
        
        # Color match risk appetite
        app_color = C_GREEN if appetite_upper == 'LOW' else (C_YELLOW if appetite_upper == 'MODERATE' else C_RED)
        
        print("\n" + f"{C_BLUE}=" * 75)
        print(f"  *** {C_BOLD}{C_CYAN}TOP 3 RECOMMENDATIONS FOR {app_color}'{appetite_upper}'{C_CYAN} RISK APPETITE{C_RESET} ***")
        print(f"{C_BLUE}=" * 75 + C_RESET)
        
        for idx, row in df_recs.iterrows():
            rank = idx + 1
            scheme_clean = row['scheme_name'].split(' - ')[0]
            
            # Print card block
            print(f" {C_BOLD}{C_GREEN}[Rank {rank}]{C_RESET} {C_BOLD}{C_CYAN}{scheme_clean}{C_RESET}")
            print(f"   {C_BLUE}->{C_RESET} AMFI Code    : {C_BOLD}{row['amfi_code']}{C_RESET}")
            print(f"   {C_BLUE}->{C_RESET} Category     : {row['category']}")
            print(f"   {C_BLUE}->{C_RESET} Risk Grade   : {app_color}{row['risk_grade']}{C_RESET}")
            print(f"   {C_BLUE}->{C_RESET} Sharpe Ratio : {C_BOLD}{C_GREEN}{row['sharpe_ratio']:.2f}{C_RESET}")
            
            aum_val = f"Rs {row['aum_crore']:,.1f} Cr" if pd.notnull(row['aum_crore']) else 'N/A'
            print(f"   {C_BLUE}->{C_RESET} Fund AUM     : {C_BOLD}{C_YELLOW}{aum_val}{C_RESET}")
            
            if rank < 3:
                print(f" {C_BLUE}-" * 75 + C_RESET)
                
        print(f"{C_BLUE}=" * 75 + C_RESET + "\n")
    elif df_recs is not None:
        print(f"\n{C_RED}No funds found matching risk categories for appetite '{risk_appetite}'.{C_RESET}\n")

if __name__ == '__main__':
    main()
