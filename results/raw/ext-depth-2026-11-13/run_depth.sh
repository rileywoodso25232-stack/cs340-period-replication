#!/bin/bash
# 用法: run_depth.sh <CVE目录名> <程序名>
CVE=$1; BIN=$2
SRC=$ROOT_DIR/evaluation/ConVul-CVE-Benchmarks/$CVE
BASE=/workdir/runs/ext-depth/$(echo $CVE | tr 'A-Z' 'a-z')
cd $SRC || exit 1
for D in 1 2 3 4 5; do
  OUT=$BASE/d$D; mkdir -p $OUT
  for i in 1 2 3; do
    if [ -e $OUT/run$i.log ]; then echo "$OUT/run$i 已存在,跳过"; continue; fi
    ./build.sh > $OUT/build$i.log 2>&1
    printf '\n' | $ROOT_DIR/tool/DBDS/run_PDS.py -d $D ./$BIN > $OUT/run$i.log 2>&1
    cp -r out_${BIN}_1 $OUT/run$i-out 2>/dev/null
    FIRST=$(ls $OUT/run$i-out/Errors 2>/dev/null | head -1)
    TOTAL=$(grep "^Round" $OUT/run$i.log | awk '{print $NF}')
    ERR=$(grep "Total Error" $OUT/run$i.log | awk '{print $NF}')
    MAXD=$(grep -o "bug depth = [0-9]*" $OUT/run$i.log | tail -1 | awk '{print $NF}')
    echo "$CVE d=$D run$i first=${FIRST:-none} total=$TOTAL errors=$ERR maxdepth=$MAXD" | tee -a $BASE/summary.txt
  done
done
