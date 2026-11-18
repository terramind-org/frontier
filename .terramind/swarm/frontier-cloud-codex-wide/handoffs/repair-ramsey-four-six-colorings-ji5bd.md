Outcome: done

## Done

- Recovered PR 118's c11 evidence directly from commit `25e9e078`. Its stored `c11-run/resume-14966.json` digest is `95b284adff33cc3253fa759d9dcdf62e0615e58533a205af7a2bbe3892939214`, and the Exoo fixture digest is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`.
- Audited the recovered c4--c11 JSON records: 16,972 lexicographic `itertools.combinations(range(35), 4)` cases cover indices 0--16,971 exactly once, all UNSAT; index 16,972 is `[3,5,11,19]`. The domain is C(35,4)=52,360, with indices 0--52,359.
- Re-ran controls in the fresh c12 output. The asymmetric encoder uses positive literals for forbidden colour-0 K4s and negative literals for forbidden colour-1 K6s. Its exhaustive control covers 14 variables and 16,384 assignments; planted reconstruction exactly matches the fixture and has forbidden counts `[0,0]`. Frontier diagnose accepts the 35-vertex baseline, tied with the known value. Declarations remain false.
- Ran one guarded cloud CPU from `--start 16972`, one second per formula, with an O_EXCL single-writer lock, run-specific `c12-run/` output, and atomic JSON replacement. `c12-run/resume-16972.json` (SHA-256 `ffb22d5efb17304548cc29d359d3c2457141a6e3dbb0d977f771ce4b886caf26`) and raw log (SHA-256 `86661399b4ef4d23185a52fcbf0826ae69afb1abfc722e3f5a378c6da6821bc0`) record 2,016 tuples, indices 16,972--18,987: UNSAT=2,016, SAT=0, UNKNOWN/timeouts=0. It exited normally after 1,380.162 seconds and removed its lock.
- Audited all c4--c12/lane outputs together: 18,988 records cover indices 0--18,987 exactly once, without duplicate, gap, or tuple mismatch. The exact first unvisited cursor is 18,988, tuple `[3,11,18,19]`. No SAT candidate arose, so candidate-specific Frontier diagnose/check was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail.

## Deviations

None.

## Concerns

- Only labelled tuples 0--18,987 of this one Exoo 35-vertex replacement neighbourhood have been exhausted. The remaining tuples and other base colourings remain unexplored.

## Follow-ups

1. Resume exactly at `--start 18988`, preserving fixture hash, lexicographic order, one-second timeout, run-specific output directory, atomic checkpoints, and the O_EXCL writer lock.
2. If a SAT model appears, write it to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if access becomes available before changing neighbourhoods.
