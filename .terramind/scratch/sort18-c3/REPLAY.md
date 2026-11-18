# c3 compact certificate and timeout bundle

Commit `0361a993` (c2) was recovered locally. Running `sha256sum -c
MANIFEST.sha256` from `.terramind/scratch/sort18-c2/` accepted every retained
object. The pinned baseline is byte-identical here (SHA-256
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`) and
Frontier's exhaustive `diagnose` accepted it on all 262,144 binary inputs at
77 comparators.

## Certified query: `[59,71) -> 11`

The query removes the 12 baseline comparators in `[59,71)` and seeks an
11-comparator replacement (seed `5912`). It extends outside the previously
certified `[60,72)`, `[61,73)`, and `[62,74)` windows, so their exclusions do
not imply it. The initial CNF encodes all 68 reachable prefix states before
the first solve: 17,385 variables and 851,433 clauses.

The one-core, externally bounded command in `run-s59-w12-t11.command` exited
0. CaDiCaL 1.5.3 returned UNSAT in 301.598 seconds. Independent DRAT-trim,
using the command recorded beside the artifacts, exited 0 and reported `s
VERIFIED` in 127.339 seconds. Thus this is a complete fixed-prefix/fixed-suffix
window exclusion, not a partial CEGIS subproblem or a global lower bound.

The retained lossless payloads decompress to:

```
68ee64f2c68180f420e850a18e267da100f7a66eef2797cf5c57edba6154fb49  query_s59_w12_t11.cnf
2008eb7ccba6c1e72b5fc0bbc95ff1cecb9315e42834531ce923bf4f87674c23  query_s59_w12_t11.drat
```

## Unresolved outward query: `[58,70) -> 11`

This distinct query (seed `5812`) also reaches outside every prior certified
enclosing interval. Its full initial CNF includes all 78 reachable prefix
states: 19,821 variables and 957,551 clauses. Its one-core external
supervisor exited 124 at 600 seconds without a SAT or UNSAT result. It is
therefore unresolved; no proof checker was run and no conclusion follows.

The compressed CNF decompresses to:

```
026f566dd67af765c50fbccaeb3b51a82d2c39ce953d7de7ce35db6040a0af05  query_s58_w12_t11.cnf
```

No SAT model or 76-comparator candidate was produced. `[59,75)` and `[42,54)`
remain unresolved.
