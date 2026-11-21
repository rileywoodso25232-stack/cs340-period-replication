#!/bin/bash
set -eu
source_dir=/workdir/PERIOD/evaluation/CS/reorder_3
session="/workdir/cs340-runs/period-batches-$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -p "$session"
printf '%s\n' "$session" > period-session-path.txt

for group in 1 2 3; do
    run="$session/group-$group"
    mkdir "$run"
    cp "$source_dir/reorder_3_bad" \
       "$source_dir/ConConfig.reorder_3_bad" \
       "$source_dir/mempair.reorder_3_bad.npz" "$run/"
    (
        cd "$run"
        ulimit -c 0
        sha256sum reorder_3_bad > binary.sha256
        printf '%s\n' 'timeout --kill-after=10s 120s python3 /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 -f 1000 -t 5 ./reorder_3_bad' > command.txt
        code=0
        timeout --kill-after=10s 120s python3 \
          /workdir/PERIOD/tool/DBDS/run_PDS.py \
          -y -d 3 -f 1000 -t 5 ./reorder_3_bad \
          > search.log 2>&1 || code=$?
        echo "$code" > search.exit
        echo "Group $group; driver exit: $code"
        tail -12 search.log
    )
done
echo "Saved: $session"
