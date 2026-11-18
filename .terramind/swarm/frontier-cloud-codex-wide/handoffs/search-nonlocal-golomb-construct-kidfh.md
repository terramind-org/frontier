Outcome: done
## Done

Recovered c5 commit `c400fd48` and checked for c6 data before starting: no c6 script, checkpoint, reachable git object, or matching Golomb process existed in this fresh restored checkout. Reconstructed the four-delete endpoint-branch experiment in `.terramind/swarm/frontier-cloud-codex-wide/search-nonlocal-golomb-construct-kidfh-c7/` and ran it on one cloud CPU.

The fixture is the checked 29-mark span-623 ruler, canonical seed SHA-256 `14e0bd44eb9199e52b3007138180355bc43efdecd086b3d0807900771bd6286d`. A disposable scaffold retaining false declarations was checked and diagnosed: both report it valid at 623 and tying the known value. The scaffold was deleted afterwards. No span-622 candidate was produced, so no candidate verifier run applies.

Coverage: all 280 inherited negative suffix shifts (cuts 6, 10, 16, 23, 24, deltas `-1..-(gap-1)`) were completed. Endpoint branching recursively chose among the four endpoints of two live equal-difference pairs, deduplicated exact four-delete sets, and enumerated exact-four supersets if conflicts cleared early. It generated 10 deletion sets, all 10 retained distinct-difference 25-mark cores at span at most 622; none cleared conflicts before four deletions. An independent brute-force `C(29,4)` comparison matched the branch output on `(cut,delta)=(6,-1)`, `(6,-2)`, and a nonzero case `(24,-3)` (0, 0, and 1 deletion set respectively).

For every surviving core, the script enumerated every coordinate in `[max(core)-622, min(core)+622]`, including negative/outside coordinates, that could be its first insertion without colliding with core differences. There were 30 such coordinates total; it then checked every four-subset of each core's exact frontier, including all inserted-inserted distances and final span. Actual candidates: 0. The final measured search run exited 0 in 6.709 seconds (`2026-11-18T16:22:05Z` through `16:22:12Z`); it did not consume the 30-minute cap.

Atomic `checkpoint-000.json` through `checkpoint-279.json`, `progress.json`, final `result.json`, raw output, time, controls, script SHA-256, and commands are preserved in the c7 artifact directory. `bun run check` passed: 434 pass, 1 skip, 0 fail; validation reported `ok: 18618 problems, 0 attempts`.

Exact resume cursor: complete for this family — all 280 c4 shifts, all endpoint-branch exact-four deletion sets, and every four-subset of every surviving core's exact single-insertion frontier. The 10 surviving states are cut 24 with deltas `-3,-5,-8,-13,-25,-28,-30,-33,-38,-41`.

## Deviations

The requested c6 process and artifacts were absent rather than merely paused, so the endpoint implementation was reconstructed and independently cross-checked. Bun 1.4.4 was installed because the cloud image did not provide the repository-required runtime.

## Concerns

This exhausts only four-mark repair after the five c4 suffix-shift families, not all span-622 29-mark rulers. The original c6 transcript cannot be recovered from this checkout, so no elapsed-time credit or unverified c6 cursor was taken.

## Follow-ups

Pivot to a distinct two-block compression or internal block-exchange family; retain the same exact coordinate-frontier technique and per-state checkpoints.
