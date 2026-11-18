# c14 exact-rational follow-up

This package recovers c13's completed Sun audit rather than reopening its
seven-term enumeration.  The recovered Sun witness SHA-256 is
`9ee984b5951f000376dbdccbb402fb166b4bd38abc5acc4402b29617a9731b8b` and
the inspected integral screen SHA-256 is
`e01177604eaab6dd1ac401e9d2fada8806aa6543ee60a3da166f7a74e10304b5`.

`rational_sample_sun.py` keeps the predecessor's exact rational linear
algebra but replaces its final *integer* complementary-vector gate with
exact-Q rank-one recovery.  Its synthetic calibration establishes the
distinction exactly:

```
4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1
  = 4e0⊗(e0+e1/2)⊗(e0+e1/2).
```

The old criterion returns no result because its complement has halves; the
new method verifies the identity and returns one rank-one replacement.  The
four input products differ in both factor positions, so this is not a
projective rescaling of an individual summand.

The measured CPU-0 run used only pre-existing low-flattening trace records:
for each Sun neighbour it hashes `sun-q-c14-v1:<neighbour>:<support_index>`
and takes the 32 smallest hashes.  It then tests those 224 selected supports
once with both criteria.  The run took 12.4 seconds (including trace loading),
found no rational replacement, and has a terminal cursor in
`rational-sample-result.json`; hence no rank-22 witness existed to send to
Frontier.  This is a bounded sample, not a tensor-rank lower bound.
