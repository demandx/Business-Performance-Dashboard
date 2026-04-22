import pandas as pd
import numpy as np
import os

# ── 1. INGEST ────────────────────────────────────────────────────────────────
print("=" * 65)
print("  BUSINESS PERFORMANCE DASHBOARD — PREPROCESSING PIPELINE")
print("=" * 65)

RAW_PATH    = "data/financial_sample.xlsx"
OUTPUT_PATH = "output/cleaned_financial_data.csv"

os.makedirs("output", exist_ok=True)

print("\n[1/7] Loading raw data...")
df = pd.read_excel(RAW_PATH)
print(f"      Rows loaded      : {len(df):,}")
print(f"      Columns loaded   : {len(df.columns)}")

# ── 2. STANDARDISE COLUMNS ───────────────────────────────────────────────────
print("\n[2/7] Standardising column names...")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(f"      Columns normalised: {list(df.columns)}")

# ── 3. DATE ENGINEERING ──────────────────────────────────────────────────────
print("\n[3/7] Parsing dates and engineering time dimensions...")
df["date"]           = pd.to_datetime(df["date"])
df["year"]           = df["date"].dt.year
df["month"]          = df["date"].dt.month
df["month_name"]     = df["date"].dt.strftime("%b")
df["quarter"]        = df["date"].dt.quarter
df["fiscal_quarter"] = "Q" + df["quarter"].astype(str) + "-" + df["year"].astype(str)
df["month_year"]     = df["date"].dt.strftime("%b-%Y")
df["week_number"]    = df["date"].dt.isocalendar().week.astype(int)
print(f"      Date range       : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"      Fiscal quarters  : {sorted(df['fiscal_quarter'].unique())}")

# ── 4. NULL HANDLING ─────────────────────────────────────────────────────────
print("\n[4/7] Handling nulls and data quality issues...")
null_before = df.isnull().sum().sum()
df["sales"]              = df["sales"].fillna(0)
df["cogs"]               = df["cogs"].fillna(0)
df["ebitda"]             = df["ebitda"].fillna(0)
df["budget"]             = df["budget"].fillna(df["sales"].median())
df["downtime_hours"]     = df["downtime_hours"].fillna(0)
df["headcount"]          = df["headcount"].fillna(df["headcount"].median())
null_after = df.isnull().sum().sum()
print(f"      Nulls before     : {null_before}")
print(f"      Nulls after      : {null_after}")

# ── 5. FEATURE ENGINEERING ───────────────────────────────────────────────────
print("\n[5/7] Engineering KPI features...")

# Margin metrics
df["gross_margin_pct"]      = np.where(df["sales"] > 0,
                                (df["sales"] - df["cogs"]) / df["sales"] * 100, 0).round(2)
df["ebitda_margin_pct"]     = np.where(df["sales"] > 0,
                                df["ebitda"] / df["sales"] * 100, 0).round(2)
df["operating_expense_pct"] = np.where(df["sales"] > 0,
                                df["operating_expenses"] / df["sales"] * 100, 0).round(2)

# Budget variance
df["budget_variance"]       = (df["sales"] - df["budget"]).round(2)
df["budget_variance_pct"]   = np.where(df["budget"] > 0,
                                df["budget_variance"] / df["budget"] * 100, 0).round(2)
df["budget_status"]         = df["budget_variance"].apply(
                                lambda x: "Over Budget" if x < 0 else "On Track")

# Cost variance
df["cost_variance"]         = (df["cost_actual"] - df["cost_budget"]).round(2)
df["cost_variance_pct"]     = np.where(df["cost_budget"] > 0,
                                df["cost_variance"] / df["cost_budget"] * 100, 0).round(2)
df["cost_status"]           = df["cost_variance"].apply(
                                lambda x: "Over Budget" if x > 0 else "Within Budget")

# Operational efficiency
df["cost_per_unit"]         = np.where(df["units_produced"] > 0,
                                df["cost_actual"] / df["units_produced"], 0).round(2)
df["revenue_per_head"]      = np.where(df["headcount"] > 0,
                                df["sales"] / df["headcount"], 0).round(2)
df["output_per_head"]       = np.where(df["headcount"] > 0,
                                df["units_produced"] / df["headcount"], 0).round(2)
df["downtime_revenue_loss"] = (df["downtime_hours"] * (df["sales"] / 8)).round(2)

# RAG flags
def rag_flag(val, amber_thresh, red_thresh, higher_is_worse=True):
    if higher_is_worse:
        if val >= red_thresh:   return "RED"
        elif val >= amber_thresh: return "AMBER"
        else:                   return "GREEN"
    else:
        if val <= red_thresh:   return "RED"
        elif val <= amber_thresh: return "AMBER"
        else:                   return "GREEN"

df["margin_rag"]    = df["gross_margin_pct"].apply(
                        lambda x: rag_flag(x, 25, 15, higher_is_worse=False))
df["cost_rag"]      = df["cost_variance_pct"].apply(
                        lambda x: rag_flag(x, 5, 10, higher_is_worse=True))
df["downtime_rag"]  = df["downtime_hours"].apply(
                        lambda x: rag_flag(x, 8, 16, higher_is_worse=True))

print(f"      Features engineered: budget_variance, cost_variance, gross_margin_pct,")
print(f"                           ebitda_margin_pct, cost_per_unit, revenue_per_head,")
print(f"                           downtime_revenue_loss, RAG flags (margin/cost/downtime)")

# ── 6. CUSTOMER CONCENTRATION ────────────────────────────────────────────────
print("\n[6/7] Computing customer concentration metrics...")
customer_sales     = df.groupby("customer")["sales"].sum().sort_values(ascending=False)
top5_customers     = customer_sales.head(5).index.tolist()
total_sales        = customer_sales.sum()
top5_revenue       = customer_sales.head(5).sum()
concentration_pct  = round(top5_revenue / total_sales * 100, 2)
top2_pct           = round(customer_sales.head(2).sum() / total_sales * 100, 2)

df["is_top5_customer"]      = df["customer"].isin(top5_customers).astype(int)
df["customer_concentration"]= concentration_pct

print(f"      Top 5 customers  : {top5_customers}")
print(f"      Top 5 revenue %  : {concentration_pct}% of total revenue")
print(f"      Top 2 revenue %  : {top2_pct}% of total revenue")

# ── 7. EXPORT ────────────────────────────────────────────────────────────────
print("\n[7/7] Exporting cleaned dataset...")
df.to_csv(OUTPUT_PATH, index=False)
print(f"      Output saved     : {OUTPUT_PATH}")
print(f"      Final rows       : {len(df):,}")
print(f"      Final columns    : {len(df.columns)}")

# ── SUMMARY REPORT ───────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  PIPELINE SUMMARY — KEY BUSINESS METRICS")
print("=" * 65)

total_revenue   = df["sales"].sum()
total_budget    = df["budget"].sum()
total_ebitda    = df["ebitda"].sum()
avg_margin      = df["gross_margin_pct"].mean()
avg_ebitda_m    = df["ebitda_margin_pct"].mean()
total_variance  = df["budget_variance"].sum()
variance_pct    = total_variance / total_budget * 100
over_budget_rows= (df["budget_status"] == "Over Budget").sum()
total_downtime  = df["downtime_hours"].sum()
downtime_loss   = df["downtime_revenue_loss"].sum()

print(f"\n  Revenue")
print(f"    Total Revenue      : ₹{total_revenue/1e7:.2f} Cr")
print(f"    Total Budget       : ₹{total_budget/1e7:.2f} Cr")
print(f"    Budget Variance    : ₹{total_variance/1e7:.2f} Cr  ({variance_pct:+.1f}%)")

print(f"\n  Profitability")
print(f"    Avg Gross Margin   : {avg_margin:.1f}%")
print(f"    Avg EBITDA Margin  : {avg_ebitda_m:.1f}%")
print(f"    Total EBITDA       : ₹{total_ebitda/1e7:.2f} Cr")

print(f"\n  Cost Health")
print(f"    Over-Budget Lines  : {over_budget_rows:,} of {len(df):,} transactions")
print(f"    Over-Budget %      : {over_budget_rows/len(df)*100:.1f}%")

print(f"\n  Operational")
print(f"    Total Downtime     : {total_downtime:,.0f} hrs")
print(f"    Est. Revenue Loss  : ₹{downtime_loss/1e7:.2f} Cr")
print(f"    Customer Conc.     : Top 5 = {concentration_pct}% | Top 2 = {top2_pct}%")

print(f"\n  RAG Distribution")
print(f"    Margin RED lines   : {(df['margin_rag']=='RED').sum():,}")
print(f"    Cost RED lines     : {(df['cost_rag']=='RED').sum():,}")
print(f"    Downtime RED lines : {(df['downtime_rag']=='RED').sum():,}")

print("\n" + "=" * 65)
print("  Pipeline complete. Load output/cleaned_financial_data.csv")
print("  into Power BI Desktop and refresh to update all visuals.")
print("=" * 65)
