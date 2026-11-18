Outcome: done

## Done

- Recovered `1952c132` and verified its unchanged unrestricted pool and compact CNF: 713 points, 20,907 triples, pool SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, sorting-network target-237 CNF SHA-256 `2174533afff4224984d090e16f6491bc8e5ccb27b498f016a86e8733c3d28fe2`, 57,344 variables and 190,179 clauses. The prior 32,768 greedy restarts and 53,173 frozen-core domains were not replayed.
- Added model decoding plus a full DIMACS/geometry verifier. A planted, separately fixed 236-control model decoded as a complete 57,344-variable assignment satisfying its CNF, selecting 236 points, and passed independent line scanning and geometry validity. The unrestricted threshold-236 control itself was also run unfixed for 90.014 seconds but timed out without a witness.
- Ran the unfixed target-237 CNF on one pinned CPU with CaDiCaL 3.1.0 `--sat --seed=18`, proof logging disabled, a 1,300-second solver limit and 1,320-second outer wall cap. It returned exit 0 with `c UNKNOWN`; no SAT model or UNSAT conclusion. The full-pool >=237 query remains unresolved. No Frontier candidate diagnose/check applied.
- Retained command outputs, exit statuses, model/status files, hashes, source and a compact manifest in `raw/c18`. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- The satisfiable decode exercise used a separately planted/fixed 236 control because the unfixed threshold-236 SAT run reached its 90-second cap without emitting a model. No such fixing or assumption was applied to target 237.

## Concerns

- No 237-point witness or checked UNSAT certificate exists. The solver returned timeout/UNKNOWN, not a bound.

## Follow-ups

1. Try a different model-producing solver or configuration on this exact unrestricted CNF; retain and independently validate any model.
2. Treat any future solver-only UNSAT as unconfirmed until a complete proof is independently checked.
