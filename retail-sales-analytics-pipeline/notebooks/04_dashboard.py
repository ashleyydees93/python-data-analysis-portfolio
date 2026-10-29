# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Retail analytics visualizations
# MAGIC Charts are generated only from the Delta reporting tables produced by notebook 03.
# MAGIC All amounts shown are historical **positive invoice-line value (GBP)**, not net profit.
# MAGIC Small aggregate tables are safe to convert to pandas for plotting.

# COMMAND ----------

from pyspark.sql import functions as F
import pandas as pd
import matplotlib.pyplot as plt

CATALOG = "dsc592ayd"
SCHEMA = "retail_portfolio"
DB = f"{CATALOG}.{SCHEMA}"

kpi = spark.table(f"{DB}.retail_kpis").first().asDict()
print("RETAIL ANALYTICS — HISTORICAL DATA")
print(f"Positive invoice-line value (£): {kpi['positive_invoice_line_value_gbp']:,.2f}")
print(f"Distinct invoices: {kpi['distinct_invoices']:,}")
print(f"Known customers: {kpi['distinct_known_customers']:,}")
print(f"Eligible invoice lines: {kpi['eligible_invoice_lines']:,}")

# COMMAND ----------

months = (
    spark.table(f"{DB}.retail_monthly_sales")
    .orderBy("sales_month")
    .select("sales_month", "positive_invoice_line_value_gbp")
    .toPandas()
)
months["sales_month"] = pd.to_datetime(months["sales_month"])
months["value"] = months["positive_invoice_line_value_gbp"].astype(float)

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(months["sales_month"], months["value"], marker="o")
ax.set_title("Monthly positive invoice-line value (GBP)")
ax.set_xlabel("Invoice month")
ax.set_ylabel("Value (£)")
ax.grid(alpha=0.25)
fig.autofmt_xdate()
plt.tight_layout()
plt.show()

# COMMAND ----------

top_products = (
    spark.table(f"{DB}.retail_product_sales")
    .orderBy("sales_rank")
    .limit(10)
    .select("stock_code", "positive_invoice_line_value_gbp")
    .toPandas()
)
top_products["value"] = top_products["positive_invoice_line_value_gbp"].astype(float)

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top_products["stock_code"].iloc[::-1], top_products["value"].iloc[::-1])
ax.set_title("Top 10 stock codes by positive invoice-line value")
ax.set_xlabel("Value (£)")
ax.set_ylabel("Stock code")
ax.grid(axis="x", alpha=0.25)
plt.tight_layout()
plt.show()

# COMMAND ----------

top_countries = (
    spark.table(f"{DB}.retail_country_sales")
    .orderBy(F.desc("positive_invoice_line_value_gbp"))
    .limit(10)
    .select("country_name", "positive_invoice_line_value_gbp")
    .toPandas()
)
top_countries["value"] = top_countries["positive_invoice_line_value_gbp"].astype(float)

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top_countries["country_name"].iloc[::-1], top_countries["value"].iloc[::-1])
ax.set_title("Top 10 countries by positive invoice-line value")
ax.set_xlabel("Value (£)")
ax.set_ylabel("Country")
ax.grid(axis="x", alpha=0.25)
plt.tight_layout()
plt.show()

# COMMAND ----------

# Save screenshots from executed charts in Databricks if you want them in a portfolio.
# Do not report chart findings before running the real source dataset.
