# c10 complete exterior sorting-window query

This bundle pins `baseline.json` and tests whether the eleven comparators at
indices `[50,61)` of the published 77-comparator 18-wire network can be
replaced by ten comparators while preserving the exact prefix and suffix.

The encoder independently enumerates every reachable prefix state over all
262,144 binary inputs with scalar and vectorised evaluators. It fails closed
unless both sets and the actual set encoded into the CNF are identical. This
query recorded 163 states in each set, with SHA-256
`66d46d069fcc41bfc31825487293203887b3b0a204e0dbac2bc654d8213d67db`.

The complete initial CNF has 39,200 variables and 1,697,280 clauses. Under
the external 600-second, one-core supervisor, CaDiCaL returned UNSAT with
89.132 seconds remaining. Independent `drat-trim` replay exited 0, reported
`s VERIFIED`, and reported a 26.499-second verification time.

The raw CNF and DRAT trace are intentionally omitted. To reconstruct and
check the lossless proof stream:

```sh
cat parts/query_s50_w11_t10.drat.gz.part-* > query_s50_w11_t10.drat.gz
sha256sum -c SHA256SUMS
gzip -dc query_s50_w11_t10.cnf.gz | sha256sum
gzip -dc query_s50_w11_t10.drat.gz | sha256sum
```

`raw.sha256`, `compressed-cnf.sha256`, and
`compressed-proof.reassembled.sha256` state the expected raw and compressed
byte hashes. Every retained proof part is at most 24 MiB.
