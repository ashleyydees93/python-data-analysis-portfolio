# Retail Sales Analysis with SQL and PySpark

**Python | SQL | PySpark | Databricks**

## Project overview

This is a beginner-friendly project where I practice the SQL and PySpark skills I learned in DSC 592: Data Engineering.

My goal is to take a retail dataset, clean the data, answer a few sales questions, and compare how the same work can be done with Python/PySpark and SQL.

This project is **practice**, not a production pipeline. The code is written using simple methods I can explain.

## Dataset

I use the **Online Retail** dataset from the UCI Machine Learning Repository. It has 541,909 original transaction rows from a UK online store, collected between December 2010 and December 2011.

- [Download Online Retail from UCI](https://archive.ics.uci.edu/dataset/352/online+retail)
- Original file: `Online Retail.xlsx`
- Source currency: **British pounds (£)**
- Credit: Daqing Chen, *Online Retail* (UCI Machine Learning Repository), [DOI: 10.24432/C5BW33](https://doi.org/10.24432/C5BW33)
- License: **CC BY 4.0**

I use the **one-year Online Retail dataset**, rather than the larger two-year Online Retail II workbook, to make the setup and code easier to follow.

## Questions I want to answer

1. How much positive sales value was there each day?
2. Which five days had the highest sales value?
3. Which products had the highest sales value?
4. Which three products performed best in each country?
5. Which countries and months had the highest sales values?

## What I used

| Skill | How I used it |
|---|---|
| pandas | Changed the Excel file into CSV |
| PySpark | Loaded data into Databricks and filtered rows |
| `withColumn` | Created a revenue column using quantity × unit price |
| `groupBy` and `sum` | Calculated totals |
| `orderBy` and `limit` | Found top-selling days and products |
| `ROW_NUMBER` and Window | Ranked products within each country |
| SQL | Used SELECT, WHERE, GROUP BY, SUM, COUNT, and ORDER BY |

## Project files

```text
retail-sales-analytics-pipeline/
├── prepare_csv.py
├── notebooks/
│   └── retail_sales_analysis.py
├── sql/
│   └── retail_queries.sql
├── requirements.txt
├── .gitignore
└── README.md
```

**Note:** The `.py` file in `notebooks/` uses Databricks notebook-format comments and opens as a notebook inside a Databricks Git folder.

## How to run it

**Step 1 — Download the data**

Download **Online Retail.xlsx** from the UCI link above. Keep the file on your computer; do not upload the original data to GitHub.

**Step 2 — Turn Excel into CSV**

In the project folder on your computer, install the two packages once:

```bash
python -m pip install -r requirements.txt
```

Put `Online Retail.xlsx` in the same folder as `prepare_csv.py`, then run:

```bash
python prepare_csv.py
```

This creates `online_retail.csv`.

**Step 3 — Upload the CSV to Databricks**

Upload `online_retail.csv` to a Unity Catalog volume that you can write to (for example, `/Volumes/dsc592ayd/retail_portfolio/source_data/`). A folder or volume may need to be created first.

**Step 4 — Open and run the notebook**

Open `notebooks/retail_sales_analysis.py` in a Databricks Git folder. Edit the `file_path` value so it matches your CSV location. Run the cells from top to bottom.

The SQL cells use the temporary view created by the Python code. Run them in the same notebook session. The separate `sql/retail_queries.sql` file is a reference copy of the queries.

## Important cleaning decisions

I keep only rows with a present invoice number, a non-cancellation invoice, a positive quantity and price, and a readable date. I do **not** remove a sale simply because the customer ID is missing.

For this project, **revenue** means the total value of positive invoice lines: `Quantity * UnitPrice`. It does **not** represent net revenue, profit, or money after returns. I don't automatically delete apparent duplicate invoice lines.

## Project status

**Code prepared; Databricks execution and results still need to be checked.**

I have not published made-up totals, graphs, or findings. Once I run the notebook against the UCI data, I can add the actual results and screenshots.

## What I am practicing

The purpose of this project is to show that I can work with a dataset, write understandable SQL and PySpark code, and explain what the results mean.
