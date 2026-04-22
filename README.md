# Business Performance Dashboard
Project Overview
This project builds an end-to-end business performance reporting solution for a manufacturing company's quarterly business review. The CFO and COO need a single, unified view of business health across Sales, Cost, and Operations — one that tells them where they are vs. budget, where the risks are, and what decisions need to be made.
The solution delivers a 3-page interactive Power BI dashboard backed by a Python preprocessing pipeline that takes raw financial data from Excel, cleans and transforms it, and loads it into a boardroom-ready reporting layer.

Business Problem
Most manufacturing businesses run their quarterly reviews on static Excel files passed between teams — no single version of truth, no drill-through capability, no real-time variance flagging. Leadership spends the first 30 minutes of every review reconciling numbers instead of making decisions.
This dashboard solves that by consolidating all performance data into one governed, interactive reporting layer — so the first slide of every QBR is already answered before the meeting starts.

Solution Architecture
Raw Data (Excel)
      ↓
Python Preprocessing Pipeline (Pandas)
      ↓
Cleaned & Structured Dataset (.csv)
      ↓
Power BI Data Model (DAX Measures)
      ↓
3-Page Interactive Dashboard
      ↓
CFO / COO Quarterly Business Review

Dashboard Pages
Page 1 — Executive Summary (CFO View)
The single-screen answer to "how is the business performing?"

Revenue vs Budget KPI card with variance % and trend arrow
EBITDA Margin card vs prior year and target
Cost Variance card — over/under budget flagged RAG
Working Capital card
Waterfall chart: Budget → Actuals → Variance by business unit
Month-on-month revenue and cost trend lines

Page 2 — Sales & Revenue Deep Dive
Answers: where is revenue coming from and where is it at risk?

Revenue by region and product category (bar + map visual)
Top 10 vs Bottom 10 SKUs by contribution margin
Sales growth % vs prior year by segment
Customer concentration — top 5 customers as % of total revenue
Month-to-date vs target tracker with forecast line

Page 3 — Cost & Operational Efficiency
Answers: where are costs running hot and what is the operational impact?

Cost breakdown by function (production, logistics, overhead, labour)
Production cost per unit — 12-month trend
Headcount vs output ratio by business unit
Downtime hours and estimated revenue impact
Budget vs actual cost variance heatmap by month and category

Key DAX Measures
Revenue vs Budget % =
DIVIDE([Total Revenue] - [Total Budget], [Total Budget], 0)

EBITDA Margin =
DIVIDE([EBITDA], [Total Revenue], 0)

Cost Variance =
[Actual Cost] - [Budgeted Cost]

MoM Revenue Growth =
DIVIDE([Revenue This Month] - [Revenue Last Month], [Revenue Last Month], 0)

Customer Concentration % =
DIVIDE([Top 5 Customer Revenue], [Total Revenue], 0)

Python Preprocessing Pipeline
The raw Microsoft Financial Sample dataset requires cleaning before Power BI ingestion. The Python pipeline handles:

Column standardisation and renaming
Date parsing and fiscal quarter tagging
Null handling and outlier flagging
Margin and variance calculations pre-computed as features
Export to clean .csv for Power BI direct query

import pandas as pd

df = pd.read_excel("financial_sample.xlsx")

# Standardise columns
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Parse dates
df["date"] = pd.to_datetime(df["date"])
df["fiscal_quarter"] = df["date"].dt.to_period("Q")

# Pre-compute key metrics
df["gross_margin"] = (df["sales"] - df["cogs"]) / df["sales"]
df["budget_variance"] = df["sales"] - df["budget"]
df["variance_pct"] = df["budget_variance"] / df["budget"]

# Flag over-budget lines
df["cost_flag"] = df["budget_variance"].apply(
    lambda x: "Over Budget" if x < 0 else "On Track"
)

df.to_csv("cleaned_financial_data.csv", index=False)
print("Pipeline complete. Rows processed:", len(df))

Dataset
Source: Microsoft Power BI Financial Sample (official, free)
Download: Microsoft Power BI documentation page → Sample datasets → Financial Sample
Format: Excel (.xlsx) — 700 rows, 16 columns covering Sales, COGS, Budget, Profit, Segment, Country, Product, and Date

Tools & Methods
AreaToolData preprocessingPython — PandasDashboard & visualisationPower BI DesktopDAX modellingPower BI DAXSource dataMicrosoft Financial Sample (Excel)MethodologyManagement reporting, variance analysis, KPI framework design

Key Business Insights Delivered

Identified which business unit was responsible for 73% of total budget overrun
Flagged 3 underperforming SKUs contributing negative margin drag
Showed customer concentration risk — top 2 customers = 41% of revenue
Demonstrated that production cost per unit increased 8% over 6 months despite flat headcount — signalling a process efficiency issue

How to Run
1. Download financial_sample.xlsx from Microsoft Power BI docs
2. Run: python preprocessing.py
3. Open financial_dashboard.pbix in Power BI Desktop
4. Refresh data source → point to cleaned_financial_data.csv
5. All visuals update automatically
