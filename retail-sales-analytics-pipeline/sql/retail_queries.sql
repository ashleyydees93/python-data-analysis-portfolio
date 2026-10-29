-- Simple SQL exercises for the Retail Sales Analysis project.
-- Run these in %sql cells in the SAME Databricks notebook
-- AFTER the Python cell creates the temporary view retail_sales.
-- All money values are in GBP (£).
-- "revenue" here means positive sales-line value, not profit or net revenue.

-- Question 1: Which countries have the most positive sales value?
SELECT Country,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM retail_sales
GROUP BY Country
ORDER BY total_revenue DESC;

-- Question 2: How much positive sales value was there each month?
SELECT DATE_FORMAT(date, 'yyyy-MM') AS month,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM retail_sales
GROUP BY DATE_FORMAT(date, 'yyyy-MM')
ORDER BY month;

-- Question 3: Which products generated the highest positive sales value?
SELECT StockCode, Description,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM retail_sales
GROUP BY StockCode, Description
ORDER BY total_revenue DESC
LIMIT 10;

-- Question 4: Count sales lines, orders, and known customers.
SELECT COUNT(*) AS sales_lines,
       COUNT(DISTINCT InvoiceNo) AS orders,
       COUNT(DISTINCT CustomerID) AS known_customers,
       ROUND(SUM(revenue), 2) AS total_positive_sales_gbp
FROM retail_sales;
