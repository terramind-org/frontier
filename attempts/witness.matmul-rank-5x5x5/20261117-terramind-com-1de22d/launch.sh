#!/bin/bash
# launch.sh <tag> <seconds> <seed> <c3flip args...>: one search process, records start, end and exit status
cd "$(dirname "$0")/.."
tag=$1; secs=$2; seed=$3; shift 3
echo "tag=$tag start_utc=$(date -u +%FT%TZ) seconds=$secs seed=$seed args=$*" > logs/$tag.status
./bin/${BIN:-c3flip} --n 5 --L 1e8 --M 5e4 --paper-plus --descents 1000000 --seconds "$secs" --seed "$seed" --tag "$tag" --out out/long --save-at ${SAVEAT:-96} "$@" > logs/$tag.log 2>&1
rc=$?
echo "tag=$tag end_utc=$(date -u +%FT%TZ) exit_status=$rc" >> logs/$tag.status
