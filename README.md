#  Bluestock Mutual Fund Capstone project


![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Star%20Schema-003B57?style=flat&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=flat&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?style=flat&logo=plotly&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-5%20Notebooks-F37626?style=flat&logo=jupyter&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-2EA44F?style=flat)

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Project Stats](#-project-stats)
4. [Folder Structure](#-folder-structure)
5. [Data Pipeline Architecture](#-data-pipeline-architecture)
6. [Database Schema (Star Schema)](#️-database-schema-star-schema)
7. [Streamlit Dashboard](#-streamlit-dashboard--6-tabs)
8. [Analytical Models](#-analytical-models)
9. [Scripts Reference](#-scripts-reference)
10. [Jupyter Notebooks](#-jupyter-notebooks)
11. [Tech Stack](#-tech-stack)
12. [Installation & Setup](#-installation--setup)
13. [Usage Guide](#-usage-guide)

---

##  Project Overview

This capstone project delivers a **production-grade mutual fund analytics platform** built during a data analytics internship at **Bluestock Fintech**. The system covers the full data engineering lifecycle — from raw CSV ingestion to a live interactive dashboard — across **40 mutual fund schemes** from India's top AMCs.

The platform provides portfolio risk intelligence, fund performance benchmarking, investor demographic analytics, and advanced quantitative models (Monte Carlo simulation and Markowitz portfolio optimization) — all powered by an automated ETL pipeline and a local SQLite data warehouse.

---

##  Key Features

- **Automated ETL Pipeline** — ingests, cleans, and loads 10 raw CSV datasets into a structured SQLite database with a single command
- **Star Schema Data Warehouse** — 2 dimension tables + 9 fact tables with B-Tree indexing for fast query performance
- **6-Tab Interactive Dashboard** — built with Streamlit and Plotly for real-time exploration of fund performance, demographics, SIP trends, and risk analytics
- **Quantitative Risk Models** — Monte Carlo NAV simulation (GBM, 1,000 paths) and Markowitz Portfolio Optimization (5,000 simulations, Efficient Frontier)
- **Live NAV Fetcher** — pulls real-time NAV data from the public `mfapi.in` API with retry/backoff logic
- **CLI Fund Recommender** — recommends top funds by risk appetite (Low / Moderate / High) using Sharpe ratio ranking
- **Auto-Generated Reports** — weekly HTML email newsletter, PDF board report, and PowerPoint pitch deck
- **Risk Scorecards** — computes VaR (95%), CVaR, Sharpe, Sortino, Alpha, and Beta for all 40 schemes

---

##  Project Stats

| Metric | Value |
|---|---|
| Mutual Fund Schemes | 40 schemes (100% AMFI code match) |
| NAV Records | ~46,000 daily NAV data points |
| Investor Transactions | ~32,778 synthetic transaction records |
| Raw Datasets | 10 CSV files + 6 live NAV files |
| Database Tables | 11 tables (2 dim + 9 fact) |
| Dashboard Tabs | 6 interactive pages |
| Jupyter Notebooks | 5 (ingestion → cleaning → EDA → performance → advanced) |
| AMCs Covered | SBI, HDFC, ICICI Pru, Axis, Kotak, Nippon India, UTI, Aditya Birla, Mirae Asset, DSP |
| Date Range | 2022-01-01 to 2026-05-29 |

---

## 📁 Folder Structure

```text
bluestock_mf_capstone/
│
├── data/
│   ├── raw/                          ← Original, unmodified source CSV datasets
│   │   ├── 01_fund_master.csv        # 40 fund schemes with AMC, category, expense ratio
│   │   ├── 02_nav_history.csv        # Daily NAV records (~46,000 rows)
│   │   ├── 03_aum_by_fund_house.csv  # AUM breakdown by fund house
│   │   ├── 04_monthly_sip_inflows.csv# Monthly SIP inflow trends
│   │   ├── 05_category_inflows.csv   # Inflows by category (Equity/Debt/Hybrid)
│   │   ├── 06_industry_folio_count.csv# Industry-level folio growth
│   │   ├── 07_scheme_performance.csv # Scheme returns, alpha, beta, ratios
│   │   ├── 08_investor_transactions.csv# ~32,778 investor transaction records
│   │   ├── 09_portfolio_holdings.csv # Underlying stock/bond holdings
│   │   ├── 10_benchmark_indices.csv  # NIFTY 50 TRI, CRISIL Gilt daily values
│   │   └── [amfi_code]_raw.csv       # 6 live NAV files fetched from mfapi.in
│   │
│   ├── processed/                    ← Cleaned and standardised CSV exports
│   └── db/
│       └── bluestock_mf.db           ← Unified SQLite data warehouse
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb       # Ingestion verification and source inspection
│   ├── 02_data_cleaning.ipynb        # Cleaning, type casting, deduplication
│   ├── 03_eda_analysis.ipynb         # Exploratory data analysis and visualisations
│   ├── 04_performance_analytics.ipynb# Sharpe, CAGR, volatility scorecards
│   └── 05_advanced_analytics.ipynb  # Monte Carlo GBM & Markowitz MPT testing
│
├── scripts/
│   ├── etl_pipeline.py               # Master ETL: ingest → clean → load → metrics
│   ├── compute_metrics.py            # VaR, CVaR, Sharpe, HHI, rolling returns engine
│   ├── live_nav_fetch.py             # Daily NAV fetch from mfapi.in (with retry logic)
│   ├── recommender.py                # CLI fund recommender by risk appetite
│   ├── email_report_generator.py     # Weekly responsive HTML email newsletter
│
├── sql/
│   ├── schema.sql                    # Star Schema DDL (CREATE TABLE, indexes)
│   └── queries.sql                   # Analytical SQL query library
│
├── dashboard/
│   └── app.py                        # Streamlit app (6-tab interactive dashboard)
│
├── reports/
│   ├── plots/
│   │   └── rolling_sharpe_chart.png  # Matplotlib rolling Sharpe ratio chart
│   ├── fund_scorecard.csv            # Computed fund rankings scorecard
│   ├── var_cvar_report.csv           # VaR & CVaR values for all 40 schemes
│   ├── alpha_beta.csv                # Alpha and beta metrics per scheme
│   ├── weekly_report.html            # Auto-generated HTML email newsletter
│   └── data_quality_report.txt       # Data validation / AMFI code match report
│
├── run_pipeline.py                   # Root-level shortcut to run full ETL pipeline
├── run_queries.py                    # Shortcut to execute analytical SQL queries
├── schedule_etl.py                   # Scheduled/automated pipeline runner
├── data_ingestion.py                 # Standalone ingestion verification script
├── load_db.py                        # Standalone DB schema loader
├── clean_data.py                     # Standalone data cleaning script
├── data_dictionary.md                # Full column-level data dictionary (11 tables)
├── requirements.txt                  # All Python dependencies
└── README.md                         # Project documentation (this file)
```

---

## ⚙️ Data Pipeline Architecture

The pipeline runs in **4 sequential stages**, all automated via `run_pipeline.py`:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        ETL PIPELINE FLOW                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   [1] INGESTION                [2] CLEANING               [3] LOADING     │
│   ─────────────                ────────────               ──────────────   │
│   • Verify 10 CSVs             • Type casting             • Execute DDL   │
│   • Check file sizes           • Date normalisation         schema.sql    │
│   • AMFI code match            • Numeric parsing          • Load all 11   │
│   • Log data quality           • Deduplication              tables into   │
│     report                     • Reindex date ranges        SQLite DB     │
│                                • Export to processed/                      │
│                                                                            │
│   [4] METRICS COMPUTATION                                                  │
│   ──────────────────────                                                   │
│   • VaR (95%) & CVaR per fund        • Sharpe & Sortino ratios            │
│   • Rolling return windows (1yr,3yr,5yr)  • HHI concentration score      │
│   • Alpha & Beta vs benchmark        • Export risk scorecards to CSV      │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema (Star Schema)

The SQLite database (`data/db/bluestock_mf.db`) uses a **Star Schema** design for query efficiency. B-Tree indexes on high-frequency filter columns (`date`, `amfi_code`) keep Streamlit dashboard queries under 10ms.

```
                        ┌──────────────────┐
                        │    dim_date      │
                        │  PK: date        │
                        │  year, month,    │
                        │  quarter,        │
                        │  day_name,       │
                        │  is_weekend      │
                        └────────┬─────────┘
                                 │
   ┌──────────────────┐          │          ┌───────────────────────┐
   │    dim_fund      │          │          │      fact_nav         │
   │  PK: amfi_code   │◄─────────┼─────────►│  PK: amfi_code, date  │
   │  fund_house      │          │          │  nav (daily value)    │
   │  scheme_name     │          │          └───────────────────────┘
   │  category        │          │
   │  expense_ratio   │          │          ┌───────────────────────┐
   │  fund_manager    │◄─────────┼─────────►│  fact_performance     │
   │  risk_category   │          │          │  sharpe, sortino      │
   └──────────────────┘          │          │  CAGR 1yr/3yr/5yr     │
                                 │          │  alpha, beta, VaR     │
                                 │          └───────────────────────┘
                                 │
                                 │          ┌───────────────────────┐
                                 ├─────────►│  fact_transactions    │
                                 │          │  investor demographics │
                                 │          │  KYC, state, tier,    │
                                 │          │  age, income, gender  │
                                 │          └───────────────────────┘
                                 │
                                 │          ┌───────────────────────┐
                                 ├─────────►│  fact_aum             │
                                 │          │  monthly AUM per AMC  │
                                 │          └───────────────────────┘
                                 │
                                 │          ┌───────────────────────┐
                                 ├─────────►│  fact_monthly_sip     │
                                 │          │  SIP inflow trends    │
                                 │          └───────────────────────┘
                                 │
                                 │          ┌───────────────────────┐
                                 ├─────────►│  fact_portfolio_holdings│
                                 │          │  stock/bond weights   │
                                 │          └───────────────────────┘
                                 │
                                 │          ┌───────────────────────┐
                                 └─────────►│  fact_benchmark_indices│
                                            │  NIFTY 50 TRI, CRISIL │
                                            └───────────────────────┘
```

**All 11 Tables:**

| Table | Type | Key Columns |
|---|---|---|
| `dim_fund` | Dimension | `amfi_code`, fund_house, category, expense_ratio, fund_manager |
| `dim_date` | Dimension | `date`, year, month, quarter, day_name, is_weekend |
| `fact_nav` | Fact | `amfi_code`, `date`, nav |
| `fact_performance` | Fact | `amfi_code`, sharpe_ratio, cagr_1yr/3yr/5yr, alpha, beta, VaR |
| `fact_transactions` | Fact | `transaction_id`, amfi_code, date, state, tier, gender, age, income |
| `fact_aum` | Fact | `amfi_code`, `month`, aum_crore |
| `fact_monthly_sip_inflows` | Fact | `month`, sip_inflow_crore |
| `fact_category_inflows` | Fact | `month`, category, inflow_crore |
| `fact_industry_folio_count` | Fact | `month`, folio_count |
| `fact_portfolio_holdings` | Fact | `amfi_code`, stock_symbol, weight_pct |
| `fact_benchmark_indices` | Fact | `date`, index_name, close_value |

---

## 🖥️ Streamlit Dashboard — 6 Tabs

Launch the dashboard with `streamlit run dashboard/app.py` and navigate to `http://localhost:8501`.

| Tab | Title | What It Shows |
|---|---|---|
| 1 | **Industry Overview** | AUM by fund house, market share treemap, category distribution, folio growth trends |
| 2 | **Fund Performance** | Risk vs Return bubble chart (AUM = bubble size), CAGR heatmap, sortable fund scorecard |
| 3 | **Investor Analytics** | Transaction demographics — KYC status, gender split, state-wise, income tier, age group |
| 4 | **SIP & Market Trends** | Monthly SIP inflow trends, category-wise inflows, benchmark index comparison |
| 5 | **Monte Carlo Simulation** | GBM simulation (1,000 paths, 5yr), 95% VaR calculation, probability of capital loss |
| 6 | **Portfolio Optimization** | Markowitz Efficient Frontier (5,000 random portfolios), Max Sharpe & Min Volatility portfolios |

---

## 📐 Analytical Models

### 1. Monte Carlo NAV Simulation (GBM)

Simulates **1,000 independent NAV pathways** over 5 years (1,260 trading days) using **Geometric Brownian Motion**:

$$dS_t = \mu S_t \, dt + \sigma S_t \, dW_t$$

Where:
- $\mu$ = historical drift (daily mean return)
- $\sigma$ = historical volatility (daily standard deviation)
- $dW_t$ = Wiener process increment

**Output:** 95% Value at Risk (VaR), probability of capital loss, P5/P50/P95 NAV trajectories.

---

### 2. Markowitz Portfolio Optimization (MPT)

Simulates **5,000 random weight portfolios** across 5 selected funds to trace the **Efficient Frontier**:

| Output | Description |
|---|---|
| **Efficient Frontier** | Scatter plot of 5,000 simulated risk-return combinations |
| **Max Sharpe Portfolio** | Optimal portfolio maximising risk-adjusted return |
| **Min Volatility Portfolio** | Portfolio minimising annualised standard deviation |
| **Weight Comparison** | Side-by-side bar chart of fund allocation weights |

**Sharpe Ratio:**

$$\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$$

Where $R_p$ = portfolio return, $R_f$ = risk-free rate (default: 6%), $\sigma_p$ = portfolio volatility.

---

### 3. Risk Scorecard Metrics (`compute_metrics.py`)

| Metric | Formula / Description |
|---|---|
| **VaR (95%)** | 5th percentile of historical daily returns |
| **CVaR (95%)** | Mean of returns below the VaR threshold |
| **Sharpe Ratio** | (Return − Risk-Free Rate) / Volatility |
| **Sortino Ratio** | (Return − Risk-Free Rate) / Downside Deviation |
| **Alpha** | Fund return − (Risk-Free + Beta × (Benchmark − Risk-Free)) |
| **Beta** | Covariance(Fund, Benchmark) / Variance(Benchmark) |
| **HHI Score** | Herfindahl-Hirschman Index for portfolio concentration |

---

## 🛠️ Scripts Reference

| Script | Purpose |
|---|---|
| `scripts/etl_pipeline.py` | Master pipeline — runs all 4 stages (ingest → clean → load → metrics) |
| `scripts/compute_metrics.py` | Calculates VaR, CVaR, Sharpe, Sortino, Alpha, Beta, HHI for all schemes |
| `scripts/live_nav_fetch.py` | Fetches daily NAV from `mfapi.in` API with exponential retry/backoff |
| `scripts/recommender.py` | CLI tool — recommends top 3 funds by risk appetite (Low / Moderate / High) |
| `scripts/email_report_generator.py` | Generates a responsive inline-CSS weekly HTML email newsletter |
| `scripts/generate_pdf.py` | Programmatically builds a 16-page PDF board report |
| `scripts/generate_pptx.py` | Programmatically builds a 12-slide PowerPoint pitch deck |

---

## 📓 Jupyter Notebooks

| Notebook | Purpose |
|---|---|
| `01_data_ingestion.ipynb` | Validates raw CSV sources, inspects shapes, checks AMFI code match (100%) |
| `02_data_cleaning.ipynb` | Type casting, date normalisation, deduplication, missing value treatment |
| `03_eda_analysis.ipynb` | Exploratory analysis — distributions, correlations, trend charts |
| `04_performance_analytics.ipynb` | Sharpe ratios, CAGR windows, volatility scorecards, rolling returns |
| `05_advanced_analytics.ipynb` | Monte Carlo GBM simulation, Markowitz MPT testing, frontier visualisation |

---

## 🧰 Tech Stack

| Layer | Tool / Library |
|---|---|
| **Language** | Python 3.10+ |
| **Data Processing** | pandas, NumPy |
| **Visualisation** | Plotly (interactive), Matplotlib, Seaborn |
| **Dashboard** | Streamlit |
| **Database** | SQLite (via `sqlite3` + SQLAlchemy) |
| **HTTP / API** | requests (mfapi.in live NAV) |
| **Notebooks** | Jupyter |

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or above
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Shashankshekhar13/bluestock-mf-capstone.git
cd bluestock-mf-capstone
```

### Step 2 — Create a Virtual Environment

```bash
# Create environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> Installs: pandas, numpy, matplotlib, seaborn, plotly, sqlalchemy, requests, jupyter, streamlit

---

## 📖 Usage Guide

### 1. Run the Full ETL Pipeline

Automates ingestion verification → data cleaning → schema creation → DB loading → metrics computation in one command:

```bash
python run_pipeline.py
```

Expected output: `[SUCCESS] Pipeline completed successfully!`

### 2. Launch the Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

Open your browser at **`http://localhost:8501`**

### 3. Get Fund Recommendations (CLI)

```bash
python scripts/recommender.py --risk low
python scripts/recommender.py --risk moderate
python scripts/recommender.py --risk high
```

Returns the top 3 funds ranked by Sharpe ratio for the selected risk appetite.

### 4. Fetch Live NAV Data

```bash
python scripts/live_nav_fetch.py
```

Pulls current NAV from `mfapi.in` for 6 tracked schemes and saves to `data/raw/`.

### 5. Generate Weekly HTML Newsletter

```bash
python scripts/email_report_generator.py
```

Output: `reports/weekly_report.html` — a responsive email showing top gainers and SIP metrics.
```

### 7. Run Analytical SQL Queries

```bash
python run_queries.py
```

Executes the full library of analytical queries from `sql/queries.sql` against the local database.

---

**Deliverables Submitted:**
- ✅ ETL pipeline + SQLite data warehouse
- ✅ 5 analytical Jupyter notebooks
- ✅ 6-tab Streamlit dashboard
- ✅ Risk scorecards (VaR, CVaR, Sharpe, Alpha/Beta)
- ✅ Monte Carlo simulation & Markowitz portfolio optimizer
- ✅ CLI fund recommender
- ✅ 16-page PDF final report
- ✅ 12-slide PowerPoint presentation
- ✅ Weekly HTML email newsletter generator
- ✅ Full data dictionary (11 tables, all columns)


---

*Built with Python · Streamlit · SQLite · Plotly · Pandas*
