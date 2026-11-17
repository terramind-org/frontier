#!/bin/sh
cd "$(dirname "$0")" || exit 2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1
run() {
  name="$1"; shift
  date -u '+%Y-%m-%dT%H:%M:%SZ' > "$name.start"
  "$@" > "$name.jsonl" 2> "$name.stderr"
  code=$?
  printf '%s\n' "$code" > "$name.exit"
  date -u '+%Y-%m-%dT%H:%M:%SZ' > "$name.end"
  echo "STAGE_FINISHED $name exit=$code"
  return "$code"
}
run sat-install uv pip install --python venv/bin/python python-sat || exit 1
run sat-control ./venv/bin/python -I full_region_sat.py control || exit 1
sat_seconds=$(./venv/bin/python -I budget_seconds.py 600)
if [ "$sat_seconds" -gt 0 ]; then
  run sat-region ./venv/bin/python -I full_region_sat.py "$sat_seconds" || exit 1
fi
warm_seconds=$(./venv/bin/python -I budget_seconds.py 900)
if [ "$warm_seconds" -gt 0 ]; then
  run exact-few-warm ./venv/bin/python -I exact_sym.py 8 few "$warm_seconds" 507 full-hint || exit 1
fi
echo ALL_SAT_FINISHED
