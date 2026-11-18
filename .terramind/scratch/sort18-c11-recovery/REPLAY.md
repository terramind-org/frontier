# c11 audited exterior-window query

This bundle records one complete fixed-prefix/fixed-suffix query against the
pinned 77-comparator 18-wire baseline.  It is solver evidence only: the
independent DRAT-trim run exhausted its 300-second deadline and did **not**
print `s VERIFIED`.

## Query

The baseline SHA-256 is
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.
It was accepted by Frontier's sorting-network verifier on all 262,144 binary
inputs (`baseline.diagnose.log`).

The command in `run-s49-w11-t10.command` ran `[49,60) -> 10` with seed 4911
under a 600-second external supervisor pinned to CPU 0.  Before solving, the
scalar evaluator, vectorised evaluator, and actual encoded set each contained
204 prefix states with SHA-256
`9dcfd02d6b550a07a72fbf23fb99c94bb1d63d67e3598e1afc4230810b598563`.
CaDiCaL returned UNSAT in 191.986 seconds (supervisor exit 0).

`query_s49_w11_t10.drat-trim.command` records the independent replay command.
Its supervisor exited 124 after 300 seconds.  Consequently the UNSAT result
is not a certified fixed-window exclusion.

## Reassembly and replay

First verify retained objects:

```sh
sha256sum -c MANIFEST.sha256
cat parts/query_s49_w11_t10.drat.gz.part-* > query_s49_w11_t10.drat.gz
sha256sum query_s49_w11_t10.drat.gz
gzip -dc query_s49_w11_t10.cnf.gz > query_s49_w11_t10.cnf
gzip -dc query_s49_w11_t10.drat.gz > query_s49_w11_t10.drat
sha256sum query_s49_w11_t10.cnf query_s49_w11_t10.drat
drat-trim query_s49_w11_t10.cnf query_s49_w11_t10.drat
```

The expected compressed proof digest is
`a345e63e01719fd6932e430662ba8888ea0a8122af02f38f63bdd12a30e0ed69`; the
expected decompressed CNF and DRAT digests are respectively
`b45d2ea1f3e34dd710d6044758590fbe9a87eece72ed08b3698fff5c943eb5aa` and
`052ad0f8701b637fe044b97a809dfebd81116ce2261d78f9699e71440a4734a8`.
Each retained proof chunk is at most 25,165,824 bytes.  Raw CNF and DRAT are
working files and intentionally are not versioned.
