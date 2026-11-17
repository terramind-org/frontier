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
run product-build ./venv/bin/python -I hill_products.py || exit 1
run product448 ./venv/bin/python -I search.py walk literature448 1400 403 hill-product448.json || exit 1
run product405 ./venv/bin/python -I search.py walk literature405 1000 404 hill-product405.json || exit 1
run other448 ./venv/bin/python -I search.py walk other448 1200 405 start448-other.json || exit 1
echo ALL_PRODUCTS_FINISHED
