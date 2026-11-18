Outcome: done

## Done

- Created c8 from c7/PR 75 and used its CF-236 control. `frontier diagnose` reported valid, value 236, tied best known, with no violations; a disposable scaffold (declarations false) also returned `verified` from `frontier check`. Baseline SHA-256: `3b42f2f7a4d9dc372601179611dd6f185418eff7c40c0c67aa1af917c7ff3582`; canonical sorted point-set SHA-256: `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- Added `cap7_twoanchor_16delete_search.py`: all 120 lexicographic pairs of 24 ten-blocker anchors with exact union cover 16; exact, de-duplicated minimum covers; cardinality filter; then exact three-uniform collinearity extension. The retained-pair-line deletion is implemented; all 120 selected pair lines are outside this base.
- Brute-force controls passed: forced-path exact covers equal all subset covers (3); F_3^7 planted extension found a valid 2-addition witness and rejected 5 additions (4 brute-force witnesses). This checks that an available but unselected third point is not a false pair conflict.
- One-core command: `taskset -c 0 env PYTHONPATH=.terramind/swarm/frontier-cloud-codex-wide python3 .terramind/swarm/frontier-cloud-codex-wide/cap7_twoanchor_16delete_search.py --seconds 1740 --out .terramind/swarm/frontier-cloud-codex-wide/raw/cap7_twoanchor_16delete_result.json`. It completed exhaustively in 424.950495 seconds. The ten-blocker pair minimum histogram was 120 at 16, 144 at 20, 12 at 21. All 491,520 exact 16-covers (4,096/pair) were cardinality-pruned: completed/pruned/unresolved `491520/491520/0`; extension calls/nodes/cutoffs `0/0/0`; best 236. Cursor: `{"pair_index":120,"cover_index":0,"state":"done"}`.
- Preserved source/control/result/stdout SHA-256: `5aa461e543665274eea09426dfbe2f3036a0273fc712f9186c56f496bddbe54a`; `b41ab3ee9bdc08801e5a0af974feef9e968e6872bbafc33e448bdfe3e2f05fae`; `31db787799d941033467a06d8ee2ebe54792744ffa47003a409fea3287031506`; `bcc89204b9197bfd73dfd5c0c8d25036878d6dd9e98811c49e308cfd8387fcf3`.
- `python3 -m py_compile` and `bun run check` passed: 434 passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts. No candidate existed for independent verification. No attempt, submission, merge, local compute, publication, or declaration change was made.

## Deviations

- The exhaustive run finished in 424.95 seconds, below the 30-minute cap.
- PR 75 was read from `refs/pull/75/head` because `gh` is unavailable.

## Concerns

- This is not global coverage: it covers only the 120 exact-minimum-16 pairs in the low (10-blocker) anchor stratum of this recovered labelled CF-236 realization.
- The cardinality bound eliminated every cover before extension solving; it is not a broader nonexistence result.

## Follow-ups

1. Explore 17+ deletions or a different extension strategy.
2. Try another CF-236 realization or a nonlocal structural move; do not repeat these 491,520 covers.
