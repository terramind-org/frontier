# c2-2: certified exterior sorting window

This compact bundle pins the 77-comparator 18-wire baseline used by the
preceding c4-recovery experiment.  Its SHA-256 is
`ec66245d95a80562ca1a14d05e2650267d38c2d7d20d4b74df422d482c2c23bd`.

## Query `[56,67) -> 10`

The query fixes gates `[0,56)` and `[67,77)` of that baseline and asks whether
the eleven gates in `[56,67)` can be replaced by ten.  It lies outside the
certified `[57,68)` window, and therefore is not implied by that certificate
or the later-starting certified windows in the ledger.

`run-s56-w11-t10.command` records the one-core command with a 600-second OS
supervisor.  It exited 0: the complete initial formula had every one of the 96
reachable prefix states, 22,638 variables, and 1,045,867 clauses.  CaDiCaL
reported UNSAT in 290.623 seconds.

`query_s56_w11_t10.drat-trim.command` records the independent replay.  It
exited 0 and reported `s VERIFIED` in 279.613 seconds.  The compressed CNF
and DRAT are lossless: `decompressed.sha256` is the original-object digest,
while the two `*.regenerated.sha256` files record matching digests after
decompression.  The uncompressed inputs are deliberately omitted to keep the
bundle replayable but compact.

The baseline diagnosis again accepts all 262,144 inputs.  This is a
certificate-backed exclusion for the specified fixed prefix/suffix window of
this 77-comparator baseline, not a global lower bound and not a claim about
all 76-comparator sorting networks.
