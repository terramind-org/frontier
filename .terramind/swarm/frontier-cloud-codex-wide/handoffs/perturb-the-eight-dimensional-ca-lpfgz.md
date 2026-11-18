Outcome: done

## Done

- Recovered the original c4 cloud commit `86330891fbd6b0881411c88e7c08d9e213233e09` locally and restored its complete three-layer record under `search/cap8-three-layer/`. This is recovered evidence, not a reconstruction.
- Verified the vendored FunSearch 512-point baseline with Frontier: SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; `frontier diagnose` reports `value: 512`, `valid: yes`, and ties the known value. The captured result is `search/cap8-two-layer-sat/diagnose-baseline.txt`.
- Implemented `search/cap8_two_layer_sat.py`, an exact 0/1 pseudo-Boolean SAT encoding. It freezes all 192 coordinate-0-slice points, freezes 148 points in each remaining slice, and exposes 12 deletable plus 24 deterministic insertable points per mutable slice. Pools use lexicographic deletion seeds, Hamming radius at most 3, and prefilter candidates which already form a line with two fixed points.
- Enumerated every affine line involving at least one variable point, yielding 1,120 constraints over 72 binary variables, with a cardinality constraint of at least 513. The exact single-core HiGHS feasibility solve returned `UNSAT` (not timeout; solver 0.003029 s). The full experiment took 185.390 s because it also exhaustively checked the 256-assignment small control.
- Confirmed planted baseline recovery: the 512-point baseline is valid and satisfies all line clauses. The small-window brute-force/control comparison has 16 feasible assignments in both direct cap checking and clause evaluation, with zero mismatches. Therefore no candidate witness exists in this bounded pool and none was submitted for diagnosis.
- Preserved result, controls, baseline diagnostic, recovered c4 artifacts, script, exact pools, clause hash `c32d5570c7cc8ed16f3d1e340cfe71f42837529d0446e335dd5019ac6744a637`, and resume cursor in `search/cap8-two-layer-sat/`. Current script/result/control hashes are `dabd1623cc5b20608013687c1037e11d199d8c3d217d4e0819c3152d099d1f5e`, `4b599ba6ba93b7fcc6f674ea09667a91120fdc719796a15cc6427be9610ac407`, and `f05c9fc561bdea6d9dbe9f7d0c4f4ce37a65f9c86a0ddc1bf18af05f9e6f0d8f` respectively.

## Deviations

- The fixed deadline was 1,740 seconds, but the exact solver proved the bounded instance infeasible immediately, so there was no reason to consume the remaining cloud budget. The independently exhaustive control consumed the measured 185.390-second total runtime.
- This used SciPy/HiGHS as an exact 0/1 pseudo-Boolean SAT backend because no standalone SAT binary was installed in the cloud checkout. Its input clauses, cardinality target, status, and raw output are retained for replay.

## Concerns

- UNSAT applies only to this deterministic 12-delete/24-insert-per-slice pool while the 192-point layer and 296 other mutable-layer points are frozen. It says nothing about larger two-layer replacements or a cap above 512 generally.
- The candidate prefilter is logically safe only for a fixed pair of points; larger pools will rapidly increase the SAT model and should be run with a recorded deadline and solver status rather than inferred from this result.

## Follow-ups

- Expand deterministic insertion pools before increasing deletion sets, then resume at `{ "pool_hash": "14e5ced4a500c1631227d93fcbeafeb818221a797e027f18a3388c2f17e8c4a5", "deadline_seconds": 1740.0, "next_phase": "expand inserts then deletes" }`.
- Add a certified standalone SAT/PB backend if available and cross-check the first expanded pool against this encoding.
