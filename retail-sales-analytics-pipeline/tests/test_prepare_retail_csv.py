"""Offline tests using a tiny, deliberately synthetic workbook."""
import csv
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from scripts.prepare_retail_csv import (
    convert_workbook, map_columns, normalize_header, cell_to_text,
)


class TestUciConverter(unittest.TestCase):
    def test_header_variants(self):
        old = ["Invoice", "StockCode", "Description", "Quantity",
               "InvoiceDate", "Price", "Customer ID", "Country"]
        new = ["InvoiceNo", "StockCode", "Description", "Quantity",
               "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
        self.assertEqual(map_columns(old)["invoice_no"], 0)
        self.assertEqual(map_columns(new)["unit_price"], 5)
        self.assertEqual(normalize_header("Customer ID"), "customerid")
        self.assertEqual(cell_to_text(123.0), "123")

    def test_convert_two_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            source, output = directory / "test.xlsx", directory / "result.csv"
            wb = Workbook()
            a = wb.active
            a.title = "Year 2009-2010"
            a.append(["Invoice", "StockCode", "Description", "Quantity",
                      "InvoiceDate", "Price", "Customer ID", "Country"])
            a.append(["100001", "ABC", "Widget", 2, datetime(2010, 1, 2, 9, 30),
                      3.25, 42, "United Kingdom"])
            b = wb.create_sheet("Year 2010-2011")
            b.append(["InvoiceNo", "StockCode", "Description", "Quantity",
                      "InvoiceDate", "UnitPrice", "CustomerID", "Country"])
            b.append(["C200001", "XYZ", "Returned", -1, datetime(2011, 2, 3, 10),
                      9.99, None, "France"])
            wb.save(source)
            wb.close()

            count = convert_workbook(source, output)
            self.assertEqual(count, 2)
            with output.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["invoice_no"], "100001")
            self.assertEqual(rows[0]["customer_id"], "42")
            self.assertEqual(rows[0]["unit_price"], "3.25")
            self.assertEqual(rows[0]["source_sheet"], "Year 2009-2010")
            self.assertEqual(rows[0]["source_row"], "2")
            self.assertEqual(rows[1]["invoice_no"], "C200001")
            self.assertEqual(rows[1]["quantity"], "-1")
            self.assertEqual(rows[1]["customer_id"], "")
            self.assertEqual(rows[1]["source_sheet"], "Year 2010-2011")


if __name__ == "__main__":
    unittest.main()
