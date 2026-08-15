"""
Validation rules for the student records CSV.

Every check returns a list of "issues". An issue is just a dict:
    {"row": <line number in the csv file>, "column": ..., "issue": ..., "value": ...}

Line numbers start at 2 because line 1 of the file is the header.
"""
import re
from datetime import datetime

import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")

# column name -> expected type
SCHEMA = {
    "student_id": "int",
    "name": "str",
    "email": "email",
    "department": "str",
    "semester": "int",
    "cgpa": "float",
    "admission_date": "date",
    "fees_paid": "float",
}

# allowed (min, max) for some numeric columns
RANGES = {
    "semester": (1, 8),
    "cgpa": (0, 10),
    "fees_paid": (0, None),   # None = no upper limit
}


def _issue(index, column, issue, value):
    return {"row": int(index) + 2, "column": column, "issue": issue, "value": value}


def find_missing(df):
    """Empty cells in any column."""
    issues = []
    for col in df.columns:
        blanks = df[df[col].str.strip() == ""]
        for idx in blanks.index:
            issues.append(_issue(idx, col, "missing value", ""))
    return issues


def find_duplicates(df):
    """Fully duplicated rows, and student_ids that are used more than once."""
    issues = []
    full_dupes = df.duplicated(keep="first")
    for idx in df[full_dupes].index:
        issues.append(_issue(idx, "*", "duplicate row", "entire row"))

    # same id but different data -> still suspicious
    only_id = df[~full_dupes]
    id_dupes = only_id.duplicated(subset=["student_id"], keep="first")
    for idx in only_id[id_dupes].index:
        issues.append(_issue(idx, "student_id", "duplicate student_id", df.loc[idx, "student_id"]))
    return issues


def _is_int(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


def _is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def _is_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def find_type_errors(df, schema=SCHEMA):
    """Values that don't match the type the schema expects."""
    checks = {
        "int": _is_int,
        "float": _is_float,
        "date": _is_date,
        "email": lambda v: bool(EMAIL_RE.match(v)),
        "str": lambda v: True,
    }
    issues = []
    for col, kind in schema.items():
        if col not in df.columns:
            continue
        for idx, value in df[col].items():
            value = value.strip()
            if value == "":
                continue  # already reported as missing
            if not checks[kind](value):
                issues.append(_issue(idx, col, f"expected {kind}", value))
    return issues


def find_range_errors(df, ranges=RANGES):
    """Numbers that are valid but outside the allowed range (e.g. cgpa = 14)."""
    issues = []
    for col, (low, high) in ranges.items():
        if col not in df.columns:
            continue
        for idx, value in df[col].items():
            if not _is_float(value.strip() or "x"):
                continue  # not a number, type check handles it
            num = float(value)
            if low is not None and num < low:
                issues.append(_issue(idx, col, f"below minimum ({low})", value))
            elif high is not None and num > high:
                issues.append(_issue(idx, col, f"above maximum ({high})", value))
    return issues


def find_outliers(df, column="fees_paid", k=3.0):
    """
    Very large / very small values using the IQR rule:
    anything beyond Q3 + k*IQR (or below Q1 - k*IQR) is flagged.
    """
    numbers = pd.to_numeric(df[column], errors="coerce")
    valid = numbers.dropna()
    if len(valid) < 4:
        return []
    q1, q3 = valid.quantile(0.25), valid.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    issues = []
    for idx, num in numbers.items():
        if pd.notna(num) and (num > high or num < low):
            issues.append(_issue(idx, column, "outlier (IQR rule)", df.loc[idx, column]))
    return issues


def run_all_checks(df):
    """Runs every check and returns one combined, sorted list of issues."""
    issues = []
    issues += find_missing(df)
    issues += find_duplicates(df)
    issues += find_type_errors(df)
    issues += find_range_errors(df)
    issues += find_outliers(df)
    return sorted(issues, key=lambda i: (i["row"], i["column"]))
