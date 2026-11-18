# c13 audited fixed-window sorting-network exclusion

This bundle records a complete exact search for a 10-comparator replacement
of baseline comparators `[48,59)` in a fixed published 77-comparator
18-wire sorting network.  The prefix and suffix are fixed.

`baseline.json` is the pinned baseline; Frontier diagnosis accepts it on all
262,144 binary inputs.  Its SHA-256 is retained in `input.sha256`.

Before encoding, scalar and vectorised prefix evaluation each produced 218
reachable states.  The set actually inserted into the CNF also contains 218
states.  All three share SHA-256
`0c134f96b179b59392d657ddd20ee5f2cf946f80240651608d4f8d1c66ce7313`.
The full CNF has 52,722 variables and 2,231,801 clauses.

The one-core solver command in `run-s48-w11-t10.command` returned UNSAT
before the 600-second external deadline, with 314.564 seconds remaining.
The independent `drat-trim` command in
`query_s48_w11_t10.drat-trim.command` exited 0 in 196 seconds and its log
ends with `s VERIFIED` (checker time: 195.692 seconds).

This compact recovery bundle intentionally stores the proof only as numbered
chunks. Reassemble the lossless compressed proof with:

```sh
cat parts/query_s48_w11_t10.drat.gz.part-* > query_s48_w11_t10.drat.gz.reassembled
sha256sum -c SHA256SUMS
gzip -dc query_s48_w11_t10.cnf.gz > query_s48_w11_t10.cnf
gzip -dc query_s48_w11_t10.drat.gz.reassembled > query_s48_w11_t10.drat
sha256sum query_s48_w11_t10.cnf query_s48_w11_t10.drat
```

The expected raw CNF and DRAT digests are respectively
`020fd77ae28edd952d83f861dc61181d530bb4aacfc6b51bfe0a99e520e633eb` and
`e824a7f526bd2f95c2e993a9b299987c11f5f6244c5fb4f6346f244ac6859085`.
The compressed proof reassembly digest is
`2f70baaebd553cdfeb774f10071ec7886d603a0c657ee1c51dfe075442651850`.

The original completed c13 commit was
`bcb02c4d2b7eff796c013b4f62aa4159b96b557a`. It also tracked the identical
131,360,533-byte compressed proof as `query_s48_w11_t10.drat.gz`; that object
exceeds GitHub's 100 MiB file limit and caused transport rejection. The
original commit remains reachable locally from
`swarm/frontier-cloud-codex-wide--resynthesize-interior-sorting-ne-ve95w-c13-recovery`.
This clean descendant starts from published c12 (`209a9d68`) and replaces that
oversized blob with the hash-checked chunks above. The compressed CNF is
8,129,401 bytes, below that limit, so it remains a single object.
