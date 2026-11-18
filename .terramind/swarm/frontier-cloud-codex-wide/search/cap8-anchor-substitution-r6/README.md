# r6 recorded-order continuation

This CPU-0 continuation begins at r5's next-item cursor
`(ed3a9b5b..., 2187, 2340)` and keeps the original seed generator parked at
197.  It loads all r1--r11 neighborhood ledgers and r1--r5 substitution
ledgers before solving.  The 192 atomic cases ran from 18:46:56Z to
18:50:45Z (229 seconds); all are prior frozen-assignment duplicates, so no
solver was invoked.  The next item is `(ed3a9b5b..., 2187, 4133)`.

`ledger.json` has SHA-256
`220b3d865ac85b71b65e90a184398a6389a12f5ba68a889d36d2062ae0773228`.
The strict yield gate and all construction invariants held for every retained
case.  The 512-point fixture is independently valid; no 513-point candidate
was produced.
