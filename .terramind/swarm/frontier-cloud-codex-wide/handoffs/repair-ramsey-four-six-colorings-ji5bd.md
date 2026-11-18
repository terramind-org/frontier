Outcome: done

## Done

- Recovered PR 99's committed c9 artifacts directly. The fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`; its c9 JSON SHA-256 is `96060e946e3aa87f07461edfc1977860abe91fdaa13e234da54a63717beab2bf`. The recovered lanes and c5--c9 records cover indices 0--12,858 exactly once, and index 12,859 is lexicographic deletion tuple `[2,6,11,23]`.
- Re-ran the controls before and after the bounded continuation. `itertools.combinations(range(35), 4)` contains exactly C(35,4)=52,360 tuples, indexed 0--52,359. Colour-0 K4 clauses require a positive 1-edge literal; colour-1 K6 clauses require a negative 0-edge literal. The exhaustive encoder control has 14 variables and 16,384 assignments; the planted reconstruction of `[31,32,33,34]` matches the fixture and has forbidden counts `[0,0]`.
- Ran the sole cloud CPU from `--start 12859`, with a one-second per-formula cap and atomic per-tuple checkpointing. `c10-resume-12859.json` (SHA-256 `2fc95bd11c179498430872c5dbc678ccd69695f64ab562f0ac5211e4396bdfbc`) preserves indices 12,859--14,965: UNSAT=2,107, SAT=0, UNKNOWN/timeouts=0. It was stopped cleanly at its durable checkpoint after 1,456.716 seconds to reserve time for validation. Its next and first unvisited cursor is 14,966, tuple `[2,13,20,22]`.
- Audited all lane and c5--c10 result JSON together: 14,966 records cover every index 0--14,965 exactly once, without a duplicate, gap, or tuple mismatch. This credits only 14,966 of the correct 52,360-case domain.
- `bun frontier diagnose ... --problem witness.ramsey-4-6` accepts `c10-baseline-witness.json` at value 35, tying the known value. No SAT candidate arose, so candidate-specific Frontier diagnose/check was inapplicable; no declarations were changed. `bun run check` passed: 434 pass, 1 skip, 0 fail.

## Deviations

- An initial foreground invocation remained alive after its controller returned; a second observer briefly attempted to use the same checkpoint path and failed on `os.replace`. I terminated the duplicate observer, retained only the original solver, and audited the resulting atomic JSON before crediting it. Its stdout log is empty because the process was stopped before its final one-line summary; the per-tuple JSON is the raw evidence and contains the full contiguous outcome sequence.

## Concerns

- Only labelled tuples 0--14,965 of this one Exoo 35-vertex replacement neighbourhood have been searched. The remaining tuples, and other base colourings, remain unexplored.

## Follow-ups

1. Resume exactly at `--start 14966`, preserving the fixture hash, lexicographic order, one-second timeout, and unique checkpoint filename.
2. Immediately write any SAT model to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if hosted access becomes available before changing the search neighbourhood.
