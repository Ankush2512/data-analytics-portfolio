"""Execution, data-quality and reconciliation tests for Project 05."""
from pathlib import Path
import importlib.util
import subprocess
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "05-business-operations-mis"
SCRIPT = PROJECT / "scripts" / "build_operations_mis.py"
OUTPUT = PROJECT / "outputs"

spec = importlib.util.spec_from_file_location("operations_mis", SCRIPT)
mis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mis)


class BusinessOperationsMisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks, cls.targets, cls.validation = mis.load_and_validate()
        cls.reports = mis.build_reports(cls.tasks, cls.targets)
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], cwd=ROOT,
            capture_output=True, text=True
        )
        if result.returncode:
            raise RuntimeError(result.stdout + "\n" + result.stderr)
        cls.stdout = result.stdout

    def test_source_data_validation_passes(self):
        self.assertEqual(len(self.tasks), 120)
        self.assertEqual(self.tasks["task_id"].nunique(), 120)
        self.assertEqual(len(self.targets), 36)
        self.assertEqual(int(self.validation.loc[
            self.validation["validation_check"] == "duplicate task IDs", "result"
        ].iloc[0]), 0)

    def test_task_status_counts_reconcile(self):
        status_total = int(self.reports["Status Summary"]["task_count"].sum())
        dept_total = int(self.reports["Department Summary"]["tasks_recorded"].sum())
        month_total = int(self.reports["Monthly Trend"]["tasks_recorded"].sum())
        self.assertEqual(status_total, 120)
        self.assertEqual(dept_total, 120)
        self.assertEqual(month_total, 120)

    def test_completed_and_open_tasks_reconcile(self):
        kpis = self.reports["KPI Summary"].set_index("metric")["value"]
        self.assertEqual(int(kpis["Completed tasks"]) + int(kpis["Open tasks"]), 120)
        self.assertEqual(int(kpis["Overdue tasks"]),
                         int(self.tasks["task_status"].eq("Overdue").sum()))

    def test_sla_compliance_uses_completed_tasks(self):
        completed = self.tasks[self.tasks["task_status"].eq("Completed")]
        expected = round(completed["sla_met"].astype(str).str.lower().eq("yes").mean() * 100, 2)
        actual = float(self.reports["KPI Summary"].set_index("metric").loc["SLA compliance", "value"])
        self.assertAlmostEqual(actual, expected, places=2)
        self.assertGreaterEqual(actual, 0)
        self.assertLessEqual(actual, 100)

    def test_target_comparison_and_ageing_snapshot_are_documented(self):
        kpis = self.reports["KPI Summary"].set_index("metric")["value"]
        self.assertEqual(int(kpis["Monthly target total"]),
                         int(self.targets["monthly_target_tasks"].sum()))
        self.assertEqual(kpis["Ageing snapshot date"], "2026-06-30")
        self.assertTrue(self.reports["Pending Ageing"]["open_task_count"].sum()
                        == int((self.tasks["task_status"] != "Completed").sum()))

    def test_script_creates_workbook_csvs_and_charts(self):
        self.assertIn("MIS report generated successfully.", self.stdout)
        expected = [
            "business_operations_mis.xlsx", "data_validation.csv",
            "kpi_summary.csv", "department_summary.csv", "monthly_dept_mis.csv",
            "monthly_trend.csv", "status_summary.csv", "pending_ageing.csv",
            "complete_task_data.csv", "completed_by_department.png",
            "task_status_distribution.png", "monthly_task_trend.png"
        ]
        for filename in expected:
            path = OUTPUT / filename
            self.assertTrue(path.is_file(), msg=filename)
            self.assertGreater(path.stat().st_size, 0, msg=filename)

    def test_workbook_contains_all_expected_sheets(self):
        workbook = pd.ExcelFile(OUTPUT / "business_operations_mis.xlsx")
        self.assertEqual(set(workbook.sheet_names), {
            "Data Validation", "KPI Summary", "Department Summary",
            "Monthly Dept MIS", "Monthly Trend", "Status Summary",
            "Pending Ageing", "Complete Task Data"
        })


if __name__ == "__main__":
    unittest.main()
