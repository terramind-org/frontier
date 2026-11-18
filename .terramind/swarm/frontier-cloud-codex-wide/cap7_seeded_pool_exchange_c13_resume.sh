#!/usr/bin/env bash
# Managed-shell continuation: each short slice consumes and atomically replaces
# the result checkpoint, so a launcher timeout cannot duplicate completed work.
set -euo pipefail
root=.terramind/swarm/frontier-cloud-codex-wide
raw="$root/raw"
deadline=$((SECONDS + 1640))
slice=2
while (( SECONDS < deadline )); do
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 taskset -c 0 timeout 25s \
    python3 "$root/cap7_seeded_pool_exchange.py" --seconds 22 --domains 256 \
    --restarts 128 --raw-dir "$raw" --resume "$raw/cap7_seeded_pool_exchange_result.json" \
    >"$raw/cap7_seeded_pool_exchange_c13_slice$(printf '%02d' "$slice").log"
  python3 - "$raw/cap7_seeded_pool_exchange_result.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print(json.dumps({'slice_resume': r['resume'], 'restarts': r['restarts_completed'],
                  'domains': r['domains_completed'], 'unique': r['unique_neighborhoods_examined']}))
if r['resume']['state'] == 'done' or r['best_verified_size'] >= 237:
    raise SystemExit(10)
PY
  slice=$((slice + 1))
done
