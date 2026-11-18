Outcome: done

## Done

- Recovered `8d712d0b` and reproduced the unrestricted 713-point pool, 20,907 triples, decoder, and target-237 DIMACS SHA-256 `2174533afff4224984d090e16f6491bc8e5ccb27b498f016a86e8733c3d28fe2` (57,344 variables, 190,179 clauses). The previous 32,768 greedy restarts and 53,173 frozen-core domains were not replayed.
- Added a documented CaDiCaL 3.1.0 C++ API runner using `Solver::phase(lit)` on exactly the 713 selection variables from CF-236. It calls neither `assume` nor `add`, and proof logging is disabled.
- The separately recorded *unfixed* threshold-236 control returned SAT in 0.231 seconds. Its complete 57,344-variable model passes the full DIMACS scan, decodes to 236 selected points, and passes independent line and geometry checks.
- Ran the unchanged, unfixed target-237 CNF on one pinned CPU with the same phase configuration and a hard 1,200-second external wall deadline. It timed out (exit 124) with no model and no UNSAT result; the unrestricted >=237 query remains unresolved.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed. Compact command outputs, hashes, models, and manifest are in `raw/c19`.

## Deviations

- None.

## Concerns

- A phase preference is not a constraint: it demonstrated the intended hint path on 236 but did not produce a 237-point model before the external deadline.
- No SAT witness and no independently checked UNSAT certificate exists for the unrestricted query.

## Follow-ups

1. Try a distinct model-producing backend or a different documented search configuration on the exact target-237 CNF.
2. Independently scan, geometry-check, and Frontier diagnose/check any future SAT model; treat any solver-only UNSAT result as unconfirmed without a checked certificate.
