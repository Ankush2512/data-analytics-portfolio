# Project 02: Sales Funnel & Conversion Analysis

## Objective
Analyse a fictional sales pipeline to understand lead volume, stage movement, order bookings, conversion, lost opportunities, and channel/region performance.

> **Practice project only:** this is a self-directed portfolio exercise using synthetic data. It does not represent the user's employment history or actual sales experience.

## Dataset
- File: `dataset/sales_leads_synthetic.csv`
- 120 fictional lead records.
- No real customer or company information.
- Fields: lead ID, lead date, channel, region, lead source, current stage, booked order value, and lost reason.

## Business questions
1. How many leads entered the funnel?
2. How many orders were booked, and what is the lead-to-order conversion rate?
3. Which channels and regions contribute the most booked orders?
4. How many leads were lost, and what are the common loss reasons?
5. What is the total booked order value?

## KPI definitions
- **Lead-to-order conversion (%)** = Order Booked leads / Total leads × 100.
- **Lost rate (%)** = Lost leads / Total leads × 100.
- **Booked order value** = Sum of order values for Order Booked leads only.
- **Stage distribution** = Count of leads at each current stage.

These are snapshot funnel metrics. They do not measure true stage-to-stage conversion because the dataset records each lead's current stage, not a complete event history.

## Run the analysis
From the repository root:

```bash
pip install -r requirements.txt
python 02-sales-funnel/scripts/analyze_sales_funnel.py
```

The script prints an executive KPI summary and saves channel, region, and stage summaries plus a chart under `02-sales-funnel/output/`.

## Skills demonstrated
Pandas, data validation, grouping, KPI calculations, funnel analysis, business reporting, and charting.
