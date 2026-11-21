#!/bin/bash
set -Eeuo pipefail

batch="$1"
root="/workdir/PERIOD"
out="/workdir/runs/$batch"

if [ -e "$out" ]; then
    echo "ERROR: Batch already exists"
    exit 1
fi

mkdir -p "$out/meta" "$out/preexisting"

echo "=== RECORDING ENVIRONMENT ==="

{
    echo "Batch: $batch"
    echo "UTC: $(date -u +%FT%TZ)"
    echo "Root: $root"
    echo "Upstream commit: $(git -C "$root" rev-parse HEAD)"
    echo "Kernel: $(uname -r)"
    gcc --version | head -1
    "$root/clang+llvm/bin/clang" --version | head -1
    python3 --version
} > "$out/meta/environment.txt"

git -C "$root" status --short --untracked-files=no \
    > "$out/meta/git-status.txt"

git -C "$root" diff --binary \
    > "$out/meta/tracked-changes.patch"

sha256sum \
    "$root/tool/DBDS/run_PDS.py" \
    "$root/tool/staticAnalysis/staticAnalysis.sh" \
    > "$out/meta/tool-hashes.sha256"

echo "=== PROTECTING EXISTING CVE DIRECTORIES ==="

for cve in CVE-2016-7911 CVE-2016-9806 CVE-2017-15265
do
    dir="$root/evaluation/ConVul-CVE-Benchmarks/$cve"

    test -d "$dir"
    test -f "$dir/build.sh"
    test -f "$dir/cleanDIR.sh"

    tar -czf "$out/preexisting/$cve.tar.gz" -C "$dir" .

    sha256sum "$dir/build.sh" "$dir/cleanDIR.sh" \
        >> "$out/meta/tool-hashes.sha256"

    echo "SAVED: $cve"
done

sha256sum "$out"/preexisting/*.tar.gz \
    > "$out/meta/preexisting-hashes.sha256"

cat > "$out/meta/run-settings.txt" <<EOF
Experiment: Controlled PERIOD Depth 5
Depth: 5
Driver option: -d 5
Skip interactive confirmation: -y
Maximum driver runs: -f 10000
Planned completed repetitions: 10 per CVE
Benchmarks:
CVE-2016-7911
CVE-2016-9806
CVE-2017-15265
EOF

echo "=== PREPARATION COMPLETE ==="
ls -lh "$out/preexisting"