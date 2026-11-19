# Healthcare MIS Reporting & Performance Analysis

## Project overview
A practical MIS analytics project using a **fully synthetic healthcare case dataset**. It demonstrates how an MIS Executive can monitor case volumes, claim values, processing status, turnaround time, pending workload, and department-wise performance.

> **Data privacy:** Every row is fictional and generated for demonstration. No real patient names, identifiers, medical records, or hospital data are included.

## Business questions
1. How many cases were received, approved, pending, rejected, or awaiting query resolution?
2. What is the total submitted claim value and approved claim value?
3. Which departments handle the highest case volumes?
4. How does case volume change month by month?
5. What is the average processing time for closed cases?
6. How many pending cases fall into ageing buckets?

## Dataset
File: `dataset/healthcare_cases_synthetic.csv`

| Field | Description |
|---|---|
| case_id | Fictional case reference (SYN prefix) |
| admission_date | Date the case entered the workflow |
| department | Treating department category |
| scheme | Fictional reporting category / scheme label |
| case_status | Approved, Pending, Rejected, or Query Raised |
| claim_amount_inr | Claim value in INR |
| days_in_process | Days in workflow; for closed cases this is turnaround time, for pending/query cases it is current ageing |
| query_raised | Yes/No query flag |

## How to run
Requires Python 3.10+.

```bash
pip install -r requirements.txt
python scripts/build_healthcare_mis.py
```

The script creates:
- `output/healthcare_mis_report.xlsx` — multi-sheet Excel MIS workbook
- `output/cleaned_healthcare_cases.csv` — validated dataset
- `output/department_case_volume.png` — department case-volume chart
- `output/monthly_case_trend.png` — monthly case trend chart

## Workbook tabs
- **KPI Summary:** total cases, status counts, total claim value, approved claim value, average closed-case turnaround, pending ageing.
- **Department Summary:** case counts, approved counts, pending counts, claim values, and approval rate by department.
- **Monthly Trend:** monthly received volume, approved cases, and claim value.
- **Case Data:** cleaned synthetic records.

## Key metric definitions
- **Approval rate:** approved cases divided by all cases received.
- **Average closed-case TAT:** average `days_in_process` for Approved and Rejected cases. Pending and Query Raised cases are excluded.
- **Pending ageing:** days in process for Pending and Query Raised cases, grouped into 0–7, 8–15, 16–30, and 31+ day buckets.
- **Approved claim value:** sum of claim values for Approved cases only.

## Skills demonstrated
Advanced Excel / MIS concepts, KPI definition, data validation, data cleaning with Python and Pandas, aggregation, reporting, and basic data visualization.

**Note:** This is a self-directed practice project. It is not presented as an official report or as work performed for an employer.


## Interactive dashboard
Open the [Healthcare MIS Performance Dashboard](dashboard/index.html) for interactive KPI cards, department and scheme filters, case-status distribution, monthly case volume, department-wise cases, and open-case ageing. The dashboard loads the synthetic CSV directly from this repository and uses Chart.js for charts. It requires an internet connection to load its libraries and dataset. To publish it as a live webpage, enable GitHub Pages for this repository and use the `main` branch with the `/ (root)` folder; then open `/01-healthcare-mis/dashboard/` on the published site.
