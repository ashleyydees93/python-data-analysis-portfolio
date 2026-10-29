# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Clean, classify, and audit transaction lines
# MAGIC Keep cancellations, zero-price rows, and possible duplicates visible in Silver.
# MAGIC Define Gold explicitly as positive non-cancelled invoice lines, **not net revenue**.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "dsc592ayd"
SCHEMA = "retail_portfolio"
DB = f"{CATALOG}.{SCHEMA}"

bronze = spark.table(f"{DB}.retail_bronze")

def nonblank(name):
    value = F.trim(F.col(name))
    return F.when((value == "") | value.isNull(), F.lit(None)).otherwise(value)

silver = (
    bronze
    .select(
        nonblank("invoice_no").alias("invoice_no"),
        nonblank("stock_code").alias("stock_code"),
        nonblank("description").alias("description"),
        nonblank("quantity").alias("quantity_raw"),
        nonblank("invoice_date").alias("invoice_date_raw"),
        nonblank("unit_price").alias("unit_price_raw"),
        nonblank("customer_id").alias("customer_id"),
        nonblank("country").alias("country"),
        F.col("source_sheet"),
        F.col("source_row").cast("long").alias("source_row"),
    )
    .withColumn("quantity", F.expr("try_cast(quantity_raw AS BIGINT)"))
    .withColumn("unit_price", F.expr("try_cast(unit_price_raw AS DECIMAL(18,4))"))
    .withColumn("invoice_date", F.try_to_timestamp(F.col("invoice_date_raw"), F.lit("yyyy-MM-dd HH:mm:ss")))
    .withColumn(
        "is_cancellation",
        F.coalesce(F.upper(F.col("invoice_no")).startswith("C"), F.lit(False))
        | F.coalesce(F.col("quantity") < 0, F.lit(False)),
    )
    .withColumn(
        "is_valid_sale",
        F.col("invoice_no").isNotNull()
        & F.col("stock_code").isNotNull()
        & F.col("invoice_date").isNotNull()
        & (F.col("quantity") > 0)
        & (F.col("unit_price") > 0)
        & (~F.col("is_cancellation")),
    )
    .withColumn(
        "positive_line_value_gbp",
        F.when(
            F.col("is_valid_sale"),
            F.col("quantity") * F.col("unit_price"),
        ).otherwise(F.lit(0).cast("decimal(24,4)")),
    )
    .withColumn("sale_date", F.to_date("invoice_date"))
)

silver.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_silver")

# COMMAND ----------

# Auditing is separate from filtering. These can overlap (e.g. negative qty + C invoice).
quality = silver.agg(
    F.count("*").alias("source_lines"),
    F.sum(F.when(F.col("customer_id").isNull(), 1).otherwise(0)).alias("missing_customer_id"),
    F.sum(F.when(F.col("invoice_date").isNull(), 1).otherwise(0)).alias("invalid_date"),
    F.sum(F.when(F.col("quantity").isNull(), 1).otherwise(0)).alias("invalid_quantity"),
    F.sum(F.when(F.col("unit_price").isNull(), 1).otherwise(0)).alias("invalid_price"),
    F.sum(F.when(F.col("unit_price") <= 0, 1).otherwise(0)).alias("nonpositive_price"),
    F.sum(F.when(F.col("is_cancellation"), 1).otherwise(0)).alias("cancellation_lines"),
    F.sum(F.when(F.col("is_valid_sale"), 1).otherwise(0)).alias("eligible_positive_lines"),
)
quality.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_quality_summary")
display(quality)

# Potential exact duplicates: informational only.
# Do not drop these without deciding whether separate same-item invoice lines are legitimate.
business_fields = [
    "invoice_no", "stock_code", "description", "quantity",
    "invoice_date", "unit_price", "customer_id", "country",
]
duplicate_groups = (
    silver.groupBy(*business_fields)
    .count()
    .filter(F.col("count") > 1)
)
duplicate_excess = duplicate_groups.agg(
    F.coalesce(F.sum(F.col("count") - 1), F.lit(0)).alias("possible_extra_lines")
).first()["possible_extra_lines"]
print("Potential repeated invoice lines above the first instance:", duplicate_excess)

# COMMAND ----------

gold = silver.filter(F.col("is_valid_sale"))
gold.write.format("delta").mode("overwrite").option(
    "overwriteSchema", "true"
).saveAsTable(f"{DB}.retail_gold_sales")

bronze_count, silver_count, gold_count = (
    bronze.count(), silver.count(), gold.count()
)
print("Bronze:", bronze_count, "Silver:", silver_count, "Gold:", gold_count)
assert bronze_count == silver_count, "Bronze/Silver row counts must match"
assert gold_count <= silver_count, "Gold cannot exceed Silver row count"
assert gold.filter((F.col("quantity") <= 0) | (F.col("unit_price") <= 0)).count() == 0
display(gold.limit(10))

# These are descriptive positive invoice-line values; NOT profit/net booked revenue.
