# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Build reusable reporting tables
# MAGIC KPI: **positive non-cancelled invoice-line value (GBP)**. This excludes returns
# MAGIC and cancellation lines, and is not a claim about net revenue or profit.
# MAGIC UCI Online Retail II does not include a product category column.

# COMMAND ----------

from pyspark.sql import Window, functions as F

CATALOG = "dsc592ayd"
SCHEMA = "retail_portfolio"
DB = f"{CATALOG}.{SCHEMA}"

sales = spark.table(f"{DB}.retail_gold_sales")

# One-row executive summary, using only identifiable customers in customer counts.
kpis = sales.agg(
    F.count("*").alias("eligible_invoice_lines"),
    F.countDistinct("invoice_no").alias("distinct_invoices"),
    F.countDistinct("customer_id").alias("distinct_known_customers"),
    F.sum("positive_line_value_gbp").cast("decimal(24,2)").alias(
        "positive_invoice_line_value_gbp"
    ),
)
kpis.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_kpis")
display(kpis)

# COMMAND ----------

monthly = (
    sales.withColumn("sales_month", F.date_trunc("month", "invoice_date"))
    .groupBy("sales_month")
    .agg(
        F.sum("positive_line_value_gbp").cast("decimal(24,2)").alias(
            "positive_invoice_line_value_gbp"
        ),
        F.countDistinct("invoice_no").alias("distinct_invoices"),
        F.count("*").alias("invoice_lines"),
    )
    .orderBy("sales_month")
)
monthly.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_monthly_sales")
display(monthly)

# COMMAND ----------

# One stock code can have multiple descriptions. MAX is a display label, not a canonical mapping.
products = (
    sales.groupBy("stock_code")
    .agg(
        F.max("description").alias("sample_description"),
        F.sum("quantity").alias("units_sold"),
        F.sum("positive_line_value_gbp").cast("decimal(24,2)").alias(
            "positive_invoice_line_value_gbp"
        ),
    )
)
rank_window = Window.orderBy(
    F.desc("positive_invoice_line_value_gbp"), F.asc("stock_code")
)
products = (
    products.withColumn("sales_rank", F.row_number().over(rank_window))
    .orderBy("sales_rank")
)
products.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_product_sales")
display(products.limit(20))

# COMMAND ----------

countries = (
    sales.withColumn("country_name", F.coalesce("country", F.lit("Unknown")))
    .groupBy("country_name")
    .agg(
        F.sum("positive_line_value_gbp").cast("decimal(24,2)").alias(
            "positive_invoice_line_value_gbp"
        ),
        F.countDistinct("invoice_no").alias("distinct_invoices"),
    )
    .orderBy(F.desc("positive_invoice_line_value_gbp"))
)
countries.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_country_sales")
display(countries.limit(20))

# COMMAND ----------

# Reconciliation: sum of monthly values should match the one-row positive-line KPI.
from decimal import Decimal
kpi_total = kpis.first()["positive_invoice_line_value_gbp"]
monthly_total = monthly.agg(
    F.sum("positive_invoice_line_value_gbp").alias("total")
).first()["total"]
print("KPI positive invoice-line value (GBP):", kpi_total)
print("Sum of monthly positive invoice-line value (GBP):", monthly_total)
assert kpi_total == monthly_total, "Monthly values should reconcile to KPI total"
print("Reconciliation passed. Reporting Delta tables are ready.")
