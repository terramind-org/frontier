Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c12` from c10 and recovered original c11 commit `1cc42689` by cherry-picking its reachable object. The primary c11 suffix artifact is present with SHA-256 `072b49fb84188c1f8324b230e199d2d0d1359a500dfbcff4b1d8f68c404826d0`; no reconstruction was substituted for it.
- Reverified the fourth fixture `57e68639f884e6ccf769367b37f9ac103f9df5c41b55f455f9ad63845e00299a`, encoder `7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`, lexicographic tuple order, exhaustive encoder/scanner control, planted reconstruction, prior color-swap-aware inequivalence evidence, and the joined prefix 0–10,446.
- Preserved the c11 timeout at index 10,447 (`[22,30,33]`) and retried only that tuple for 120s: UNSAT in 0.3813294380015577s with 1,994 decisions (retry hash `d7810e7323320d5a15f65231b6344d32ce37694792cb3cd37f8f0a1e9f69121b`). c12 controls passed (hash `0a98cbd579e07eb369c70694e9ca0563e0394ab256ed4eadeab90b9fecccb23e`).
- Ran only fourth-seed indices 10,448–11,479 on CPU 0 with atomic per-tuple checkpoints: 1,032 UNSAT, 0 timeout, 0 SAT in 372.0919919680018s and 2,026,410 decisions; suffix hash `67717050932f26f127673b3f977e522f66469704be99f1a2e0275e9aaf0cdf6f`.
- Audit of c9, c10, recovered c11, c12, and both separate retries gives all 11,480 fourth-seed triples final UNSAT exactly once, no gaps, no duplicates, no unresolved tuple, and no SAT graph. Frontier `diagnose` and `check` were inapplicable because no candidate existed.
- Pivoted only after exhaustion. Fifth seed is source line 3 of `r55_42some.g6` (source hash `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`), fixture hash `df6906e1f1dcec79b23196a052f41c1eb53f239c76e36c3c9a9ea3d67b295467`, and differs in degree sequence from each of the four prior seeds and their color-swapped complements. Its control passed; bounded independent indices 0–3,046 yielded 3,047 UNSAT, 0 timeout, 0 SAT in 1,100.2294532849992s and 5,992,163 decisions. Fifth result hash: `34dbd8e323fcc640c6e726731f310e902b8e86218f87f47535eafe0b8fea0467`; first unvisited cursor is 3,047.
- `bun run check` passed: 434 tests passed, 1 skipped; validation reported 18,618 problems and 0 attempts. No attempt, submission, declaration change, push, PR, or merge was made.

## Deviations

- Restored `python-sat==1.9.dev23` in a temporary virtual environment because the fresh sandbox lacked PySAT. The isolated c12 selector script records the fifth-seed provenance and inequivalence evidence.

## Concerns

- These searches only exclude the tested frozen-39-core/four-insertion families; they do not determine `R(5,5)`.
- Fourth seed is exhausted, but fifth-seed indices 3,047–11,479 remain unvisited. Declarations remain false and publication remains pending human approval.

## Follow-ups

1. Resume the fifth fixture at `--start 3047`, preserving atomic per-tuple outcomes and any timeout separately.
2. Immediately validate any SAT candidate with disposable Frontier `diagnose` and `check` before any claim.
3. Pivot again only after fifth-seed exhaustion, with source, fixture, encoder, ordering, and color-swap-aware inequivalence hashes recorded.
