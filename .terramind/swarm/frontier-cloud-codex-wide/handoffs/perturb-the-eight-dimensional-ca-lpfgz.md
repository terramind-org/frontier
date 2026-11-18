Outcome: done

## Done

- Recovered PR 91 / `4a36bb76` and re-verified the 512-point fixture with Frontier: valid, value 512, ties the known value.
- Independently rebuilt the unresolved mixed pool from the fixture and its recorded screen, not the prior PB clauses. Assertions passed: slice sizes `192/160/160`; frozen slice 0 unchanged; 264 fixed plus 248 optional baseline points equals 512; 813 variables; target 249 gives total 513; and exactly 294,873 variable-containing affine-line constraints.
- The regenerated DIMACS has 547,842 variables including counters and 1,094,306 clauses, SHA-256 `9ccc7972116c1c1f0624a7a56efef57853b89eec31fa03e65dcf31ee45fcbbf1`. Direct baseline validity, planted-baseline constraint satisfaction, and all 256 direct-versus-encoding small-window assignments passed.
- Ran one-core CaDiCaL with LRAT and internal proof checks under an external 900-second deadline. It exited `124` on timeout after 900.00 seconds with no SAT/UNSAT verdict. Its 5,037,277,209-byte partial LRAT has SHA-256 `894088ff7385ac5e724d1374d52362d0c74f5b4ca52d491719e7be8d50de9fb5`; it is incomplete and was not proof-checked. No candidate exists for Frontier validation.
- Preserved the reproducible encoder, semantic constraints, CNF, manifest, solver output, hashes, timeout result, and exact restart command under `.terramind/swarm/frontier-cloud-codex-wide/search/cap8-mixed-proof-sat/`. The oversized incomplete LRAT remains local-only and is represented by its size/hash, because it is not a valid proof. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- Used the prior cloud-built CaDiCaL binary in `/tmp`; the committed replay artifacts are portable, but the binary itself is not.
- The partial LRAT is deliberately not committed because it is 4.7 GiB, incomplete due to timeout, and cannot support a proof claim.

## Concerns

- The mixed-slice family remains unresolved. The timeout provides no exclusion and the partial LRAT is unusable.
- The prior checked proof still applies only to its corrected batch-32 pool, not this mixed pool or a general cap-set bound.

## Follow-ups

- Retry this exact instance with a longer proof budget or a more compact cardinality encoding; regenerate rather than reusing the partial LRAT.
- Replay a smaller balanced mixed-slice prefix through the same frozen-slice, partition, target, planted, and small-control assertions.
