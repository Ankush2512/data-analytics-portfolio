# Project 03: Python Data Cleaning & Exploratory Data Analysis

## Objective
Use Python to inspect, clean, validate, and explore a fictional healthcare operations dataset. The project demonstrates a repeatable data-preparation workflow before reporting or dashboard development.

> All records are synthetic and are not real patient, hospital, or employer data.

## Dataset
- File: `dataset/raw_healthcare_operations.csv`
- 102 rows including two intentionally duplicated records.
- Some department, length-of-stay, and claim-amount values are intentionally missing.
- Fields include case ID, admission date, department, diagnosis group, length of stay, claim amount, case status, and follow-up flag.

## Cleaning workflow
1. Inspect shape, data types, missing values, and duplicate rows.
2. Remove exact duplicate records.
3. Convert dates and numeric columns to suitable types.
4. Standardise text fields and fill missing categories with `Unknown`.
5. Keep missing numeric values explicit and create validation flags; do not invent clinical or financial values.
6. Check for invalid negative length-of-stay or claim amounts.
7. Export the cleaned data and summary tables.

## EDA questions
- Which departments have the most cases?
- What is the distribution of case statuses?
- What is the average length of stay?
- How do claim amounts vary by department?
- How many records require follow-up?

## Run
```bash
pip install -r requirements.txt
python 03-python-eda/scripts/clean_and_explore.py
```

Outputs are written to `03-python-eda/output/`. The accompanying notebook provides an interactive learning version of the same workflow.

## Skills demonstrated
Python, Pandas, NumPy, data profiling, missing-value analysis, duplicate handling, validation, aggregation, and Matplotlib.
