"""
CSV Quality Checker - command line entry point.

Example:
    python main.py data/students_sample.csv
    python main.py data/students_sample.csv --out output --clean
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

from checker.report import print_report, save_json, summarize
from checker.rules import SCHEMA, run_all_checks


def load_csv(path):
    # read everything as text so pandas doesn't silently convert (or hide) bad values
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def main():
    parser = argparse.ArgumentParser(description="Check a student-records CSV for data quality problems.")
    parser.add_argument("csv_file", help="path to the csv file")
    parser.add_argument("--out", default="output", help="folder for the report / cleaned file")
    parser.add_argument("--clean", action="store_true", help="also save a cleaned copy (bad rows removed)")
    parser.add_argument("--strict", action="store_true", help="exit with code 1 if any issue is found")
    args = parser.parse_args()

    path = Path(args.csv_file)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    df = load_csv(path)

    missing_cols = [c for c in SCHEMA if c not in df.columns]
    if missing_cols:
        print("Schema mismatch - these columns are missing:", ", ".join(missing_cols))
        sys.exit(2)

    issues = run_all_checks(df)
    summary = summarize(df, issues)
    print_report(summary, issues)

    report_path = save_json(summary, issues, args.out)
    print(f"Saved report -> {report_path}")

    if args.clean:
        bad_lines = {i["row"] for i in issues}
        keep = [idx for idx in df.index if (idx + 2) not in bad_lines]
        cleaned = df.loc[keep]
        clean_path = Path(args.out) / f"clean_{path.name}"
        cleaned.to_csv(clean_path, index=False)
        print(f"Saved cleaned csv ({len(cleaned)} rows) -> {clean_path}")

    if args.strict and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
