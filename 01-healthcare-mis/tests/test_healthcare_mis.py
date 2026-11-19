"""Automated checks for the Healthcare MIS reporting project."""
import importlib.util
from pathlib import Path
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_DIR / "scripts" / "build_healthcare_mis.py"
spec = importlib.util.spec_from_file_location("healthcare_mis", SCRIPT)
healthcare_mis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(healthcare_mis)


class HealthcareMISTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = healthcare_mis.load_and_validate(
            PROJECT_DIR / "dataset" / "healthcare_cases_synthetic.csv"
        )
        cls.kpis, cls.department, cls.monthly, cls.ageing = (
            healthcare_mis.build_summaries(cls.df)
        )

    def test_dataset_has_unique_case_ids_and_valid_statuses(self):
        self.assertTrue(self.df["case_id"].is_unique)
        self.assertGreater(len(self.df), 0)
        self.assertTrue(set(self.df["case_status"]).issubset(healthcare_mis.VALID_STATUSES))

    def test_numeric_fields_are_non_negative(self):
        self.assertTrue((self.df["claim_amount_inr"] >= 0).all())
        self.assertTrue((self.df["days_in_process"] >= 0).all())

    def test_department_and_monthly_totals_reconcile(self):
        total = self.df["case_id"].nunique()
        self.assertEqual(int(self.department["total_cases"].sum()), total)
        self.assertEqual(int(self.monthly["cases_received"].sum()), total)

    def test_status_counts_reconcile_to_total_cases(self):
        values = dict(zip(self.kpis["Metric"], self.kpis["Value"]))
        status_total = sum(values[k] for k in [
            "Approved Cases", "Pending Cases", "Rejected Cases", "Query Raised Cases"
        ])
        self.assertEqual(status_total, values["Total Cases"])

    def test_open_case_ageing_includes_pending_and_query_raised(self):
        expected = self.df["case_status"].isin(["Pending", "Query Raised"]).sum()
        self.assertEqual(int(self.ageing["open_cases"].sum()), int(expected))

    def test_approved_claim_value_matches_approved_records(self):
        values = dict(zip(self.kpis["Metric"], self.kpis["Value"]))
        expected = self.df.loc[
            self.df["case_status"].eq("Approved"), "claim_amount_inr"
        ].sum()
        self.assertAlmostEqual(values["Approved Claim Value (INR)"], expected)


if __name__ == "__main__":
    unittest.main()
