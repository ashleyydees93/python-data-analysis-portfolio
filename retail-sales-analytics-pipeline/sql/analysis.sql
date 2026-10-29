-- Retail Sales Analytics Pipeline — Databricks SQL
-- UCI Online Retail II: historical transactions 2009–2011.
-- Replace dsc592ayd.retail_portfolio if your catalog or schema differs.
-- "positive_invoice_line_value_gbp" excludes cancellations/returns and
-- MUST NOT be described as audited net sales, margin, or profit.

-- 1. Dataset quality overview (checks may overlap).
SELECT *
FROM dsc592ayd.retail_portfolio.retail_quality_summary;

-- 2. Executive KPIs.
SELECT eligible_invoice_lines,
       distinct_invoices,
       distinct_known_customers,
       ROUND(positive_invoice_line_value_gbp, 2) AS positive_invoice_line_value_gbp
FROM dsc592ayd.retail_portfolio.retail_kpis;

-- 3. Monthly positive invoice-line value.
SELECT DATE_FORMAT(sales_month, 'yyyy-MM') AS sales_month,
       ROUND(positive_invoice_line_value_gbp, 2) AS positive_invoice_line_value_gbp,
       distinct_invoices,
       invoice_lines
FROM dsc592ayd.retail_portfolio.retail_monthly_sales
ORDER BY sales_month;

-- 4. Top ten product codes; no category column exists in this source.
SELECT sales_rank, stock_code, sample_description, units_sold,
       ROUND(positive_invoice_line_value_gbp, 2) AS positive_invoice_line_value_gbp
FROM dsc592ayd.retail_portfolio.retail_product_sales
WHERE sales_rank <= 10
ORDER BY sales_rank;

-- 5. Country contribution, with percentage of all eligible positive-line value.
WITH total_value AS (
  SELECT positive_invoice_line_value_gbp AS total_gbp
  FROM dsc592ayd.retail_portfolio.retail_kpis
)
SELECT c.country_name,
       ROUND(c.positive_invoice_line_value_gbp, 2) AS positive_invoice_line_value_gbp,
       c.distinct_invoices,
       ROUND(100.0 * c.positive_invoice_line_value_gbp / NULLIF(t.total_gbp, 0), 2)
         AS share_pct
FROM dsc592ayd.retail_portfolio.retail_country_sales c
CROSS JOIN total_value t
ORDER BY c.positive_invoice_line_value_gbp DESC;

-- 6. Missing-ID prevalence among eligible positive lines.
SELECT
  COUNT(*) AS eligible_lines,
  SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS unknown_customer_lines,
  ROUND(
    100.0 * SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
    2
  ) AS unknown_customer_line_pct
FROM dsc592ayd.retail_portfolio.retail_gold_sales;

-- 7. Cancellations / negative quantities remain in Silver for investigation.
SELECT is_cancellation, COUNT(*) AS lines,
       SUM(CASE WHEN quantity < 0 THEN 1 ELSE 0 END) AS negative_quantity_lines
FROM dsc592ayd.retail_portfolio.retail_silver
GROUP BY is_cancellation
ORDER BY is_cancellation DESC;
