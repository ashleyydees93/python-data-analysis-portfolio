# Runbook: reproduce in Databricks

## 1. Obtain the data legally

Download **Online Retail II** from [UCI](https://archive.ics.uci.edu/dataset/502/online+retail+ii), and extract the file \`online_retail_II.xlsx\`. This is a two-sheet historical dataset (~1,067,371 lines). Its license is CC BY 4.0; cite Daqing Chen and the DOI in any reports.

Do **not** commit the workbook, generated CSV, personal credentials, or processed data to GitHub.

## 2. Convert both worksheets to one consistent CSV

Install \`openpyxl\` locally: \`python -m pip install -r requirements.txt\`.

Run from the **project folder**:

\`\`\`bash
python scripts/prepare_retail_csv.py --input /path/to/online_retail_II.xlsx --output data/raw/online_retail_ii.csv
python -m unittest discover -s tests -v
\`\`\`

The converter streams rows in read-only mode and prints the total number converted. It handles the column-header differences between the two worksheets.

## 3. Set up isolated Databricks storage

The sample notebooks default to your own catalog **dsc592ayd** and a new schema **retail_portfolio**, separate from your class's \`retail\` schema. Edit \`CATALOG\` and \`SCHEMA\` in notebook 01 if needed.

Run the first setup cell of notebook **01_ingest**. It tries to create the schema and managed volume **source_data**. Required privileges: CREATE SCHEMA in the chosen catalog and CREATE VOLUME in the schema.

If permission is denied, ask for a writable schema/volume and update the notebook settings. **Do not overwrite shared course tables.**

Upload \`data/raw/online_retail_ii.csv\` through Databricks **Catalog Explorer → catalog → schema → Volumes → source_data → Upload**, with the final path:

\`\`\`text
/Volumes/dsc592ayd/retail_portfolio/source_data/online_retail_ii.csv
\`\`\`

If your path differs, edit \`RAW_CSV\` in notebook 01.

## 4. Run the notebooks in order

1. **01_ingest.py** – load typed-as-text source fields into a Bronze Delta table; count and inspect rows.
2. **02_transform.py** – clean and flag data in Silver; create a valid positive-line Gold table; quality checks.
3. **03_analyze.py** – materialize KPIs, monthly, product, and country tables.
4. **04_dashboard.py** – query the materialized tables. Use Databricks visualization UI to display monthly trend, top products and countries. Save screenshots only after running the real dataset.

The \`.py\` notebook files contain \`# Databricks notebook source\` and \`# COMMAND ----------\`; they are recognized as notebooks in Databricks Git folders. SQL analytics are also in \`sql/analysis.sql\`.

## 5. Checks

- The source workbook is described by UCI as ~1,067,371 records; the converter/bronze row counts should agree with the actual file.
- Bronze and Silver row counts should match (no silent deletion).
- Gold count should be no larger than Silver count; all Gold rows should have positive quantity and price.
- The duplicate quality check is **diagnostic**, not a deletion command.
- Revenue in reports uses GBP and is labeled as **positive invoice-line value**, not audited net revenue.

## 6. Scope

This project is a reproducible code implementation prepared for Databricks. Databricks execution, resulting screenshots, and real dataset-specific KPIs must be verified in the connected workspace. It is not a deployed scheduled production pipeline.
