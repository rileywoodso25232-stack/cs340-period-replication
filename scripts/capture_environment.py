"""Capture observed machine/tool versions; never invent unavailable fields."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def probe(command):
    if not shutil.which(command[0]):
        return {"status": "unavailable", "command": command}
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15,
        )
        return {"command": command, "returncode": result.returncode,
                "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": command, "status": "failed", "error": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New output file (never overwrite)")
    args = parser.parse_args()
    timestamp = datetime.now(timezone.utc)
    output = args.output or ROOT / "environment/records" / (
        timestamp.strftime("%Y%m%dT%H%M%S%fZ") + ".json"
    )
    data = {
        "captured_at_utc": timestamp.isoformat(),
        "system": platform.system(), "release": platform.release(),
        "version": platform.version(), "machine": platform.machine(),
        "processor": platform.processor(), "python": platform.python_version(),
        "git": probe(["git", "--version"]),
        "gcc": probe(["gcc", "--version"]),
        "clang": probe(["clang", "--version"]),
        "docker": probe(["docker", "--version"]),
        "group_commit": probe(["git", "-C", str(ROOT), "rev-parse", "HEAD"]),
        "group_worktree": probe(["git", "-C", str(ROOT), "status", "--short"]),
        "linux_cpu": probe(["lscpu"]) if platform.system() == "Linux" else None,
        "upstream_reference": json.loads((ROOT / "config/upstream.json").read_text(encoding="utf-8")),
        "not_collected_automatically": [
            "RAM", "container image digest", "CPU affinity", "build flags",
            "workload checksums", "oracle settings", "dependency versions",
        ],
        "experiment_environment_validated": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"Environment recorded: {output}")
    print("Review missing fields. This record does not certify the experiment environment.")


if __name__ == "__main__":
    main()
