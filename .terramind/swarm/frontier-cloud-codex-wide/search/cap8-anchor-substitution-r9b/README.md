# r9 atomic recorded-order continuation

This CPU-0 continuation resumes the r8 cursor exactly at
`(734ade9f7438dc97e899e1a70bfd44b899a119badff06537dbf0159c141ca0ae,
2187, 3464)`.  It loads every available original witness-neighborhood ledger
(r1--r11), substitution r1--r6 aggregate ledger, and all r7/r8 atomic cases
before any restricted solver call.  The original seed generator remains
parked at 197.

The matching 264-fixed/813-optional mixed-pool screen has SHA-256
`7ed2e8b2a4caec32f242a60d461f2d41df706df5ba8d23109997c88d17260bac`;
the evaluator has SHA-256
`52e21e4ade6c47af3d129ae101e77a767018a72a39e6b2f94e5ee17f2493c836`.
The planted 512-point fixture has SHA-256
`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`
and independently diagnoses as valid.

The 96 durable atomic cases comprise 81 `DUPLICATE_PRIOR`, 3
`DUPLICATE_RUN`, and 12 exact restricted `UNSAT` outcomes.  There were no
prunes, timeouts, or SAT candidates.  The novel cases preserve the mixed-slice
and strict `125 * eligible > 60 * deletions` conditions and pass the
planted/direct, exhaustive 256-assignment encoding, and positive-gain
controls.  No 513-point witness was decoded.  The next exact valid item in
recorded order is `(734ade..., 2187, 3220)`.
