#!/bin/bash
# every 20 s: lift each saved scheme of rank < 93 and run the repo verifier on the result
cd "$(dirname "$0")/.."
while [ ! -f logs/autolift.stop ]; do
  for f in out/long/*-r9[0-2]-*.c3 out/long/*-r[0-8][0-9]-*.c3; do
    [ -f "$f" ] || continue; [ -f "$f.lifted" ] && continue
    echo "$(date -u +%FT%TZ) LIFTING $f" >> logs/autolift.log
    uv run -q --no-project --with numpy python -I src/c3lift.py "$f" "${f%.c3}.json" 20 24 2 1 >> logs/autolift.log 2>&1
    echo "lift_exit=$?" >> logs/autolift.log
    [ -f "${f%.c3}.json" ] && (cd ../../.. && bun frontier diagnose ".terramind/scratch/matmul5-r2/${f%.c3}.json" --problem witness.matmul-rank-5x5x5) >> logs/autolift.log 2>&1
    touch "$f.lifted"
  done
  sleep 20
done
