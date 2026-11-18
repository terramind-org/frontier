Outcome: done

## Done

- Audited PR 83 commit `434aab18` directly against the original FunSearch fixture (`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`). Frontier diagnose again accepts the 512-point baseline for `witness.cap-set-f3-8` and reports a tie with the known value.
- Reconstructed all six historical pools from the actual `cover_steps` point IDs, rather than the incomplete `delete_b`/`delete_c` summaries. All pools have a valid fixed set, complete partition, surviving selected anchors, exact `>=513` target, and passed direct line checks. Batches 1, 2, 16, and 32 did delete frozen-slice points (respectively 4, 8, 32, and 8); their prior claims to retain slice 0 are retracted. The batch-32 arithmetic was encoded correctly but narrated incompletely: 120 total deletions, 392 fixed, and target 121, not 112/400/113.
- Corrected the endpoint-cover code so frozen-slice IDs can never be chosen, then reran batches 1/2/4/8/16/32. They have immutable-slice deletion count zero; the corrected batch 32 uses 64 deletions in slice 1 and 56 in slice 2 (120 total), 392 fixed points, 23+12 screened insertions, 155 variables, 11,948 exact affine-line constraints, and target 121 (`fixed + target = 513`). The primary HiGHS PB encoding returned UNSAT in 0.032554 s.
- Every corrected instance has a valid 512-point planted baseline and an exhaustive 256-assignment direct-versus-clause control with zero mismatches. An independent generic Boolean DPLL/cardinality solver also proves corrected batches 1, 2, and 4 UNSAT. Its 180-second batch-32 run reached 62,497 nodes / 31,231 conflicts and timed out, so it is explicitly not an independent full proof of that batch-32 UNSAT result.
- Retained code, raw logs, pool screens, clauses, controls, input hashes, solver outputs and resume cursors under `.terramind/swarm/frontier-cloud-codex-wide/search/cap8-anchor-deletion-sat/`. Key SHA-256 values: audit `b776258b3c55c580809959314e5ed4e404deefccd6e0ebdcdce4bdea8132dd10`; corrected batch-32 primary result `d09b25ea13572176b152b9581895f5ca2cdab023849e739b2f35942985081649`; independent result `4529b0096828277299678e7830c5ae7d517d8dd6d43a8c1315d2748aac3c803c`.
- Ran `bun run check`: 434 passed, 1 skipped, 0 failed. No positive candidate was found, so no candidate witness check was applicable. No attempt, submission, merge, or declaration change was made.

## Deviations

- The conditional mixed-slice anchor family was not started: correcting and independently cross-checking the prior exclusion consumed the available one-core experiment window. This avoids presenting a second family without its required controls.

## Concerns

- The corrected batch-32 UNSAT conclusion is corroborated by controls but not by a completed independent full solver run; treat it as a single-backend bounded negative result, not a proved exclusion.
- The historical fixed-layer assertion was false in four of six pools. Their frozen-layer interpretations must not be reused; only the recovered raw pool facts remain valid.

## Follow-ups

- Build a deterministic anchor batch seeded in both mutable slices and optimize shared mutable blocker endpoints, then apply the corrected immutable-slice guard.
- Cross-check corrected batch 32 with a standalone SAT/PB proof-producing solver before relying on its UNSAT classification beyond search guidance.
