import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure Streamlit page layout
st.set_page_config(
    page_title="Bluestock Mutual Fund Capstone Dashboard",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "data", "db", "bluestock_mf.db")

if not os.path.exists(db_path):
    st.error(f"Database not found at: {db_path}")
    st.stop()

@st.cache_resource
def get_connection():
    return sqlite3.connect(db_path, check_same_thread=False)

conn = get_connection()

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

# Premium CSS customization
st.markdown("""
<style>
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .kpi-card-navy { border-top: 4px solid #1e3a8a; }
    .kpi-card-teal { border-top: 4px solid #0d8a72; }
    .kpi-card-coral { border-top: 4px solid #e66f50; }
    .kpi-card-gold { border-top: 4px solid #e6ad12; }
    
    .kpi-title {
        color: #64748b;
        font-size: 0.85em;
        font-weight: 700;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.55em;
        font-weight: 700;
        line-height: 1.2;
    }
</style>
""", unsafe_allow_html=True)

st.title(" Bluestock Mutual Fund Executive Dashboard")
st.markdown("Interactive Fund Analytics, Investor Demographics, and Performance Scorecard")

# Set up tabs for the 6 pages
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    " Industry Overview", 
    " Fund Performance", 
    " Investor Analytics", 
    " SIP & Market Trends",
    " Monte Carlo Simulation",
    " Portfolio Optimization "
])

