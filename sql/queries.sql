
SELECT 
    scheme_name, 
    amfi_code, 
    category,
    ROUND(aum_crore, 2) AS aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;


SELECT 
    f.scheme_name, 
    f.amfi_code, 
    d.year, 
    d.month_name, 
    ROUND(AVG(n.nav), 4) AS average_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date
GROUP BY f.amfi_code, d.year, d.month
ORDER BY f.scheme_name, d.year, d.month;


SELECT 
    t1.month AS current_month,
    ROUND(t1.sip_inflow_crore, 2) AS current_inflow_crore,
    t2.month AS prior_year_month,
    ROUND(t2.sip_inflow_crore, 2) AS prior_year_inflow_crore,
    ROUND(t1.yoy_growth_pct, 2) AS recorded_yoy_growth_pct,
    ROUND(((t1.sip_inflow_crore - t2.sip_inflow_crore) / t2.sip_inflow_crore) * 100, 2) AS calculated_yoy_growth_pct
FROM fact_monthly_sip_inflows t1
LEFT JOIN fact_monthly_sip_inflows t2 
    ON CAST(SUBSTR(t1.month, 1, 4) AS INTEGER) = CAST(SUBSTR(t2.month, 1, 4) AS INTEGER) + 1
    AND SUBSTR(t1.month, 6, 2) = SUBSTR(t2.month, 6, 2)
ORDER BY current_month;


SELECT 
    state, 
    COUNT(*) AS total_transactions, 
    ROUND(AVG(amount_inr), 2) AS avg_transaction_amount_inr,
    ROUND(SUM(amount_inr), 2) AS total_transaction_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_transaction_amount_inr DESC;



SELECT 
    amfi_code, 
    scheme_name, 
    category,
    ROUND(expense_ratio_pct, 2) AS expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;



SELECT 
    sector, 
    ROUND(SUM(weight_pct), 2) AS total_weight_pct,
    ROUND(AVG(weight_pct), 2) AS avg_weight_per_fund_pct,
    COUNT(DISTINCT amfi_code) AS fund_count
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC
LIMIT 5;


SELECT 
    kyc_status, 
    transaction_type, 
    COUNT(*) AS transaction_count, 
    ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM fact_transactions
GROUP BY kyc_status, transaction_type
ORDER BY kyc_status, total_amount_inr DESC;


SELECT 
    f.scheme_name, 
    f.amfi_code, 
    d.year, 
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    ROUND(MAX(n.nav) - MIN(n.nav), 4) AS nav_range,
    ROUND(AVG(n.nav * n.nav) - AVG(n.nav) * AVG(n.nav), 4) AS nav_variance
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date
GROUP BY f.amfi_code, d.year, d.month
ORDER BY f.scheme_name, d.year, d.month;



WITH fund_returns AS (
    SELECT 
        n.amfi_code,
        f.scheme_name,
        f.benchmark,
        MIN(CASE WHEN strftime('%Y', n.date) = '2025' THEN n.nav END) AS start_nav,
        MAX(CASE WHEN strftime('%Y', n.date) = '2025' THEN n.nav END) AS end_nav
    FROM fact_nav n
    JOIN dim_fund f ON n.amfi_code = f.amfi_code
    GROUP BY n.amfi_code
),
benchmark_mapped AS (
    SELECT 
        amfi_code,
        scheme_name,
        benchmark,
        CASE benchmark
            WHEN 'NIFTY 50 TRI' THEN 'NIFTY50'
            WHEN 'NIFTY 100 TRI' THEN 'NIFTY100'
            WHEN 'NIFTY Midcap 150 TRI' THEN 'NIFTY_MIDCAP150'
            WHEN 'BSE 250 SmallCap TRI' THEN 'BSE_SMALLCAP'
            WHEN 'NIFTY 500 TRI' THEN 'NIFTY500'
            WHEN 'CRISIL Liquid Fund AI Index' THEN 'CRISIL_LIQUID'
            WHEN 'CRISIL Dynamic Gilt Index' THEN 'CRISIL_GILT'
            ELSE NULL
        END AS mapped_index,
        start_nav,
        end_nav
    FROM fund_returns
),
bench_returns AS (
    SELECT 
        index_name,
        MIN(CASE WHEN strftime('%Y', date) = '2025' THEN close_value END) AS start_idx,
        MAX(CASE WHEN strftime('%Y', date) = '2025' THEN close_value END) AS end_idx
    FROM fact_benchmark_indices
    GROUP BY index_name
)
SELECT 
    bm.scheme_name,
    bm.benchmark AS benchmark_name,
    ROUND(((bm.end_nav - bm.start_nav) / bm.start_nav) * 100, 2) AS fund_return_2025_pct,
    ROUND(((br.end_idx - br.start_idx) / br.start_idx) * 100, 2) AS benchmark_return_2025_pct
FROM benchmark_mapped bm
LEFT JOIN bench_returns br ON bm.mapped_index = br.index_name
WHERE bm.mapped_index IS NOT NULL
ORDER BY fund_return_2025_pct DESC;


SELECT 
    fund_house,
    MIN(date) AS start_date,
    ROUND(MIN(aum_crore), 2) AS start_aum_crore,
    MAX(date) AS end_date,
    ROUND(MAX(aum_crore), 2) AS end_aum_crore,
    ROUND(MAX(aum_crore) - MIN(aum_crore), 2) AS aum_growth_crore,
    ROUND(((MAX(aum_crore) - MIN(aum_crore)) / MIN(aum_crore)) * 100, 2) AS growth_pct
FROM fact_aum
GROUP BY fund_house
ORDER BY growth_pct DESC;
