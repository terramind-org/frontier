# r5 recorded-order single substitutions

This second disjoint continuation begins at r4's exact next-item cursor
`(ed3a9b5b..., 2187, 3651)`, still in recorded-stream order and with the
original generator parked at seed 197.  It uses all r1--r11 neighborhood
ledgers and r1--r4 substitution ledgers for frozen-assignment deduplication.

The CPU-0 batch atomically checkpointed 48 cases.  All were prior duplicates
before solver invocation; there were no prunes, within-run duplicates,
restricted SAT/UNSAT results, or timeouts.  The next unvisited item is
`(ed3a9b5b..., 2187, 2340)`.  `ledger.json` has SHA-256
`1162ea94855279a847be8525bac5924e056e3b3b2bbd5d48e58c495203a3ef19`.

The fixture diagnosis reports a valid 512-cap tying the known value.  The
ledger's planted/direct and positive-gain controls pass; no 513-point
candidate exists to diagnose or check.
