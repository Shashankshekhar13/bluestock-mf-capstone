import os
import sqlite3
import pandas as pd
from datetime import datetime

def get_db_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    db_path = os.path.join(project_root, "data", "db", "bluestock_mf.db")
    if not os.path.exists(db_path):
        db_path = os.path.join(project_root, "bluestock_mf.db")
    return db_path

def generate_email():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    
    # 1. Fetch Top 3 Funds by 3-Year CAGR
    query_cagr = """
        SELECT p.amfi_code, f.scheme_name, f.category, p.return_3yr_pct, p.sharpe_ratio, p.aum_crore
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.return_3yr_pct DESC
        LIMIT 3
    """
    df_cagr = pd.read_sql_query(query_cagr, conn)
    
    # 2. Fetch Top 3 Funds by Sharpe Ratio
    query_sharpe = """
        SELECT p.amfi_code, f.scheme_name, f.category, p.return_3yr_pct, p.sharpe_ratio, p.aum_crore
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.sharpe_ratio DESC
        LIMIT 3
    """
    df_sharpe = pd.read_sql_query(query_sharpe, conn)
    
    # 3. Fetch latest SIP inflow data
    query_sip = """
        SELECT month, sip_inflow_crore, active_sip_accounts_crore, new_sip_accounts_lakh, sip_aum_lakh_crore
        FROM fact_monthly_sip_inflows
        ORDER BY month DESC
        LIMIT 3
    """
    df_sip = pd.read_sql_query(query_sip, conn)
    
    # 4. Fetch top categories by net inflows
    query_categories = """
        SELECT category, net_inflow_crore
        FROM fact_category_inflows
        WHERE month = (SELECT MAX(month) FROM fact_category_inflows)
        ORDER BY net_inflow_crore DESC
        LIMIT 3
    """
    df_categories = pd.read_sql_query(query_categories, conn)
    latest_cat_month = pd.read_sql_query("SELECT MAX(month) as max_m FROM fact_category_inflows", conn).iloc[0,0]
    
    conn.close()
    
    # Prepare data for rendering
    # Latest SIP figures
    latest_sip = df_sip.iloc[0] if not df_sip.empty else None
    
    # Build HTML Content
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bluestock Weekly Mutual Fund Intelligence</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f8fafc;
            color: #334155;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }}
        .wrapper {{
            width: 100%;
            background-color: #f8fafc;
            padding: 30px 0;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
            border: 1px solid #e2e8f0;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
            padding: 35px 30px;
            text-align: center;
            color: #ffffff;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .header p {{
            margin: 5px 0 0 0;
            color: #93c5fd;
            font-size: 14px;
            font-weight: 500;
        }}
        .content {{
            padding: 30px;
        }}
        .intro-text {{
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 25px;
            color: #475569;
        }}
        .kpi-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            gap: 12px;
        }}
        .kpi-card {{
            flex: 1;
            background-color: #f1f5f9;
            border-top: 4px solid #1e3a8a;
            border-radius: 6px;
            padding: 15px 10px;
            text-align: center;
        }}
        .kpi-card.accent {{
            border-top-color: #0d8a72;
        }}
        .kpi-card.coral {{
            border-top-color: #e66f50;
        }}
        .kpi-title {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }}
        .kpi-value {{
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #1e3a8a;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #cbd5e1;
            padding-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .fund-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
        }}
        .fund-table th {{
            text-align: left;
            padding: 10px 12px;
            font-size: 12px;
            font-weight: 700;
            color: #475569;
            background-color: #f8fafc;
            border-bottom: 2px solid #e2e8f0;
        }}
        .fund-table td {{
            padding: 12px;
            font-size: 13.5px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .fund-name {{
            font-weight: 600;
            color: #1e293b;
        }}
        .fund-meta {{
            font-size: 11px;
            color: #64748b;
            margin-top: 2px;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 6px;
            font-size: 10.5px;
            font-weight: 600;
            border-radius: 4px;
            background-color: #dbeafe;
            color: #1e40af;
        }}
        .badge.success {{
            background-color: #dcfce7;
            color: #15803d;
        }}
        .metric-highlight {{
            font-weight: 700;
            color: #0f172a;
        }}
        .bullet-list {{
            padding-left: 20px;
            margin: 0 0 25px 0;
        }}
        .bullet-list li {{
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 8px;
            color: #334155;
        }}
        .footer {{
            background-color: #f1f5f9;
            padding: 25px 30px;
            text-align: center;
            font-size: 12px;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .footer a {{
            color: #1e3a8a;
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>BLUESTOCK MUTUAL FUND</h1>
                <p>Weekly Market Intelligence & Analytics Dashboard</p>
            </div>
            
            <!-- Content -->
            <div class="content">
                <div class="intro-text">
                    Dear Investment Partner,<br><br>
                    Welcome to this week's <strong>Bluestock Mutual Fund Report</strong>. Below is a curated summary of industry scale, category dynamics, and top-ranked fund performances to aid your strategic asset allocation.
                </div>
                
                <!-- KPI Section -->
                <div class="kpi-row">
                    <div class="kpi-card">
                        <div class="kpi-title">Monthly SIP Inflow</div>
                        <div class="kpi-value">₹{latest_sip['sip_inflow_crore']:,.0f} Cr</div>
                    </div>
                    <div class="kpi-card accent">
                        <div class="kpi-title">Active SIPs</div>
                        <div class="kpi-value">{latest_sip['active_sip_accounts_crore']:.2f} Cr</div>
                    </div>
                    <div class="kpi-card coral">
                        <div class="kpi-title">Industry SIP AUM</div>
                        <div class="kpi-value">₹{latest_sip['sip_aum_lakh_crore']:.2f}L Cr</div>
                    </div>
                </div>
                
                <!-- Top Performing Section -->
                <div class="section-title">Top 3 Funds by 3-Year CAGR</div>
                <table class="fund-table">
                    <thead>
                        <tr>
                            <th>Scheme Name</th>
                            <th>Category</th>
                            <th style="text-align: right;">3Yr CAGR (%)</th>
                            <th style="text-align: right;">Sharpe</th>
                        </tr>
                    </thead>
                    <tbody>"""
                    
    for _, row in df_cagr.iterrows():
        short_scheme = row['scheme_name'].split(' - ')[0]
        html += f"""
                        <tr>
                            <td>
                                <div class="fund-name">{short_scheme}</div>
                                <div class="fund-meta">AMFI: {row['amfi_code']}</div>
                            </td>
                            <td><span class="badge">{row['category']}</span></td>
                            <td style="text-align: right;" class="metric-highlight">{row['return_3yr_pct']*100:.2f}%</td>
                            <td style="text-align: right;">{row['sharpe_ratio']:.2f}</td>
                        </tr>"""
                        
    html += """
                    </tbody>
                </table>
                
                <!-- Highest Sharpe Ratio Section -->
                <div class="section-title">Top 3 Funds by Sharpe Ratio (Risk-Adjusted Return)</div>
                <table class="fund-table">
                    <thead>
                        <tr>
                            <th>Scheme Name</th>
                            <th>Category</th>
                            <th style="text-align: right;">Sharpe Ratio</th>
                            <th style="text-align: right;">AUM (₹ Cr)</th>
                        </tr>
                    </thead>
                    <tbody>"""
                    
    for _, row in df_sharpe.iterrows():
        short_scheme = row['scheme_name'].split(' - ')[0]
        html += f"""
                        <tr>
                            <td>
                                <div class="fund-name">{short_scheme}</div>
                                <div class="fund-meta">AMFI: {row['amfi_code']}</div>
                            </td>
                            <td><span class="badge success">{row['category']}</span></td>
                            <td style="text-align: right;" class="metric-highlight">{row['sharpe_ratio']:.2f}</td>
                            <td style="text-align: right;">₹{row['aum_crore']:,.0f}</td>
                        </tr>"""
                        
    html += f"""
                    </tbody>
                </table>
                
                <!-- Market Context / Dynamics -->
                <div class="section-title">Category Inflow Dynamics ({latest_cat_month})</div>
                <ul class="bullet-list">"""
                
    for _, row in df_categories.iterrows():
        html += f"""
                    <li><strong>{row['category']}</strong> recorded net monthly inflows of <strong>₹{row['net_inflow_crore']:,.1f} Crore</strong>.</li>"""
                    
    html += f"""
                </ul>
                
                <div class="intro-text" style="margin-top: 25px;">
                    For interactive projections, risk modeling (Monte Carlo), and portfolio frontiers (Markowitz optimization), please launch the **Bluestock Mutual Fund Executive Dashboard** locally.
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>This report is programmatically compiled on {datetime.now().strftime('%B %d, %Y')} via the Bluestock ETL Pipeline.</p>
                <p>&copy; {datetime.now().year} Bluestock Mutual Fund Analytics. Confidential - Internal Use Only.</p>
                <p><a href="#">Access Analytics Dashboard</a> | <a href="#">Unsubscribe</a></p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "weekly_report.html")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"[SUCCESS] HTML Email Report successfully generated at {output_path}")
    return True

if __name__ == '__main__':
    generate_email()
