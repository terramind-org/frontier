#!/bin/sh
# run.sh NAME CMD... : runs CMD in the background with nohup, records PID, UTC start, exit status and UTC end.
name=$1; shift
( echo "START $(date -u +%FT%TZ) cmd: $*" > logs/$name.status
  "$@" > logs/$name.out 2>&1
  echo "EXIT $? $(date -u +%FT%TZ)" >> logs/$name.status ) &
echo $! > logs/$name.pid
