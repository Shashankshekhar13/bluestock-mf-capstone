# Bluestock Mutual Fund Capstone Project

An enterprise-grade, end-to-end data engineering, visual analytics, database migration, and portfolio risk intelligence system. This platform transforms raw mutual fund datasets and investor transactional logs into structured databases, compiles advanced risk scorecards, and provides an interactive web-based dashboard.

---

## 📁 Repository Directory Layout

The codebase is organized into a modular structure to separate raw data, processed assets, SQL definitions, execution modules, frontend interfaces, and Jupyter notebooks:

```text
bluestock_mf_capstone/
├── dashboard/
│   └── app.py                     # Streamlit dashboard application (6 tabs)
├── data/
│   ├── db/
│   │   └── bluestock_mf.db        # Unified SQLite database file
│   ├── processed/                 # Cleaned and processed CSV datasets
│   └── raw/                       # Original, unmodified client CSV datasets
├── notebooks/
│   ├── 01_data_ingestion.ipynb    # Ingestion validation notebooks
│   ├── 02_data_cleaning.ipynb     # Data cleaning notebooks
│   ├── 03_eda_analysis.ipynb      # Exploratory Analysis notebook
│   ├── 04_performance_analytics.ipynb # Volatility scorecard notebook
│   └── 05_advanced_analytics.ipynb # Monte Carlo & Markowitz testing notebook
├── reports/
│   ├── plots/
│   │   └── rolling_sharpe_chart.png # Matplotlib compiled chart
│   ├── fund_scorecard.csv         # Calculated rankings scorecard
│   ├── var_cvar_report.csv        # Calculated risk values
│   └── weekly_report.html         # Auto-generated styled HTML email newsletter
├── scripts/
│   ├── compute_metrics.py         # Sharpe, HHI, and Value at Risk engine
│   ├── email_report_generator.py  # Weekly responsive HTML generator
│   ├── etl_pipeline.py            # Automated master ETL pipeline logic
│   ├── live_nav_fetch.py          # Daily API NAV fetch script
│   └── recommender.py             # CLI-based fund recommendation engine
├── sql/
│   ├── queries.sql                # Analytical SQL query sets
│   └── schema.sql                 # Star Schema DDL schema definitions
├── requirements.txt               # Dashboard and pipeline dependencies
├── run_pipeline.py                # Shortcut execution script (ETL & metrics)
└── README.md                      # Comprehensive project documentation
```

---

## 🗄️ Relational Database Schema Design

The SQLite database (`data/db/bluestock_mf.db`) utilizes a unified **Star Schema** to ensure data integrity and query performance.

### Dimensions
- **`dim_fund`** (PK: `amfi_code`): Scheme properties (AUM, AMC name, category, plans, manager, expense and load values).
- **`dim_date`** (PK: `date`): Calendar dimensions (year, month, quarter, day name, weekend/weekday flag).

### Facts
- **`fact_nav`** (PK: `amfi_code, date`): Daily NAV histories with foreign keys linking back to dim tables.
- **`fact_performance`** (PK: `amfi_code`): Volatility profiles, CAGR metrics (1yr, 3yr, 5yr), alpha, beta, Sharpe, and Sortino ratios.
- **`fact_transactions`** (PK: `transaction_id`): Individual transactions mapping demographic groups (KYC status, state, tier, income, gender, age).
- **`fact_portfolio_holdings`** (PK: `amfi_code, stock_symbol, portfolio_date`): Asset allocation weights and underlying security data.
- **`fact_benchmark_indices`** (PK: `date, index_name`): Daily closing values for comparative indexes (NIFTY 50 TRI, CRISIL Gilt, etc.).

### Indexing Optimization
B-Tree database indexes are created on high-frequency query filters (`idx_nav_date`, `idx_transactions_fund`, `idx_transactions_date`, `idx_holdings_fund`) to reduce Streamlit dashboard latency under 10ms.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ (configured on your path)
- Git command line interface

### 2. Set Up Virtual Environment
Initialize an isolated virtualenv and install core dependencies:
```powershell
# Create environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Execution & Usage Guide

### 1. Execute the ETL Pipeline
The master ETL pipeline automates ingestion verification, cleaning/reindexing daily NAV ranges, executing SQL schemas, loading database rows, and calculating analytical risk metrics:
```powershell
python run_pipeline.py
```

### 2. Launch the Streamlit Dashboard
Launch the interactive web portal:
```powershell
streamlit run dashboard/app.py
```
Open your web browser and navigate to `http://localhost:8501`.

### 3. Generate HTML Weekly Email Newsletter
Generate a responsive inline-CSS newsletter of performance gainers and SIP metrics:
```powershell
python scripts/email_report_generator.py
```
Output will be saved to `reports/weekly_report.html`.

### 4. Compile Final Reports & Pitch Decks
To build print-ready documents programmatically (saving them to your designated workspace download artifacts):
```powershell
# Compile the 16-page Board Report (PDF)
py scripts/generate_pdf.py

# Compile the 12-slide Pitch Deck (PowerPoint)
py scripts/generate_pptx.py
```

---

## 📊 Analytical Financial Models

### 1. Monte Carlo NAV Simulation 
Uses **Geometric Brownian Motion (GBM)** to forecast NAV trajectories over 5 years (1,260 business days):
$$dS_t = \mu S_t dt + \sigma S_t dW_t$$

By calculating historical returns, we extract drift ($\mu$) and asset volatility ($\sigma$) to project 1,000 independent pathways, computing **95% Value at Risk (VaR)** and **probability of capital loss**.

### 2. Markowitz Portfolio Optimization 
Implements **Modern Portfolio Theory (MPT)**. Simulates 5,000 random weight portfolios across 5 selected funds to trace the **Efficient Frontier**, isolating the **Maximum Sharpe Ratio** portfolio and the **Minimum Volatility** portfolio.
