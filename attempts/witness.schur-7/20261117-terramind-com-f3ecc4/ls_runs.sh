#!/bin/sh
# Breakout local search at N = 1699 from two non-Rowley start points (integers past the start length random).
bin/breakout 1699 7 best/N1698_b1_0014_sym.json 11 780 ls/ls_N1699_from1698sym.json 0.01 > logs/ls_A.log 2>&1; echo "A exit $? $(date -u +%FT%TZ)"
bin/breakout 1699 7 best/N1697_b1_0014_free.json 12 780 ls/ls_N1699_from1697free.json 0.01 > logs/ls_B.log 2>&1; echo "B exit $? $(date -u +%FT%TZ)"
