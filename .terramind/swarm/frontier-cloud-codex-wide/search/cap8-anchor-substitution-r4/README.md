# r4 recorded-order single substitutions

This batch resumes the r3 next-item cursor exactly at
`(ed3a9b5b..., 2187, 2674)`, rather than sorting added IDs numerically.  The
original generator remains parked at seed 197.  The deterministic stream,
compatibility and mixed-slice filters, strict `125 * eligible > 60 *
deletions` gate, and all prior-fingerprint inputs are unchanged.

The CPU-0 batch persisted 48 atomic case records.  Every case was a prior
frozen-assignment duplicate before solver entry; there were no prunes,
within-run duplicates, restricted SAT/UNSAT results, or timeouts.  The next
unvisited stream item is `(ed3a9b5b..., 2187, 3651)`.  `ledger.json` has
SHA-256 `18cb50aa26bfe08df9143af301fc90a56192e3d4d82f02f6c7886fd025f21670`.

The ledger retains planted/direct and positive-gain controls.  No candidate
was decoded; the independently diagnosed vendored cap remains valid at 512.
