# r8 atomic cutoff

The CPU-0 continuation started at `2026-11-18T19:15:16Z` from r7's first
unvisited identity `(734ade9f..., 2187, 2360)`.  It was deliberately stopped
after durable atomic case `0054.json`; no aggregate ledger is presented as a
complete batch.  All completed classifications are therefore represented by
their individual files in `cases/`.

The 54 durable records comprise 42 `DUPLICATE_PRIOR`, 2 `DUPLICATE_RUN`, and
10 restricted `UNSAT`, with no prune, timeout, or SAT classification.  The
last durable record is `(734ade9f..., 2187, 3463)`.  A one-item CPU-0 cursor
probe, loading both r7 and r8 atomic cases as deduplication inputs, classified
that already-durable identity as a prior duplicate and reconstructed the next
valid, compatibility-filtered item in recorded order as
`(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae,
2187, 3464)`.

The original generator cursor remains parked at 197.  The fixture SHA-256 is
`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; the
cached screen SHA-256 is
`7ed2e8b2a4caec32f242a60d461f2d41df706df5ba8d23109997c88d17260bac`.
