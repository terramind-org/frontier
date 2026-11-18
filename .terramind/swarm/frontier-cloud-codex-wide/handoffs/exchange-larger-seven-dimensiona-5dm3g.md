Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--exchange-larger-seven-dimensiona-5dm3g-c6` from c5 and read PR 69 through its advertised remote head `de132cd73d2e225927dff8ef13821dc8366c1fd6` (the c5 11-pair experiment). `gh` is not installed in this image, but the remote pull ref and full committed handoff/source were available locally.
- Independently rechecked the recovered CF-236 baseline. `bun frontier diagnose .terramind/swarm/frontier-cloud-codex-wide/raw/cap7_cf236.json --problem witness.cap-set-f3-7 --json` returned valid, 236, ties best known, and no violations. A disposable scaffold with both declarations left false also returned `verified` from `bun frontier check`, value 236. It was moved out of the checkout after checking; no attempt, submission, merge, publication, or declaration change was made. Baseline file SHA-256 is `3b42f2f7a4d9dc372601179611dd6f185418eff7c40c0c67aa1af917c7ff3582`; sorted canonical point-set SHA-256 is `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- Added `cap7_10pair_11delete_search.py` and completed its one-core `taskset -c 0` run with a 1,740-second budget. It exhaustively covered the 24 exactly-10-pair anchors without repeating c4's 10-deletion masks. Per anchor it enumerated 221,184 disjoint kind-A masks (one endpoint from each pair plus one of the 216 vertices outside the 20 pair endpoints) and 5,120 disjoint kind-B masks (both endpoints of one pair plus one endpoint of every other pair): `24 * (221184 + 5120) = 5,431,296` unique exactly-11-deletion cases.
- The full domain completed in 3.517149 seconds: `cases_started=cases_completed=cases_pruned=5,431,296`, `cases_cutoff=0`, `candidate_checks=0`, `solver_nodes=0`, `best_size=236`, `records=[]`, `timed_out=false`. Every case had fewer than the eleven individually compatible extra points required after retaining 225 base points and forcing its anchor, so each was safely pruned before the bounded extension solver. Exact terminal cursor: `{"anchor_index":24,"kind":"done","mask":0,"extra_index":0,"double_pair":0}`.
- The bucket/pruning implementation compares candidate sets to the slow direct predicate for 16 kind-A and 8 kind-B fixture cases; both passed. Its exact decision solver passed a positive three-point independent-set control and rejected target four. `python3 -m py_compile` and `bun run check` passed (434 tests passed, 1 skipped, 0 failed; validator reports 18,618 problems and 0 attempts).
- Preserved sources and raw output: `cap7_10pair_11delete_search.py` SHA-256 `23acfe83510e6e99e33c20e42d6a708d38da9a0b670eeee36ab44563cd28f2ff`; zero-second control `raw/cap7_10pair_11delete_control.json` `9985f7e628cb93dc79c31d55be17a9fa417d9bf4f36d7c82371d42975d0cccd0`; measured result `raw/cap7_10pair_11delete_result.json` `6e274f33a186a60df766c8590930f3c7832b84f7ef85ef8a5a976300706322a5`; raw stdout `raw/cap7_10pair_11delete_stdout.log` `a2472d1dbee0dad57255eb8d00d114f2ea86795804b766bf42b968409945b633`.

## Deviations

- The requested maximum 30-minute run completed exhaustively in under four seconds, so no time cutoff/resume continuation was necessary. The command was foregrounded and pinned to one core with `taskset -c 0`.
- PR 69 was read from its Git remote pull ref rather than GitHub CLI output because this image has no `gh` binary.

## Concerns

- This is a local negative result only for exactly-11-deletion exchanges at the 24 ten-pair anchors of this recovered labelled CF-236 realization. It does not exclude larger exchanges, joint anchor changes, or a distinct 236-point realization.
- No 237-point candidate was generated, hence there was no candidate witness for an independent Frontier verification. The baseline itself received both required checks.

## Follow-ups

1. A distinct search should change the exchange family (for example 12 deletions, multiple forced anchors, or a different 236-cap); both 10-pair/11-deletion forms and the 11-pair minimum form are now exhausted for this baseline.
2. Retain the exact cursor and direct-fixture tests if extending any branch; record solver cutoffs separately from mathematical prunes.
