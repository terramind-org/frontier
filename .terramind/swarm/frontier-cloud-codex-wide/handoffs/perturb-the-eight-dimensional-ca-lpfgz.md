Outcome: done

## Done

- Recovered corrected PR 87 / `b50db48a` and independently rebuilt batch 32 from the original fixture and recorded point IDs. The 512-point fixture (`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`) again passed Frontier diagnose and ties the known value.
- The reconstruction asserts slice sizes `192/160/160`, an unchanged frozen slice 0, 392 fixed plus 120 optional baseline points equals 512, 155 variables, and target 121 equals total 513. It independently enumerated 11,948 line constraints; planted baseline and a 256-assignment direct-versus-encoding control passed.
- Wrote a complete DIMACS encoding (5,931 variables including counter auxiliaries; 11,672 clauses). CaDiCaL returned UNSAT in 0.29 seconds, emitting LRAT with internal checking. A separate DRAT proof was accepted by separately built drat-trim (`s VERIFIED`), with proof and checker outputs retained independently. This is a proof-backed negative result for this exact batch-32 CNF.
- Ran a new mixed-slice batch: 16 anchors from each mutable slice, chosen by alternating slices and favouring recurring mutable blocker endpoints. All 32 anchors survived full screening; it deleted 147 points in slice 1 and 101 in slice 2, retaining frozen slice 0, and exposed 115 and 450 safe insertions. Baseline, planted, and 256-assignment controls passed.
- The mixed model (813 variables, 294,873 line constraints, 264 fixed points, target 249) reached its externally enforced 480-second HiGHS deadline without a witness or proof. It is explicitly `TIMEOUT`, not UNSAT. No candidate existed for Frontier validation.
- Saved source, semantic constraints, CNF, LRAT/DRAT proof files, external checker result, screens, raw logs, hashes and cursors under `.terramind/swarm/frontier-cloud-codex-wide/search/cap8-proof-sat-batch32/` and `cap8-mixed-anchor-batch32/`. `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- Built CaDiCaL and drat-trim in disposable cloud `/tmp` directories because no proof-producing SAT backend was installed. Only the portable instance/proof/checker artifacts are committed.
- The timed mixed instance was not converted to CNF because it produced neither a candidate nor an UNSAT claim.

## Concerns

- The checked proof covers only the recorded corrected batch-32 pool, not a general cap-set bound.
- The mixed-slice family remains unresolved; its broad screen leaves many insertions after 248 deletions.

## Follow-ups

- Replay a smaller balanced mixed-slice prefix and send any UNSAT instance through the saved CNF/LRAT pipeline.
- Retain the frozen-slice, partition, target, planted, and small-control assertions in all future pool experiments.
