import pandas as pd

from checker.rules import (
    find_duplicates,
    find_missing,
    find_outliers,
    find_range_errors,
    find_type_errors,
    run_all_checks,
)


def make_df(rows):
    cols = ["student_id", "name", "email", "department", "semester", "cgpa", "admission_date", "fees_paid"]
    return pd.DataFrame(rows, columns=cols, dtype=str)


GOOD = ["1", "Test User", "test@brcm.edu", "CSE", "3", "8.0", "2024-08-05", "60000"]


def test_clean_row_has_no_issues():
    assert run_all_checks(make_df([GOOD])) == []


def test_missing_value_is_found():
    row = GOOD.copy()
    row[1] = ""
    issues = find_missing(make_df([row]))
    assert len(issues) == 1
    assert issues[0]["column"] == "name"
    assert issues[0]["row"] == 2          # first data row is line 2 in the file


def test_full_duplicate_row():
    issues = find_duplicates(make_df([GOOD, GOOD]))
    assert len(issues) == 1
    assert issues[0]["issue"] == "duplicate row"


def test_same_id_different_data():
    other = GOOD.copy()
    other[1] = "Someone Else"
    issues = find_duplicates(make_df([GOOD, other]))
    assert [i["issue"] for i in issues] == ["duplicate student_id"]


def test_bad_email_and_date():
    row = GOOD.copy()
    row[2] = "not-an-email"
    row[6] = "2024-13-45"
    columns = {i["column"] for i in find_type_errors(make_df([row]))}
    assert columns == {"email", "admission_date"}


def test_text_in_number_column():
    row = GOOD.copy()
    row[4] = "five"
    issues = find_type_errors(make_df([row]))
    assert issues[0]["column"] == "semester"


def test_cgpa_out_of_range():
    row = GOOD.copy()
    row[5] = "14.5"
    issues = find_range_errors(make_df([row]))
    assert issues[0]["column"] == "cgpa"


def test_negative_fees():
    row = GOOD.copy()
    row[7] = "-100"
    issues = find_range_errors(make_df([row]))
    assert issues[0]["column"] == "fees_paid"


def test_outlier_is_flagged():
    rows = []
    for i in range(8):
        r = GOOD.copy()
        r[0] = str(i)
        r[7] = str(60000 + i * 100)
        rows.append(r)
    big = GOOD.copy()
    big[0] = "99"
    big[7] = "6000000"
    rows.append(big)
    issues = find_outliers(make_df(rows))
    assert len(issues) == 1
    assert issues[0]["value"] == "6000000"
