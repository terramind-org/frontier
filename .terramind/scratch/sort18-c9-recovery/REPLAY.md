# c9 complete exterior sorting-window query

This bundle pins `baseline.json` and tests whether the eleven comparators at
indices `[51,62)` of the published 77-comparator 18-wire network can be
replaced by ten comparators while preserving the exact prefix and suffix.

The encoder independently enumerates every reachable prefix state over all
262,144 binary inputs with scalar and vectorised evaluators. It fails closed
unless both sets and the actual set encoded into the CNF are identical. This
query recorded 136 states in each set, with SHA-256
`d0a141e947222e871823ef04ee531b13951af9ee8c2df674ab7b6f75c370b584`.

The complete initial CNF has 32,718 variables and 1,435,347 clauses. Under
the external 600-second, one-core supervisor, CaDiCaL returned UNSAT in
443.376 seconds (156.624 seconds remained). Independent `drat-trim` replay
exited 0, reported `s VERIFIED`, and took 123.025 seconds.

The raw CNF and DRAT trace are intentionally omitted. To reconstruct and
check the lossless proof stream:

```sh
cat parts/query_s51_w11_t10.drat.gz.part-* > query_s51_w11_t10.drat.gz
sha256sum -c SHA256SUMS
gzip -dc query_s51_w11_t10.cnf.gz | sha256sum
gzip -dc query_s51_w11_t10.drat.gz | sha256sum
```

`raw.sha256`, `compressed-proof.reassembled.sha256`, and the regenerated
digest files state the expected raw-byte hashes. Every retained proof part is
at most 24 MiB.
