"""Check scaffold structure, metadata, links and candidate Git file sizes."""

import ast
import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "GETTING_STARTED.zh-CN.md", "CONTRIBUTING.md", "LICENSE",
    ".gitignore", ".gitattributes", "THIRD_PARTY_NOTICES.md", "Makefile",
    "config/upstream.json", "config/experiments.example.json",
    "docs/team.md", "docs/project-plan.md", "docs/claims.md", "docs/analysis.md",
    "docs/deviations.csv", "docs/upstream-modifications.csv", "docs/ai-usage.md",
    "docs/weekly-log.md", "environment/README.md", "environment/records/README.md",
    "experiments/smoke/README.md", "experiments/baseline/README.md",
    "experiments/extension/README.md", "src/README.md", "src/patches/README.md",
    "third_party/README.md", "licenses/PERIOD-MIT.txt", "results/raw/README.md",
    "results/raw/measurements.csv", "results/processed/README.md",
    "results/processed/paper_vs_ours.csv", "results/figures/README.md",
    "report/outline.md", "report/references.bib", "presentation/README.md",
    "scripts/fetch_upstream.py", "scripts/capture_environment.py",
    "scripts/summarize.py", "scripts/check_repository.py",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/task.md",
]


def candidate_files():
    if shutil.which("git") and (ROOT / ".git").exists():
        names = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
        ).decode("utf-8").split("\0")
        return [ROOT / name for name in set(names) if name and (ROOT / name).is_file()]
    excluded = {".git", "__pycache__", ".venv", "build", "downloads", "tmp", ".cache"}
    return [path for path in ROOT.rglob("*") if path.is_file()
            and not excluded.intersection(path.relative_to(ROOT).parts)
            and not path.is_relative_to(ROOT / "third_party/PERIOD")]


def main():
    errors = [f"Missing required file: {name}" for name in REQUIRED if not (ROOT / name).is_file()]
    upstream = json.loads((ROOT / "config/upstream.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[0-9a-f]{40}", upstream.get("commit", "")):
        errors.append("upstream commit is not a full SHA")
    config = json.loads((ROOT / "config/experiments.example.json").read_text(encoding="utf-8"))
    if config.get("repeats", 0) < 3:
        errors.append("At least three repeats are required")
    with (ROOT / "results/raw/measurements.csv").open(encoding="utf-8-sig", newline="") as handle:
        expected = ["experiment_id", "claim_id", "benchmark", "mode", "run_id", "metric",
                    "value", "unit", "log_path", "environment_path"]
        if next(csv.reader(handle), []) != expected:
            errors.append("Unexpected measurement CSV header")
    files = candidate_files()
    for path in files:
        if path.stat().st_size > 50_000_000:
            errors.append(f"File exceeds 50 MB: {path.relative_to(ROOT)}")
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if path.suffix == ".md":
            for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                target = target.split("#", 1)[0]
                if target and not (path.parent / target).exists():
                    errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Repository checks passed: {len(REQUIRED)} required files; {len(files)} candidate files inspected.")
    print("These checks do not build PERIOD, run benchmarks or certify course compliance.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f"Repository check failed: {error}", file=sys.stderr)
        sys.exit(1)
