"""Summarize real numeric observations with log/environment traceability."""

import argparse
import csv
from collections import defaultdict
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ["experiment_id", "claim_id", "benchmark", "mode", "run_id", "metric",
           "value", "unit", "log_path", "environment_path"]
GROUP = ["experiment_id", "claim_id", "benchmark", "mode", "metric", "unit"]


def evidence_file(value, line):
    relative = Path(value)
    path = (ROOT / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"Line {line}: evidence must be an existing repository-relative file: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "results/raw/measurements.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results/processed/summary.csv")
    args = parser.parse_args()
    groups = defaultdict(list)
    seen = set()
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise ValueError("Measurement CSV columns differ from results/raw/README.md")
        for line, row in enumerate(reader, start=2):
            if None in row or any(not (row.get(key) or "").strip() for key in COLUMNS):
                raise ValueError(f"Line {line}: missing or extra values")
            row = {key: value.strip() for key, value in row.items()}
            key = tuple(row[name] for name in GROUP)
            identity = key + (row["run_id"],)
            if identity in seen:
                raise ValueError(f"Line {line}: duplicate observation for the same run and metric")
            seen.add(identity)
            value = float(row["value"])
            if not math.isfinite(value):
                raise ValueError(f"Line {line}: value must be finite")
            evidence_file(row["log_path"], line)
            evidence_file(row["environment_path"], line)
            groups[key].append(value)
    if not groups:
        print("No measured data yet. Collect runs and logs before computing statistics.")
        return
    incomplete = [key for key, values in groups.items() if len(values) < 3]
    if incomplete:
        raise ValueError(f"At least three independent runs required per group; incomplete: {incomplete}")
    rows = []
    for key, values in sorted(groups.items()):
        rows.append(dict(zip(GROUP, key)) | {
            "n": len(values), "mean": statistics.mean(values),
            "stddev": statistics.stdev(values), "min": min(values), "max": max(values),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GROUP + ["n", "mean", "stddev", "min", "max"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} groups to {args.output}; sample standard deviation uses n-1.")
    print("Check experiment completeness and unsuccessful attempts separately before interpretation.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"Summary failed: {error}", file=sys.stderr)
        sys.exit(1)
