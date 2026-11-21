#!/usr/bin/env bash
set -Eeuo pipefail

batch="$1"
root="/workdir/PERIOD"
case_dir="$root/evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911"
out="/workdir/runs/$batch/trial-CVE-2016-7911"

if [ -e "$out" ]; then
    echo "ERROR: Trial already exists. Refusing overwrite."
    exit 1
fi

test -d "$case_dir"
test -f "$case_dir/build.sh"
test -f "$root/tool/DBDS/run_PDS.py"

mkdir -p "$out/generated"

export ROOT_DIR="$root"
export PATH="$root/clang+llvm/bin:$root/tool/SVF/Release-build/bin:$PATH"
export LD_LIBRARY_PATH="$root/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

{
    echo "UTC_START=$(date -u +%FT%TZ)"
    echo "CVE=CVE-2016-7911"
    echo "DEPTH=5"
    echo "RUN_LIMIT=10000"
    echo "DRIVER_OPTIONS=-y -d 5 -f 10000"
    echo "SOURCE_COMMIT=$(git -C "$root" rev-parse HEAD)"
    echo "KERNEL=$(uname -r)"
    sha256sum "$root/tool/DBDS/run_PDS.py"
    sha256sum "$case_dir/build.sh"
    sha256sum "$case_dir/2016-7911.cpp"
} > "$out/metadata.txt"

cd "$case_dir"

echo "===== BUILD START ====="

if timeout --signal=TERM --kill-after=15s 900s \
    ./build.sh > "$out/build.log" 2>&1
then
    build_rc=0
else
    build_rc=$?
fi

echo "$build_rc" > "$out/build.exitcode"

if [ "$build_rc" -ne 0 ]; then
    echo "BUILD FAILED: $build_rc"
    tail -30 "$out/build.log"
    exit "$build_rc"
fi

sha256sum ./2016-7911 > "$out/binary.sha256"

echo "===== SEARCH START: DEPTH 5 ====="

if timeout --signal=TERM --kill-after=15s 600s \
    python3 "$root/tool/DBDS/run_PDS.py" \
    -y -d 5 -f 10000 ./2016-7911 \
    < /dev/null > "$out/search.log" 2>&1
then
    search_rc=0
else
    search_rc=$?
fi

echo "$search_rc" > "$out/search.exitcode"

find . -maxdepth 1 -mindepth 1 -name "out_*" \
    -exec cp -a {} "$out/generated/" \;

echo "UTC_END=$(date -u +%FT%TZ)" >> "$out/metadata.txt"

echo "===== SEARCH EXIT CODE: $search_rc ====="
echo "===== LAST 35 LOG LINES ====="

tail -35 "$out/search.log"

exit "$search_rc"
