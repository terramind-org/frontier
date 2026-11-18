# c4 recovery: certified exterior sorting window

Recovered PR 100's c3 commit `adeb3d10` locally and ran
`sha256sum -c MANIFEST.sha256` from `.terramind/scratch/sort18-c3/`.
Every retained c3 object matched. The baseline used here is byte-identical to
c3's verified 77-comparator witness:

```
ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd  baseline.json
```

## Query `[57,68) -> 10`

The query fixes gates `[0,57)` and `[68,77)` of the 77-comparator baseline,
replacing the eleven gates in `[57,68)` with ten. It is not contained by the
previous certified windows `[59,71)`, `[60,72)`, `[61,73)`, or `[62,74)`, so
those fixed-window exclusions do not imply this result. The still-unresolved
`[58,70)`, `[59,75)`, and `[42,54)` queries were not rerun.

`run-s57-w11-t10.command` records the exact one-core command. The 600-second
external supervisor exited 0; CaDiCaL reported UNSAT in 78.711 seconds. The
initial query encodes every one of the 90 reachable prefix states before the
first solve: 21,150 variables and 987,517 clauses.

`drat-trim` independently exited 0 and reported `s VERIFIED` in 33.374
seconds. Its complete output and command are retained beside the compressed
CNF and proof. The lossless payloads decompress to the following hashes:

```
f15a4f5512c7fd1c8cb9359e0aa0f85bf06f031e4fa8d357b3173806e69e62eb  query_s57_w11_t10.cnf
c80f6f53b0119babb8c5e9063a98f2816c07e6419c9a67e6130987c8d00eae73  query_s57_w11_t10.drat
```

`MANIFEST.sha256` checks every retained artifact. The uncompressed CNF and
DRAT are intentionally omitted from this compact bundle; `decompressed.*`
records the independently regenerated hashes.

This is a certificate-backed exclusion for one fixed prefix/suffix window of
one 77-comparator network, not a global lower bound and not evidence that no
76-comparator network exists.
