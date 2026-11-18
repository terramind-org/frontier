# r9 atomic deterministic continuation

This batch resumes the 12-anchor mixed-slice search at seed 173. It uses the
same 264 fixed points, 813 optionals, 248 selected planted optionals, cached
evaluator, and strict integer screen as r8: `125 * eligible > 60 * deletions`.

Each seed was run as an independent `taskset -c 0` Python invocation with a
75-second solver cap and written to `seed-N/ledger.json` before the next seed
started. Each invocation loaded the r1--r7 ledgers, r8 seeds 165--172, and all
completed r9 ledgers as `--prior-ledger` inputs. `run.log` holds raw stdout and
start/finish timestamps; `SHA256SUMS` hashes both durable files.

Inputs: fixture SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`,
mixed-pool screen SHA-256 `7ed2e8b2a4caec32f242a60d461f2d41df706df5ba8d23109997c88d17260bac`,
and evaluator SHA-256 `171732ef571287fa4e783c2ebb65d76deab3ed446184e4bb40ff60242af34e13`.

Seeds 173 and 175 were novel exact restricted UNSAT cases. Seeds 174 and
176--180 were deduplicated against prior fingerprints before solver work. No
case was pruned, timed out, or SAT. The two novel cases passed the planted and
direct scanner controls, all 256 small direct-versus-encoding assignments with
zero mismatches, and the positive-gain toy control. No candidate file was
emitted. The first unvisited seed is 181 and the best directly verified cap
remains 512. Restricted results do not imply anything about the full
813-optional pool.
