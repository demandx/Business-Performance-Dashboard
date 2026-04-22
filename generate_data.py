import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ── CONFIG ──────────────────────────────────────────────────────────────────
SEGMENTS      = ["Automotive Components", "Industrial Equipment", "Consumer Electronics"]
COUNTRIES     = ["India", "Germany", "USA", "Japan", "UK"]
PRODUCTS      = {
    "Automotive Components": ["Drive Shaft", "Brake Assembly", "Gear Box", "Clutch Kit", "Suspension Unit"],
    "Industrial Equipment": ["Hydraulic Pump", "Conveyor Belt", "CNC Module", "Robotic Arm", "Sensor Array"],
    "Consumer Electronics": ["PCB Assembly", "Power Unit", "Control Panel", "Display Module", "Wiring Harness"]
}
CUSTOMERS     = [f"Client_{i:02d}" for i in range(1, 21)]
BIZ_UNITS     = ["North Zone", "South Zone", "East Zone", "West Zone", "Export Division"]
FUNCTIONS     = ["Production", "Logistics", "Overhead", "Labour", "R&D"]

START_DATE    = datetime(2023, 1, 1)
END_DATE      = datetime(2024, 12, 31)
N_ROWS        = 1200

# ── GENERATE ────────────────────────────────────────────────────────────────
dates = [START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
         for _ in range(N_ROWS)]
dates.sort()

rows = []
for date in dates:
    segment  = random.choice(SEGMENTS)
    product  = random.choice(PRODUCTS[segment])
    country  = random.choice(COUNTRIES)
    customer = random.choice(CUSTOMERS)
    biz_unit = random.choice(BIZ_UNITS)
    function = random.choice(FUNCTIONS)

    units_sold   = random.randint(50, 800)
    unit_price   = round(random.uniform(500, 8000), 2)
    sales        = round(units_sold * unit_price, 2)

    cogs_pct     = random.uniform(0.45, 0.72)
    cogs         = round(sales * cogs_pct, 2)
    gross_profit = round(sales - cogs, 2)

    opex_pct     = random.uniform(0.10, 0.22)
    operating_exp = round(sales * opex_pct, 2)
    ebitda       = round(gross_profit - operating_exp, 2)

    # Budget: sometimes over, sometimes under
    budget_factor = random.uniform(0.82, 1.18)
    budget        = round(sales * budget_factor, 2)

    cost_actual   = round(cogs + operating_exp, 2)
    cost_budget   = round(cost_actual * random.uniform(0.88, 1.12), 2)

    downtime_hrs  = round(random.uniform(0, 24), 1)
    headcount     = random.randint(10, 120)
    units_produced = random.randint(40, 850)

    rows.append({
        "date":             date.strftime("%Y-%m-%d"),
        "segment":          segment,
        "product":          product,
        "country":          country,
        "customer":         customer,
        "business_unit":    biz_unit,
        "cost_function":    function,
        "units_sold":       units_sold,
        "unit_price":       unit_price,
        "sales":            sales,
        "cogs":             cogs,
        "gross_profit":     gross_profit,
        "operating_expenses": operating_exp,
        "ebitda":           ebitda,
        "budget":           budget,
        "cost_actual":      cost_actual,
        "cost_budget":      cost_budget,
        "downtime_hours":   downtime_hrs,
        "headcount":        headcount,
        "units_produced":   units_produced,
    })

df = pd.DataFrame(rows)
df.to_excel("data/financial_sample.xlsx", index=False)
print(f"Dataset generated: {len(df)} rows → data/financial_sample.xlsx")
print(df.head(3).to_string())
