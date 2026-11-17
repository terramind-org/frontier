## Done

Corrected the audit's five findings for `attempts/witness.superpermutation-7/20261117-terramind-com-4180d7`.

1. Replaced “Strong LKH full paths” in the title with “Capped LKH (no full-path run completed)” and aligned the writeup heading with the title.
2. Replaced “completed-run and trial totals remain unmeasured” with the logged count of 10 completed runs across 80 calls. Nine finished in 1000-permutation windows and one in a 1500-permutation window. The four full-path calls and all windows of 2000 permutations or more finished zero runs. Added the auditor's full-path timing and trial-count estimate, with 116 trials in 59.8 user CPU seconds in the rerun and about 2.5 CPU hours estimated for 20,000 trials, plus preprocessing.
3. Changed “four full ATSP calls” in the claim to “four full ATSP calls (none completed its first LKH run).”
4. Expanded the original calibration caveat with the auditor's from-scratch results and the scope of the record-seeded runs. Across the author and audit runs, zero of four reached 872 at n=6. The auditor's random-interior windows finished 1 to 9 cost units above the corresponding record segments. The seeded controls repaired the published words.
5. Replaced “Caps apply to solver subprocesses” with the shared-machine wall-cap explanation. The author's sampled CPU shares were 63% and 26%. The auditor observed a load average of 55 to 77 on 14 cores. LKH logs user CPU time, so wall-clock-to-trial ratios are unreliable.

Documented the swapped scratch inputs for `second/*` and why buffered stdout leaves kernel search entry unknown. Added an independent audit section and put the audit's method follow-ups first, covering n=6 calibration, reuse of ascent files, random-interior windows, exact fixed-end windows and an unbuffered 5906 kernel control.

Preserved the existing disclosure and added the auditor and corrections roles. The audit identified no missing tools. Both declarations remain false. The required local-path grep found no matches (exit 1), and the privacy scan found no personal names. LKH runs as an external binary. The attempt contains the drivers and descriptions of the third-party modifications. The audit found no bundled AGPL source, so no files needed removal. Ran no search.

**Title**

> Capped LKH (no full-path run completed) and large windows, scheduled 2 h, no 5904; kernel completion controls timed out

**Claim**

> No word shorter than 5905 was found in 80 capped LKH-3 calls: four full ATSP calls (none completed its first LKH run) and 76 fixed-end windows of 1000-3000 permutations. Seventy-nine calls returned valid tours; all reproduce the two published starting words, with 69 edges of weight at least three. Twenty-one distinct disturbed starts were also tested, with lengths up to 6444. The requested broad n=6 calibration failed; narrower record-repair controls passed. Three published 5906 kernel completion controls timed out, so the planned bridged-kernel completion search and four legacy score-15 runs were dropped under the preflight rule. This writeup is not machine-checked and establishes no lower bound.

`bun install` succeeded. `bun run check` passed type checking and reported 434 passed, 1 skipped (actionlint), and 0 failed. Its repository-wide validation exited 1 with only unconfirmed-declaration errors. `git diff --check` was clean.

```text
$ bun src/cli.ts check "attempts/witness.superpermutation-7/20261117-terramind-com-4180d7"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

```text
$ bun src/cli.ts validate "attempts/witness.superpermutation-7/20261117-terramind-com-4180d7"
attempts/witness.superpermutation-7/20261117-terramind-com-4180d7/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

The brief named two handoff files. Committed the task-slug handoff and kept an identical local copy at `.terramind/swarm/witness-records/handoffs/correct-superperm7-r2.md`.

## Concerns

None.

## Follow-ups

None.
