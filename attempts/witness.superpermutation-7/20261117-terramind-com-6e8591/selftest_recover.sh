#!/bin/sh
# Recovery self-test for the kernel line: cut Teodorescu's score-15 kernel at several points, let kernelwalk
# re-complete the tail (target score 15, max length 75, one restart of 5e7 nodes, seed 1), and report whether his
# exact kernel is among the kernels it emits; then run PermutationChains on that kernel and count the solutions.
# Run from the scratch directory: sh src/selftest_recover.sh
K='4666446666-6666466636666-666646646666-666646646666-6666366646666-6666446664'
for c in 72 70 65 60 55 50 45 40; do
  P=$(printf %s "$K" | cut -c1-$c)
  bin/kernelwalk 7 15 75 50000000 1 1 0 "$P" > /tmp/recover_$c.txt
  n=$(sort -u /tmp/recover_$c.txt | wc -l | tr -d ' ')
  if grep -qx -- "$K" /tmp/recover_$c.txt; then hit=yes; else hit=no; fi
  echo "cut $c: $n distinct score>=15 kernels emitted, Teodorescu's kernel among them: $hit"
done
mkdir -p runs/selftest_recover && cp runs/teo/IntersectionFlags7.dat runs/selftest_recover/
cd runs/selftest_recover && rm -f 7_*.txt && ../../bin/PermutationChains 7 "nsk$K" > pc.out 2>&1
echo "PermutationChains on Teodorescu's kernel: exit $?, $(grep -c 'Found SOLUTION' pc.out) solutions, $(grep -h -c . 7_5905_nsk*.txt | head -1) words in 7_5905 file"
