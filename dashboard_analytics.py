import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("output/cleaned_financial_data.csv", parse_dates=["date"])

# ── PALETTE ──────────────────────────────────────────────────────────────────
BLUE    = "#1F4E79"
LBLUE   = "#2E75B6"
GREEN   = "#1E8449"
AMBER   = "#D4AC0D"
RED     = "#C0392B"
LGRAY   = "#F2F2F2"
MGRAY   = "#CCCCCC"

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor("#F8F9FA")
fig.suptitle("Business Performance Dashboard — MI Analytics Preview",
             fontsize=18, fontweight="bold", color=BLUE, y=0.98)

# ── PAGE 1: REVENUE vs BUDGET BY BUSINESS UNIT (Waterfall style) ─────────────
ax1 = fig.add_subplot(2, 3, 1)
bu_data = df.groupby("business_unit").agg(
    sales=("sales", "sum"), budget=("budget", "sum")
).reset_index()
bu_data["variance"] = bu_data["sales"] - bu_data["budget"]
bu_data["color"]    = bu_data["variance"].apply(lambda x: GREEN if x >= 0 else RED)
bu_data = bu_data.sort_values("variance")

bars = ax1.barh(bu_data["business_unit"], bu_data["variance"] / 1e6,
                color=bu_data["color"], edgecolor="white", height=0.6)
ax1.axvline(0, color=BLUE, linewidth=1.5, linestyle="--")
ax1.set_title("Budget Variance by Business Unit (₹ Mn)", fontweight="bold",
              color=BLUE, fontsize=11)
ax1.set_xlabel("Variance (₹ Mn)", fontsize=9)
ax1.tick_params(axis="y", labelsize=9)
ax1.set_facecolor(LGRAY)
ax1.grid(axis="x", alpha=0.3)
for bar, val in zip(bars, bu_data["variance"] / 1e6):
    ax1.text(val + (0.5 if val >= 0 else -0.5), bar.get_y() + bar.get_height() / 2,
             f"₹{val:.1f}M", va="center", ha="left" if val >= 0 else "right",
             fontsize=8, fontweight="bold")

# ── PAGE 1: MONTHLY REVENUE vs BUDGET TREND ──────────────────────────────────
ax2 = fig.add_subplot(2, 3, 2)
monthly = df.groupby(["year", "month"]).agg(
    sales=("sales", "sum"), budget=("budget", "sum")
).reset_index().sort_values(["year", "month"])
monthly["label"] = monthly["month"].apply(
    lambda m: ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"][m-1]
) + "-" + monthly["year"].astype(str).str[-2:]

x = range(len(monthly))
ax2.fill_between(x, monthly["budget"]/1e6, alpha=0.15, color=AMBER, label="Budget")
ax2.plot(x, monthly["budget"]/1e6, color=AMBER, linewidth=1.5, linestyle="--")
ax2.plot(x, monthly["sales"]/1e6, color=BLUE, linewidth=2.5, marker="o",
         markersize=4, label="Actual Revenue")
ax2.set_title("Monthly Revenue vs Budget (₹ Mn)", fontweight="bold",
              color=BLUE, fontsize=11)
ax2.set_xticks(list(x)[::3])
ax2.set_xticklabels(monthly["label"].iloc[::3], rotation=45, fontsize=8)
ax2.legend(fontsize=8)
ax2.set_facecolor(LGRAY)
ax2.grid(alpha=0.3)
ax2.set_ylabel("₹ Mn", fontsize=9)

# ── PAGE 2: TOP 10 vs BOTTOM 5 SKUs by Gross Margin ──────────────────────────
ax3 = fig.add_subplot(2, 3, 3)
sku_margin = df.groupby("product").agg(
    revenue=("sales", "sum"),
    margin=("gross_margin_pct", "mean")
).reset_index().sort_values("margin", ascending=True)

colors = [GREEN if m >= 30 else AMBER if m >= 20 else RED
          for m in sku_margin["margin"]]
ax3.barh(sku_margin["product"], sku_margin["margin"],
         color=colors, edgecolor="white", height=0.6)
ax3.axvline(30, color=GREEN, linewidth=1.5, linestyle="--", alpha=0.7, label="Target (30%)")
ax3.axvline(20, color=RED,   linewidth=1.5, linestyle="--", alpha=0.7, label="Threshold (20%)")
ax3.set_title("Gross Margin % by Product (SKU)", fontweight="bold",
              color=BLUE, fontsize=11)
ax3.set_xlabel("Gross Margin %", fontsize=9)
ax3.tick_params(axis="y", labelsize=8)
ax3.set_facecolor(LGRAY)
ax3.grid(axis="x", alpha=0.3)
ax3.legend(fontsize=8)

