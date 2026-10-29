# Retail Sales Analytics Pipeline

**Databricks · PySpark · SQL · Delta Lake · Data Quality**

An end-to-end, reproducible retail analytics project based on **UCI Online Retail II**, a public two-year transaction dataset from a UK online retailer. The project demonstrates how to ingest raw invoice-line data, audit quality, build bronze/silver/gold Delta tables, and answer practical sales questions with PySpark and SQL.

> **Execution status:** The code and automated converter tests are provided, but the Databricks notebooks have **not** been executed in the author's workspace. The full data must be downloaded and uploaded to a Databricks volume before the dashboard tables can be generated. No fabricated analysis results are presented.

## The business questions

1. How does positive invoice-line value change month by month?
2. Which products and countries contribute most to that value?
3. How much of the source data is missing customer IDs, cancelled, nonpositive, or potentially duplicated?
4. How many orders and identifiable customers appear in the eligible sales lines?

## Pipeline

1. **Source:** Download the original UCI Excel workbook, then convert both worksheets to a consistently named CSV using `scripts/prepare_retail_csv.py`.
2. **Bronze:** Load all rows, preserving original raw fields and worksheet/row provenance.
3. **Silver:** Parse quantities, prices and dates; flag cancellations, valid sale lines, missing IDs, and quality issues. Preserve exceptions for auditing.
4. **Gold:** Keep qualifying positive sales lines for descriptive analysis without silently deleting possible duplicate invoice lines.
5. **Analytics:** Build Delta reporting tables for monthly sales, top products, country contributions, and overall KPIs; query them using SQL.

## Tech stack

Python 3.10+ · openpyxl · PySpark · Databricks · Delta Lake · Databricks SQL · Git/GitHub

## Project layout

```text
retail-sales-analytics-pipeline/
├── notebooks/
│   ├── 01_ingest.py
│   ├── 02_transform.py
│   ├── 03_analyze.py
│   └── 04_dashboard.py
├── scripts/
│   └── prepare_retail_csv.py
├── sql/
│   └── analysis.sql
├── tests/
│   └── test_prepare_retail_csv.py
├── docs/
│   ├── data_dictionary.md
│   └── runbook.md
├── requirements.txt
├── .gitignore
└── README.md
```

## Run it

See **[Step-by-step setup and verification](docs/runbook.md)**. In short:

1. Download the UCI **online_retail_II.xlsx** file (two sheets); do not commit the workbook to Git.
2. Run: `python scripts/prepare_retail_csv.py --input path/to/online_retail_II.xlsx --output data/raw/online_retail_ii.csv`.
3. In Databricks, choose your own catalog and create a dedicated schema/volume (the notebook defaults to `dsc592ayd.retail_portfolio`; change if needed).
4. Upload the generated CSV to the volume, then run notebooks **01**, **02**, **03**, and **04** in order.
5. Use `sql/analysis.sql` for additional queries.

The `.py` notebooks use the Databricks source-notebook format and are recognized as notebooks in Databricks Git folders.

## Definitions & design choices

- **Positive invoice-line value (£)** = quantity × unit price for a non-cancellation invoice with positive quantity and price, a valid timestamp, and nonempty invoice/product codes. This is **not net revenue or profit**: returns, cancellations, discount adjustments, postage, and stock costs require more complete accounting rules.
- Cancellation indicators are **invoice numbers starting with C** or a negative quantity. These records stay available in Silver for inspection, but are not included in the positive-line analysis.
- Missing CustomerID does **not** automatically make an otherwise valid sale invalid. Those rows remain in product/country totals but are excluded from identifiable-customer counts.
- Potentially repeated invoice lines are flagged in quality checks, **not automatically deleted**, since apparent duplicate lines might be legitimate.
- The dataset has **no product category** column. Products are ranked overall rather than inventing categories.
- Source prices are in **GBP**, and the dataset covers **2009–2011**. This is historical analysis, not current retail performance.

## Reproducibility and limitations

- All transformations and definitions are in version-controlled files; no data or notebook outputs are fabricated.
- Database creation and volume access require the appropriate Databricks permissions.
- This repo does **not** redistribute the source workbook or generated retail data. You must obtain it from UCI.
- Historic transaction data alone cannot establish profit, margins, inventory, marketing attribution, or causality.

## Source and attribution

Daqing Chen (2012), **Online Retail II** [Dataset], UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5CG6D. [Dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii). **Dataset license: CC BY 4.0.** This project's code is original project work; source data remains subject to its own license.
