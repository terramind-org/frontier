Outcome: done

## Done

- Recovered PR 133's c13 evidence directly from checked-out commit `18733a16`. The required c13 result SHA-256 matches: `69c991fed296868e19c37bf58d5ca0bbb3e206d46d306930dc968e8f2a417c55`. The Exoo fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`.
- Audited the stored lanes and c5--c13 JSON records before resuming. They contain exactly 20,919 outcomes for every lexicographic `itertools.combinations(range(35), 4)` index 0--20,918, exactly once and with matching deletion tuples; index 20,919 is `[4,5,6,31]`. The full domain is C(35,4)=52,360, indexed 0--52,359.
- Re-ran controls within the c14 output record. The asymmetric encoder requires a positive literal to break a colour-0 K4 and a negative literal to break a colour-1 K6. Its exhaustive control passed all 16,384 assignments over 14 variables. The planted reconstruction of deleted vertices `[31,32,33,34]` satisfies the CNF, exactly matches the fixture, and has forbidden counts `[0,0]`.
- Ran the sole guarded cloud CPU from `--start 20919`, with a one-second per-formula cap, fresh `c14-run/` directory, O_EXCL single-writer lock, and atomic per-tuple JSON replacement. `c14-run/resume-20919.json` (SHA-256 `f1ac60e7eb25560d916db1c2f6ef464f49b5d251e6c5e309fedfdbbb014edb87`) and raw log (SHA-256 `15fe0a9e57382c9e4ea6e06d03ac65ea92e04b44d29b764691b2328beb8eb64c`) record indices 20,919--22,909: UNSAT=1,991, SAT=0, UNKNOWN/timeouts=0. It exited normally after 1,380.692 seconds and removed its lock.
- Audited all lane/c4--c14 JSON outputs together: 22,910 records cover indices 0--22,909 exactly once, without a duplicate, gap, or tuple mismatch. The exact first unvisited cursor is 22,910, tuple `[4,10,28,29]`. No SAT witness arose, so candidate-specific Frontier diagnose/check was inapplicable. Frontier diagnose accepts the value-35 baseline, tying the known value; declarations remain false. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

None.

## Concerns

- Only labelled tuples 0--22,909 of this one Exoo 35-vertex replacement neighbourhood have been exhausted. The remaining tuples and other base colourings remain unexplored.

## Follow-ups

1. Resume exactly at `--start 22910`, preserving fixture hash, lexicographic order, one-second timeout, run-specific output directory, atomic checkpoints, and the O_EXCL writer lock.
2. If a SAT model appears, write it to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if access becomes available before changing the search neighbourhood.
