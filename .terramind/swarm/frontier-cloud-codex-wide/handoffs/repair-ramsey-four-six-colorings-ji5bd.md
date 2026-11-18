Outcome: done

## Done

- Recovered the committed c8 artifacts (PR 94 state) directly: the Exoo fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`, and c8's raw JSON and log SHA-256 digests match `771e51e87d7d762f701d49b649da2b7971cb0642885033ecd66bf1b5ca2b8f2c` and `9d1bacd3d2f2d72f9fc5f6c937d823db07fd09f3cd9b797e73fd5760bf2c52bf`. Its checkpoint is contiguous through index 10,330.
- Re-ran the asymmetric encoder controls before continuation. Colour-0 K4 clauses contain positive literals (requiring a 1-edge); colour-1 K6 clauses contain negative literals (requiring a 0-edge). The exhaustive control has 14 variables and 16,384 assignments. The planted reconstruction of deleted vertices `[31,32,33,34]` matches the fixture, satisfies the CNF, and has forbidden counts `[0,0]`.
- Ran one CPU for 1,740.590 seconds from `--start 10331`, using `itertools.combinations(range(35), 4)` and exclusive end 52,360. `c9-resume-10331.json` (SHA-256 `96060e946e3aa87f07461edfc1977860abe91fdaa13e234da54a63717beab2bf`) and its raw log (SHA-256 `92513c19bd3b383626939c75b250bf3fddde33e76c262bcbd3c4f7282c8f96a7`) preserve every result: indices 10,331–12,858, UNSAT=2,528, SAT=0, UNKNOWN/timeouts=0. The exact first unvisited cursor is 12,859; its tuple is `[2,6,11,23]`.
- Audited all lane and c5–c9 result files together: 12,859 records cover every index 0–12,858 exactly once, with no duplicate, missing, or tuple-order mismatch. The domain remains C(35,4)=52,360, indexed 0–52,359.
- Frontier diagnose accepted the baseline at value 35, tying the best known. A disposable witness scaffold (declarations kept false) also passed `bun frontier check` as a valid value-35 witness; it was moved out of the repository after checking. No candidate arose to validate.

## Deviations

- The terminal-pane service was unavailable, so the sole bounded process ran directly and was observed from its atomic checkpoint. No concurrent solver was started.

## Concerns

- Only labelled tuples 0–12,858 of the 52,360-case replacement neighbourhood of this one Exoo 35-vertex colouring have been exhausted. Other tuples and base colourings remain.

## Follow-ups

1. Resume exactly at `--start 12859`, preserving the fixture hash, lexicographic order, one-second per-case timeout, and per-tuple checkpoints.
2. If a SAT model appears, immediately write it to a disposable witness scaffold and run Frontier diagnose and check while declarations remain false.
3. Inspect hosted PR 36 if `gh` becomes available before changing neighbourhoods.
