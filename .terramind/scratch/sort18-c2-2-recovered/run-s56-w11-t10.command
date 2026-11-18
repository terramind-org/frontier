timeout --signal=TERM --kill-after=10s 600s taskset -c 0 /tmp/sort18-venv/bin/python -u window_cegis_artifacts.py baseline.json 56 11 590 5611 > run-s56-w11-t10.log 2>&1
