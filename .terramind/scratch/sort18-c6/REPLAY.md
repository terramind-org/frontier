# c6 complete exterior sorting-window query

This bundle pins `baseline.json` (SHA-256 in `SHA256SUMS`) and asks whether
the eleven gates at baseline indices `[54,65)` can be replaced by ten gates.

The encoder independently computes the prefix image twice over all 262,144
binary inputs: once vectorised and once with a scalar comparator evaluator.
It then compares the set actually passed to `constrain` to that independent
image, and raises an error before solving on any mismatch.  The successful
run recorded 113 states on both sides, with set SHA-256
`7314a583fe3ffbd0e26a035707d2038aa4aaa4ba20a610e9af37fce99bd9d4cc`.

The complete initial CNF has 26,796 variables and 1,211,018 clauses.
CaDiCaL returned UNSAT in 272.332 seconds; the 600-second external
supervisor exited 0.  `drat-trim` independently reported `s VERIFIED` in
281.607 seconds (exit 0).

The raw CNF and trace are intentionally omitted.  Reassemble and validate
the lossless trace with:

```sh
cat parts/query_s54_w11_t10.drat.gz.part-* > query_s54_w11_t10.drat.gz
sha256sum -c SHA256SUMS
sha256sum query_s54_w11_t10.drat.gz
gzip -dc query_s54_w11_t10.cnf.gz | sha256sum
gzip -dc query_s54_w11_t10.drat.gz | sha256sum
```

`raw.sha256`, `compressed-proof.reassembled.sha256`, and the two regenerated
decompressed digest files give the expected byte hashes.  Every committed
trace chunk is at most 24 MiB.
