#!/bin/sh
cd /Users/agrim/.terramind/worktrees/frontier/parental-glacier || exit 2
p=.terramind/scratch/schur7
date -u '+START %Y-%m-%dT%H:%M:%SZ'
"$p/local" 7190 "$p" > "$p/local.log" 2>&1 &
lpid=$!
"$p/venv/bin/python" -I "$p/sat.py" 7190 > "$p/sat.log" 2>&1 &
spid=$!
echo "local_pid=$lpid sat_pid=$spid"
wait "$lpid"; lcode=$?
wait "$spid"; scode=$?
echo "EXIT local=$lcode sat=$scode"
date -u '+END %Y-%m-%dT%H:%M:%SZ'
