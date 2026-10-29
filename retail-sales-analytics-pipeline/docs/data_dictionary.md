# Data dictionary and business logic

## Source

UCI Online Retail II, two Excel worksheets (2009–2010 and 2010–2011). The original headers differ slightly between worksheets (Invoice vs InvoiceNo, Price vs UnitPrice, Customer ID vs CustomerID). The preparation script normalizes both.

## Prepared CSV (bronze input)

| Field | Meaning |
|---|---|
| invoice_no | Source invoice number, kept as text; a C prefix denotes cancellation |
| stock_code | Item identifier, as text |
| description | Item description, may be missing |
| quantity | Invoice-line quantity, may be negative |
| invoice_date | Local timestamp in YYYY-MM-DD HH:MM:SS |
| unit_price | Price in British pounds (£) |
| customer_id | Nullable source customer ID, kept as text |
| country | Customer country (source text) |
| source_sheet | Worksheet identifier for provenance |
| source_row | Source worksheet row number for debugging |

## Processed columns

| Field | Definition |
|---|---|
| is_cancellation | Invoice starts with C (case-insensitive) or quantity is negative |
| is_valid_sale | Invoice/code present, date parsed, positive quantity and price, and not a cancellation |
| positive_line_value_gbp | Quantity × price for eligible positive invoice lines; 0 otherwise |
| invoice_date | Parsed timestamp |
| sale_date | Calendar date from invoice_date |

## Reporting grain and caveats

- **Bronze and Silver:** one row per source worksheet row.
- **Gold:** one row per eligible positive invoice line. Possible identical source lines are **not** automatically removed.
- **monthly_sales:** one month, gross positive invoice-line value in GBP, distinct invoice count, line count.
- **product_sales:** one product stock code, positive line value and sold units.
- **country_sales:** one country, positive line value and distinct invoice count.
- **retail_kpis:** one row; valid sale lines, distinct invoices, distinct *known* customers, total eligible positive invoice-line value.
- **Revenue caveat:** positive invoice-line value is *not* net booked revenue, cash flow, margin, or profit. It can contain non-product items such as postage. Refunds/returns are deliberately excluded from this positive-line metric and inspected separately.
- **No product-category source field:** do not infer or claim top 3 per category without adding an independently justified mapping.
