Outcome: done

## Done

- Recovered PR 78 / commit `3d7effc347623f9fa6e56a95460cf921e1c5cc8c` and its full 512-cap screen. The vendored baseline is `test/fixtures/witness/cap-set-f3-8-size512.json`, SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`, with slices `192/160/160`.
- Re-verified that baseline through Frontier: value 512, valid yes, ties best known; retained output is `search/cap8-anchor-deletion-sat/diagnose-baseline.txt`.
- Added `search/cap8_anchor_deletion_sat.py`, an anchor-directed replacement experiment. It fully enumerates every nonbaseline point in mutable coordinate slices 1 and 2, enumerates every baseline blocker pair, rejects anchors with an immutable 0-slice pair (there were zero), and selects a deterministic compatible anchor batch by blocker count. It covers all remaining blocker pairs using greedy maximum endpoint incidence (tie: lowest base-3 id), deliberately allowing more than 12 deletions per slice.
- For each batch size 1, 2, 4, 8, 16, and 32, the complete post-deletion mutable slices were screened against every fixed-point pair; `screen.json` records all survivors, exclusions, deletion-cover steps, full coverage statement, and exact anchor list. Every selected anchor survived its chosen deletion pool. Controls passed in all six runs: the 512 baseline is direct-valid, its planted assignment satisfies the encoded clauses, and an independent direct versus clause enumeration over 256 small-window assignments had zero mismatches.
- The strongest completed batch was 32 anchors: 60 deletions in slice 1 and 52 in slice 2 (fixed count 392), with 23 and 12 safe insertions respectively. Its exact full model has 147 variables and 10,752 affine-line constraints, target 121 selected variables (total >=513), and SciPy/HiGHS reported `UNSAT` in 0.029791 s—not a timeout. It is therefore an exact negative result for this bounded deletion cover, not a general bound.
- The deterministic batch ladder also yielded UNSAT for 1 (4 deletions/1 insertion; cardinality), 2 (8/2; cardinality), 4 (24/4), 8 (32/8), and 16 (32/16) anchors. Full counts, raw start/finish events, exact clauses, pool definitions, hashes, and cursor are retained under `search/cap8-anchor-deletion-sat/`.
- Key batch-32 hashes: script `44c9900f1c62c482ffbe1d2ee08e78d704816b657b56e42a6705d9327046aad0`; screen `4968a5b60d8509c4d978344434ccaf363da020fccb94de6c0a38625d268469b3`; clauses `0ae0f671e78c685e77a1ddfec5bbbf287cf6eaea91e8269641409122624e3f6c`; controls `24651e6cdc4675b873549668b1aa505bf33ecce4c09a63c30fa9097653191f40`; result `c16b606be48494cdbe3e8a733d0879de830843eddb5e3e5f287a14ceaf11c812`.
- Ran `bun run check`: 434 passed, 1 skipped, 0 failed. No candidate existed, so no candidate Frontier check/diagnose was applicable. No attempt, submission, merge, or declaration change was made.

## Deviations

- The 32-anchor PB model finished conclusive UNSAT immediately, so the cloud core was used for approximately six minutes rather than its 30-minute ceiling. No fixed-core exhaustion occurred and therefore the conditional alternate deletion pool was not needed.
- No standalone SAT package was present. The exact full instance used SciPy/HiGHS PB; the direct verifier, planted control, and exhaustive 256-case clause cross-check are retained. The prior custom Boolean solver remains available from PR 78 but was not used as a second solver on this enlarged instance.

## Concerns

- The lexicographically lowest blocker-count anchors are concentrated in slice 1. The 32-anchor cover loses 112 baseline points to unlock only 35 screened insertions, so it is a poor net-gain family even though all selected anchors genuinely survive.
- UNSAT only covers the deterministic greedy cover and the six recorded prefix batches with frozen 0-slice. It does not rule out a differently optimized shared deletion cover, deletion of different baseline points, or any cap above 512.

## Follow-ups

- Seed the cover with anchors from both mutable slices and optimize maximum net survivors per deletion endpoint rather than raw blocker count.
- Install or vendor a standalone SAT/PB solver in a future cloud session and cross-check the batch-32 clauses before extending this family.
