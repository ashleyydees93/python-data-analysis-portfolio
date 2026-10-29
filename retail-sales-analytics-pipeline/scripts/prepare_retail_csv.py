#!/usr/bin/env python3
"""Convert the two-sheet UCI Online Retail II Excel workbook to a normalized CSV.

Source: Chen (2012), https://doi.org/10.24432/C5CG6D (CC BY 4.0).
Requires: openpyxl. No downloaded source data is stored in this repository.
"""
import argparse
import csv
import re
import shutil
import tempfile
import zipfile
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

OUTPUT_COLUMNS = [
    "invoice_no", "stock_code", "description", "quantity", "invoice_date",
    "unit_price", "customer_id", "country", "source_sheet", "source_row",
]
ALIASES = {
    "invoice_no": ("invoiceno", "invoice"),
    "stock_code": ("stockcode",),
    "description": ("description",),
    "quantity": ("quantity",),
    "invoice_date": ("invoicedate",),
    "unit_price": ("unitprice", "price"),
    "customer_id": ("customerid",),
    "country": ("country",),
}


def normalize_header(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def map_columns(header):
    locations = {normalize_header(name): i for i, name in enumerate(header)}
    result = {}
    for output, choices in ALIASES.items():
        matched = next((locations[c] for c in choices if c in locations), None)
        if matched is None:
            raise ValueError(f"Required column {output!r} is missing from {header!r}")
        result[output] = matched
    return result


def cell_to_text(value):
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def convert_workbook(input_xlsx, output_csv):
    """Stream all nonblank data rows; return count (does not modify source)."""
    input_xlsx, output_csv = Path(input_xlsx), Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    workbook = load_workbook(input_xlsx, read_only=True, data_only=True)
    count = 0
    try:
        with output_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for sheet in workbook.worksheets:
                iterator = sheet.iter_rows(values_only=True)
                header = next(iterator, None)
                if header is None:
                    continue
                indexes = map_columns(header)
                for excel_row_number, values in enumerate(iterator, start=2):
                    if not any(v is not None and str(v).strip() for v in values):
                        continue
                    record = {
                        key: cell_to_text(values[idx] if idx < len(values) else None)
                        for key, idx in indexes.items()
                    }
                    record["source_sheet"] = sheet.title
                    record["source_row"] = excel_row_number
                    writer.writerow(record)
                    count += 1
    finally:
        workbook.close()
    return count


def find_xlsx_from_zip(path, destination):
    with zipfile.ZipFile(path) as archive:
        candidates = [n for n in archive.namelist() if n.lower().endswith(".xlsx")]
        if len(candidates) != 1:
            raise ValueError(f"Expected one .xlsx in archive; found {candidates}")
        output = Path(destination) / "online_retail_II.xlsx"
        with archive.open(candidates[0]) as source, output.open("wb") as target:
            shutil.copyfileobj(source, target)
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                        help="Original UCI .xlsx workbook or downloaded .zip")
    parser.add_argument("--output", type=Path,
                        default=Path("data/raw/online_retail_ii.csv"))
    args = parser.parse_args()
    if not args.input.exists():
        parser.error(f"Input file does not exist: {args.input}")
    if args.input.suffix.lower() == ".zip":
        with tempfile.TemporaryDirectory() as temp:
            workbook = find_xlsx_from_zip(args.input, temp)
            count = convert_workbook(workbook, args.output)
    elif args.input.suffix.lower() == ".xlsx":
        count = convert_workbook(args.input, args.output)
    else:
        parser.error("Input must be .xlsx or .zip")
    print(f"Converted {count:,} data rows to {args.output}")
    print("Upload the CSV to your Databricks source_data volume. Do NOT commit raw data.")


if __name__ == "__main__":
    main()
