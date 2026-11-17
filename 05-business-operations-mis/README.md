# Project 05 – Business Operations MIS & Performance Dashboard

## Project overview
A self-directed Python MIS automation project using fictional operational task records. It demonstrates how to validate source data, prepare department and monthly summaries, monitor task status and SLA compliance, analyse open-task ageing, and export a multi-sheet Excel report.

**Data disclaimer:** Both CSV files are synthetic and created for portfolio practice. They are not actual company, employee, customer, or operational records. This project is not evidence of professional experience in the represented departments.

## Dataset
- `dataset/operations_tasks_synthetic.csv`: 120 task records across six departments, January–June 2026.
- `dataset/monthly_targets_synthetic.csv`: 36 department-month target records for the same period.

The task file is a small sample, while supplied monthly targets are substantially larger than the task sample. Therefore, target achievement is calculated as recorded completed sample tasks divided by the supplied target. It should be interpreted as a demonstration of the calculation, not as a representative business performance result.

## KPIs and analysis
- Tasks recorded, completed, open and overdue
- SLA compliance among completed tasks only
- Completed sample tasks versus supplied monthly targets
- Department-wise and month-wise operational summaries
- Open-task ageing as of **30 June 2026** (fixed historical snapshot)
- Task status distribution and monthly task-volume charts

Open tasks are defined as Pending, In Progress and Overdue. SLA compliance is calculated only for Completed tasks with a Yes/No SLA result. Ageing uses the fixed snapshot date to keep results reproducible; it is not a live ageing calculation.

## Run locally
From the repository root, install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the script:

```bash
python 05-business-operations-mis/scripts/build_operations_mis.py
```

The script reads the CSV files from the project's `dataset` folder and creates an `outputs` folder containing:
- A multi-sheet Excel workbook: `business_operations_mis.xlsx`
- CSV summaries for KPIs, departments, monthly MIS, trends, statuses and ageing
- A data validation report
- PNG charts for department completion, task status and monthly volume

## Tools
Python, pandas, matplotlib and openpyxl.

## Current project status
The source data and initial reporting script are committed. The generated outputs should be run and checked locally before being presented as verified deliverables. No claim is made here that the script or workbook has been independently executed or tested.
