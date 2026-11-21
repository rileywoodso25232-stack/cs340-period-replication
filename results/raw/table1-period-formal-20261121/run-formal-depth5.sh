#!/usr/bin/env bash
set -Eeuo pipefail

batch="$1"
cve="$2"
number="$3"
expected="$4"

root="/workdir/PERIOD"

case "$cve" in
  CVE-2016-7911) binary="2016-7911" ;;
  CVE-2016-9806) binary="2016-9806" ;;
  CVE-2017-15265) binary="2017-15265" ;;
  *) echo "Unknown CVE"; exit 2 ;;
esac

case_dir="$root/evaluation/ConVul-CVE-Benchmarks/$cve"
run_id=$(printf "run%02d" "$number")
out="/workdir/runs/$batch/formal/$cve/$run_id"
driver="$root/tool/DBDS/run_PDS.py"

if [ -e "$out" ]; then
  echo "REFUSING OVERWRITE: $out"
  exit 3
fi

actual=$(sha256sum "$driver" | awk '{print $1}')

if [ "$actual" != "$expected" ]; then
  echo "DRIVER HASH MISMATCH"
  exit 4
fi

test -f "$case_dir/build.sh"
test -f "$case_dir/$binary.cpp"

mkdir -p "$out/generated"

export ROOT_DIR="$root"
export PATH="$root/clang+llvm/bin:$root/tool/SVF/Release-build/bin:$PATH"
export LD_LIBRARY_PATH="$root/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

{
  echo "batch=$batch"
  echo "cve=$cve"
  echo "run=$run_id"
  echo "utc_start=$(date -u +%FT%TZ)"
  echo "depth=5"
  echo "run_limit=10000"
  echo "driver_options=-y -d 5 -f 10000"
  echo "upstream_commit=$(git -C "$root" rev-parse HEAD)"
  echo "kernel=$(uname -r)"
  sha256sum "$driver" "$case_dir/build.sh" "$case_dir/$binary.cpp"
} > "$out/metadata.txt"

cd "$case_dir"

echo "===== $cve $run_id BUILD ====="

if timeout --signal=TERM --kill-after=15s 900s \
  ./build.sh > "$out/build.log" 2>&1
then
  build_rc=0
else
  build_rc=$?
fi

echo "$build_rc" > "$out/build.exitcode"

if [ "$build_rc" -ne 0 ]; then
  echo "build_failed" > "$out/status.txt"
  echo "BUILD FAILED: $build_rc"
  exit 0
fi

sha256sum "./$binary" > "$out/binary.sha256"

echo "===== $cve $run_id SEARCH ====="

if timeout --signal=TERM --kill-after=15s 600s \
  python3 "$driver" -y -d 5 -f 10000 "./$binary" \
  < /dev/null > "$out/search.log" 2>&1
then
  search_rc=0
else
  search_rc=$?
fi

echo "$search_rc" > "$out/search.exitcode"

find . -maxdepth 1 -mindepth 1 -name 'out_*' \
  -exec cp -a {} "$out/generated/" \;

if [ "$search_rc" -eq 0 ] &&
   grep -q 'End Testing!' "$out/search.log" &&
   grep -q 'Total Error Interleavings:' "$out/search.log" &&
   grep -q '^Round' "$out/search.log"
then
  echo "completed" > "$out/status.txt"
else
  echo "incomplete_or_aborted" > "$out/status.txt"
fi

echo "utc_end=$(date -u +%FT%TZ)" >> "$out/metadata.txt"

echo "===== RESULT: $(cat "$out/status.txt") ====="

grep -E 'Total Error Interleavings:|Total Timeouts Interleavings:|^Round' \
  "$out/search.log" | tail -4 || true

echo "SEARCH_EXIT=$search_rc"
