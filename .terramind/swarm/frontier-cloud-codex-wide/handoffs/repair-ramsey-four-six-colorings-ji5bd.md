Outcome: done

## Done

- Recovered PR 142 commit `951fc62b` directly from the checked-out history. The Exoo fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`; the committed c14 record SHA-256 is `f1ac60e7eb25560d916db1c2f6ef464f49b5d251e6c5e309fedfdbbb014edb87`.
- Audited the per-tuple lane/c5--c14 JSON before resuming: 22,910 records cover every lexicographic `itertools.combinations(range(35), 4)` index 0--22,909 exactly once, with matching deletion tuples and all prior outcomes UNSAT. Index 22,910 is `[4,10,28,29]`; the domain is C(35,4)=52,360.
- Re-ran controls in `c15-control.json`. The asymmetric encoder uses positive literals to break colour-0 K4s and negative literals to break colour-1 K6s. Its exhaustive control covers 14 variables and all 16,384 assignments. The planted reconstruction of `[31,32,33,34]` satisfies the CNF, exactly matches the fixture, and has forbidden counts `[0,0]`. Frontier diagnose accepts the baseline at value 35, tying the known value; declarations remain false.
- Ran the sole guarded cloud CPU from `--start 22910` for 1,380.296 seconds with a one-second per-formula cap, fresh `c15-run/` output, O_EXCL single-writer lock, and atomic JSON replacement after each tuple. `c15-run/resume-22910.json` (SHA-256 `bed2473e54dae7d6a95f266b92aebb8bad9bd12b03c3ec82dfc70bc8fc78bb04`) and its raw log (SHA-256 `fc68c0c47d91c17e238ae6c93b95398d6f5393484029ff4077fc112e6364cd88`) record indices 22,910--24,886: UNSAT=1,977, SAT=0, UNKNOWN/timeouts=0. The writer exited normally and removed its lock.
- Audited all lane/c4--c15 outputs after the run: 24,887 records cover indices 0--24,886 exactly once, without a duplicate, gap, or tuple mismatch. The exact first unvisited cursor is 24,887, tuple `[4,26,29,33]`. No SAT candidate arose, so candidate-specific Frontier diagnose/check was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

None.

## Concerns

- Only labelled tuples 0--24,886 of this one Exoo 35-vertex replacement neighbourhood are exhausted. The remaining tuples and other base colourings remain unexplored.

## Follow-ups

1. Resume exactly at `--start 24887`, preserving the fixture hash, lexicographic order, one-second timeout, run-specific output directory, atomic checkpoints, and O_EXCL writer lock.
2. If a SAT model appears, write it to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if access becomes available before changing the search neighbourhood.
