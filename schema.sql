-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Drop tables if they exist to start fresh
DROP TABLE IF EXISTS fact_portfolio_holdings;
DROP TABLE IF EXISTS fact_benchmark_indices;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_monthly_sip_inflows;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_industry_folio_count;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;

-- 1. Dimension Table: Fund Master
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. Dimension Table: Date
CREATE TABLE dim_date (
    date TEXT PRIMARY KEY, -- format: YYYY-MM-DD
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0 (Monday) to 6 (Sunday)
    day_name TEXT NOT NULL,
    month_name TEXT NOT NULL,
    is_weekend INTEGER NOT NULL -- 0 or 1
);

-- 3. Fact Table: NAV History (Daily)
CREATE TABLE fact_nav (
    amfi_code INTEGER NOT NULL,
    date TEXT NOT NULL,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 4. Fact Table: Investor Transactions
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT, -- Verified, Pending
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

-- 5. Fact Table: Scheme Performance (Latest)
CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT,
    plan TEXT,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE
);

-- 6. Fact Table: AUM by Fund House (Quarterly/Monthly)
CREATE TABLE fact_aum (
    date TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    PRIMARY KEY (date, fund_house),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 7. Fact Table: Monthly SIP Inflows
CREATE TABLE fact_monthly_sip_inflows (
    month TEXT PRIMARY KEY, -- format: YYYY-MM
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- 8. Fact Table: Category Inflows
CREATE TABLE fact_category_inflows (
    month TEXT NOT NULL, -- format: YYYY-MM
    category TEXT NOT NULL,
    net_inflow_crore REAL,
    PRIMARY KEY (month, category)
);

-- 9. Fact Table: Industry Folio Count
CREATE TABLE fact_industry_folio_count (
    month TEXT PRIMARY KEY, -- format: YYYY-MM
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- 10. Fact Table: Portfolio Holdings (Latest snapshots)
CREATE TABLE fact_portfolio_holdings (
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol, portfolio_date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code) ON DELETE CASCADE,
    FOREIGN KEY (portfolio_date) REFERENCES dim_date(date)
);

-- 11. Fact Table: Benchmark Indices (Daily Close)
CREATE TABLE fact_benchmark_indices (
    date TEXT NOT NULL,
    index_name TEXT NOT NULL,
    close_value REAL,
    PRIMARY KEY (date, index_name),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- Indexes for performance optimization
CREATE INDEX idx_nav_date ON fact_nav (date);
CREATE INDEX idx_transactions_fund ON fact_transactions (amfi_code);
CREATE INDEX idx_transactions_date ON fact_transactions (transaction_date);
CREATE INDEX idx_transactions_state ON fact_transactions (state);
CREATE INDEX idx_holdings_sector ON fact_portfolio_holdings (sector);
CREATE INDEX idx_holdings_fund ON fact_portfolio_holdings (amfi_code);
CREATE INDEX idx_benchmark_index_date ON fact_benchmark_indices (index_name, date);
