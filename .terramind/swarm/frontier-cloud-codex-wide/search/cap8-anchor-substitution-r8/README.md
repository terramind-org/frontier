# r8 atomic recorded-order continuation

This continuation resumes r7 exactly at
`(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae,
2187, 2360)`, with the original generator seed cursor still parked at 197.
It loads all recorded witness-neighborhood ledgers, substitution r1--r6
ledgers, and r7's 249 atomic case files before any restricted solver call.

The CPU-0 run retained 54 atomic classifications before its deliberate
cutoff: 42 `DUPLICATE_PRIOR`, 2 `DUPLICATE_RUN`, and 10 exact restricted
`UNSAT`; it had no prunes, timeouts, or SAT candidates.  The ten novel
restricted neighborhoods have planted/direct validity and zero mismatches in
the exhaustive 256-assignment clause control.  The evaluator's positive-gain
control passes.  No 513-point witness was decoded.

The r8 cursor probe loads the r8 atomic files as prior work, replays only the
last durable identity without solver entry, and establishes the exact next
valid stream item as `(734ade9f..., 2187, 3464)`.  The independently
diagnosed fixture remains a valid 512-cap; these restricted-neighborhood
results do not settle the full 813-optional pool.
