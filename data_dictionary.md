# Bluestock Mutual Fund Database Data Dictionary

This document provides a detailed definition of all tables, columns, data types, business definitions, and sources loaded into the SQLite database (`bluestock_mf.db`).

---

## Table of Contents
1. [dim_fund](#dim_fund)
2. [dim_date](#dim_date)
3. [fact_nav](#fact_nav)
4. [fact_transactions](#fact_transactions)
5. [fact_performance](#fact_performance)
6. [fact_aum](#fact_aum)
7. [fact_monthly_sip_inflows](#fact_monthly_sip_inflows)
8. [fact_category_inflows](#fact_category_inflows)
9. [fact_industry_folio_count](#fact_industry_folio_count)
10. [fact_portfolio_holdings](#fact_portfolio_holdings)
11. [fact_benchmark_indices](#fact_benchmark_indices)

---

## 1. dim_fund
* **Description:** Mutual fund master dimension table containing details about each mutual fund scheme.
* **Source Reference:** `01_fund_master.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Primary Key | Unique 6-digit code assigned to each mutual fund scheme by AMFI (Association of Mutual Funds in India). |
| `fund_house` | TEXT | - | Asset Management Company (AMC) name running the fund (e.g. SBI Mutual Fund). |
| `scheme_name` | TEXT | - | Full name of the mutual fund scheme. |
| `category` | TEXT | - | Broad asset category (e.g. Equity, Debt, Hybrid). |
| `sub_category` | TEXT | - | Specific sub-category of the scheme (e.g. Large Cap, Liquid, Flexi Cap). |
| `plan` | TEXT | - | Purchase plan type: Direct or Regular. |
| `launch_date` | TEXT | - | Launch date of the mutual fund scheme (format: YYYY-MM-DD). |
| `benchmark` | TEXT | - | Reference index used to measure scheme performance (e.g. NIFTY 50 TRI). |
| `expense_ratio_pct` | REAL | - | Annual fees charged by the scheme to manage the assets, expressed as a percentage. |
| `exit_load_pct` | REAL | - | Fee charged to investors when they sell/redeem their mutual fund units within a specific period. |
| `min_sip_amount` | REAL | - | Minimum monthly SIP (Systematic Investment Plan) contribution amount allowed. |
| `min_lumpsum_amount` | REAL | - | Minimum one-time lumpsum investment amount allowed. |
| `fund_manager` | TEXT | - | Name of the professional manager overseeing the fund portfolio. |
| `risk_category` | TEXT | - | Scheme risk category based on AMFI riskometer (e.g. Very High, Moderate). |
| `sebi_category_code` | TEXT | - | Official SEBI category designation code. |

---

## 2. dim_date
* **Description:** Date dimension table used to perform time-series analysis and group data by years, months, quarters, and days.
* **Source Reference:** Programmatically generated daily calendar (2022-01-01 to 2026-12-31)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | Primary Key | The calendar date (format: YYYY-MM-DD). |
| `year` | INTEGER | - | Calendar year (e.g. 2024). |
| `month` | INTEGER | - | Calendar month number (1 to 12). |
| `day` | INTEGER | - | Day of the month (1 to 31). |
| `quarter` | INTEGER | - | Financial quarter (1 to 4). |
| `day_of_week` | INTEGER | - | Index of the weekday (0 for Monday to 6 for Sunday). |
| `day_name` | TEXT | - | String name of the day (e.g. Monday). |
| `month_name` | TEXT | - | Full string name of the month (e.g. January). |
| `is_weekend` | INTEGER | - | Boolean flag: 1 if Saturday/Sunday, 0 if weekday. |

---

## 3. fact_nav
* **Description:** Daily Net Asset Value (NAV) history for all mutual fund schemes. Missing NAVs for holidays/weekends are forward-filled.
* **Source Reference:** `02_nav_history.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Composite PK, FK | Foreign key referencing `dim_fund(amfi_code)`. |
| `date` | TEXT | Composite PK, FK | Date of NAV entry referencing `dim_date(date)`. |
| `nav` | REAL | - | Net Asset Value (per unit price) of the fund scheme on that date. |

---

## 4. fact_transactions
* **Description:** Fact table documenting individual transactions executed by investors in mutual funds.
* **Source Reference:** `08_investor_transactions.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `transaction_id` | INTEGER | Primary Key (Auto) | Unique auto-incrementing transaction ID. |
| `investor_id` | TEXT | - | Unique identifier representing an individual investor. |
| `transaction_date` | TEXT | FK | Date the transaction took place, referencing `dim_date(date)`. |
| `amfi_code` | INTEGER | FK | The fund scheme transacted in, referencing `dim_fund(amfi_code)`. |
| `transaction_type` | TEXT | - | The purchase vehicle used: SIP, Lumpsum, or Redemption. |
| `amount_inr` | REAL | - | Transaction amount in Indian Rupees (INR). |
| `state` | TEXT | - | Indian state where the investor resides. |
| `city` | TEXT | - | Indian city where the investor resides. |
| `city_tier` | TEXT | - | Tier classification of the city (Tier 1, Tier 2, etc.). |
| `age_group` | TEXT | - | Age bracket of the investor (e.g. 18-30, 31-45). |
| `gender` | TEXT | - | Gender of the investor (e.g. Male, Female). |
| `annual_income_lakh` | REAL | - | Annual income of the investor in Lakhs (INR 100,000s). |
| `payment_mode` | TEXT | - | Transaction payment method (e.g. Net Banking, UPI, Cheque, Mandate). |
| `kyc_status` | TEXT | - | Know Your Customer (KYC) compliance status: Verified or Pending. |

---

## 5. fact_performance
* **Description:** Performance metrics, standard risk indicators, ratings, and return rates for mutual fund schemes.
* **Source Reference:** `07_scheme_performance.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Primary Key, FK | Unique mutual fund code, referencing `dim_fund(amfi_code)`. |
| `scheme_name` | TEXT | - | Name of the mutual fund scheme. |
| `fund_house` | TEXT | - | Asset Management Company running the scheme. |
| `category` | TEXT | - | Asset class category of the mutual fund. |
| `plan` | TEXT | - | Direct or Regular option plan. |
| `return_1yr_pct` | REAL | - | Annualised returns of the fund over the last 1 year (%). |
| `return_3yr_pct` | REAL | - | Annualised returns of the fund over the last 3 years (%). |
| `return_5yr_pct` | REAL | - | Annualised returns of the fund over the last 5 years (%). |
| `benchmark_3yr_pct` | REAL | - | Annualised returns of the fund's benchmark index over the last 3 years (%). |
| `alpha` | REAL | - | Excess return of the fund relative to the return of its benchmark index. |
| `beta` | REAL | - | Relative volatility of the fund compared to the market benchmark. |
| `sharpe_ratio` | REAL | - | Risk-adjusted return metric measuring excess return per unit of standard deviation. |
| `sortino_ratio` | REAL | - | Risk-adjusted return metric measuring return relative to downside standard deviation. |
| `std_dev_ann_pct` | REAL | - | Annualised standard deviation of weekly fund returns (overall volatility). |
| `max_drawdown_pct` | REAL | - | Maximum observed peak-to-trough loss of the fund (%). |
| `aum_crore` | REAL | - | Latest total Assets Under Management in Crores (INR 10,000,000s). |
| `expense_ratio_pct` | REAL | - | Internal scheme fee percentage. |
| `morningstar_rating`| INTEGER | - | Morningstar star rating of the fund (1 to 5). |
| `risk_grade` | TEXT | - | Qualitative risk description (e.g. Above Average, Average, High). |

---

## 6. fact_aum
* **Description:** Historically recorded total Assets Under Management (AUM) values for individual fund houses.
* **Source Reference:** `03_aum_by_fund_house.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | Composite PK, FK | Reporting date, referencing `dim_date(date)`. |
| `fund_house` | TEXT | Composite PK | Asset Management Company name. |
| `aum_lakh_crore` | REAL | - | AUM of the fund house in Lakh Crores (INR). |
| `aum_crore` | REAL | - | AUM of the fund house in Crores (INR). |
| `num_schemes` | INTEGER | - | Total count of active schemes offered by the fund house. |

---

## 7. fact_monthly_sip_inflows
* **Description:** Total Indian mutual fund industry-wide monthly SIP inflows and active account counts.
* **Source Reference:** `04_monthly_sip_inflows.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | Primary Key | Year-month of reporting (format: YYYY-MM). |
| `sip_inflow_crore` | REAL | - | Monthly SIP investment inflows in Crores (INR). |
| `active_sip_accounts_crore` | REAL | - | Total count of active SIP accounts in Crores. |
| `new_sip_accounts_lakh` | REAL | - | New SIP accounts registered during the month in Lakhs. |
| `sip_aum_lakh_crore` | REAL | - | Total industry AUM sourced through SIPs in Lakh Crores (INR). |
| `yoy_growth_pct` | REAL | - | Year-over-Year percentage growth of SIP inflows for this calendar month. |

---

## 8. fact_category_inflows
* **Description:** Net monthly industry inflows broken down by asset categories.
* **Source Reference:** `05_category_inflows.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | Composite PK | Year-month of reporting (format: YYYY-MM). |
| `category` | TEXT | Composite PK | Mutual fund category (e.g. Equity, Debt, Hybrid). |
| `net_inflow_crore` | REAL | - | Net investment inflows into the category during the month in Crores (INR). |

---

## 9. fact_industry_folio_count
* **Description:** Industry-wide total and category-wise folio (account) counts.
* **Source Reference:** `06_industry_folio_count.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | Primary Key | Year-month of reporting (format: YYYY-MM). |
| `total_folios_crore` | REAL | - | Total mutual fund accounts (folios) across the industry in Crores. |
| `equity_folios_crore` | REAL | - | Equity mutual fund accounts in Crores. |
| `debt_folios_crore` | REAL | - | Debt mutual fund accounts in Crores. |
| `hybrid_folios_crore` | REAL | - | Hybrid mutual fund accounts in Crores. |
| `others_folios_crore` | REAL | - | Other mutual fund accounts (e.g. Solution-oriented, ETFs) in Crores. |

---

## 10. fact_portfolio_holdings
* **Description:** Equity stock-level holdings weightings and market values held by mutual fund schemes.
* **Source Reference:** `09_portfolio_holdings.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Composite PK, FK | Foreign key referencing `dim_fund(amfi_code)`. |
| `stock_symbol` | TEXT | Composite PK | Unique NSE/BSE trading symbol of the stock (e.g. HDFCBANK). |
| `stock_name` | TEXT | - | Full name of the corporation. |
| `sector` | TEXT | - | Industry sector of the company (e.g. Financial Services, IT). |
| `weight_pct` | REAL | - | Portfolio weight of this stock in the fund, as a percentage. |
| `market_value_cr` | REAL | - | Market value of the holding in Crores (INR). |
| `current_price_inr` | REAL | - | Current price of the stock unit in INR. |
| `portfolio_date` | TEXT | Composite PK, FK | Date of the portfolio snapshot, referencing `dim_date(date)`. |

---

## 11. fact_benchmark_indices
* **Description:** Daily close values for market benchmark indices to compare against fund performance.
* **Source Reference:** `10_benchmark_indices.csv` (processed)

| Column Name | SQLite Data Type | Primary/Foreign Key | Business Definition |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | Composite PK, FK | Trading date, referencing `dim_date(date)`. |
| `index_name` | TEXT | Composite PK | Benchmark index name (e.g. NIFTY50, BSE_SMALLCAP). |
| `close_value` | REAL | - | Closing point value of the index on that date. |
