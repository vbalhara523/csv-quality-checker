"""Turns the list of issues into a summary, a printed table and a JSON file."""
import json
from collections import Counter
from pathlib import Path


def summarize(df, issues):
    bad_rows = {i["row"] for i in issues}
    total = len(df)
    clean = total - len(bad_rows)
    score = round(clean / total * 100, 1) if total else 0.0
    return {
        "total_rows": total,
        "clean_rows": clean,
        "rows_with_issues": len(bad_rows),
        "total_issues": len(issues),
        "quality_score": score,
        "issues_by_type": dict(Counter(i["issue"].split(" (")[0] for i in issues)),
    }


def print_report(summary, issues):
    print("\n=== CSV QUALITY REPORT ===")
    print(f"Rows checked      : {summary['total_rows']}")
    print(f"Clean rows        : {summary['clean_rows']}")
    print(f"Rows with issues  : {summary['rows_with_issues']}")
    print(f"Quality score     : {summary['quality_score']}%")
    print("\nIssues by type:")
    for name, count in sorted(summary["issues_by_type"].items(), key=lambda x: -x[1]):
        print(f"  {name:<22} {count}")

    if issues:
        print(f"\n{'ROW':<5} {'COLUMN':<15} {'ISSUE':<24} VALUE")
        print("-" * 62)
        for i in issues:
            print(f"{i['row']:<5} {i['column']:<15} {i['issue']:<24} {i['value']}")
    print()


def save_json(summary, issues, out_dir, name="report.json"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "issues": issues}, f, indent=2)
    return path
