#!/bin/bash
# tuning sweep on the paper's partition {{1,5},{2,4},{3}}: two variants at a time, 120 s each
cd "$(dirname "$0")/.."
run(){ ./bin/c3flip --n 5 --partition "15|24|3" --descents 1000 --seconds 120 --save-at 93 --out out/cal "$@"; }
run --L 1e8 --M 5e4 --paper-plus --seed 21 --tag tune-paperplus > logs/tune-paperplus.log 2>&1 &
run --L 1e8 --M 5e3 --seed 22 --tag tune-M5e3 > logs/tune-M5e3.log 2>&1 &
wait
run --L 3e7 --M 5e5 --seed 23 --tag tune-M5e5 > logs/tune-M5e5.log 2>&1 &
run --L 1e8 --M 5e4 --plus-cap 1 --seed 24 --tag tune-cap1 > logs/tune-cap1.log 2>&1 &
wait
