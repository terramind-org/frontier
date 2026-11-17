## Done

Left exactly one new writeup attempt: `attempts/witness.superpermutation-7/20261117-terramind-com-4180d7`.

Title: "Strong LKH full paths and large windows, scheduled 2 h, no 5904; kernel completion controls timed out".

Best valid word: 5905, the published input, tying the record. Its heavy-edge count remains 69. Ran 80 LKH calls: four full ATSP calls and 76 fixed-end windows of 1000-3000 permutations. All reached their wall caps with return code -15. Seventy-nine returned valid tours, all replaying exactly to the two published starts. There were 23 distinct initial words, including 21 disturbed starts reaching length 6444; 20 disturbed starts repaired to the original word and one timed out without a tour.

Scheduled UTC window: 2026-11-17 19:06:31.155 to 21:06:31.155. Last solver call ended 21:06:28.455; both final drivers exited 0. The old second driver was stopped with signal 15 between completed calls, with zero solver children. All search, deadline and archive processes have ended.

N=7 kernel completion calls: score 10, three timeouts with code -15 and no output; score 15, one completed call with code 0 yielding four validated 5905 baseline words; score 20, zero calls. The bridge generator recovered a planted score-20 middle without guided ordering. No new kernel completion population was tested.

Evidence remains in worktree `equal-nectar`, `.terramind/scratch/superperm7-r2/`: calibration JSONL files, `kernel.jsonl`, both LKH logs, `archive/`, `replay-final.log`, `report-stats.json`, and `provenance.json`. The separate replay passed for all 79 returned tours. Derived AGPL code, binaries and data dumps are excluded from the attempt.

Verbatim attempt-check output:

```text
$ bun src/cli.ts check "attempts/witness.superpermutation-7/20261117-terramind-com-4180d7"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

The new attempt's validation reports only unconfirmed declarations. `bun run check` passed type-checking and ran 435 tests: 434 passed, one skipped, zero failed. Its final validation exits 1 for seven false declarations and two pre-existing private-path violations in other attempts. Declarations remain false. No submission or AI-review command was run.

## Deviations

Broad n=6 calibration missed the 872 target, returning 878 from the lexicographic seed and 873 from the five-swap start. Narrower adjacent-swap n=6 controls reached 872 on all three tested seeds; n=5 controls reached 153, and an n=7 damaged segment repaired to its original cost. The record-seeded LKH line continued on that narrower calibration evidence.

All three published 5906 completion controls failed within caps of 900, 300 and 217.801 seconds. The preflight rule therefore dropped the kernel stage before its 25-minute deadline. The requested four historical score-15 long reruns and score-20 bridge completion search remain unrun. The freed core ran a second LKH line, later adding perturbed initial orders after stationary returns.

The recorded launcher needed a different local Python interpreter; native supervised processes carried the long runs. The evidence collector was restarted after fixing its handling of no-tour timeouts.

## Concerns

This is a bounded heuristic failure with limited calibration. It establishes no lower bound, unrestricted local optimum, or kernel non-completion claim. Configured RUNS and MAX_TRIALS are limits; completed-run and internal distinct-state totals are unmeasured.

Second-worker iteration 17 retains exact timeout/status metadata but lost stdout before the collector fix. All returned tours and their words remain available. The full repository gate is not green because of the existing validation failures described above.

## Follow-ups

Have the lead's independent audit replay this attempt from the preserved scratch evidence. Establish a working published-5906 completion control before another kernel search, then revisit the four historical score-15 timeouts and fixed-middle score-20 generation/completion.

Existing private-path violations remain in `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/writeup.md` and `attempts/witness.schur-7/20261117-terramind-com-c8ca32/run.sh`. Their owning correction tasks must address them; this task left immutable attempts unchanged.
