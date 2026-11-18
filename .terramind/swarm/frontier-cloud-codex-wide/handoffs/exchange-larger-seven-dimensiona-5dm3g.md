Outcome: done

## Done

- Recovered `205f381f` and the CF-236 fixture. Its canonical SHA-256 is `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`; a disposable declarations-false witness scaffold passed Frontier diagnose and check at 236. The scaffold was deleted afterwards.
- Closed the earlier x0 affine, frozen-core, greedy, and SAT routes without replaying them. Built a distinct x1-hyperplane relative-affine pool: six non-common layer-map domains, 583 points, pool SHA-256 `b5acc3b97539aba8cf1bd37785bca605b9adf357aa041ae92b0567b4f1e9b5d9`. It intersects the old 713-point pool in 315 points and has 268 points outside it, so it is not merely a whole-pool coordinate relabeling.
- The planted baseline and a delete-then-restore positive exchange control passed direct F3-line validation. The new pool used exact line checks and exact one-per-disjoint-blocker-pair masks for each inserted new point, then deterministic new-point-first greedy extensions.
- Ran one CPU for 890.083 seconds: 151 fresh points entered, 9,614 exchange masks completed, every completed trial directly passed the line scan, and all were heuristic misses below 237. Best remained 236. No exclusion proof is claimed; the run stopped at new-point rank 150, mask 14 and has unvisited masks.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed. Commands, map/domain fingerprints, logs, controls, exact cursor, and manifest are in `raw/c21`.

## Deviations

- The bounded exchange pass timed out before all 347 fresh candidates; its cursor explicitly preserves the first unvisited mask. This is a heuristic cutoff, not an exclusion result.

## Concerns

- The unrestricted 713-point >=237 query remains unresolved. No SAT witness, checked UNSAT certificate, or improved full cap exists.
- The fresh x1 pool is new relative to the old aggregate, but only its first 151 ranked new points have received this exchange schedule.

## Follow-ups

1. Resume the x1 schedule at rank 150, mask 14, without repeating its 9,614 visited masks; or use an exact optimizer over this 583-point pool.
2. Directly scan and Frontier diagnose/check any future 237-point candidate before claiming an improvement.
