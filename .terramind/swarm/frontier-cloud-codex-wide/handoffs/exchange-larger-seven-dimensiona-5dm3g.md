Outcome: done

## Done

- Recovered `b771e1b4` and regenerated the unrestricted 713-point pool, its 20,907 triples, decoder, and target-237 DIMACS. Its SHA-256 reproduced exactly as `2174533afff4224984d090e16f6491bc8e5ccb27b498f016a86e8733c3d28fe2` (57,344 variables; 190,179 clauses). The 32,768 greedy restarts, 53,173 frozen-core domains, and prior CaDiCaL runs were not replayed.
- Built the distinct model-producing backend Kissat 3.1.1 from upstream `rel-3.1.1` commit `71caafb4d182ced9f76cef45b00f37cc598f2a37` (`./configure && make -j1`; binary SHA-256 `596f52a7d304812702d769e0f9d7bd12a24af4f877325eb665025bb3f0a2448c`). Both runs used `--sat --seed=20`, one CPU via `taskset -c 0`, and no proof output.
- The *unfixed* Kissat threshold-236 calibration reached its separate 90-second wall (exit 124) without a model. A separately labelled **planted** 236 control, with 713 explicit CF-236 selection units, returned SAT in 0.053636 seconds; its complete model passed the full DIMACS scan and decoded to 236 points that passed independent line and geometry checks.
- Ran the verbatim, unrestricted target-237 CNF with zero added clauses and zero assumptions for 1,200.010 seconds. It timed out (exit 124) without SAT or UNSAT; no model, proof, or certificate was produced. The unrestricted >=237 query remains unresolved.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed. Compact regeneration logs, hashes, complete solver stdout, status, decoded planted control, and manifest are in `raw/c20` (the reproducible DIMACS files themselves remain regenerated-by-hash rather than committed).

## Deviations

- The terminal-pane launcher failed before starting the production search, so the same one-core command ran in a managed foreground process with the external wall limit preserved.

## Concerns

- Kissat did not decode an **unfixed** 236 model inside its 90-second calibration allowance; its decoder path is demonstrated only by the clearly separated planted control. Earlier c19 independently decoded an unfixed 236 model with CaDiCaL, but that is not a Kissat result.
- No SAT witness and no independently checked UNSAT certificate exists for the unrestricted query.

## Follow-ups

1. Try another distinct model-producing backend or a materially different documented Kissat configuration on the exact target-237 CNF.
2. Independently scan, geometry-check, and Frontier diagnose/check any future SAT model; treat any solver-only UNSAT result as unconfirmed without a checked certificate.
