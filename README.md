# Business Performance Dashboard
### Power BI · Python · DAX · Excel
*CFO & COO-Ready Financial Intelligence | Budget vs Actual | Cost Variance | Operational KPIs*

---

## Project Overview

This project builds an end-to-end business performance reporting solution for a manufacturing company's quarterly business review. The CFO and COO need a single, unified view of business health across Sales, Cost, and Operations — one that tells them where they are vs. budget, where the risks are, and what decisions need to be made.

The solution delivers a **3-page interactive Power BI dashboard** backed by a **Python preprocessing pipeline** that takes raw financial data from Excel, cleans and transforms it into a structured, analytics-ready layer for boardroom reporting.

---

## Business Problem

Most manufacturing businesses run their quarterly reviews on static Excel files passed between teams — no single version of truth, no drill-through capability, no real-time variance flagging. Leadership spends the first 30 minutes of every review reconciling numbers instead of making decisions.

This dashboard solves that by consolidating all performance data into one governed, interactive reporting layer — so the first question of every QBR is already answered before the meeting starts.

---

## Solution Architecture

```
Raw Data (financial_sample.xlsx)
            ↓
  generate_data.py
  [Simulates 1,200 manufacturing transactions across
   segments, products, business units, customers]
            ↓
  preprocessing.py
  [Cleans, transforms, engineers 45 analytical features]
            ↓
  output/cleaned_financial_data.csv
            ↓
  Power BI Desktop (financial_dashboard.pbix)
  [DAX measures + 3-page interactive report]
            ↓
  CFO / COO Quarterly Business Review
```

---

## Project Structure

```
business-performance-dashboard/
│
├── data/
│   └── financial_sample.xlsx        # Raw simulated dataset (1,200 rows)
│
├── output/
│   └── cleaned_financial_data.csv   # Pipeline output → load into Power BI
│
├── charts/
│   └── dashboard_preview.png        # Python-rendered MI dashboard preview
│
├── generate_data.py                 # Simulates realistic manufacturing financial data
├── preprocessing.py                 # Full ETL pipeline (7-step, 45 features)
├── dashboard_analytics.py           # Python dashboard preview (validates Power BI logic)
├── dax_measures.dax                 # All Power BI DAX measures (copy-paste ready)
├── requirements.txt
└── README.md
```

---

## Dashboard Pages

### Page 1 — Executive Summary (CFO View)
*The single-screen answer to "how is the business performing?"*

| Visual | What It Shows |
|--------|--------------|
| KPI Card | Revenue vs Budget with variance % and RAG flag |
| KPI Card | EBITDA Margin vs prior year and target |
| KPI Card | Cost Variance — over/under budget (RAG coded) |
| KPI Card | Working Capital proxy |
| Waterfall Chart | Budget → Actuals → Variance by business unit |
| Line Chart | Month-on-month revenue and cost trend |

### Page 2 — Sales & Revenue Deep Dive
*Answers: where is revenue coming from and where is it at risk?*

| Visual | What It Shows |
|--------|--------------|
| Bar + Map | Revenue by country and product segment |
| Ranked Bar | Top 10 vs Bottom 5 SKUs by gross margin % |
| Line Chart | Sales growth % vs prior year by segment |
| Donut | Customer concentration — top 5 as % of total |
| MTD Tracker | Month-to-date vs target with forecast line |

### Page 3 — Cost & Operational Efficiency
*Answers: where are costs running hot and what is the operational impact?*

| Visual | What It Shows |
|--------|--------------|
| Pie Chart | Cost breakdown by function (Production/Logistics/Labour/Overhead/R&D) |
| Bar + Line | Production cost per unit — 12-month trend |
| Column | Headcount vs output ratio by business unit |
| KPI Card | Total downtime hours and estimated revenue impact |
| Heatmap | Budget vs actual cost variance by month and category |

---

## Python Preprocessing Pipeline

The pipeline (`preprocessing.py`) runs 7 steps and engineers **45 analytical features** from 20 raw columns:

### Step-by-Step

| Step | What Happens |
|------|-------------|
| 1. Ingest | Load raw Excel, log shape |
| 2. Standardise | Normalise all column names |
| 3. Date Engineering | Parse dates → year, month, quarter, fiscal_quarter, month_year, week |
| 4. Null Handling | Fill nulls with medians / zeros; log before vs after |
| 5. Feature Engineering | Compute margin %, budget variance, cost variance, cost per unit, RAG flags |
| 6. Customer Concentration | Compute top 5 / top 2 customer revenue share |
| 7. Export | Save to `output/cleaned_financial_data.csv` |

