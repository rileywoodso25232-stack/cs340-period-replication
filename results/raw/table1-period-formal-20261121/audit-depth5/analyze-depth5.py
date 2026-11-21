import csv
import hashlib
import re
import statistics
import sys
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])

driver_hash = "c6ed1312f61f7ec739e3dcead0086e0265d37f07bd88ef64d6588d3ff61a8e8f"

paper = {
    "CVE-2016-7911": (3, 19, 8),
    "CVE-2016-9806": (6, 42, 4),
    "CVE-2017-15265": (11, 96, 1),
}

metrics = ("first_error", "schedules", "error_interleavings")
rows = []
summaries = []
comparisons = []

def required(path):
    if not path.is_file():
        raise RuntimeError(f"Missing evidence: {path}")
    return path.read_text(encoding="utf-8", errors="replace")

def extract(pattern, text, path):
    match = re.search(pattern, text, re.M)
    if not match:
        raise RuntimeError(f"Cannot parse {pattern}: {path}")
    return int(match.group(1))

for cve, reference in paper.items():
    folder = root / "formal" / cve
    runs = sorted(folder.glob("run[0-9][0-9]"))

    completed = []

    for run in runs:
        status = required(run / "status.txt").strip()
        build_rc = int(required(run / "build.exitcode").strip())
        search_rc_file = run / "search.exitcode"

        search_rc = (
            int(required(search_rc_file).strip())
            if search_rc_file.exists() else None
        )

        log = required(run / "search.log") if (run / "search.log").exists() else ""
        meta = required(run / "metadata.txt")

        if driver_hash not in meta.lower():
            raise RuntimeError(f"Driver hash missing or changed: {run}")

        record = {
            "benchmark": cve,
            "run": run.name,
            "status": status,
            "build_exit": build_rc,
            "search_exit": search_rc,
            "first_error": "",
            "schedules": "",
            "error_interleavings": "",
            "timeouts": "",
            "log_path": (run / "search.log").relative_to(root).as_posix(),
        }

        if status == "completed":
            if build_rc != 0 or search_rc != 0 or "End Testing!" not in log:
                raise RuntimeError(f"Invalid completed status: {run}")

            required(run / "binary.sha256")

            total = extract(r"(?m)^\s*Round\s+\S+\s+(\d+)\s*$", log, run)
            errors = extract(r"Total Error Interleavings:\s*(\d+)", log, run)
            timeouts = extract(r"Total Timeouts Interleavings:\s*(\d+)", log, run)

            saved = sorted(
                p for p in (run / "generated").rglob("*")
                if p.is_file() and p.parent.name == "Errors"
            )

            positions = []
            for p in saved:
                match = re.match(r"^\d+_(\d+)_", p.name)
                if not match:
                    raise RuntimeError(f"Unexpected error file: {p}")
                positions.append(int(match.group(1)))

            if len(saved) != errors:
                raise RuntimeError(
                    f"Error-file count differs from search.log: {run}"
                )

            first = min(positions) if positions else None

            if errors > 0 and first is None:
                raise RuntimeError(f"First error missing: {run}")

            record.update({
                "first_error": first if first is not None else "",
                "schedules": total,
                "error_interleavings": errors,
                "timeouts": timeouts,
            })

            completed.append(record)

        elif status == "incomplete_or_aborted":
            if "Aborted" not in log:
                print("WARNING: Incomplete run needs further review:", run)

        else:
            raise RuntimeError(f"Unexpected run status: {run}")

        rows.append(record)

    if len(completed) != 10:
        raise RuntimeError(
            f"{cve}: expected 10 completed runs, got {len(completed)}"
        )

    for index, metric in enumerate(metrics):
        values = [float(r[metric]) for r in completed]
        mean = statistics.mean(values)
        sd = statistics.stdev(values)
        original = reference[index]

        summary = {
            "benchmark": cve,
            "depth": 5,
            "metric": metric,
            "n": len(values),
            "mean": round(mean, 6),
            "sample_sd": round(sd, 6),
        }
        summaries.append(summary)

        comparisons.append({
            **summary,
            "paper_value": original,
            "absolute_gap": round(mean - original, 6),
            "relative_gap_percent": round(
                100 * (mean - original) / original, 6
            ) if original else "",
            "numeric_match": abs(mean - original) < 1e-9,
        })

def write_csv(filename, data):
    path = out / filename
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    print("CREATED:", path)

write_csv("all-attempts.csv", rows)
write_csv("summary-depth5.csv", summaries)
write_csv("paper-vs-ours-depth5.csv", comparisons)

with (out / "evidence-sha256.csv").open(
    "w", newline="", encoding="utf-8-sig"
) as file:
    writer = csv.writer(file)
    writer.writerow(["relative_path", "size_bytes", "sha256"])

    for dirname in ("formal", "meta", "preexisting", "trial-CVE-2016-7911"):
        directory = root / dirname
        if not directory.exists():
            continue

        for path in sorted(directory.rglob("*")):
            if path.is_file():
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                writer.writerow([
                    path.relative_to(root).as_posix(),
                    path.stat().st_size,
                    digest,
                ])

print("\n===== VALIDATED SUMMARY =====")
for row in comparisons:
    print(
        row["benchmark"], row["metric"],
        "Paper:", row["paper_value"],
        "Ours:", row["mean"],
        "+/-", row["sample_sd"],
        "Match:", row["numeric_match"]
    )

print("\nAttempts:", len(rows))
print("Completed:", sum(r["status"] == "completed" for r in rows))
print("Incomplete:", sum(r["status"] != "completed" for r in rows))
print("Matching metrics:", sum(r["numeric_match"] for r in comparisons), "/ 9")
print("===== AUDIT PASSED =====")