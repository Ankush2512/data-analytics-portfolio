"""Build a multi-sheet healthcare MIS report from a synthetic dataset.

Run from the repository root:
    python 01-healthcare-mis/scripts/build_healthcare_mis.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_DIR / "dataset" / "healthcare_cases_synthetic.csv"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

REQUIRED_COLUMNS = {
    "case_id", "admission_date", "department", "scheme", "case_status",
    "claim_amount_inr", "days_in_process", "query_raised"
}
VALID_STATUSES = {"Approved", "Pending", "Rejected", "Query Raised"}


def load_and_validate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = df.copy()
    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
    df["claim_amount_inr"] = pd.to_numeric(df["claim_amount_inr"], errors="coerce")
    df["days_in_process"] = pd.to_numeric(df["days_in_process"], errors="coerce")
    df["case_id"] = df["case_id"].astype("string").str.strip()
    df["department"] = df["department"].astype("string").str.strip()
    df["case_status"] = df["case_status"].astype("string").str.strip()

    # Remove duplicate case references; keep the first occurrence.
    df = df.drop_duplicates(subset=["case_id"], keep="first")
    df = df.dropna(subset=["case_id", "admission_date", "department", "case_status"])
    df = df[df["case_status"].isin(VALID_STATUSES)]
    df = df[df["claim_amount_inr"].ge(0) & df["days_in_process"].ge(0)]

    df["month"] = df["admission_date"].dt.to_period("M").astype(str)
    df["ageing_bucket"] = pd.cut(
        df["days_in_process"],
        bins=[-1, 7, 15, 30, float("inf")],
        labels=["0-7 days", "8-15 days", "16-30 days", "31+ days"]
    )
    return df


def build_summaries(df: pd.DataFrame):
    total_cases = int(df["case_id"].nunique())
    approved = int(df["case_status"].eq("Approved").sum())
    pending = int(df["case_status"].eq("Pending").sum())
    rejected = int(df["case_status"].eq("Rejected").sum())
    query = int(df["case_status"].eq("Query Raised").sum())
    closed = df[df["case_status"].isin(["Approved", "Rejected"])]

    kpis = pd.DataFrame({
        "Metric": [
            "Total Cases", "Approved Cases", "Pending Cases", "Rejected Cases",
            "Query Raised Cases", "Approval Rate", "Total Claim Value (INR)",
            "Approved Claim Value (INR)", "Average Closed-Case TAT (Days)"
        ],
        "Value": [
            total_cases, approved, pending, rejected, query,
            approved / total_cases if total_cases else 0,
            df["claim_amount_inr"].sum(),
            df.loc[df["case_status"].eq("Approved"), "claim_amount_inr"].sum(),
            closed["days_in_process"].mean() if not closed.empty else 0
        ]
    })

    dept = df.groupby("department", as_index=False).agg(
        total_cases=("case_id", "nunique"),
        approved_cases=("case_status", lambda s: s.eq("Approved").sum()),
        pending_cases=("case_status", lambda s: s.eq("Pending").sum()),
        claim_value_inr=("claim_amount_inr", "sum")
    )
    dept["approval_rate"] = dept["approved_cases"] / dept["total_cases"]
    dept = dept.sort_values("total_cases", ascending=False)

    monthly = df.groupby("month", as_index=False).agg(
        cases_received=("case_id", "nunique"),
        approved_cases=("case_status", lambda s: s.eq("Approved").sum()),
        claim_value_inr=("claim_amount_inr", "sum")
    ).sort_values("month")

    ageing = (
        df[df["case_status"].isin(["Pending", "Query Raised"])]
        .groupby("ageing_bucket", observed=False)
        .size().rename("open_cases").reset_index()
    )
    return kpis, dept, monthly, ageing


def main():
    df = load_and_validate(DATA_FILE)
    kpis, dept, monthly, ageing = build_summaries(df)

    df.to_csv(OUTPUT_DIR / "cleaned_healthcare_cases.csv", index=False)
    with pd.ExcelWriter(OUTPUT_DIR / "healthcare_mis_report.xlsx", engine="openpyxl") as writer:
        kpis.to_excel(writer, sheet_name="KPI Summary", index=False)
        dept.to_excel(writer, sheet_name="Department Summary", index=False)
        monthly.to_excel(writer, sheet_name="Monthly Trend", index=False)
        ageing.to_excel(writer, sheet_name="Pending Ageing", index=False)
        df.to_excel(writer, sheet_name="Case Data", index=False)

        # Improve readability of every worksheet.
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for column_cells in ws.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 34)

    plt.figure(figsize=(9, 5))
    plt.bar(dept["department"], dept["total_cases"])
    plt.title("Synthetic Healthcare Cases by Department")
    plt.xlabel("Department")
    plt.ylabel("Number of Cases")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "department_case_volume.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(monthly["month"], monthly["cases_received"], marker="o")
    plt.title("Monthly Synthetic Case Trend")
    plt.xlabel("Month")
    plt.ylabel("Cases Received")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_case_trend.png", dpi=150)
    plt.close()

    print(f"Validated {len(df)} unique synthetic cases.")
    print(f"Excel report saved to: {OUTPUT_DIR / 'healthcare_mis_report.xlsx'}")


if __name__ == "__main__":
    main()
