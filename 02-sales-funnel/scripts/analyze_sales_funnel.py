"""Sales funnel analysis using a fictional synthetic leads dataset."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "sales_leads_synthetic.csv"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
required = {"lead_id", "stage", "channel", "region", "order_value_inr"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

df["order_value_inr"] = pd.to_numeric(df["order_value_inr"], errors="coerce").fillna(0)
total_leads = len(df)
booked = int((df["stage"] == "Order Booked").sum())
lost = int((df["stage"] == "Lost").sum())
conversion = booked / total_leads * 100 if total_leads else 0
lost_rate = lost / total_leads * 100 if total_leads else 0
booked_value = df.loc[df["stage"] == "Order Booked", "order_value_inr"].sum()

kpis = pd.DataFrame([
    ("Total Leads", total_leads),
    ("Orders Booked", booked),
    ("Lead-to-Order Conversion (%)", round(conversion, 2)),
    ("Lost Leads", lost),
    ("Lost Rate (%)", round(lost_rate, 2)),
    ("Total Booked Order Value (INR)", round(booked_value, 2)),
], columns=["KPI", "Value"])

stage_summary = (df.groupby("stage").size().rename("lead_count").reset_index()
                 .sort_values("lead_count", ascending=False))
channel_summary = (df.groupby("channel").agg(
    total_leads=("lead_id", "count"),
    orders_booked=("stage", lambda s: (s == "Order Booked").sum()),
    booked_value_inr=("order_value_inr", "sum")
).reset_index())
channel_summary["conversion_pct"] = (
    channel_summary["orders_booked"] / channel_summary["total_leads"] * 100
).round(2)
region_summary = (df.groupby("region").agg(
    total_leads=("lead_id", "count"),
    orders_booked=("stage", lambda s: (s == "Order Booked").sum()),
    booked_value_inr=("order_value_inr", "sum")
).reset_index())
region_summary["conversion_pct"] = (
    region_summary["orders_booked"] / region_summary["total_leads"] * 100
).round(2)
loss_summary = (df[df["stage"] == "Lost"].groupby("lost_reason").size()
                .rename("lost_leads").reset_index()
                .sort_values("lost_leads", ascending=False))

kpis.to_csv(OUT / "kpi_summary.csv", index=False)
stage_summary.to_csv(OUT / "stage_summary.csv", index=False)
channel_summary.to_csv(OUT / "channel_performance.csv", index=False)
region_summary.to_csv(OUT / "region_performance.csv", index=False)
loss_summary.to_csv(OUT / "lost_reasons.csv", index=False)

ax = stage_summary.set_index("stage")["lead_count"].plot(kind="bar", title="Sales Funnel: Leads by Current Stage")
ax.set_xlabel("Current stage")
ax.set_ylabel("Number of leads")
plt.tight_layout()
plt.savefig(OUT / "sales_funnel_stage_counts.png", dpi=150)
plt.close()
print(kpis.to_string(index=False))
print(f"\nOutputs saved to: {OUT}")