# ==========================================
# PAGE 1: Industry Overview
# ==========================================
with tab1:
    st.header("Industry Overview & Market Scale")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-card kpi-card-navy"><div class="kpi-title">Total AUM (Industry)</div><div class="kpi-value" style="color:#1e3a8a;">₹81.00L Cr</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-card kpi-card-teal"><div class="kpi-title">SIP Inflow (Dec 25)</div><div class="kpi-value" style="color:#0d8a72;">₹31,002 Cr</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-card kpi-card-coral"><div class="kpi-title">Total Folio Count</div><div class="kpi-value" style="color:#e66f50;">26.12 Cr</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="kpi-card kpi-card-gold"><div class="kpi-title">Active Schemes</div><div class="kpi-value" style="color:#e6ad12;">1,908</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Visuals
    c1, c2 = st.columns(2)
    
    with c1:
        df_sip_trend = pd.read_sql_query("SELECT month, sip_aum_lakh_crore FROM fact_monthly_sip_inflows ORDER BY month", conn)
        fig_line = px.line(
            df_sip_trend, x='month', y='sip_aum_lakh_crore',
            title="Industry AUM Growth Trend (2022-2025)",
            labels={'month': 'Reporting Month (YYYY-MM)', 'sip_aum_lakh_crore': 'AUM (₹ Lakh Crore)'},
            color_discrete_sequence=['#0d8a72']
        )
        fig_line.update_traces(mode='lines+markers', marker=dict(color='#1e3a8a'))
        fig_line.update_layout(template="plotly_white")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with c2:
        df_aum = pd.read_sql_query("""
            SELECT fund_house, aum_lakh_crore 
            FROM fact_aum 
            WHERE date = '2025-12-31' 
            ORDER BY aum_lakh_crore DESC
        """, conn)
        df_aum['fund_house'] = df_aum['fund_house'].replace(amc_mapping)
        
        fig_bar = px.bar(
            df_aum, x='aum_lakh_crore', y='fund_house', orientation='h',
            title="Assets Under Management (AUM) by AMC (Dec 2025)",
            labels={'aum_lakh_crore': 'AUM (₹ Lakh Crore)', 'fund_house': 'Asset Management Company'},
            color='aum_lakh_crore', color_continuous_scale='Blues'
        )
        fig_bar.update_layout(template="plotly_white", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# PAGE 2: Fund Performance
# ==========================================
with tab2:
    st.header("Fund Performance & Scorecard")
    
    # Load Scorecard data
    scorecard_path = 'reports/fund_scorecard.csv'
    if not os.path.exists(scorecard_path):
        scorecard_path = '../reports/fund_scorecard.csv'
    
    if not os.path.exists(scorecard_path):
        st.error("### ❌ Fund Scorecard CSV File Not Found")
        st.markdown("""
        The file `fund_scorecard.csv` could not be located in your `reports/` directory on GitHub.
        Please make sure you have committed and pushed the files inside the `reports/` folder.
        """)
        st.stop()
        
    df_score = pd.read_csv(scorecard_path)
    
    # Page 2 KPI Cards
    p2_col1, p2_col2, p2_col3, p2_col4 = st.columns(4)
    with p2_col1:
        st.markdown('<div class="kpi-card kpi-card-navy"><div class="kpi-title">Top Ranked Fund</div><div class="kpi-value" style="color:#1e3a8a; font-size:1.3em;">Mirae Asset Large Cap</div></div>', unsafe_allow_html=True)
    with p2_col2:
        st.markdown('<div class="kpi-card kpi-card-teal"><div class="kpi-title">Best 3yr Return</div><div class="kpi-value" style="color:#0d8a72; font-size:1.3em;">35.10% (Axis Mid)</div></div>', unsafe_allow_html=True)
    with p2_col3:
        st.markdown('<div class="kpi-card kpi-card-coral"><div class="kpi-title">Highest Sharpe Ratio</div><div class="kpi-value" style="color:#e66f50; font-size:1.3em;">1.07 (Mirae Lg)</div></div>', unsafe_allow_html=True)
    with p2_col4:
        st.markdown('<div class="kpi-card kpi-card-gold"><div class="kpi-title">Average Expense Ratio</div><div class="kpi-value" style="color:#e6ad12; font-size:1.3em;">1.18%</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Top Slicers
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        amc_list = ["All"] + sorted(list(df_score['scheme_name'].apply(lambda x: x.split(' ')[0]).unique()))
        selected_amc = st.selectbox("Slicer: Fund House (AMC)", amc_list)
    with s_col2:
        cat_list = ["All"] + sorted(list(df_score['category'].unique()))
        selected_cat = st.selectbox("Slicer: Category", cat_list)
    with s_col3:
        plan_list = ["All", "Regular", "Direct"]
        selected_plan = st.selectbox("Slicer: Plan", plan_list)
        
    # Filter Data
    df_score_filtered = df_score.copy()
    if selected_amc != "All":
        df_score_filtered = df_score_filtered[df_score_filtered['scheme_name'].str.startswith(selected_amc)]
    if selected_cat != "All":
        df_score_filtered = df_score_filtered[df_score_filtered['category'] == selected_cat]
    if selected_plan != "All":
        df_score_filtered = df_score_filtered[df_score_filtered['scheme_name'].str.contains(selected_plan, case=False)]
        
    # Scatter return vs risk
    df_perf_raw = pd.read_sql_query("""
        SELECT f.scheme_name, f.category, p.return_3yr_pct, p.std_dev_ann_pct, p.aum_crore
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
    """, conn)
    
    # Filter raw performance too based on slicers
    df_perf_filtered = df_perf_raw.copy()
    if selected_amc != "All":
        df_perf_filtered = df_perf_filtered[df_perf_filtered['scheme_name'].str.startswith(selected_amc)]
    if selected_cat != "All":
        df_perf_filtered = df_perf_filtered[df_perf_filtered['category'] == selected_cat]
    if selected_plan != "All":
        df_perf_filtered = df_perf_filtered[df_perf_filtered['scheme_name'].str.contains(selected_plan, case=False)]
        
    pc1, pc2 = st.columns([1.3, 1.0])
    
    with pc1:
        fig_scatter = px.scatter(
            df_perf_filtered, x='return_3yr_pct', y='std_dev_ann_pct', color='category',
            size='aum_crore', hover_name='scheme_name',
            title="Risk (Volatility) vs Return Profile (Bubble size = AUM)",
            labels={'return_3yr_pct': '3-Year Annualised Return (%)', 'std_dev_ann_pct': 'Annualised Volatility (%)'},
            color_discrete_sequence=['#1e3a8a', '#e66f50', '#0d8a72']
        )
        fig_scatter.update_layout(template="plotly_white")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with pc2:
        st.subheader("Selected Fund NAV vs Benchmark")
        # List of funds matching filter
        fund_dropdown_list = df_score_filtered['scheme_name'].tolist()
        if fund_dropdown_list:
            selected_fund_name = st.selectbox("Select Fund for NAV Detail:", fund_dropdown_list)
            # Query NAV
            selected_code = df_score[df_score['scheme_name'] == selected_fund_name]['amfi_code'].values[0]
            df_fund_nav = pd.read_sql_query(f"""
                SELECT date, nav FROM fact_nav WHERE amfi_code = {selected_code} ORDER BY date
            """, conn)
            df_fund_nav['date'] = pd.to_datetime(df_fund_nav['date'])
            
            # Query Benchmark
            bench_name = pd.read_sql_query(f"SELECT benchmark FROM dim_fund WHERE amfi_code = {selected_code}", conn).iloc[0, 0]
            # Map benchmark name
            bench_map = {
                'NIFTY 50 TRI': 'NIFTY50',
                'NIFTY 100 TRI': 'NIFTY100',
                'NIFTY Midcap 150 TRI': 'NIFTY_MIDCAP150',
                'BSE 250 SmallCap TRI': 'BSE_SMALLCAP',
                'NIFTY 500 TRI': 'NIFTY500',
                'CRISIL Liquid Fund AI Index': 'CRISIL_LIQUID',
                'CRISIL Dynamic Gilt Index': 'CRISIL_GILT'
            }
            mapped_index = bench_map.get(bench_name, 'NIFTY50')
            
            df_bench_val = pd.read_sql_query(f"""
                SELECT date, close_value FROM fact_benchmark_indices WHERE index_name = '{mapped_index}' ORDER BY date
            """, conn)
            df_bench_val['date'] = pd.to_datetime(df_bench_val['date'])
            
            # Merge and normalize to 100
            df_nav_bench = pd.merge(df_fund_nav, df_bench_val, on='date').dropna()
            df_nav_bench['Fund NAV (Base 100)'] = (df_nav_bench['nav'] / df_nav_bench['nav'].iloc[0]) * 100
            df_nav_bench[f'{mapped_index} (Base 100)'] = (df_nav_bench['close_value'] / df_nav_bench['close_value'].iloc[0]) * 100
            
            fig_nav_line = px.line(
                df_nav_bench, x='date', y=['Fund NAV (Base 100)', f'{mapped_index} (Base 100)'],
                title=f"Relative Performance Growth: {selected_fund_name.split(' - ')[0]}",
                labels={'value': 'Normalized Growth (Base 100)', 'date': 'Date'},
                color_discrete_sequence=['#1e3a8a', '#e66f50']
            )
            fig_nav_line.update_layout(template="plotly_white", legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_nav_line, use_container_width=True)
        else:
            st.warning("No funds match current filters.")
            
    # Full Scorecard Table
    st.subheader("Sortable Fund Scorecard Table")
    
    # Create clean display table with shortened names
    df_score_display = df_score_filtered.copy()
    for amc, short_amc in amc_mapping.items():
        df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(amc, short_amc, regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Growth - Direct Plan', ' (Dir)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Growth - Regular Plan', ' (Reg)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Direct Plan - Growth Option', ' (Dir)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Regular Plan - Growth Option', ' (Reg)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Growth Option - Direct Plan', ' (Dir)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Growth Option - Regular Plan', ' (Reg)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Direct Plan', ' (Dir)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' - Regular Plan', ' (Reg)', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' Fund', ' Fnd', regex=False)
    df_score_display['scheme_name'] = df_score_display['scheme_name'].str.replace(' Plan', ' Pln', regex=False)
    
    st.dataframe(df_score_display, use_container_width=True)

# ==========================================
# PAGE 3: Investor Analytics
# ==========================================
with tab3:
    st.header("Investor Demographics & Transaction Volumes")
    
    # Page 3 KPI Cards
    p3_col1, p3_col2, p3_col3, p3_col4 = st.columns(4)
    with p3_col1:
        st.markdown('<div class="kpi-card kpi-card-navy"><div class="kpi-title">Retail Inflows (SIP)</div><div class="kpi-value" style="color:#1e3a8a;">65.2% (T30)</div></div>', unsafe_allow_html=True)
    with p3_col2:
        st.markdown('<div class="kpi-card kpi-card-teal"><div class="kpi-title">Peak Age Demographic</div><div class="kpi-value" style="color:#0d8a72;">26-35 Years (34.8%)</div></div>', unsafe_allow_html=True)
    with p3_col3:
        st.markdown('<div class="kpi-card kpi-card-coral"><div class="kpi-title">Average Transaction Size</div><div class="kpi-value" style="color:#e66f50;">₹4,250 (SIP)</div></div>', unsafe_allow_html=True)
    with p3_col4:
        st.markdown('<div class="kpi-card kpi-card-gold"><div class="kpi-title">Active Transacting States</div><div class="kpi-value" style="color:#e6ad12;">28 States</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Demographics Slicers
    is_col1, is_col2, is_col3 = st.columns(3)
    with is_col1:
        df_states = pd.read_sql_query("SELECT DISTINCT state FROM fact_transactions", conn)
        state_list = ["All"] + sorted(list(df_states['state'].dropna().unique()))
        selected_state = st.selectbox("Slicer: State", state_list)
    with is_col2:
        df_ages = pd.read_sql_query("SELECT DISTINCT age_group FROM fact_transactions", conn)
        age_list = ["All"] + sorted(list(df_ages['age_group'].dropna().unique()))
        selected_age = st.selectbox("Slicer: Age Group", age_list)
    with is_col3:
        df_tiers = pd.read_sql_query("SELECT DISTINCT city_tier FROM fact_transactions", conn)
        tier_list = ["All"] + sorted(list(df_tiers['city_tier'].dropna().unique()))
        selected_tier = st.selectbox("Slicer: City Tier", tier_list)
        
    # Query Transaction data with filters applied
    query_txn = "SELECT state, age_group, city_tier, transaction_type, amount_inr, transaction_date FROM fact_transactions WHERE 1=1"
    params = []
    if selected_state != "All":
        query_txn += " AND state = ?"
        params.append(selected_state)
    if selected_age != "All":
        query_txn += " AND age_group = ?"
        params.append(selected_age)
    if selected_tier != "All":
        query_txn += " AND city_tier = ?"
        params.append(selected_tier)
        
    df_txns_filtered = pd.read_sql_query(query_txn, conn, params=params)
    
    ic1, ic2, ic3 = st.columns(3)
    
    with ic1:
        # Bar chart state
        df_state_sum = df_txns_filtered[df_txns_filtered['transaction_type'] == 'SIP'].groupby('state')['amount_inr'].sum().reset_index()
        df_state_sum = df_state_sum.sort_values('amount_inr', ascending=False).head(10)
        
        fig_state = px.bar(
            df_state_sum, x='amount_inr', y='state', orientation='h',
            title="Top States by Aggregate SIP volume (INR)",
            labels={'amount_inr': 'Total SIP volume (₹)', 'state': 'State'},
            color_discrete_sequence=['#1e3a8a']
        )
        fig_state.update_layout(template="plotly_white", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_state, use_container_width=True)
        
    with ic2:
        # Donut split
        df_type_cnt = df_txns_filtered['transaction_type'].value_counts().reset_index()
        df_type_cnt.columns = ['transaction_type', 'count']
        
        fig_donut = px.pie(
            df_type_cnt, values='count', names='transaction_type', hole=0.4,
            title="Transaction Split (Donut)",
            color_discrete_sequence=['#1e3a8a', '#e66f50', '#0d8a72']
        )
        fig_donut.update_layout(template="plotly_white")
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with ic3:
        # Avg SIP size by age
        df_age_avg = df_txns_filtered[df_txns_filtered['transaction_type'] == 'SIP'].groupby('age_group')['amount_inr'].mean().reset_index()
        
        # Sort age categories properly
        age_order_map = {'18-25':1, '26-35':2, '36-45':3, '46-55':4, '56+':5}
        df_age_avg['order'] = df_age_avg['age_group'].map(age_order_map)
        df_age_avg = df_age_avg.sort_values('order')
        
        fig_age = px.bar(
            df_age_avg, x='age_group', y='amount_inr',
            title="Average SIP Amount by Age Group (INR)",
            labels={'amount_inr': 'Average SIP Amount (₹)', 'age_group': 'Age Group'},
            color_discrete_sequence=['#e66f50']
        )
        fig_age.update_layout(template="plotly_white")
        st.plotly_chart(fig_age, use_container_width=True)

# ==========================================
# PAGE 4: SIP & Market Trends
# ==========================================
with tab4:
    st.header("SIP & Market Linkage")
    
    # Page 4 KPI Cards
    p4_col1, p4_col2, p4_col3, p4_col4 = st.columns(4)
    with p4_col1:
        st.markdown('<div class="kpi-card kpi-card-navy"><div class="kpi-title">YoY SIP Growth</div><div class="kpi-value" style="color:#1e3a8a;">+42.5% (FY25)</div></div>', unsafe_allow_html=True)
    with p4_col2:
        st.markdown('<div class="kpi-card kpi-card-teal"><div class="kpi-title">All-Time High SIP Month</div><div class="kpi-value" style="color:#0d8a72; font-size:1.35em;">Dec 2025 (₹31,002 Cr)</div></div>', unsafe_allow_html=True)
    with p4_col3:
        st.markdown('<div class="kpi-card kpi-card-coral"><div class="kpi-title">Correlation (SIP vs Nifty)</div><div class="kpi-value" style="color:#e66f50;">0.94 (Strong Link)</div></div>', unsafe_allow_html=True)
    with p4_col4:
        st.markdown('<div class="kpi-card kpi-card-gold"><div class="kpi-title">Nifty Peak in Period</div><div class="kpi-value" style="color:#e6ad12;">27,798 (March 24)</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    tc1, tc2 = st.columns(2)
    
    with tc1:
        # Dual axis representation using Plotly
        df_sip_raw = pd.read_sql_query("SELECT month, sip_inflow_crore FROM fact_monthly_sip_inflows ORDER BY month", conn)
        df_nifty_raw = pd.read_sql_query("""
            SELECT STRFTIME('%Y-%m', date) as month, AVG(close_value) as avg_nifty
            FROM fact_benchmark_indices
            WHERE index_name = 'NIFTY50'
            GROUP BY month
            ORDER BY month
        """, conn)
        df_merged_trends = pd.merge(df_sip_raw, df_nifty_raw, on='month')
        
        fig_dual = go.Figure()
        
        # Add Bar for SIP Inflow
        fig_dual.add_trace(go.Bar(
            x=df_merged_trends['month'], y=df_merged_trends['sip_inflow_crore'],
            name="SIP Inflow (₹ Cr)",
            marker_color='#93c5fd', opacity=0.75,
            yaxis='y1'
        ))
        
        # Add Line for Nifty 50
        fig_dual.add_trace(go.Scatter(
            x=df_merged_trends['month'], y=df_merged_trends['avg_nifty'],
            name="Nifty 50 Index (average close)",
            line=dict(color='#e66f50', width=2.5),
            yaxis='y2'
        ))
        
        # Layout double axes
        fig_dual.update_layout(
            title=dict(text="Monthly SIP Inflows vs Nifty 50 Performance", font=dict(size=14, color='#1e3a8a')),
            xaxis=dict(title="Month (YYYY-MM)"),
            yaxis=dict(title=dict(text="SIP Inflow (₹ Crore)", font=dict(color="#1e3a8a")), tickfont=dict(color="#1e3a8a")),
            yaxis2=dict(title=dict(text="Nifty 50 Index Level", font=dict(color="#e66f50")), tickfont=dict(color="#e66f50"), overlaying='y', side='right'),
            template="plotly_white",
            legend=dict(orientation="h", y=-0.2, x=0.2)
        )
        
        st.plotly_chart(fig_dual, use_container_width=True)
        
    with tc2:
        # Heatmap
        df_cat_heatmap = pd.read_sql_query("SELECT month, category, net_inflow_crore FROM fact_category_inflows ORDER BY month", conn)
        df_pivot_heatmap = df_cat_heatmap.pivot(index='category', columns='month', values='net_inflow_crore')
        
        # Shorten categories on heatmap y-axis matching reports
        df_pivot_heatmap = df_pivot_heatmap.rename(index={
            'Sectoral/Thematic': 'Sectoral',
            'Large & Mid Cap': 'Large & Mid',
            'Value/Contra': 'Value',
            'Short Duration': 'Short Dur'
        })
        
        fig_heat = px.imshow(
            df_pivot_heatmap,
            title="Category Net Monthly Inflows Heatmap (₹ Crore)",
            labels=dict(x="Month", y="Category", color="Net Inflow (Cr)"),
            color_continuous_scale="YlGnBu"
        )
        fig_heat.update_layout(template="plotly_white")
        st.plotly_chart(fig_heat, use_container_width=True)
        
    # Top 5 Categories in FY25
    st.subheader("Top 5 Categories by Net Inflows (FY25: Apr 2024 - Mar 2025)")
    df_fy25 = pd.read_sql_query("""
        SELECT category, SUM(net_inflow_crore) as total_inflow
        FROM fact_category_inflows
        WHERE month BETWEEN '2024-04' AND '2025-03'
        GROUP BY category
        ORDER BY total_inflow DESC
        LIMIT 5
    """, conn)
    
    fig_fy25 = px.bar(
        df_fy25, x='category', y='total_inflow',
        labels={'category': 'Fund Category', 'total_inflow': 'Total Inflow (₹ Crore)'},
        color='total_inflow', color_continuous_scale='Greens'
    )
    fig_fy25.update_layout(template="plotly_white")
    st.plotly_chart(fig_fy25, use_container_width=True)

# ==========================================
# PAGE 5: Monte Carlo Simulation (B3)
# ==========================================
with tab5:
    st.header("Monte Carlo NAV Growth Simulation")
    st.markdown("""
    This simulator models the future NAV of a chosen mutual fund over a 5-year horizon (1,260 trading days) using **Geometric Brownian Motion (GBM)**.
    The simulation is based on the fund's historical daily return volatility and mean.
    
    $$dS_t = \\mu S_t dt + \\sigma S_t dW_t$$
    """)
    
    # Selection of Fund
    mc_fund_name = st.selectbox("Select Fund for Simulation:", df_score['scheme_name'].tolist(), key="mc_fund_sel")
    
    # Query NAV history for the selected fund
    mc_code = df_score[df_score['scheme_name'] == mc_fund_name]['amfi_code'].values[0]
    df_mc_nav = pd.read_sql_query(f"""
        SELECT date, nav FROM fact_nav WHERE amfi_code = {mc_code} ORDER BY date
    """, conn)
    
    if len(df_mc_nav) < 30:
        st.warning("Insufficient historical NAV data to perform Monte Carlo simulation.")
    else:
        df_mc_nav['date'] = pd.to_datetime(df_mc_nav['date'])
        df_mc_nav = df_mc_nav.sort_values('date')
        
        # Calculate daily returns
        df_mc_nav['daily_return'] = df_mc_nav['nav'].pct_change()
        returns = df_mc_nav['daily_return'].dropna()
        
        # Parameters computation
        mu_daily = returns.mean()
        sigma_daily = returns.std()
        
        # Annualized parameters
        mu_ann = mu_daily * 252
        sigma_ann = sigma_daily * np.sqrt(252)
        
        # Controls
        c1, c2, c3 = st.columns(3)
        with c1:
            initial_investment = st.number_input("Initial Investment (INR)", min_value=1000, max_value=10000000, value=100000, step=5000, key="mc_inv")
        with c2:
            num_simulations = st.slider("Number of Simulation Paths", min_value=100, max_value=2000, value=1000, step=100, key="mc_sims")
        with c3:
            horizon_years = st.slider("Simulation Horizon (Years)", min_value=1, max_value=5, value=5, step=1, key="mc_years")
            
        trading_days = int(horizon_years * 252)
        dt = 1 / 252
        
        # Run Simulation
        np.random.seed(42)  # For reproducible results
        
        drift = (mu_ann - 0.5 * (sigma_ann ** 2)) * dt
        shock = sigma_ann * np.sqrt(dt)
        
        # Z is (trading_days, num_simulations)
        Z = np.random.normal(0, 1, size=(trading_days, num_simulations))
        daily_growth_factors = np.exp(drift + shock * Z)
        
        # Cumulative product over time
        paths = np.zeros((trading_days + 1, num_simulations))
        paths[0, :] = initial_investment
        for t in range(1, trading_days + 1):
            paths[t, :] = paths[t - 1, :] * daily_growth_factors[t - 1, :]
            
        # Get percentiles
        p5 = np.percentile(paths, 5, axis=1)
        p50 = np.percentile(paths, 50, axis=1)
        p95 = np.percentile(paths, 95, axis=1)
        
        # Timeline
        last_date = df_mc_nav['date'].max()
        future_dates = pd.date_range(start=last_date, periods=trading_days + 1, freq='B')
        
        # Create simulation dataframe for plotting
        df_sim = pd.DataFrame({
            'Date': future_dates,
            'P5': p5,
            'Median (P50)': p50,
            'P95': p95
        })
        
        # Add sample paths
        sample_path_indices = np.random.choice(num_simulations, size=min(5, num_simulations), replace=False)
        for i, idx in enumerate(sample_path_indices):
            df_sim[f'Path {i+1}'] = paths[:, idx]
            
        # Plotly chart
        fig_mc = go.Figure()
        
        # Add shading between P5 and P95
        fig_mc.add_trace(go.Scatter(
            x=df_sim['Date'].tolist() + df_sim['Date'].tolist()[::-1],
            y=df_sim['P95'].tolist() + df_sim['P5'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(147, 197, 253, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='90% Uncertainty Band',
            hoverinfo='skip'
        ))
        
        # Add Median path
        fig_mc.add_trace(go.Scatter(
            x=df_sim['Date'], y=df_sim['Median (P50)'],
            line=dict(color='#1e3a8a', width=3),
            name='Median Path (50th Percentile)'
        ))
        
        # Add P95 path
        fig_mc.add_trace(go.Scatter(
            x=df_sim['Date'], y=df_sim['P95'],
            line=dict(color='#0d8a72', width=1.5, dash='dash'),
            name='Optimistic Path (95th Percentile)'
        ))
        
        # Add P5 path
        fig_mc.add_trace(go.Scatter(
            x=df_sim['Date'], y=df_sim['P5'],
            line=dict(color='#e66f50', width=1.5, dash='dash'),
            name='Pessimistic Path (5th Percentile)'
        ))
        
        # Add sample paths in gray
        for i in range(min(5, num_simulations)):
            fig_mc.add_trace(go.Scatter(
                x=df_sim['Date'], y=df_sim[f'Path {i+1}'],
                line=dict(color='#94a3b8', width=0.8),
                name=f'Sample Scenario {i+1}',
                showlegend=False
            ))
            
        fig_mc.update_layout(
            title=dict(text=f"5-Year Monte Carlo Projection for {mc_fund_name.split(' - ')[0]}", font=dict(size=14, color='#1e3a8a')),
            xaxis=dict(title="Timeline"),
            yaxis=dict(title="Investment Value (INR)"),
            template="plotly_white",
            legend=dict(orientation="h", y=-0.2, x=0.0)
        )
        st.plotly_chart(fig_mc, use_container_width=True)
        
        # Summary details
        final_p5 = p5[-1]
        final_p50 = p50[-1]
        final_p95 = p95[-1]
        
        c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
        with c_kpi1:
            st.metric("Drift (Annualised Return)", f"{mu_ann * 100:.2f}%")
        with c_kpi2:
            st.metric("Volatility (Annualised)", f"{sigma_ann * 100:.2f}%")
        with c_kpi3:
            gain_loss_ratio = (final_p50 / initial_investment - 1) * 100
            st.metric("Expected Return (Median)", f"₹{final_p50:,.2f}", f"{gain_loss_ratio:+.2f}%")
        with c_kpi4:
            prob_loss = np.mean(paths[-1, :] < initial_investment) * 100
            st.metric("Probability of Loss", f"{prob_loss:.1f}%", delta=f"{prob_loss:.1f}% risk", delta_color="inverse")
            
        st.markdown(f"""
        ###  Key Interpretation:
        * **Median Scenario (50% Probability)**: If the historical returns structure holds, your investment of **₹{initial_investment:,.2f}** is expected to grow to **₹{final_p50:,.2f}** in {horizon_years} years.
        * **Optimistic Scenario (95th Percentile)**: In a strong bull market, the value could reach **₹{final_p95:,.2f}**.
        * **Pessimistic Scenario (5th Percentile)**: In a severe market downturn, the value could drop to **₹{final_p5:,.2f}**.
        * **Value at Risk (VaR)**: The 95% 5-year Value at Risk is **₹{max(0, initial_investment - final_p5):,.2f}** (maximum expected loss with 95% confidence).
        """)

# ==========================================
# PAGE 6: Portfolio Optimization (B4)
# ==========================================
with tab6:
    st.header("Markowitz Portfolio Optimization & Efficient Frontier")
    st.markdown("""
    This optimizer calculates the **Modern Portfolio Theory (MPT) Efficient Frontier** for a set of selected funds.
    It simulates 5,000 random weight combinations to identify the **Maximum Sharpe Ratio** portfolio and the **Minimum Volatility** portfolio.
    """)
    
    # Fund Selector
    available_funds = df_score['scheme_name'].tolist()
    default_funds = available_funds[:5] if len(available_funds) >= 5 else available_funds
    
    selected_opt_funds = st.multiselect(
        "Select exactly 5 funds for optimization:",
        options=available_funds,
        default=default_funds,
        key="opt_funds_sel"
    )
    
    if len(selected_opt_funds) != 5:
        st.warning(f"Please select exactly 5 funds to run the optimizer. Currently selected: {len(selected_opt_funds)}")
    else:
        # Load NAV histories and compute daily returns
        list_dfs = []
        for fund_name in selected_opt_funds:
            code = df_score[df_score['scheme_name'] == fund_name]['amfi_code'].values[0]
            df_nav_f = pd.read_sql_query(f"""
                SELECT date, nav FROM fact_nav WHERE amfi_code = {code} ORDER BY date
            """, conn)
            df_nav_f['date'] = pd.to_datetime(df_nav_f['date'])
            df_nav_f = df_nav_f.sort_values('date')
            
            # Short name for column
            short_name = fund_name.split(' - ')[0]
            df_nav_f = df_nav_f.rename(columns={'nav': short_name})
            list_dfs.append(df_nav_f[['date', short_name]])
            
        # Merge all dataframes on Date
        df_merged_nav = list_dfs[0]
        for df_next in list_dfs[1:]:
            df_merged_nav = pd.merge(df_merged_nav, df_next, on='date', how='inner')
            
        if len(df_merged_nav) < 30:
            st.warning("Insufficient overlapping date range for the selected funds to compute correlations.")
        else:
            df_merged_nav = df_merged_nav.sort_values('date')
            fund_cols = [c for c in df_merged_nav.columns if c != 'date']
            
            # Compute daily returns
            df_returns = df_merged_nav[fund_cols].pct_change().dropna()
            
            # Compute annualized mean returns and covariance matrix
            mean_returns = df_returns.mean() * 252
            cov_matrix = df_returns.cov() * 252
            
            # Risk free rate input
            rf_rate = st.slider("Risk-Free Rate (Annualised)", min_value=0.0, max_value=0.10, value=0.06, step=0.005, format="%.3f")
            
            # Monte Carlo Simulation of Portfolios
            num_portfolios = 5000
            np.random.seed(42)
            
            results = np.zeros((3 + len(fund_cols), num_portfolios))
            weights_record = []
            
            for i in range(num_portfolios):
                weights = np.random.random(len(fund_cols))
                weights /= np.sum(weights)
                weights_record.append(weights)
                
                # Portfolio Return
                p_ret = np.sum(weights * mean_returns)
                
                # Portfolio Volatility
                p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                
                # Portfolio Sharpe Ratio
                p_sharpe = (p_ret - rf_rate) / p_vol
                
                results[0, i] = p_ret
                results[1, i] = p_vol
                results[2, i] = p_sharpe
                for j in range(len(weights)):
                    results[3 + j, i] = weights[j]
                    
            # Create a dataframe for results
            df_results = pd.DataFrame(results.T, columns=['Return', 'Volatility', 'Sharpe'] + fund_cols)
            
            # Find key portfolios
            max_sharpe_idx = df_results['Sharpe'].idxmax()
            max_sharpe_portfolio = df_results.iloc[max_sharpe_idx]
            
            min_vol_idx = df_results['Volatility'].idxmin()
            min_vol_portfolio = df_results.iloc[min_vol_idx]
            
            # Plots
            # 1. Efficient Frontier Scatter Plot
            fig_ef = px.scatter(
                df_results, x='Volatility', y='Return', color='Sharpe',
                color_continuous_scale='Viridis',
                title="Efficient Frontier (5,000 Simulated Portfolios)",
                labels={'Volatility': 'Annualised Volatility', 'Return': 'Annualised Return', 'Sharpe': 'Sharpe Ratio'},
                hover_data=fund_cols
            )
            
            # Formatting markers
            fig_ef.update_traces(marker=dict(size=4, opacity=0.7))
            
            # Add Max Sharpe portfolio point
            fig_ef.add_trace(go.Scatter(
                x=[max_sharpe_portfolio['Volatility']],
                y=[max_sharpe_portfolio['Return']],
                mode='markers',
                marker=dict(color='#e66f50', size=14, symbol='star', line=dict(color='black', width=2)),
                name='Max Sharpe Ratio Portfolio'
            ))
            
            # Add Min Volatility portfolio point
            fig_ef.add_trace(go.Scatter(
                x=[min_vol_portfolio['Volatility']],
                y=[min_vol_portfolio['Return']],
                mode='markers',
                marker=dict(color='#0d8a72', size=14, symbol='star', line=dict(color='black', width=2)),
                name='Minimum Variance Portfolio'
            ))
            
            fig_ef.update_layout(
                template="plotly_white",
                legend=dict(orientation="h", y=-0.2, x=0.0),
                coloraxis_colorbar=dict(title="Sharpe Ratio", yanchor="top", y=1, x=1.05)
            )
            st.plotly_chart(fig_ef, use_container_width=True)
            
            # Optimal Portfolios Details
            ec1, ec2 = st.columns(2)
            
            with ec1:
                st.subheader(" Maximum Sharpe Ratio Portfolio")
                st.markdown(f"**Annualised Return:** {max_sharpe_portfolio['Return'] * 100:.2f}%")
                st.markdown(f"**Annualised Volatility (Risk):** {max_sharpe_portfolio['Volatility'] * 100:.2f}%")
                st.markdown(f"**Sharpe Ratio:** {max_sharpe_portfolio['Sharpe']:.3f}")
                
                # Weights table
                max_w_df = pd.DataFrame({
                    'Asset': fund_cols,
                    'Weight (%)': [max_sharpe_portfolio[col] * 100 for col in fund_cols]
                })
                max_w_df['Weight (%)'] = max_w_df['Weight (%)'].round(2)
                st.dataframe(max_w_df, use_container_width=True)
                
            with ec2:
                st.subheader(" Minimum Volatility Portfolio")
                st.markdown(f"**Annualised Return:** {min_vol_portfolio['Return'] * 100:.2f}%")
                st.markdown(f"**Annualised Volatility (Risk):** {min_vol_portfolio['Volatility'] * 100:.2f}%")
                st.markdown(f"**Sharpe Ratio:** {min_vol_portfolio['Sharpe']:.3f}")
                
                # Weights table
                min_w_df = pd.DataFrame({
                    'Asset': fund_cols,
                    'Weight (%)': [min_vol_portfolio[col] * 100 for col in fund_cols]
                })
                min_w_df['Weight (%)'] = min_w_df['Weight (%)'].round(2)
                st.dataframe(min_w_df, use_container_width=True)
                
            # Weight Comparison Bar Chart
            df_compare_w = pd.DataFrame({
                'Fund': fund_cols * 2,
                'Weight (%)': [max_sharpe_portfolio[col] * 100 for col in fund_cols] + [min_vol_portfolio[col] * 100 for col in fund_cols],
                'Portfolio': ['Max Sharpe'] * len(fund_cols) + ['Min Volatility'] * len(fund_cols)
            })
            
            fig_w_bar = px.bar(
                df_compare_w, x='Fund', y='Weight (%)', color='Portfolio', barmode='group',
                title="Optimal Asset Allocation Comparison",
                color_discrete_sequence=['#e66f50', '#0d8a72']
            )
            fig_w_bar.update_layout(template="plotly_white")
            st.plotly_chart(fig_w_bar, use_container_width=True)
