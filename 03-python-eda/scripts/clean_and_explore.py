"""Clean and explore a fictional healthcare operations dataset."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "raw_healthcare_operations.csv"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
print("RAW SHAPE:", df.shape)
print("\nRAW DATA TYPES:\n", df.dtypes)
print("\nMISSING VALUES:\n", df.isna().sum())
duplicate_count = int(df.duplicated().sum())
print("\nEXACT DUPLICATE ROWS:", duplicate_count)

clean = df.drop_duplicates().copy()
clean["admission_date"] = pd.to_datetime(clean["admission_date"], errors="coerce")
for col in ["length_of_stay_days", "claim_amount_inr"]:
    clean[col] = pd.to_numeric(clean[col], errors="coerce")
for col in ["department", "diagnosis_group", "case_status", "follow_up_required"]:
    clean[col] = clean[col].astype("string").str.strip().replace("", pd.NA).fillna("Unknown")

# Flag invalid values; preserve unknown numeric values rather than guessing them.
clean["invalid_length_of_stay"] = clean["length_of_stay_days"].lt(0).fillna(False)
clean["invalid_claim_amount"] = clean["claim_amount_inr"].lt(0).fillna(False)
clean["claim_amount_band"] = pd.cut(
    clean["claim_amount_inr"],
    bins=[-np.inf, 10000, 25000, 50000, np.inf],
    labels=["Up to 10k", "10k-25k", "25k-50k", "Above 50k"]
)

department_summary = clean.groupby("department").agg(
    case_count=("case_id", "count"),
    avg_length_of_stay=("length_of_stay_days", "mean"),
    avg_claim_amount=("claim_amount_inr", "mean")
).reset_index()
status_summary = clean.groupby("case_status").size().rename("case_count").reset_index()
follow_up_summary = clean.groupby("follow_up_required").size().rename("case_count").reset_index()

clean.to_csv(OUT / "cleaned_healthcare_operations.csv", index=False)
department_summary.to_csv(OUT / "department_summary.csv", index=False)
status_summary.to_csv(OUT / "status_summary.csv", index=False)
follow_up_summary.to_csv(OUT / "follow_up_summary.csv", index=False)

ax = status_summary.set_index("case_status")["case_count"].plot(kind="bar", title="Cases by Status")
ax.set_xlabel("Case status")
ax.set_ylabel("Number of cases")
plt.tight_layout()
plt.savefig(OUT / "cases_by_status.png", dpi=150)
plt.close()

print("\nCLEANED SHAPE:", clean.shape)
print("\nDEPARTMENT SUMMARY:\n", department_summary.round(2).to_string(index=False))
print(f"\nOutputs saved to: {OUT}")
