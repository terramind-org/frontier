Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--exchange-larger-seven-dimensiona-5dm3g-c5`, read `AGENTS.md`, and recovered c4 commit `363bcd93` locally. The baseline (`raw/cap7_cf236.json`), c4 exact size-10 search source/result, and prior handoff are recovered byte-for-byte; the new c5 source/result are explicitly labelled as new. The recovered baseline file SHA-256 is `3b42f2f7a4d9dc372601179611dd6f185418eff7c40c0c67aa1af917c7ff3582`; the sorted canonical `{\"points\":...}` serialization SHA-256 is `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- `bun frontier diagnose raw/cap7_cf236.json --problem witness.cap-set-f3-7 --json` reported valid, value 236, ties best known, no violations. A disposable witness scaffold, with both declarations retained as false, also passed `bun frontier check` as a valid 236-point witness and `bun frontier diagnose`; it was moved out of the checkout afterwards. No attempt, submission, merge, declaration change, or publication was made.
- The recovered measured blocker-pair histogram is: 10: 24, 11: 416, 12: 480, 13: 160, 14: 120, 15: 192, 16: 224, 18: 240, 25: 60, 30: 32, 38: 1, 56: 2. Because 416 exactly-11 anchors exist, c5 performed the requested minimum-deletion branch, not the alternate 10-pair/11-deletion branch.
- Added `cap7_11pair_search.py`, an exact deterministic mask-bucket enumerator. For each exact-11 anchor it enumerates the 2,048 one-endpoint-per-disjoint-pair deletion masks, filters every possible second outside point by all of its blocker pairs and by its forced-anchor line, and would run a node-bounded exact independent-set decision solver when at least 11 second points remain. The bucket construction was checked against a direct reference on 32 masks; the solver was checked against exhaustive subsets of a 3-vertex positive-control cap (maximum 3 found, target 4 rejected).
- One `taskset -c 0` CPU experiment with a 1,740-second ceiling completed all `416 * 2^11 = 851,968` cases in 4.588536500930786 seconds. Every case was pruned before solver invocation: `cases_started=851968`, `cases_completed=851968`, `cases_pruned=851968`, `cases_cutoff=0`, `candidate_checks=0`, `solver_nodes=0`, `best_size=236`, `records=[]`, `timed_out=false`. Exact resume cursor: `{\"anchor_index\":416,\"next_mask\":0}`. This gives a local negative result for every minimum 11-deletion exchange around this recovered labeled cap.
- New c5 artifact SHA-256 values: source `cap7_11pair_search.py` `6da9676cb20e78594d0dd6b649964c118b432260eb9406d62b45a63527c1444f`; raw result `cap7_11pair_result.json` `5e03d64cfc2b57988ce7614a4531282aba51f27159f72fdb63b5e26d13412e0b`; zero-second control `cap7_11pair_control.json` `b015a4fc4637a9e1d56810a96b05a9ac95cf188c5de911d5b9615fe90532c9fb`. `python3 -m py_compile` passed. `bun run check` passed: 434 tests passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts.

## Deviations

- The terminal-pane launcher failed before starting a process (`ipcMain.removeListener is not a function`), so the one-core command ran in the foreground with `taskset -c 0`. It finished normally and did not need the remaining time budget.
- `gh` is unavailable in this cloud image, so the temporary local scaffold used the non-submission `local-check` login accepted by Frontier. It was only to invoke the required checker, not credited or retained as an attempt.

## Concerns

- The result excludes only the exact one-deletion-per-pair exchanges for the 416 anchors with exactly 11 blocker pairs of this particular recovered CF-236 realization. It does not rule out 10-pair anchors with 11 deletions, larger/joint exchanges, or a different 236-cap realization.
- No 237 candidate was produced, so there is no candidate witness to independently check with Frontier. The prune is stronger than a solver cutoff here: no case admitted even one additional compatible outside point, whereas eleven were necessary.

## Follow-ups

1. Search the requested alternate 10-pair anchors with exactly 11 deletions, including one deletion outside the pairs and both endpoints of a pair; do not repeat c4's complete size-10 sweep.
2. For any future non-pruned branch, retain the current mask-bucket reference control and exact solver cutoff accounting, and run Frontier check/diagnose on every 237-point witness.
