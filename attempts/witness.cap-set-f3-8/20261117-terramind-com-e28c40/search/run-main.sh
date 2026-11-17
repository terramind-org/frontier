#!/bin/sh
cd "$(dirname "$0")" || exit 2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
run() {
  name="$1"; shift
  date -u '+%Y-%m-%dT%H:%M:%SZ' > "$name.start"
  cp search.py "$name.search-source.py"
  "$@" > "$name.jsonl" 2> "$name.stderr"
  code=$?
  printf '%s\n' "$code" > "$name.exit"
  date -u '+%Y-%m-%dT%H:%M:%SZ' > "$name.end"
  echo "STAGE_FINISHED $name exit=$code"
  return "$code"
}
run control-few ./venv/bin/python -I exact_sym.py 4 few 60 303 control || exit 1
run control-half ./venv/bin/python -I exact_sym.py 4 half 60 304 control || exit 1
run plateau ./venv/bin/python -I search.py walk plateau 2100 211 baseline.json || exit 1
run region ./venv/bin/python -I search.py walk region 600 212 baseline.json || exit 1
run exact-few ./venv/bin/python -I exact_sym.py 8 few 1000 305 || exit 1
run exact-half ./venv/bin/python -I exact_sym.py 8 half 1000 306 || exit 1
run smaller ./venv/bin/python -I search.py walk smaller 1800 216 start448.json || exit 1
echo ALL_SEARCH_FINISHED
