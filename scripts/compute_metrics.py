import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_db_path():
    db_path = 'data/db/bluestock_mf.db'
    if not os.path.exists(db_path):
        db_path = '../data/db/bluestock_mf.db'
    return db_path

# Standard AMC name mapping to shorten names in visual reports
amc_mapping = {
    'SBI Mutual Fund': 'SBI MF',
    'ICICI Prudential Mutual Fund': 'ICICI Pru MF',
    'ICICI Prudential MF': 'ICICI Pru MF',
    'HDFC Mutual Fund': 'HDFC MF',
    'Nippon India Mutual Fund': 'Nippon India MF',
    'Nippon India MF': 'Nippon India MF',
    'Kotak Mahindra Mutual Fund': 'Kotak MF',
    'Kotak Mahindra MF': 'Kotak MF',
    'Aditya Birla Sun Life Mutual Fund': 'Aditya Birla MF',
    'Aditya Birla Sun Life MF': 'Aditya Birla MF',
    'UTI Mutual Fund': 'UTI MF',
    'Axis Mutual Fund': 'Axis MF',
    'Mirae Asset Mutual Fund': 'Mirae Asset MF',
    'Mirae Asset MF': 'Mirae Asset MF',
    'DSP Mutual Fund': 'DSP MF'
}

def calculate_all_metrics():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    
    # 1. Historical VaR & CVaR (95%)
    print("Computing Value at Risk (VaR) & CVaR...")
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
    
    os.makedirs('reports', exist_ok=True)
    os.makedirs('../reports', exist_ok=True)
    df_report.to_csv('reports/var_cvar_report.csv', index=False)
    df_report.to_csv('../reports/var_cvar_report.csv', index=False)
    
    # 2. Rolling 90-day Sharpe Ratio
    print("Generating rolling Sharpe ratio chart...")
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
    
    os.makedirs('reports/plots', exist_ok=True)
    os.makedirs('../reports/plots', exist_ok=True)
    plt.savefig('reports/plots/rolling_sharpe_chart.png', dpi=150)
    plt.savefig('../reports/plots/rolling_sharpe_chart.png', dpi=150)
    plt.close()
    
    conn.close()
    print("All advanced analytics metrics computed and saved successfully.")

if __name__ == '__main__':
    calculate_all_metrics()
