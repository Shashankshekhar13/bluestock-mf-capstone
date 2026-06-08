# Power BI Implementation Guide — Bluestock Mutual Fund Capstone Project

This guide provides step-by-step instructions to recreate the Bluestock Mutual Fund Executive Dashboard in **Power BI Desktop**, matching the structure, metrics, relationships, and layout of the Day 5 dashboard requirements.

---

## 1. Connecting Power BI to the SQLite Database

Power BI does not have a native SQLite connector, so we must connect using **SQLite ODBC Driver**.

### Step A: Install the SQLite ODBC Driver
1. Download the installer for Windows (64-bit version `sqliteodbc_w64.exe` is recommended) from official sources (e.g. Christian Werner's SQLite ODBC page).
2. Run the installer and complete the setup.

### Step B: Configure the System DSN (ODBC Data Source Administrator)
1. Open **ODBC Data Sources (64-bit)** in Windows.
2. Go to the **System DSN** tab and click **Add...**
3. Select **SQLite 3 ODBC Driver** and click **Finish**.
4. Configure the DSN settings:
   - **Data Source Name (DSN):** `BluestockMF`
   - **Database Name:** Browse and select the absolute path to your `bluestock_mf.db` file (e.g., `D:\bluestock_mf_capstone\bluestock_mf.db`).
   - Leave other fields as default and click **OK**.

### Step C: Load Data into Power BI Desktop
1. Open **Power BI Desktop**.
2. Click **Get Data** > **More...** > **ODBC** and click **Connect**.
3. Select `DSN=BluestockMF` from the dropdown and click **OK**.
4. In the Navigator window, select the following 8 core tables:
   - `dim_fund`
   - `dim_date`
   - `fact_nav`
   - `fact_aum`
   - `fact_performance`
   - `fact_transactions`
   - `fact_monthly_sip_inflows`
   - `fact_category_inflows`
   - `fact_industry_folio_count`
   - `fact_portfolio_holdings`
   - `fact_benchmark_indices`
5. Click **Load**.

---

## 2. Setting Up Relationships (Entity-Relationship Diagram)

Go to the **Model View** in Power BI and configure the relationships between tables. The database follows a clean star/snowflake schema with `dim_fund` and `dim_date` serving as primary shared dimensions.

Configure the relationships as follows:

| From Table (Dimension) | From Column | To Table (Fact) | To Column | Cardinality | Cross Filter Direction |
|:---|:---|:---|:---|:---|:---|
| `dim_fund` | `amfi_code` | `fact_nav` | `amfi_code` | 1 to Many (1:*) | Single |
| `dim_fund` | `amfi_code` | `fact_transactions` | `amfi_code` | 1 to Many (1:*) | Single |
| `dim_fund` | `amfi_code` | `fact_performance` | `amfi_code` | 1 to 1 (1:1) | Both |
| `dim_fund` | `amfi_code` | `fact_portfolio_holdings` | `amfi_code` | 1 to Many (1:*) | Single |
| `dim_date` | `date` | `fact_nav` | `date` | 1 to Many (1:*) | Single |
| `dim_date` | `date` | `fact_transactions` | `transaction_date` | 1 to Many (1:*) | Single |
| `dim_date` | `date` | `fact_aum` | `date` | 1 to Many (1:*) | Single |
| `dim_date` | `date` | `fact_portfolio_holdings` | `portfolio_date` | 1 to Many (1:*) | Single |
| `dim_date` | `date` | `fact_benchmark_indices` | `date` | 1 to Many (1:*) | Single |

*Note: For monthly aggregated tables like `fact_monthly_sip_inflows` and `fact_category_inflows`, keep them stand-alone or relate them to `dim_date` using a calculated Month key (e.g. `YYYY-MM`).*

---

## 3. Core DAX Measures Reference

Create the following measures in Power BI to populate the KPI cards and charts:

### Total AUM (Latest Reported)
```dax
Total AUM = 
VAR LatestDate = MAX('fact_aum'[date])
RETURN
CALCULATE(
    SUM('fact_aum'[aum_lakh_crore]),
    'fact_aum'[date] = LatestDate
)
```

### Monthly SIP Inflow
```dax
Latest SIP Inflow = 
VAR LatestMonth = MAX('fact_monthly_sip_inflows'[month])
RETURN
CALCULATE(
    SUM('fact_monthly_sip_inflows'[sip_inflow_crore]),
    'fact_monthly_sip_inflows'[month] = LatestMonth
)
```

### Folio Count
```dax
Latest Folios = 
VAR LatestMonth = MAX('fact_industry_folio_count'[month])
RETURN
CALCULATE(
    SUM('fact_industry_folio_count'[total_folios_crore]),
    'fact_industry_folio_count'[month] = LatestMonth
)
```

### Active Schemes Count
```dax
Schemes Count = DISTINCTCOUNT('dim_fund'[amfi_code])
```

### Volatility / Standard Deviation
```dax
Fund Volatility = STDEV.S('fact_nav'[nav])
```

### Sharpe Ratio
```dax
Sharpe Ratio = 
VAR RiskFreeRate = 0.065
VAR FundReturn = [3Yr CAGR Return] -- Computed in Day 4
VAR Volatility = STDEV.S('fact_nav'[nav]) * SQRT(252)
RETURN
DIVIDE(FundReturn - RiskFreeRate, Volatility, 0)
```

---

## 4. Visual Layout Specification (Page by Page)

### Page 1: Industry Overview
*   **Theme Color Code:** Navy (`#1e3a8a`), Teal (`#0d8a72`).
*   **KPI Cards:**
    *   *Total AUM:* Metric = `[Total AUM]`, format = `₹0.00L Cr`.
    *   *SIP Inflows:* Metric = `[Latest SIP Inflow]`, format = `₹#,##0 Cr`.
    *   *Folios:* Metric = `[Latest Folios]`, format = `0.00 Cr`.
    *   *Schemes:* Metric = `[Schemes Count]`, format = `#,##0`.
*   **Line Chart (AUM Trend):**
    *   *X-Axis:* `fact_monthly_sip_inflows[month]`
    *   *Y-Axis:* `fact_monthly_sip_inflows[sip_aum_lakh_crore]`
*   **Bar Chart (AUM by AMC):**
    *   *Y-Axis (Category):* `fact_aum[fund_house]`
    *   *X-Axis (Values):* `fact_aum[aum_lakh_crore]` (Filtered to latest date)

### Page 2: Fund Performance
*   **Slicers (Top Pane):**
    *   `dim_fund[fund_house]` (Dropdown list)
    *   `dim_fund[category]` (Horizontal button list)
    *   `dim_fund[plan]` (Direct/Regular radio list)
*   **Scatter Plot (Risk vs Return):**
    *   *X-Axis:* `fact_performance[return_3yr_pct]`
    *   *Y-Axis:* `fact_performance[std_dev_ann_pct]`
    *   *Details:* `dim_fund[scheme_name]`
    *   *Size:* `fact_performance[aum_crore]`
*   **Scorecard Table:**
    *   Fields: `rank`, `scheme_name`, `cagr_3yr`, `sharpe_ratio`, `sortino_ratio`, `annualized_alpha`, `beta`, `max_drawdown`, `expense_ratio_pct`
*   **NAV vs Benchmark Line Chart:**
    *   *X-Axis:* `fact_nav[date]`
    *   *Y-Axis:* `fact_nav[nav]` and `fact_benchmark_indices[close_value]` (Dual axis / normalized)

### Page 3: Investor Analytics
*   **Slicers (Top Pane):**
    *   `fact_transactions[state]` (Dropdown)
    *   `fact_transactions[age_group]` (List)
    *   `fact_transactions[city_tier]` (Radio list)
*   **Bar Chart (Inflows by State):**
    *   *Y-Axis:* `fact_transactions[state]`
    *   *X-Axis:* `SUM(fact_transactions[amount_inr])` (Filter `transaction_type = 'SIP'`)
*   **Donut Chart (Transaction Type Split):**
    *   *Legend:* `fact_transactions[transaction_type]`
    *   *Values:* `COUNT(fact_transactions[transaction_id])`
*   **Bar Chart (Age Group SIP):**
    *   *X-Axis:* `fact_transactions[age_group]`
    *   *Y-Axis:* `AVERAGE(fact_transactions[amount_inr])` (Filter `transaction_type = 'SIP'`)

### Page 4: SIP & Market Trends
*   **Dual Axis Line/Bar Chart (SIP & Market Linkage):**
    *   *Shared X-Axis:* `Month` (derived from dim_date)
    *   *Column Values (Bar):* `fact_monthly_sip_inflows[sip_inflow_crore]`
    *   *Line Values:* `AVERAGE(fact_benchmark_indices[close_value])` (Filtered to NIFTY50)
*   **Matrix (Heatmap visual):**
    *   *Rows:* `fact_category_inflows[category]`
    *   *Columns:* `fact_category_inflows[month]`
    *   *Values:* `SUM(fact_category_inflows[net_inflow_crore])`
    *   *Conditional Formatting:* Enable **Background Color** scales (using YlGnBu palette).
