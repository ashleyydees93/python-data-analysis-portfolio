# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Ingest and profile source transactions
# MAGIC Original data: UCI Online Retail II (CC BY 4.0).
# MAGIC Run the local converter first; then upload the resulting CSV to a managed volume.
# MAGIC This notebook writes ONLY to your dedicated portfolio schema, not class retail tables.

# COMMAND ----------

from pyspark.sql import functions as F, types as T

# Modify these settings for your own Databricks account.
CATALOG = "dsc592ayd"
SCHEMA = "retail_portfolio"
VOLUME = "source_data"
TABLE_PREFIX = f"{CATALOG}.{SCHEMA}"
RAW_CSV = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/online_retail_ii.csv"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {TABLE_PREFIX}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {TABLE_PREFIX}.{VOLUME}")
print(f"Upload your prepared file to: {RAW_CSV}")

# COMMAND ----------

# Run this cell only AFTER uploading the generated CSV via Catalog Explorer.
columns = [
    "invoice_no", "stock_code", "description", "quantity", "invoice_date",
    "unit_price", "customer_id", "country", "source_sheet", "source_row",
]
csv_schema = T.StructType([T.StructField(c, T.StringType(), True) for c in columns])

try:
    file_listing = dbutils.fs.ls(f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/")
except Exception as exc:
    raise RuntimeError("Cannot access your volume. Check catalog/schema/permissions.") from exc

if "online_retail_ii.csv" not in [x.name for x in file_listing]:
    raise FileNotFoundError(
        f"Missing {RAW_CSV}. Run scripts/prepare_retail_csv.py locally "
        "and upload the resulting CSV with Catalog Explorer first."
    )

bronze = (
    spark.read.format("csv")
    .option("header", "true")
    .option("mode", "FAILFAST")
    .option("multiLine", "true")
    .schema(csv_schema)
    .load(RAW_CSV)
)

# Bronze contains original strings and source provenance.
bronze.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{TABLE_PREFIX}.retail_bronze")

print("Bronze rows:", bronze.count())
bronze.printSchema()
display(bronze.limit(10))

# COMMAND ----------

# Source completeness and provenance, without making assumptions about quality.
display(
    bronze.groupBy("source_sheet")
    .agg(F.count("*").alias("invoice_lines"))
    .orderBy("source_sheet")
)

# A published dataset describes approximately 1,067,371 invoice lines.
# Your actual workbook/converter count is the reproducibility check.
