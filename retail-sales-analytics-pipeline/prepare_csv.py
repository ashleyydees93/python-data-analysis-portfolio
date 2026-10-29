# Step 1: Change the filename if your downloaded Excel file has a different name.
# Run this on your computer BEFORE opening Databricks.

import pandas as pd

df = pd.read_excel("Online Retail.xlsx")
print("Rows in original data:", len(df))
print(df.head())

df.to_csv("online_retail.csv", index=False)
print("Saved online_retail.csv")
