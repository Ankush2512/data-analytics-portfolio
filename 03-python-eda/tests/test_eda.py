"""Execution and reconciliation tests for Project 03."""
from pathlib import Path
import subprocess
import sys
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "03-python-eda"
OUTPUT = PROJECT / "output"


class PythonEdaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [sys.executable, str(PROJECT / "scripts" / "clean_and_explore.py")],
            cwd=ROOT, capture_output=True, text=True
        )
        if result.returncode:
            raise RuntimeError(result.stdout + "\n" + result.stderr)
        cls.stdout = result.stdout
        cls.raw = pd.read_csv(PROJECT / "dataset" / "raw_healthcare_operations.csv")
        cls.clean = pd.read_csv(OUTPUT / "cleaned_healthcare_operations.csv")
        
    def test_script_executes_and_reports_output_location(self):
        self.assertIn("Outputs saved to:", self.stdout)

    def test_exact_duplicates_are_removed(self):
        self.assertEqual(len(self.raw), 102)
        self.assertEqual(int(self.raw.duplicated().sum()), 2)
        self.assertEqual(len(self.clean), 100)
        self.assertEqual(int(self.clean.duplicated().sum()), 0)

    def test_cleaned_case_ids_are_unique(self):
        self.assertEqual(self.clean["case_id"].nunique(), len(self.clean))

    def test_missing_categories_are_standardised(self):
        for col in ["department", "diagnosis_group", "case_status", "follow_up_required"]:
            self.assertFalse(self.clean[col].isna().any(), msg=col)
        self.assertIn("Unknown", set(self.clean["department"]))

    def test_missing_numeric_values_are_not_fabricated(self):
        self.assertGreater(self.clean["length_of_stay_days"].isna().sum(), 0)
        self.assertGreater(self.clean["claim_amount_inr"].isna().sum(), 0)

    def test_summary_totals_reconcile(self):
        status = pd.read_csv(OUTPUT / "status_summary.csv")
        departments = pd.read_csv(OUTPUT / "department_summary.csv")
        follow_up = pd.read_csv(OUTPUT / "follow_up_summary.csv")
        self.assertEqual(int(status["case_count"].sum()), len(self.clean))
        self.assertEqual(int(departments["case_count"].sum()), len(self.clean))
        self.assertEqual(int(follow_up["case_count"].sum()), len(self.clean))

    def test_expected_outputs_exist_and_are_nonempty(self):
        expected = [
            "cleaned_healthcare_operations.csv", "department_summary.csv",
            "status_summary.csv", "follow_up_summary.csv", "cases_by_status.png"
        ]
        for filename in expected:
            path = OUTPUT / filename
            self.assertTrue(path.is_file(), msg=filename)
            self.assertGreater(path.stat().st_size, 0, msg=filename)


if __name__ == "__main__":
    unittest.main()
