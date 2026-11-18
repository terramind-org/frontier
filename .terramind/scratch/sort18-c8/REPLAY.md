# c8 complete exterior sorting-window query

This bundle pins `baseline.json` and tests whether the eleven comparators at
indices `[52,63)` of the published 77-comparator 18-wire network can be
replaced by ten comparators while preserving the exact prefix and suffix.

The encoder independently enumerates all reachable prefix states over all
262,144 binary inputs using scalar and vectorised evaluators.  It then fails
closed unless the actual state set passed to the encoder is identical to that
independent image.  This query recorded 121 states in all three sets, with
SHA-256 `215ca982c00343a794bd54a0bad2276bd5d65c487f431ad2ec58a5fa7116daab`.

The complete initial CNF has 29,056 variables and 1,289,646 clauses.  Under
the external 600-second supervisor on one CPU, CaDiCaL returned UNSAT with
exit 0.  Independent `drat-trim` replay exited 0 and reported `s VERIFIED`.

The raw CNF and DRAT trace are intentionally omitted.  To reconstruct and
check the lossless proof stream:

```sh
cat parts/query_s52_w11_t10.drat.gz.part-* > query_s52_w11_t10.drat.gz
sha256sum -c SHA256SUMS
gzip -dc query_s52_w11_t10.cnf.gz | sha256sum
gzip -dc query_s52_w11_t10.drat.gz | sha256sum
```

`raw.sha256`, `compressed-proof.reassembled.sha256`, and the regenerated
digest files state the expected raw-byte hashes.  Every retained proof part
is at most 24 MiB.
