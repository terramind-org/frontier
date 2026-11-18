# r11 atomic deterministic continuation

This batch resumes the 12-anchor mixed-slice search at seed 189. It retains
the 264 fixed points, 813 optionals, 248 selected planted optionals, cached
evaluator, and strict integer gate `125 * eligible > 60 * deletions`.

Each seed ran in an independent `taskset -c 0` Python invocation with a
75-second solver allowance. Every invocation loaded every r1--r10 ledger and
the earlier r11 checkpoints before it could invoke the restricted solver.
The atomic `seed-N/` directory holds the ledger, raw timestamped log, and
SHA-256 sums.

Seeds 189--196 all cleared the yield screen but matched an earlier frozen
assignment, so all eight were `DUPLICATE_PRIOR` and no solver was invoked.
There were no unique restricted outcomes, yield/cardinality prunes, same-run
duplicates, SAT candidates, or timeouts. The highest screened boundary was
seed 196 (201 incumbent deletions, 182 eligible alternatives); it is only a
duplicate and does not alter the best directly verified cap size of 512. No
candidate file was emitted. The first unvisited seed is 197.

The planted/direct baseline is valid. Because every r11 case was skipped
before solving, the inherited direct/planted, exhaustive 256-assignment
encoding, and positive-gain controls were not rerun on a novel case. The
fixture was independently diagnosed with Frontier at 512. These restricted
neighborhood records make no statement about the complete 813-optional pool.
