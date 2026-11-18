Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c7` from recovered `05e3f42c`. No attempt, submission, declaration change, push, PR, or merge was made.
- Recovered and matched the alternate McKay fixture (`557b03cb5670af1e1cef2378f13cfb44121e1d46d98df5ef50c30729d43fc28c`), encoder (`7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`), and c6 raw checkpoint (`2ae17f07d95f4495f25f5f5a433716045c9f1b3c937f98b3c0d34c31da3`). Its c7 zero-search control reran exhaustive 262,144-assignment CNF/scanner equivalence and planted reconstruction successfully.
- Ran only alternate-seed indices 10,564–11,479 with the recovered lexicographic ordering on one `taskset -c 0` core. All 916 were UNSAT, with 0 SAT and 0 timeouts; 1,759,127 decisions in 335.49129326599996 seconds. Result `ramsey_c8_alternate_c7_result.json` SHA-256: `39195266cd694ce7ec8bedc4f113a6c072fd4967e4c56abfa0d49365493565c5`.
- Audited all four alternate results: 11,480 classifications, 11,480 distinct indices, no gaps and no duplicates. Thus the selected alternate seed is fully exhausted: all indices 0–11,479 UNSAT.
- Pivoted to source line 1 of the 328-graph McKay source (`067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`). `ramsey_c8_third_seed_probe.py` SHA-256 `4347a7796dca9dcb9626e13b55dd734bdef131e543e4363ec9c6bc7a43020310` records a degree-sequence certificate that the new seed is inequivalent to both Exoo and the exhausted alternate even after color swap; it is independently K5-free. Fixture SHA-256: `f7b6530fc32e2544bd0b37fce3a9d605691254db49027f4514d68cd3f5249135`.
- Repeated the exhaustive and planted controls for the third seed (262,144 assignments, 18 variables/clauses; planted 39-to-42 CNF/scanner reconstruction passed with 12,177 clauses). On one pinned core, 1,200.0470612239997 seconds from index 0 classified 3,395 UNSAT, 1 timeout, and 0 SAT, with 6,746,175 decisions. The timeout is index 3,395 (`[4,16,27]`); it is unresolved, not UNSAT. First unvisited cursor is 3,396. Raw result SHA-256: `e71773e1aa11f7bcc118df2a647469671dd53aa1e91d125a03bad23deaa7333a`.
- No SAT graph appeared, so Frontier candidate `diagnose` and `check` were not applicable. Bun was available; all raw stdout/stderr, fixtures, controls, provenance, and result JSON are retained under `.terramind/swarm/frontier-cloud-codex-wide/`.

## Deviations

- The visible-terminal launcher failed before executing either search (`ipcMain.removeListener is not a function`). Both exact `taskset -c 0` commands instead ran through the managed shell, with exit status 0 and retained raw logs.

## Concerns

- This excludes only the particular frozen-39-core/four-insertion encodings searched; it does not determine `R(5,5)`.
- Third-seed index 3,395 is unresolved due to its eight-second cap, while indices 3,396–11,479 are unvisited. Neither class is UNSAT.
- No candidate arose for independent Frontier validation. Declarations remain false and publication is pending human approval.

## Follow-ups

1. Re-run third-seed index 3,395 with a separately recorded longer cap, then resume unvisited indices from 3,396 using the identical fixture and encoder.
2. If a SAT graph appears, materialize it in a disposable Frontier witness and run `diagnose` and `check` before making any claim.
3. When the third seed is exhausted, select another McKay graph only with a recorded color-swap-aware inequivalence certificate and fixture/order hashes.
