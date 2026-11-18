#!/bin/bash
# Stage Table 2: SCTBench reorder thread series, PERIOD vs Serial, 3 attempts.
set -uo pipefail
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT="/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069"
BASE="/root/cs340-period/table2"
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$BASE/stage-table2-$TS.log"
PREP_LOG="$BASE/stage-table2-$TS-prepare.log"
RUN_LOG="$BASE/stage-table2-$TS-run.log"
mkdir -p "$BASE"
exec > >(tee -a "$LOG") 2>&1

echo "=== table2 start $(date -Is) ==="
echo "REPO=$REPO"
echo "ROOT=$ROOT"
echo "LOG=$LOG"

fail() {
    echo "TABLE2_FAILED: $*"
    if [ -n "${OUT:-}" ] && [ -d "${OUT:-}" ] && [ -f "${OUT}/manifest.json" ]; then
        python3 "$REPO/scripts/linux/export_table2_formal.py" "$OUT" || echo "EXPORT_FAILED"
    fi
    exit 1
}

[ "$(id -u)" = "0" ] || fail "must run as root"
[ -d "$ROOT/evaluation/CS/reorder_3" ] || fail "missing SCTBench sources"
[ -d "$ROOT/tool/DBDS" ] || fail "missing drivers"
[ -x "$ROOT/clang+llvm/bin/clang" ] || fail "missing clang"
for cmd in python3 unshare patch readelf dpkg-query gcc git; do
    command -v "$cmd" >/dev/null 2>&1 || fail "missing command: $cmd"
done
python3 -c 'import sys; assert sys.version_info[:2] == (3, 6), sys.version' || fail "unexpected python3"
echo "--- kernel/affinity ---"; uname -r
python3 - <<'PY'
import os
print('affinity:', sorted(os.sched_getaffinity(0)))
PY
echo "--- disk ---"; df -h /root | tail -1
echo "--- running drivers ---"
if pgrep -af 'run_PDS.py|run_OldPDS.py|run_table2_formal.py' | grep -v "pgrep -af"; then
    fail "another driver is running"
fi
echo "--- shared memory ---"; ipcs -m || true
echo "--- repo ---"; git -C "$REPO" rev-parse HEAD; git -C "$REPO" rev-parse --abbrev-ref HEAD
git -C "$REPO" status --short

echo "=== prepare $(date -Is) ==="
set +e
python3 "$REPO/scripts/linux/run_table2_formal.py" --phase prepare 2>&1 | tee "$PREP_LOG"
PREP_RC=${PIPESTATUS[0]}
set -e
OUT="$(sed -n 's/^Evidence directory: //p' "$PREP_LOG" | tail -1)"
echo "PREP_RC=$PREP_RC"
echo "EVIDENCE_DIR=$OUT"
if [ "$PREP_RC" -ne 0 ] || [ -z "$OUT" ] || [ ! -d "$OUT" ]; then
    fail "prepare failed"
fi

echo "=== run $(date -Is) ==="
set +e
python3 "$REPO/scripts/linux/run_table2_formal.py" --phase run --directory "$OUT" 2>&1 | tee "$RUN_LOG"
RUN_RC=${PIPESTATUS[0]}
set -e
echo "RUN_RC=$RUN_RC"
python3 - "$OUT/manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
print('status:', m.get('status'), 'runs:', len(m.get('runs', [])))
for r in m.get('runs', []):
    print(' ', r.get('method'), r.get('case'), r.get('run'), r.get('status'))
PY

echo "=== export $(date -Is) ==="
python3 "$REPO/scripts/linux/export_table2_formal.py" "$OUT" || fail "export failed"
echo "=== table2 end $(date -Is) rc=$RUN_RC ==="
exit "$RUN_RC"