### Key Engineered Features

```python
# Margin metrics
gross_margin_pct      = (sales - cogs) / sales * 100
ebitda_margin_pct     = ebitda / sales * 100

# Budget & cost variance
budget_variance       = sales - budget
budget_variance_pct   = budget_variance / budget * 100
budget_status         = "Over Budget" | "On Track"

cost_variance         = cost_actual - cost_budget
cost_variance_pct     = cost_variance / cost_budget * 100

# Operational efficiency
cost_per_unit         = cost_actual / units_produced
revenue_per_head      = sales / headcount
output_per_head       = units_produced / headcount
downtime_revenue_loss = downtime_hours * (sales / 8)

# RAG flags
margin_rag            = GREEN (≥30%) | AMBER (≥20%) | RED (<20%)
cost_rag              = GREEN (≤5%)  | AMBER (≤10%) | RED (>10%)
downtime_rag          = GREEN (<8h)  | AMBER (<16h) | RED (≥16h)
```

---

## DAX Measures (Power BI)

All measures are in `dax_measures.dax`. Key ones:

```dax
Revenue vs Budget % =
DIVIDE([Total Revenue] - [Total Budget], [Total Budget], 0)

EBITDA Margin % =
DIVIDE([Total EBITDA], [Total Revenue], 0)

Cost Variance =
[Total Cost Actual] - [Total Cost Budget]

MoM Revenue Growth =
VAR CurrentMonth = MAX(financials[date])
VAR PrevMonth    = EDATE(CurrentMonth, -1)
...
RETURN DIVIDE(RevCurrent - RevPrev, RevPrev, 0)

Customer Concentration % =
DIVIDE([Top 5 Customer Revenue], [Total Revenue], 0)

Margin RAG =
IF(M >= 30, "🟢 GREEN", IF(M >= 20, "🟡 AMBER", "🔴 RED"))
```

---

## Key Business Insights Delivered

- **Budget variance identified by unit** — dashboard surfaces which business unit drives overrun, not just the total
- **SKU-level margin drag** — bottom 3 SKUs flagged as margin-negative, enabling product mix decisions
- **Customer concentration risk** — top 5 customers = ~29% of revenue; top 2 = ~13%; risk visible at a glance
- **Cost per unit trend** — 8%+ increase over 6 months with flat headcount flags a process efficiency problem before it becomes a P&L problem
- **Downtime impact quantified** — estimated revenue loss from downtime converted to ₹ Cr, making the operational case for maintenance investment

---

## Pipeline Output Summary (Sample Run)

```
Revenue
  Total Revenue      : ₹215.03 Cr
  Total Budget       : ₹214.80 Cr
  Budget Variance    : ₹0.23 Cr  (+0.1%)

Profitability
  Avg Gross Margin   : 41.9%
  Avg EBITDA Margin  : 25.8%
  Total EBITDA       : ₹55.24 Cr

Cost Health
  Over-Budget Lines  : 583 of 1,200 (48.6%)
  Cost RED lines     : 157 transactions

Operational
  Total Downtime     : 14,561 hrs
  Est. Revenue Loss  : ₹328.02 Cr
  Customer Conc.     : Top 5 = 29.4% | Top 2 = 12.6%
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate dataset
python generate_data.py

# 3. Run preprocessing pipeline
python preprocessing.py

# 4. Generate Python dashboard preview
python dashboard_analytics.py

# 5. Load into Power BI
#    → Open Power BI Desktop
#    → Get Data → Text/CSV → output/cleaned_financial_data.csv
#    → Create measures from dax_measures.dax
#    → Build 3-page report using the dashboard structure above
```

---

## Tools & Methods

| Area | Tool / Method |
|------|--------------|
| Data generation | Python — NumPy, Pandas |
| ETL pipeline | Python — Pandas (7-step, 45 features) |
| Dashboard & BI | Power BI Desktop |
| DAX modelling | Power BI DAX |
| Python dashboard preview | Matplotlib |
| Methodology | Management reporting, variance analysis, KPI framework design, RAG reporting |

---

## Dataset

- **Source:** Simulated manufacturing financial data (mirrors Microsoft Financial Sample structure)
- **Rows:** 1,200 transactions
- **Period:** Jan 2023 – Dec 2024 (8 fiscal quarters)
- **Dimensions:** Segment, Product, Country, Customer, Business Unit, Cost Function
- **Measures:** Sales, COGS, EBITDA, Budget, Cost Actual, Cost Budget, Downtime, Headcount, Units Produced

---

*Project: Business Performance Dashboard | Manufacturing Financial Analytics | Power BI + Python*
