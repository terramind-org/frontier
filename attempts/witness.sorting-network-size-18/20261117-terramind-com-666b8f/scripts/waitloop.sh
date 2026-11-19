#!/bin/bash
# wait until $1 seconds elapse, the overall deadline passes, or a candidate <=76 appears
end=$(( $(date +%s) + $1 )); dl=$(( $(cat search_start.txt) + 7200 ))
while [ $(date +%s) -lt $end ] && [ $(date +%s) -lt $dl ]; do
  ls found_*.json >/dev/null 2>&1 && { echo FOUND_SAT; break; }
  grep -qE "'L':(7[0-6]|6[0-9]),'D'" sh_*.out 2>/dev/null && { echo FOUND_SH; break; }
  sleep 20
done
date; grep -h "Most" sh_*.out | tail -1
