# Databricks notebook source
# MAGIC %md
# MAGIC # Retail Sales Analysis — SQL and PySpark
# MAGIC This is a beginner-friendly project based on the same code used in DSC 592.
# MAGIC We will load data, clean it, calculate sales, and compare PySpark with SQL.
# MAGIC Data: UCI Online Retail (2010–2011). Prices are in British pounds (£).

# COMMAND ----------

# 1. Load the CSV data into Databricks.
from pyspark.sql import functions as F
from pyspark.sql import Window

# Change this path to where YOU uploaded online_retail.csv.
file_path = "/Volumes/dsc592ayd/retail_portfolio/source_data/online_retail.csv"

df = spark.read.csv(file_path, header=True, inferSchema=True)

print("Original rows:", df.count())
display(df.limit(5))
df.printSchema()

# COMMAND ----------

# 2. Keep positive sales (no cancellations, negative quantities, or zero prices).
# The raw DataFrame is still available as df.
sales = (df
         .filter(F.col("InvoiceNo").isNotNull())
         .filter(~F.col("InvoiceNo").cast("string").startswith("C"))
         .filter(F.col("Quantity") > 0)
         .filter(F.col("UnitPrice") > 0)
         .withColumn("revenue", F.col("Quantity") * F.col("UnitPrice"))
         .withColumn("date", F.to_date("InvoiceDate"))
         .filter(F.col("date").isNotNull()))

print("Rows after cleaning:", sales.count())
display(sales.limit(5))

# COMMAND ----------

# 3. Daily sales: same groupBy, sum, and orderBy methods used in class.
daily = (sales.groupBy("date")
         .agg(F.sum("revenue").alias("total_revenue"))
         .orderBy("date"))

display(daily)

# COMMAND ----------

# 4. Find the five days with the highest sales.
top5 = (daily
        .orderBy(F.desc("total_revenue"))
        .limit(5))

display(top5)

# COMMAND ----------

# 5. The ten products with the highest positive sales value.
products = (sales.groupBy("StockCode", "Description")
            .agg(F.sum("revenue").alias("total_revenue"))
            .orderBy(F.desc("total_revenue"))
            .limit(10))

display(products)

# COMMAND ----------

# 6. Find the top three products in each country with ROW_NUMBER().
# This is the same Window concept as DSC 592 Lab 2C.
country_products = (sales.groupBy("Country", "StockCode", "Description")
                    .agg(F.sum("revenue").alias("total_revenue")))

w = (Window.partitionBy("Country")
     .orderBy(F.desc("total_revenue")))

top3 = (country_products
        .withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") <= 3)
        .orderBy("Country", "rn"))

display(top3)

# COMMAND ----------

# 7. Create a temporary SQL view so the SQL cells below can use our clean data.
# The view lasts only for this Spark session.
sales.createOrReplaceTempView("retail_sales")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 8. How much positive sales value came from each country?
# MAGIC SELECT Country,
# MAGIC        ROUND(SUM(revenue), 2) AS total_revenue
# MAGIC FROM retail_sales
# MAGIC GROUP BY Country
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 9. Which months had the highest positive sales value?
# MAGIC SELECT DATE_FORMAT(date, 'yyyy-MM') AS month,
# MAGIC        ROUND(SUM(revenue), 2) AS total_revenue
# MAGIC FROM retail_sales
# MAGIC GROUP BY DATE_FORMAT(date, 'yyyy-MM')
# MAGIC ORDER BY month;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 10. Basic summary numbers.
# MAGIC SELECT COUNT(*) AS sales_lines,
# MAGIC        COUNT(DISTINCT InvoiceNo) AS orders,
# MAGIC        COUNT(DISTINCT CustomerID) AS known_customers,
# MAGIC        ROUND(SUM(revenue), 2) AS total_positive_sales_gbp
# MAGIC FROM retail_sales;

# COMMAND ----------

# MAGIC %md
# MAGIC ## What I learned
# MAGIC - Reading a CSV into a Spark DataFrame.
# MAGIC - Filtering data and creating a new revenue column.
# MAGIC - Using groupBy, sum, orderBy, and limit.
# MAGIC - Ranking products with ROW_NUMBER and Window.
# MAGIC - Using SQL SELECT, GROUP BY, SUM, COUNT, and ORDER BY.
# MAGIC
# MAGIC **Important:** This project calculates positive invoice-line sales value, not net revenue or profit.
# MAGIC Returns/cancellations are excluded, and missing customer IDs are not treated as known customers.
