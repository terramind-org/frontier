# c7 audited exterior sorting-window query

This bundle pins `baseline.json` (its SHA-256 is in `SHA256SUMS`) and asks
whether the eleven baseline comparators at indices `[53,64)` can be replaced
by ten comparators.

Before encoding, `window_cegis_artifacts.py` independently enumerates every
reachable prefix state over all 262,144 binary inputs with vectorised and
scalar comparator evaluators.  It then fails closed unless the actual set
passed to `constrain` is identical to that independent image.  This run
recorded 120 states in each set with digest
`dd23ade8025422f11898342f16c32de9e60e370b531033d86c53d642dd8e29a0`.

The complete initial CNF has 28,590 variables and 1,279,267 clauses.  One
CPU, under an external 600-second deadline, returned UNSAT in 243.499
seconds (supervisor exit 0).  Independent `drat-trim` replay reported
`s VERIFIED` in 204.421 seconds (exit 0).

The raw CNF and trace are intentionally omitted.  The lossless compressed
CNF and individually hashable proof chunks can be reassembled and checked
with:

```sh
cat parts/query_s53_w11_t10.drat.gz.part-* > query_s53_w11_t10.drat.gz
sha256sum -c SHA256SUMS
sha256sum query_s53_w11_t10.drat.gz
gzip -dc query_s53_w11_t10.cnf.gz | sha256sum
gzip -dc query_s53_w11_t10.drat.gz | sha256sum
```

`raw.sha256`, `compressed-proof.reassembled.sha256`, and the regenerated
decompressed digest files contain the expected byte hashes.  Every committed
proof chunk is at most 24 MiB.
