Outcome: done

## Done

- Recovered PR 129 / `0931c35d`, the r1--r10 ledgers, deterministic evaluator and seed ordering, mixed-pool screen, and planted 512-point fixture. The fixture SHA-256 remains `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; independent Frontier diagnose accepts it at 512, tying the known value.
- Continued the 12-anchor mixed-slice search at seeds 189--196 on CPU 0 with atomic checkpoints and unchanged gate `125 * eligible > 60 * deletions`. All eight seed directories have verified `ledger.json` and raw `run.log` checksums.
- Every screened boundary passed the gate, then matched a prior frozen-assignment fingerprint before solver invocation: 189 (201 deletions, 179 eligible), 190 (213, 155), 191 (213, 155), 192 (201, 179), 193 (173, 125), 194 (197, 129), 195 (173, 120), and 196 (201, 182). Counts are 8 prior duplicates; 0 same-run duplicates, yield prunes, cardinality prunes, restricted UNSAT, SAT candidates, or timeouts.
- The recovered baseline/direct and inherited small-encoding and positive-gain controls remain valid. No r11 case was novel, so no candidate was decoded and candidate Frontier check was not applicable. Best directly verified cap size remains 512; first unvisited seed is 197.
- Stored compact reproducibility evidence in `search/cap8-witness-neighborhood-r11/`. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The r6b historical SHA-256 manifest has a stale relative fixture path, so its all-file checksum replay cannot resolve that one path from its directory. Its recorded ledger checksum, the current fixture hash, r7--r10 checkpoint sums, and the r11 sums all verify; no historical artifact was modified.
- All r11 cases were deduplicated before solving, so the direct/planted, 256-assignment encoding, and positive-gain controls were verified on the recovered implementation and baseline rather than rerun per duplicate.

## Concerns

- The deterministic generator is increasingly revisiting previously tested frozen assignments; a wider seed range without a generator change may mostly produce duplicate-only progress.
- Any future restricted UNSAT result applies only to its recorded frozen assignment, not the complete 813-optional pool.

## Follow-ups

- Resume at seed 197 with r1--r11 fingerprint deduplication and the same strict gate; consider a fresh deterministic grouping rule only if it preserves reproducibility and remains distinct from prior neighborhoods.
- Independently scan and run Frontier diagnose and check on any future 513+ candidate before making a claim.
