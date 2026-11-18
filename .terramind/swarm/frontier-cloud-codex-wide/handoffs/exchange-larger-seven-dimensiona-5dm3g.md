Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--exchange-larger-seven-dimensiona-5dm3g-c7` from c6 and recovered PR 71 through `refs/pull/71/head` (`75867097a72a41012e34383ffdb0ac00b38ded4c`). Its verified CF-236 control, prior one-anchor scripts, raw outputs, and c6 handoff were present.
- Independently verified the recovered CF-236 cap. `bun frontier diagnose .terramind/swarm/frontier-cloud-codex-wide/raw/cap7_cf236.json --problem witness.cap-set-f3-7 --json` returned valid, value 236, tied best known, and no violations. A disposable witness scaffold with declarations left false returned `verified` from `bun frontier check` at value 236; it was removed afterwards. Baseline file SHA-256: `3b42f2f7a4d9dc372601179611dd6f185418eff7c40c0c67aa1af917c7ff3582`; canonical sorted point-set SHA-256: `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- Added `cap7_twoanchor_12delete_search.py`. The selected, deterministic pair domain was all `C(24,2)=276` lexicographic pairs from the previously measured 24 outside points with the smallest individual blocker count (10). For each pair it unions both blocker matchings, forces deletion of the pair line if that third point is retained, and computes the exact cover lower bound component-by-component (the union has maximum degree two). The direct exhaustive cover fixture agrees with the degree-two bound; a planted three-addition extension control succeeds and an impossible four-addition control fails.
- Ran the one-core command `taskset -c 0 env PYTHONPATH=.terramind/swarm/frontier-cloud-codex-wide python3 .terramind/swarm/frontier-cloud-codex-wide/cap7_twoanchor_12delete_search.py --seconds 1740 --out .terramind/swarm/frontier-cloud-codex-wide/raw/cap7_twoanchor_12delete_result.json`. It completed exhaustively in `0.440947` seconds with no cutoff and terminal cursor `{"pair_index":0,"cover_index":0,"state":"done"}`. Exact required deletion-cover histogram: 120 pairs require 16 deletions, 144 require 20, and 12 require 21; therefore all 276 were filtered, no size-12 hitting sets exist in this selected domain, and none reached the 11-further-additions solver. Counts: selected pairs/covers `0/0`, cases started/completed/pruned/cutoff `0/0/0/0`, candidate checks/nodes `0/0`, best size 236, unresolved 0.
- Preserved source, control, result, and stdout: source SHA-256 `b9ffcf04e1cfe07ef9384a0359d4b2432a50d708e37b7929930a1cec64298007`; zero-second control `426ebba69223ee20940c0c88326935f581eab2d8cc2e83fb323b6c497cd6533a`; measured result `ecac32042d210d52eaca27abc05cd44de51a2df1ed19dff89ab9356c7801779c`; stdout `467afcd859c6e54c2b9fd3f75288b4719b8eaad404d3d1f90d0df623dee1b7fc`.
- `python3 -m py_compile` and `bun run check` passed: 434 tests passed, 1 skipped, 0 failed; validation reports 18,618 problems and 0 attempts. No candidate existed for independent Frontier verification. No attempt, submission, merge, local compute, publication, or declaration change was made.

## Deviations

- The selected two-anchor family was exhausted far below the 30-minute cap because its joint blocker lower bounds rule out twelve deletions before enumerating masks. The specified 11-further-additions test was implemented and positive-controlled, but no admissible mask reached it.
- PR 71 was read from the remote pull ref rather than GitHub CLI because `gh` is unavailable in this image.

## Concerns

- This is not a global claim about 12-deletion/two-anchor exchanges: it covers only the 276 pairs in the most favorable (10-blocker) anchor stratum of this recovered labelled CF-236 realization. Pairs with higher individual blocker counts were deliberately not treated as covered.
- The control verifies the cover and extension routines on small cases; the production extension solver had zero invocations because no size-12 cover exists in the selected domain.

## Follow-ups

1. If pursuing two anchors, move to a deletion budget of at least 16 or find a different CF-236 realization; the full low-blocker pair stratum cannot start at 12.
2. Alternatively, select a different exchange family (three anchors or structural moves) and retain the explicit selected-domain and lower-bound reporting.
