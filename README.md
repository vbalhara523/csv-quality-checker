# CSV Quality Checker

A small Python command-line tool that checks a CSV file for common data quality problems before the data is used for analysis. I built it while learning pandas and data cleaning, using a made-up college student records dataset as the test case.

It finds:

- **Missing values** – empty cells in any column
- **Duplicates** – identical rows, and repeated `student_id` values
- **Type / format errors** – text in number columns, invalid emails, impossible dates like `2025-13-40`
- **Out-of-range values** – e.g. `cgpa = 14.5`, `semester = 9`, negative fees
- **Outliers** – extreme values in `fees_paid`, using the IQR rule

After checking, it prints a report, saves a `report.json`, and can optionally write a cleaned copy of the CSV with the bad rows removed.

## Tech used

Python 3.10+, pandas, pytest, argparse

## Project structure

```
csv-quality-checker/
├── checker/
│   ├── rules.py          # all the validation checks
│   └── report.py         # summary, printing and JSON export
├── data/
│   └── students_sample.csv   # sample data with intentional mistakes
├── tests/
│   └── test_rules.py
├── output/               # reports are saved here
├── main.py               # command line entry point
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/vbalhara523/csv-quality-checker.git
cd csv-quality-checker

python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
# basic check
python main.py data/students_sample.csv

# also save a cleaned csv (rows with problems removed)
python main.py data/students_sample.csv --clean

# exit code 1 if any issue is found (useful for scripts)
python main.py data/students_sample.csv --strict

# custom output folder
python main.py data/students_sample.csv --out my_reports --clean
```

### Example output

```
=== CSV QUALITY REPORT ===
Rows checked      : 24
Clean rows        : 12
Rows with issues  : 12
Quality score     : 50.0%

ROW   COLUMN          ISSUE                    VALUE
--------------------------------------------------------------
4     email           expected email           rohan.dahiya@brcm
5     cgpa            missing value
9     *               duplicate row            entire row
11    cgpa            above maximum (10)       14.5
13    admission_date  expected date            2025-13-40
17    fees_paid       outlier (IQR rule)       620000
...
```

Row numbers match the line numbers in the CSV file (line 1 is the header), so you can open the file and jump straight to the problem.

## Running the tests

```bash
pytest
```

## How it works (short version)

1. The CSV is loaded with `dtype=str` so pandas does not quietly convert or hide bad values.
2. Each check in `rules.py` is a separate function that returns a list of issues.
3. `run_all_checks()` combines them, and `report.py` turns the list into a summary and a JSON file.
4. For the outlier check I used the IQR rule: values beyond `Q3 + 3 × IQR` (or below `Q1 − 3 × IQR`) are flagged.

## Using your own data

Edit the `SCHEMA` and `RANGES` dictionaries at the top of `checker/rules.py` to match your column names and types. Supported types are `int`, `float`, `str`, `email` and `date` (YYYY-MM-DD).

## What I learned

- Why reading everything as text first makes validation easier
- How to use the IQR method to detect outliers
- Structuring a small project into modules instead of one long script
- Writing unit tests for each rule with pytest

## Future improvements

- Load the schema from a YAML/JSON file instead of editing code
- Add an HTML report
- Fuzzy duplicate detection (similar names)
- Support Excel files

## Author

**Vallabh Balhara** – B.Tech CSE student
[LinkedIn](https://linkedin.com/in/vallabhbalhara) · [GitHub](https://github.com/vbalhara523)

## License

MIT
