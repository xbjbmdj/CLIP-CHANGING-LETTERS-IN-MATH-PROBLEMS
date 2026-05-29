#!/usr/bin/env python3
"""
Scan a file for occurrences of the pattern:
    "completion_tokens": <integer>
Prints matching line numbers and the extracted integers, and a summary list.
Usage:
    python find_completion_tokens.py [path/to/file]
Default file: ori1.json
"""
import re
import csv
from pathlib import Path


def collect_values(filename, max_rows=22):
    pattern = re.compile(r'"completion_tokens"\s*:\s*(\d+)')
    pattern_target = re.compile(r'target": 1')
    vals = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                m = pattern.search(line)
                if m and pattern_target.search(line):
                    vals.append(int(m.group(1)))
                    if len(vals) >= max_rows:
                        break
                else:
                    vals.append("sss")
    except FileNotFoundError:
        # missing file -> return empty column
        return []
    return vals


def main():
    # Read var1.json .. var16.json and build a CSV with 16 columns and 20 rows
    cols = []
    for i in range(1, 13):
        fname = f"o{i}.json"
        cols.append(collect_values(fname, max_rows=22))

    # Prepare 20 rows, filling missing entries with empty strings
    rows = []
    for r in range(22):
        row = []
        for col in cols:
            if r < len(col):
                row.append(str(col[r]))
            else:
                row.append("")
        rows.append(row)

    out_path = Path("exp2_ori.csv")
    with out_path.open("w", encoding="utf-8-sig", newline="") as csvf:
        writer = csv.writer(csvf)
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