# ── PAGE 3: COST per UNIT TREND (12-month) ───────────────────────────────────
ax4 = fig.add_subplot(2, 3, 4)
cpu = df.groupby(["year", "month"]).agg(
    cost=("cost_actual", "sum"),
    units=("units_produced", "sum")
).reset_index().sort_values(["year", "month"])
cpu["cost_per_unit"] = cpu["cost"] / cpu["units"]
cpu["label"] = cpu["month"].apply(
    lambda m: ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"][m-1]
) + "-" + cpu["year"].astype(str).str[-2:]

colors_cpu = [RED if v > cpu["cost_per_unit"].quantile(0.75)
              else AMBER if v > cpu["cost_per_unit"].mean()
              else GREEN for v in cpu["cost_per_unit"]]
ax4.bar(range(len(cpu)), cpu["cost_per_unit"], color=colors_cpu, edgecolor="white")
ax4.plot(range(len(cpu)), cpu["cost_per_unit"], color=BLUE, linewidth=2,
         marker="o", markersize=4, zorder=5)
ax4.axhline(cpu["cost_per_unit"].mean(), color=AMBER, linewidth=1.5,
            linestyle="--", label=f"Avg: ₹{cpu['cost_per_unit'].mean():.0f}")
ax4.set_title("Production Cost per Unit — Monthly Trend", fontweight="bold",
              color=BLUE, fontsize=11)
ax4.set_xticks(range(len(cpu))[::3])
ax4.set_xticklabels(cpu["label"].iloc[::3], rotation=45, fontsize=8)
ax4.legend(fontsize=8)
ax4.set_facecolor(LGRAY)
ax4.grid(axis="y", alpha=0.3)
ax4.set_ylabel("₹ / Unit", fontsize=9)

# ── PAGE 3: COST BREAKDOWN BY FUNCTION ───────────────────────────────────────
ax5 = fig.add_subplot(2, 3, 5)
func_cost = df.groupby("cost_function")["cost_actual"].sum().sort_values(ascending=False)
wedge_colors = [BLUE, LBLUE, AMBER, GREEN, MGRAY]
wedges, texts, autotexts = ax5.pie(
    func_cost.values, labels=func_cost.index,
    autopct="%1.1f%%", colors=wedge_colors,
    startangle=90, pctdistance=0.75,
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
for t in autotexts:
    t.set_fontsize(9)
    t.set_fontweight("bold")
ax5.set_title("Cost Breakdown by Function", fontweight="bold",
              color=BLUE, fontsize=11)

# ── KPI SUMMARY TABLE ────────────────────────────────────────────────────────
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis("off")
ax6.set_facecolor(LGRAY)

total_rev   = df["sales"].sum() / 1e7
total_bud   = df["budget"].sum() / 1e7
variance    = total_rev - total_bud
var_pct     = variance / total_bud * 100
avg_ebitda  = df["ebitda_margin_pct"].mean()
avg_gm      = df["gross_margin_pct"].mean()
top5_conc   = df["customer_concentration"].iloc[0]
downtime    = df["downtime_hours"].sum()
dt_loss     = df["downtime_revenue_loss"].sum() / 1e7

kpis = [
    ("Total Revenue",       f"₹{total_rev:.1f} Cr",    GREEN),
    ("vs Budget",           f"{var_pct:+.1f}%",         GREEN if variance >= 0 else RED),
    ("EBITDA Margin",       f"{avg_ebitda:.1f}%",       GREEN if avg_ebitda > 10 else AMBER),
    ("Gross Margin",        f"{avg_gm:.1f}%",           GREEN if avg_gm > 25 else AMBER),
    ("Top 5 Cust. Conc.",   f"{top5_conc:.1f}%",        AMBER),
    ("Total Downtime",      f"{downtime:,.0f} hrs",     RED if downtime > 5000 else AMBER),
    ("Est. Downtime Loss",  f"₹{dt_loss:.1f} Cr",       RED),
]

ax6.set_title("Executive KPI Summary", fontweight="bold", color=BLUE, fontsize=11, pad=10)
y_pos = 0.92
for label, value, color in kpis:
    ax6.text(0.05, y_pos, label, transform=ax6.transAxes,
             fontsize=10, color="#333333", va="top")
    ax6.text(0.95, y_pos, value, transform=ax6.transAxes,
             fontsize=11, fontweight="bold", color=color, va="top", ha="right")
    ax6.plot([0.05, 0.95], [y_pos - 0.04, y_pos - 0.04],
             color=MGRAY, linewidth=0.5, transform=ax6.transAxes)
    y_pos -= 0.13

rect = mpatches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                boxstyle="round,pad=0.01",
                                linewidth=2, edgecolor=BLUE,
                                facecolor="white", transform=ax6.transAxes, zorder=0)
ax6.add_patch(rect)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("charts/dashboard_preview.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print("Dashboard preview saved → charts/dashboard_preview.png")
