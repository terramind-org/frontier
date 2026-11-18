# c5: complete exterior sorting-window query

This bundle pins the 77-comparator 18-wire baseline with SHA-256
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.

## Complete query `[55,66) -> 10`

The query fixes gates `[0,55)` and `[66,77)` and asks whether the eleven
baseline gates in `[55,66)` can be replaced with ten.  All 104 reachable
prefix states are encoded before the first SAT solve: 24,590 variables and
1,123,571 clauses.  The one-core, externally supervised solver returned
UNSAT after 218.722 seconds (supervisor exit 0).  The independent checker
returned `s VERIFIED` in 67.019 seconds (exit 0).

`run-s55-w11-t10.command` and `query_s55_w11_t10.drat-trim.command` are the
exact solver and checker commands. `SHA256SUMS` hashes every retained input
and proof chunk. Reassemble the proof exactly as follows, then validate both
the compressed stream and decompressed object:

```sh
cat parts/query_s55_w11_t10.drat.gz.part-* > query_s55_w11_t10.drat.gz
sha256sum query_s55_w11_t10.drat.gz
gzip -dc query_s55_w11_t10.drat.gz | sha256sum
gzip -dc query_s55_w11_t10.cnf.gz | sha256sum
```

`compressed-proof.reassembled.sha256` gives the compressed stream digest;
`decompressed.sha256` and the regenerated digest records give the expected
uncompressed byte hashes. Each chunk is at most 25,165,824 bytes. The raw CNF
and trace are deliberately not versioned.

`incomplete-initial-100-state-query/` records an earlier implementation error:
the 100-state query reported UNSAT but is not evidence and is retained only as
a log/control. The corrected source in this bundle iterates over every
reachable state.
