# r10 atomic deterministic continuation

This batch resumes the 12-anchor mixed-slice search at seed 181. It uses the
same 264 fixed points, 813 optionals, 248 selected planted optionals, cached
evaluator, and strict integer screen as r9: `125 * eligible > 60 * deletions`.

Each seed was run as an independent `taskset -c 0` Python invocation with a
75-second solver cap and written to `seed-N/ledger.json` before the next seed
started. Every invocation loaded r1--r9 ledgers and all earlier completed r10
ledgers through `--prior-ledger`. `run.log` holds raw stdout and start/finish
timestamps; `SHA256SUMS` hashes the durable ledger and log.

Seeds 181--184 and 186--188 were deduplicated against a prior frozen
assignment before solver work. Seed 185 was a novel exact restricted UNSAT
case (197 deletions, 115 eligible alternatives, 312 variables, 46,684 line
constraints). Its planted and direct scanner controls passed; all 256 small
direct-versus-encoding assignments had zero mismatches, and the positive-gain
toy control passed. No case was pruned, timed out, or SAT; no candidate file
was emitted. The first unvisited seed is 189 and the best directly verified
cap remains 512. Restricted results do not imply anything about the full
813-optional pool.
