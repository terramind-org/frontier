#!/bin/sh
# Core 2 schedule: program search (greedy.py), then exchange search from its best non-baseline cap and from the
# best product cap, then a second exchange-search seed on the baseline with always-accept plateau moves.
cd "$(dirname "$0")/.."
PY="venv/bin/python -I"
$PY src/greedy.py runs/B 8 6 12
V=$(ls runs/B/variant*.json | grep -v variant0_ | head -1)
$PY src/lns.py "$V" runs/B_variant 21 20
P=$(ls runs/B/product0_*.json | head -1)
KMIN=40 KMAX=380 $PY src/lns.py "$P" runs/B_product 31 15
PLATEAU=1.0 KMIN=150 KMAX=500 TMAX=90 $PY src/lns.py baseline.json runs/B_baseline 41 "${BMIN:-38}"
echo "run_b done"
