Outcome: done

## Done

- Recovered the c11/a2e50c59 mixed-pool artifacts from reachable local refs, preserving its original manifest, constraints, CNF, logs, and timeout result. The original partial LRAT remains untracked and is not part of this handoff.
- Reconstructed the same mixed scope directly from the 512-point fixture and recorded screen: frozen slice unchanged; 264 fixed plus 248 optional baseline points; 813 optional variables; 294,873 line constraints; and a 249-selected target for total size at least 513.
- Replaced only the sequential cardinality encoding with a standard Batcher descending bitonic sorting network, padded to 1,024 false inputs. It asserts output 249, exactly expressing at least 249 selected optionals.
- The compact DIMACS has 57,344 variables and 204,206 clauses (SHA-256 `384d289c201609ed4ac05549de68c597de09832c2f69611ed21d4841f41c4dc9`), versus the recovered sequential DIMACS's 547,842 variables and 1,094,306 clauses. This is an 89.53% variable and 81.34% clause reduction.
- Baseline validity, planted-line validity, the 256-assignment direct-versus-line control, and threshold boundaries at 248/249/250 all passed. The compact semantic constraints and audit are retained separately from DIMACS.
- Ran fresh one-core CaDiCaL with LRAT/internal checking requested and a 600-second external deadline. It timed out (exit 124; 588.55 CPU seconds) without SAT or UNSAT. The 5.9 GiB partial LRAT is unverified and deliberately untracked; no candidate exists for Frontier validation.
- Ran `bun run check`: 434 passed, 1 skipped, 0 failed.

## Deviations

- Used the prior cloud-built CaDiCaL binary in `/tmp`; committed replay artifacts are portable, but the binary is not.
- Used a 600-second proof budget rather than the 30-minute ceiling, reserving time for result preservation and handoff after the prior 900-second run also timed out. No old CNF solve was repeated.

## Concerns

- The compact encoding is much smaller but the exact mixed instance remains unresolved. This timeout is not evidence of UNSAT.
- The partial LRAT must never be reused or uploaded as proof; regenerate a proof stream from the retained compact encoder.
- The prior checked proof still applies only to its corrected batch-32 pool, not this mixed pool or a general cap-set bound.

## Follow-ups

- Try a longer fresh proof search or a solver with a different proof-producing core on the compact CNF.
- Replay a smaller balanced mixed-slice prefix through the same frozen-slice, partition, target, planted, and small-control assertions.
