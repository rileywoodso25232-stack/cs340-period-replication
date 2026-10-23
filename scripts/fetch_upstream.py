"""Retrieve the pinned PERIOD source without changing an existing checkout."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = json.loads((ROOT / "config/upstream.json").read_text(encoding="utf-8"))
    commit = config["commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("upstream commit must be a full 40-character SHA")
    destination = (ROOT / config["destination"]).resolve()
    if not destination.is_relative_to(ROOT / "third_party"):
        raise ValueError("destination must be inside third_party/")
    if not shutil.which("git"):
        raise RuntimeError("Git is required; install it and add it to PATH")
    if destination.exists():
        if not (destination / ".git").exists():
            raise RuntimeError(f"Destination exists and is not a Git checkout: {destination}")
        current = subprocess.check_output(
            ["git", "-C", str(destination), "rev-parse", "HEAD"], text=True
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(destination), "status", "--porcelain"], text=True
        ).strip()
        if current != commit or dirty:
            raise RuntimeError("Existing checkout differs or has local changes; inspect it manually")
        print(f"Already present at pinned commit: {commit}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", str(destination)], check=True)
    subprocess.run(
        ["git", "-C", str(destination), "remote", "add", "origin", config["repository"]],
        check=True,
    )
    # Fetch the exact object rather than relying on the moving default branch.
    subprocess.run(
        ["git", "-C", str(destination), "fetch", "--depth", "1", "origin", commit],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(destination), "checkout", "--detach", commit], check=True
    )
    actual = subprocess.check_output(
        ["git", "-C", str(destination), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != commit:
        raise RuntimeError(f"Wrong upstream commit: {actual}")
    print(f"Fetched {config['name']} at {actual}")
    print("Next: validate environment/README.md. No build or experiment was run.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Source retrieval failed: {error}", file=sys.stderr)
        print("Inspect any partial checkout; this script never deletes it automatically.", file=sys.stderr)
        sys.exit(1)
