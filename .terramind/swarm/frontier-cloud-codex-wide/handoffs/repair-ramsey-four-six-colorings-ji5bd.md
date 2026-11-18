Outcome: done

## Done

- Recovered PR 151's committed c15 evidence from `086c7cd3`. The Exoo fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`; prior c15 result SHA-256 is `bed2473e54dae7d6a95f266b92aebb8bad9bd12b03c3ec82dfc70bc8fc78bb04`.
- Audited all lane/c4--c15 JSON before continuing: 24,887 records cover every lexicographic `itertools.combinations(range(35), 4)` index 0--24,886 exactly once, all UNSAT; index 24,887 is `[4,26,29,33]`. The full domain has C(35,4)=52,360 labelled deletion tuples.
- Re-ran controls in the fresh c16 output. The asymmetric clauses use positive literals to forbid colour-0 K4s and negative literals to forbid colour-1 K6s. The exhaustive 2-core/4-new control covers 14 variables and all 16,384 assignments; planted reconstruction of `[31,32,33,34]` matches the fixture with forbidden counts `[0,0]`. `bun frontier diagnose` accepts the 35-vertex baseline, tying the known value; no declarations changed.
- Ran the sole cloud CPU from `--start 24887` with one second per formula, a unique `c16-run/` directory, O_EXCL single-writer lock, and atomic per-tuple JSON updates. `c16-run/resume-24887.json` (SHA-256 `37bc852df3aef382f42a402ea66949258896f6ed89e8812c47fef06b5b7d01fb`) and its raw log (SHA-256 `21c2c02a44a0f61e1dcc48890630829412d4907969e76a9b9b2fc9d3dde1ac7d`) record 2,021 tuples, indices 24,887--26,907: UNSAT=2,021, SAT=0, UNKNOWN/timeouts=0. The writer exited normally after 1,380.218 seconds and removed its lock.
- Audited all lane/c4--c16 results together: 26,908 records cover every index 0--26,907 exactly once, without duplicate, gap, or tuple mismatch. The exact first unvisited cursor is 26,908, tuple `[5,12,16,27]`. No SAT candidate arose, so candidate-specific Frontier diagnose/check was inapplicable.
- `bun run check` passed: 434 pass, 1 skip, 0 fail; validation reported 18,618 problems and 0 attempts.

## Deviations

- The requested hosted PR 36 inspection could not run because the cloud worker lacks the `gh` executable. The recovery and audit used the reachable committed c15 objects instead. The terminal-pane launcher also errored, so the same single foreground PTY process was used and observed to normal exit; no second writer was started.

## Concerns

- Only tuples 0--26,907 of this one Exoo 35-vertex replacement neighbourhood have been exhausted. The remaining 25,452 tuples and other base colourings remain unexplored.

## Follow-ups

1. Resume exactly at `--start 26908`, preserving the fixture hash, lexicographic order, one-second timeout, run-specific output directory, atomic checkpoints, and O_EXCL writer lock.
2. If a SAT model appears, write it to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if hosted access becomes available before changing neighbourhoods.
