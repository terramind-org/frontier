Outcome: done

## Done

- Recovered original commit `ac02f23c` directly from the local object database and restored its c10 artifacts. The fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`; the recovered `c10-resume-12859.json` SHA-256 is `2fc95bd11c179498430872c5dbc678ccd69695f64ab562f0ac5211e4396bdfbc`. This is recovered evidence, not transcript-only.
- Audited c4--c10 before searching: their 14,966 records cover every lexicographic `itertools.combinations(range(35), 4)` index 0--14,965 exactly once, with no tuple mismatch; index 14,966 is `[2,13,20,22]`. The domain is C(35,4)=52,360, indices 0--52,359.
- Re-ran controls before the production run. The asymmetric clauses use positive literals for a forbidden colour-0 K4 and negative literals for a forbidden colour-1 K6. The exhaustive control has 14 variables and 16,384 assignments; the planted fixture reconstruction passed with forbidden counts `[0,0]`. Frontier diagnose accepts the baseline at value 35, tied with the known value; declarations remain false.
- Added a per-output O_EXCL writer lock, per-run `c11-run/` checkpoint directory, and existing atomic JSON replacement. The completed run removed its lock. This prevents a second controller from writing the same checkpoint while the original PID is alive.
- Ran one CPU for 1,380.330 seconds from `--start 14966`, with one second per formula. `c11-run/resume-14966.json` (SHA-256 `95b284adff33cc3253fa759d9dcdf62e0615e58533a205af7a2bbe3892939214`) and its raw log (SHA-256 `b76c53af616b1a96ecff03e810b73522de289b8c7817ee1c714c7d8a23df277f`) record 2,006 cases, indices 14,966--16,971: UNSAT=2,006, SAT=0, UNKNOWN/timeouts=0. The joined c4--c11 records cover 0--16,971 exactly once, so the first unvisited cursor is 16,972, tuple `[3,5,11,19]`.
- No SAT candidate appeared, so candidate-specific Frontier diagnose/check was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail.

## Deviations

- The prior c10 lock writer accidentally recorded a literal backslash-n after its PID; this did not affect exclusivity and the c11 run had one writer. The lock output now uses a real newline. No second writer was started.

## Concerns

- Only labelled tuples 0--16,971 of this one Exoo 35-vertex replacement neighbourhood have been exhausted. The remaining tuples and other base colourings remain unexplored.

## Follow-ups

1. Resume exactly at `--start 16972`, preserving fixture hash, lexicographic order, one-second timeout, run-specific output directory, atomic checkpoints, and the O_EXCL writer lock.
2. If a SAT model appears, write it to a disposable witness scaffold and run Frontier diagnose and check with declarations false.
3. Inspect hosted PR 36 if access becomes available before changing neighbourhoods.
