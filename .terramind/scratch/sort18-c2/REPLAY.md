# c2 compact certificate bundle

This bundle records one complete, fixed-prefix/fixed-suffix sorting-window
UNSAT query against the pinned 77-comparator baseline. Payloads are retained
only as losslessly compressed files.

## Prior-bundle control

Commit `e1328694` and its `sort18-c10` bundle were recovered locally. Running
`sha256sum -c MANIFEST.sha256` from that bundle's own directory validated every
listed object. Its baseline SHA-256 is
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`; the
same byte-identical baseline is used here.

## Fresh query: `[60,72) -> 11`

The search removes the 12 baseline comparators at positions `[60,72)` and
seeks an 11-comparator replacement. The exact one-core invocation was:

```sh
timeout --signal=TERM --kill-after=10s 600s taskset -c 0 \
  /workspace/repo/.terramind/scratch/sort18-c4/venv/bin/python -u \
  window_cegis_artifacts.py baseline.json 60 12 600 6012
```

CaDiCaL 1.5.3 returned UNSAT in 69.453 seconds; the supervisor exit status was
0, so this was neither a timeout nor launcher termination. The initial formula
encodes all 65 reachable prefix states before its first solve and has 16,571
variables and 819,348 clauses. Therefore this proof covers the full
fixed-window formula, not merely a CEGIS subproblem.

`drat-trim` independently replayed the decompressed CNF and DRAT with `s
VERIFIED` in 17.327 seconds. The compressed CNF and proof hashes are:

```
9efc7a5987678e4dede58c25c35d06b5b2598a779f0bbf42290d19a06ac86e9c  CNF.gz
2cacacc81057ddb3a31e84e7db7606b5a2d85419c9641624e8fa61692104a05d  DRAT.xz
```

`MANIFEST.sha256` covers every retained object and validates with `sha256sum
-c MANIFEST.sha256`. The exact command, solver log, exit status, and checker
output are retained alongside the artifacts. This result is a fixed-window
exclusion only: it neither proves a global lower bound nor rules out a
different 76-comparator 18-wire sorting network.
