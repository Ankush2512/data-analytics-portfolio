"""Build validated MIS summaries, charts and an Excel workbook.

All source records are synthetic. Open-task ageing is measured as of
2026-06-30, the end of the dataset period, for reproducible reporting.
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = BASE_DIR / "outputs"
SNAPSHOT_DATE = pd.Timestamp("2026-06-30")

TASK_FILE = DATA_DIR / "operations_tasks_synthetic.csv"
TARGET_FILE = DATA_DIR / "monthly_targets_synthetic.csv"

TASK_COLUMNS = {
    "task_id", "task_date", "department", "task_type", "priority",
    "task_status", "target_sla_days", "actual_tat_days", "sla_met", "owner_team"
}
TARGET_COLUMNS = {"month", "department", "monthly_target_tasks"}
VALID_STATUSES = {"Completed", "Pending", "In Progress", "Overdue"}


def load_and_validate():
    tasks = pd.read_csv(TASK_FILE)
    targets = pd.read_csv(TARGET_FILE)

    missing_task_cols = TASK_COLUMNS - set(tasks.columns)
    missing_target_cols = TARGET_COLUMNS - set(targets.columns)
    if missing_task_cols or missing_target_cols:
        raise ValueError(
            f"Missing task columns: {sorted(missing_task_cols)}; "
            f"missing target columns: {sorted(missing_target_cols)}"
        )

    tasks["task_date"] = pd.to_datetime(tasks["task_date"], errors="coerce")
    tasks["target_sla_days"] = pd.to_numeric(tasks["target_sla_days"], errors="coerce")
    tasks["actual_tat_days"] = pd.to_numeric(tasks["actual_tat_days"], errors="coerce")
    targets["month"] = targets["month"].astype(str)
    targets["monthly_target_tasks"] = pd.to_numeric(
        targets["monthly_target_tasks"], errors="coerce"
    )

    checks = [
        ("task row count", len(tasks)),
        ("unique task IDs", tasks["task_id"].nunique()),
        ("duplicate task IDs", int(tasks["task_id"].duplicated().sum())),
        ("missing task IDs", int(tasks["task_id"].isna().sum())),
        ("invalid task dates", int(tasks["task_date"].isna().sum())),
        ("unknown statuses", int((~tasks["task_status"].isin(VALID_STATUSES)).sum())),
        ("completed rows missing actual TAT", int(
            (tasks["task_status"].eq("Completed") & tasks["actual_tat_days"].isna()).sum()
        )),
        ("completed rows missing SLA result", int(
            (tasks["task_status"].eq("Completed") & tasks["sla_met"].isna()).sum()
        )),
        ("negative actual TAT values", int((tasks["actual_tat_days"] < 0).sum())),
        ("duplicate department-month targets", int(
            targets.duplicated(["month", "department"]).sum()
        )),
        ("invalid target values", int(
            (targets["monthly_target_tasks"].isna() |
             (targets["monthly_target_tasks"] < 0)).sum()
        )),
    ]
    validation = pd.DataFrame(checks, columns=["validation_check", "result"])

    if tasks["task_id"].duplicated().any():
        raise ValueError("Duplicate task IDs found; stopping to avoid misleading totals.")
    if tasks["task_date"].isna().any():
        raise ValueError("Invalid task dates found.")
    if not tasks["task_status"].isin(VALID_STATUSES).all():
        raise ValueError("Unexpected task status found.")
    if targets.duplicated(["month", "department"]).any():
        raise ValueError("Duplicate department-month target combinations found.")
    if (targets["monthly_target_tasks"].isna() |
            (targets["monthly_target_tasks"] < 0)).any():
        raise ValueError("Invalid monthly target values found.")

    completed = tasks["task_status"].eq("Completed")
    if tasks.loc[completed, "actual_tat_days"].isna().any():
        raise ValueError("Completed tasks must have actual_tat_days.")
    if tasks.loc[completed, "sla_met"].isna().any():
        raise ValueError("Completed tasks must have an SLA result.")
    if (tasks.loc[completed, "actual_tat_days"] < 0).any():
        raise ValueError("Actual TAT cannot be negative.")

    return tasks, targets, validation


def build_reports(tasks, targets):
    tasks = tasks.copy()
    tasks["month"] = tasks["task_date"].dt.to_period("M").astype(str)
    tasks["is_completed"] = tasks["task_status"].eq("Completed")
    tasks["is_open"] = ~tasks["is_completed"]
    tasks["is_sla_met"] = tasks["sla_met"].astype(str).str.strip().str.lower().eq("yes")

    # Ageing is a fixed historical snapshot, not a live calculation.
    tasks["open_age_days"] = (SNAPSHOT_DATE - tasks["task_date"]).dt.days
    tasks.loc[~tasks["is_open"], "open_age_days"] = pd.NA
    tasks["ageing_bucket"] = pd.cut(
        tasks["open_age_days"],
        bins=[-1, 7, 14, 30, float("inf")],
        labels=["0-7 days", "8-14 days", "15-30 days", "31+ days"]
    ).astype("string")

    monthly_dept = (
        tasks.groupby(["month", "department"], as_index=False)
        .agg(
            tasks_recorded=("task_id", "count"),
            completed_tasks=("is_completed", "sum"),
            open_tasks=("is_open", "sum"),
            overdue_tasks=("task_status", lambda s: s.eq("Overdue").sum()),
            completed_sla_met=("is_sla_met", lambda s: s[tasks.loc[s.index, "is_completed"]].sum()),
            completed_sla_breached=("sla_met", lambda s: (s.astype(str).str.lower().eq("no") & tasks.loc[s.index, "is_completed"]).sum()),
        )
        .merge(targets, on=["month", "department"], how="outer")
    )
    numeric_cols = [
        "tasks_recorded", "completed_tasks", "open_tasks", "overdue_tasks",
        "completed_sla_met", "completed_sla_breached", "monthly_target_tasks"
    ]
    monthly_dept[numeric_cols] = monthly_dept[numeric_cols].fillna(0).astype(int)
    monthly_dept["target_achievement_pct"] = (
        monthly_dept["completed_tasks"].div(monthly_dept["monthly_target_tasks"].replace(0, pd.NA))
        .mul(100).astype("Float64").round(2)
    )
    sla_denominator = monthly_dept["completed_sla_met"] + monthly_dept["completed_sla_breached"]
    monthly_dept["sla_compliance_pct"] = (
        monthly_dept["completed_sla_met"].div(sla_denominator.replace(0, pd.NA))
        .mul(100).astype("Float64").round(2)
    )

    dept_summary = (
        tasks.groupby("department", as_index=False)
        .agg(
            tasks_recorded=("task_id", "count"),
            completed_tasks=("is_completed", "sum"),
            open_tasks=("is_open", "sum"),
            overdue_tasks=("task_status", lambda s: s.eq("Overdue").sum()),
        )
        .merge(
            monthly_dept.groupby("department", as_index=False)
            .agg(monthly_target_tasks=("monthly_target_tasks", "sum")),
            on="department", how="left"
        )
    )
    dept_summary["target_achievement_pct"] = (
        dept_summary["completed_tasks"].div(
            dept_summary["monthly_target_tasks"].replace(0, pd.NA)
        ).mul(100).astype("Float64").round(2)
    )

    status_summary = (
        tasks.groupby("task_status", as_index=False)
        .agg(task_count=("task_id", "count"))
        .sort_values("task_count", ascending=False)
    )
    ageing_summary = (
        tasks.loc[tasks["is_open"]]
        .groupby(["department", "ageing_bucket"], observed=False, as_index=False)
        .agg(open_task_count=("task_id", "count"))
    )
    monthly_summary = (
        tasks.groupby("month", as_index=False)
        .agg(
            tasks_recorded=("task_id", "count"),
            completed_tasks=("is_completed", "sum"),
            open_tasks=("is_open", "sum"),
        )
    )

    completed = tasks[tasks["is_completed"]]
    total_tasks = len(tasks)
    total_completed = int(tasks["is_completed"].sum())
    total_open = int(tasks["is_open"].sum())
    sla_rate = (
        round(completed["sla_met"].astype(str).str.lower().eq("yes").mean() * 100, 2)
        if len(completed) else None
    )
    total_targets = int(targets["monthly_target_tasks"].sum())
    overall_target_achievement = (
        round(total_completed / total_targets * 100, 2) if total_targets else None
    )
    kpi_summary = pd.DataFrame([
        ["Tasks recorded", total_tasks, "Count of rows in the synthetic task file"],
        ["Completed tasks", total_completed, "Tasks with status Completed"],
        ["Open tasks", total_open, "Pending + In Progress + Overdue"],
        ["Overdue tasks", int(tasks["task_status"].eq("Overdue").sum()), "Status explicitly marked Overdue"],
        ["SLA compliance", sla_rate, "SLA-met completed tasks / all completed tasks (%)"],
        ["Completed vs target", overall_target_achievement, "Completed sample tasks / sum of monthly department targets (%)"],
        ["Monthly target total", total_targets, "Sum of supplied department-month targets"],
        ["Ageing snapshot date", SNAPSHOT_DATE.date().isoformat(), "Fixed date used for open-task ageing"],
    ], columns=["metric", "value", "definition"])

    return {
        "KPI Summary": kpi_summary,
        "Department Summary": dept_summary,
        "Monthly Dept MIS": monthly_dept,
        "Monthly Trend": monthly_summary,
        "Status Summary": status_summary,
        "Pending Ageing": ageing_summary,
        "Complete Task Data": tasks,
    }


def create_charts(reports):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dept = reports["Department Summary"].sort_values("completed_tasks", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(dept["department"], dept["completed_tasks"], label="Completed tasks")
    ax.set_title("Completed Tasks by Department")
    ax.set_ylabel("Task count")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "completed_by_department.png", dpi=160)
    plt.close(fig)

    status = reports["Status Summary"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(status["task_status"], status["task_count"])
    ax.set_title("Task Status Distribution")
    ax.set_ylabel("Task count")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "task_status_distribution.png", dpi=160)
    plt.close(fig)

    monthly = reports["Monthly Trend"].sort_values("month")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(monthly["month"], monthly["tasks_recorded"], marker="o", label="Recorded")
    ax.plot(monthly["month"], monthly["completed_tasks"], marker="o", label="Completed")
    ax.set_title("Monthly Task Volume")
    ax.set_ylabel("Task count")
    ax.legend()
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "monthly_task_trend.png", dpi=160)
    plt.close(fig)


def main():
    try:
        tasks, targets, validation = load_and_validate()
        reports = build_reports(tasks, targets)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        validation.to_csv(OUTPUT_DIR / "data_validation.csv", index=False)
        for sheet_name, frame in reports.items():
            safe_name = sheet_name.lower().replace(" ", "_")
            frame.to_csv(OUTPUT_DIR / f"{safe_name}.csv", index=False)

        create_charts(reports)
        workbook_path = OUTPUT_DIR / "business_operations_mis.xlsx"
        with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
            validation.to_excel(writer, sheet_name="Data Validation", index=False)
            for sheet_name, frame in reports.items():
                frame.to_excel(writer, sheet_name=sheet_name[:31], index=False)

        print("MIS report generated successfully.")
        print(f"Input tasks: {len(tasks)} | Departments: {tasks['department'].nunique()}")
        print(f"Completed: {int(tasks['task_status'].eq('Completed').sum())}")
        print(f"Open: {int((~tasks['task_status'].eq('Completed')).sum())}")
        print(f"Snapshot date for ageing: {SNAPSHOT_DATE.date()}")
        print(f"Output folder: {OUTPUT_DIR}")
        print("Note: target achievement compares the recorded sample completions with the supplied targets.")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
