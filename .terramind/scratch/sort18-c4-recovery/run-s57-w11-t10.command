timeout --signal=TERM --kill-after=10s 600s taskset -c 0 ./venv/bin/python -u window_cegis_artifacts.py baseline.json 57 11 590 5711 > run-s57-w11-t10.log 2>&1
