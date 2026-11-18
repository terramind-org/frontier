Outcome: done

## Done

- Recovered original commit `694d2715` directly from the local object database and restored its c12 artifacts. The fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`; recovered `c12-run/resume-16972.json` SHA-256 is `ffb22d5efb17304548cc29d359d3c2457141a6e3dbb0d977f771ce4b886caf26`. This is primary committed evidence, not transcript-only recovery.
- Re-ran the c13 asymmetric and planted controls. The encoder uses positive literals to forbid colour-0 K4s and negative literals to forbid colour-1 K6s. Its exhaustive control covers 14 variables and 16,384 assignments; the planted reconstruction matches the fixture and has forbidden counts `[0,0]`. Frontier diagnose accepts the baseline at value 35, tied with the known value; declarations remain false.
- Audited c4--c12 before resuming: 18,988 stored records cover every lexicographic `itertools.combinations(range(35), 4)` index 0--18,987 exactly once, all UNSAT; index 18,988 is `[3,11,18,19]`. The full domain is C(35,4)=52,360, indexed 0--52,359.
- Ran the sole guarded cloud CPU from `--start 18988`, with one second per formula, a unique `c13-run/` output directory, O_EXCL single-writer lock and atomic JSON replacement. `c13-run/resume-18988.json` (SHA-256 `69c991fed296868e19c37bf58d5ca0bbb3e206d46d306930dc968e8f2a417c55`) and raw log (SHA-256 `19c4c5ae4accafb6dfca7fb4921c9733b7e90ef0abd1c1d416248baa0a523b44`) record 1,931 tuples, indices 18,988--20,918: UNSAT=1,931, SAT=0, UNKNOWN/timeouts=0. It exited normally after 1,380.565 seconds and removed its lock.
- Audited all lane/c4--c13 JSON outputs together: 20,919 records cover indices 0--20,918 exactly once, with no duplicate, gap, or tuple mismatch. The exact first unvisited cursor is 20,919, tuple `[4,5,6,31]`. No SAT candidate arose, so candidate-specific Frontier diagnose/check was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

- The controller returned immediately after launching the production command, but the original PID and O_EXCL lock remained live. I verified that PID and observed only its atomic checkpoint; no replacement writer was started.

## Concerns

- Only labelled tuples 0--20,918 of this one Exoo 35-vertex replacement neighbourhood have been exhausted. The remaining tuples and other base colourings remain unexplored.

## Follow-ups

1. Resume exactly at `--start 20919`, preserving the fixture hash, lexicographic order, one-second timeout, run-specific output directory, atomic checkpoints, and the O_EXCL writer lock.
2. If a SAT model appears, write it to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if access becomes available before changing the search neighbourhood.
