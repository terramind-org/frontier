Outcome: done

## Done

- Recovered the c16 evidence (`21b93686`) and closed its completed work without replay: 32,768 seeded greedy restarts / 256 neighborhoods and all 53,173 frozen-core domains. Revalidated the unrestricted c9 pool: 713 points, pool SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, and 20,907 triples (line-list SHA-256 `1a46c9344de5f3298635bc8b143bf859ccd663d04302392bb141eb728b668f2f`).
- Inspected the prior PR 101/Sinz configuration and generated a genuinely different unrestricted DIMACS model: a Batcher bitonic sorting network over the 713 selection bits plus 311 forced-false pads. The target-237 CNF has 57,344 variables and 190,179 clauses; reproducible CNF SHA-256 is `2174533afff4224984d090e16f6491bc8e5ccb27b498f016a86e8733c3d28fe2`.
- Direct controls passed: a non-vacuous collinear triple rejects three selections but accepts two; independent brute-force small enumeration agrees; the planted CF-236 assignment satisfies every line and network clause, passes threshold 236, and fails threshold 237. Frontier diagnose of CF-236 exited 0 (valid, 236, tied best known).
- Built CaDiCaL 2.1.3 and drat-trim locally from recorded source hashes, then ran the full unrestricted target on one pinned cloud CPU with a 950-second external cap / 930-second solver cap. The run was stopped after 135 seconds because its incomplete DRAT trace reached 247 MiB. It produced neither SAT witness nor UNSAT result. The partial trace was discarded; no certificate is claimed. The full-pool >=237 query is explicitly unresolved.
- Retained compact reproduction evidence only: encoder, metadata, manifest, solver log/status and validation logs. `bun run check` exited 0: 434 passed, 1 skipped, 0 failed.

## Deviations

- The intended 950-second wall allocation was ended early at 135 seconds to honor the no-oversized-partial-proofs constraint after the incomplete proof trace grew to 247 MiB. This is an unchecked interruption, not a solver conclusion.
- CaDiCaL and drat-trim were absent from the image, so they were built from their upstream source archives; their exact archive hashes are in `raw/c17/manifest.json`.

## Concerns

- No 237-point witness and no complete independently checked UNSAT certificate exists from this run. Neither the proof trace nor a bound is retained or asserted.
- The old restricted families are exhausted but do not decide the unrestricted model; this new global run also remains unresolved.

## Follow-ups

1. Resume only with a proof-capable solver configuration that can retain a complete, independently checkable certificate within storage limits, or a model-producing solver that emits a 237-point witness.
2. If an UNSAT result is obtained, regenerate this exact CNF and check the complete proof independently with drat-trim before making any global claim.
