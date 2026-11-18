Outcome: done

## Done

- Recovered PR 157 / `92749d63`; `raw/c21` manifest and search hashes reproduce, including the CF-236 canonical SHA-256 `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`, the 583-point x1 pool SHA-256 `b5acc3b97539aba8cf1bd37785bca605b9adf357aa041ae92b0567b4f1e9b5d9`, all six domain fingerprints, and saved first-unvisited cursor rank 150/mask 14.
- Revalidated the CF-236 direct F3-line fixture and the planted delete-then-restore exchange control in a fresh preflight. The resumable runner now atomically writes a complete checkpoint after every completed exchange mask.
- Resumed precisely at rank 150/mask 14, without replaying old trials. One pinned CPU completed 12,050 further exact line-checked blocker-hit exchange masks in 1,100.033 seconds: all were heuristic misses below 237, no candidate occurred, and no exact exclusion is claimed. Cumulative c21+c22 work is 21,664 masks, 0 proved exclusions, and best size 236.
- The atomic continuation records its first unvisited mask as rank 338/mask 32. No 237+ cap arose, so Frontier diagnose/check was not applicable to a new candidate. `bun run check` passed: 434 pass, 1 skip, 0 fail. Compact commands, hashes, raw output, and gate log are in `raw/c22`.

## Deviations

- Terminal-pane launching failed; the same one-core bounded command was run in the foreground. The continuation ended at its declared 1,100-second inner deadline, while the outer 1,120-second wall was not reached.

## Concerns

- The unrestricted 713-point >=237 query remains unresolved. No SAT witness, checked UNSAT certificate, or improved full cap exists.
- The fresh x1 pool remains only partially screened: the next unvisited state is rank 338/mask 32. These no-improvement trials are heuristic misses, never impossibility results.

## Follow-ups

1. Resume the x1 schedule at rank 338, mask 32, without repeating its 21,664 completed masks; or use an exact optimizer over this 583-point pool.
2. Directly scan and Frontier diagnose/check any future 237-point candidate before claiming an improvement.
