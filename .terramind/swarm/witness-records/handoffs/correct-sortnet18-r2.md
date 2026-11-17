## Done

Applied all five audit corrections to the round-two sorting-network writeup.

1. “The smallest valid network visited has 77 gates and ties the published record.” The claim had “The best valid size is 77, which ties the record.” Both now say “No SorterHunter run produced a valid network smaller than its input. The only 77-gate networks the runs printed are the two 77-gate inputs (the published record and round 1's network), so the best valid size, 77, is the input, which ties the record.”
2. “Eight distinct printed ordered sequences have 77 gates.” The writeup now adds “They are four orderings each of the two 77-gate inputs. The auditor found that up to commuting gates and mirror symmetry, the 86 printed networks form 77 classes. These include the three inputs, 16 new 78-gate classes and larger networks.”
3. “Each lasting 196.0 to 197.6 seconds” now specifies wall time and adds “In the auditor's recount, SorterHunter's own CPU clock reports 33 to 178 s per run, 3,717 CPU s in total. That is 52% of the 7,095 s wall total, about half a core on a shared machine.”
4. “`RestartRate=0` leaves the bounded wrapper in charge of restarting from the known inputs.” The writeup now adds “Each input was therefore started 12 times in total (36 runs over 3 inputs). The logs do not record the size of the accepted network after the start. In audit reruns of two of these configurations, the accepted network left 77 gates within the first 0.32 CPU seconds and stayed at 78 to 95 gates for the rest of the run, so nearly all run time in those reruns was spent above 77.”
5. “Nine stop at the outer deadline without a final solver answer” now reads “nine were stopped by the per-query 120-second limit (110-second internal deadline plus 10 seconds) without a final solver answer.” The recommendation “The next attempt should preserve the 48-failure candidate as another repair start” was replaced with the audit result. “An audit control showed that the same repair loop could not restore the record with one wrong gate at n = 18 within 4 to 5 minutes (best 43 failures at 240 s and 317 at 300 s). The 8-input controls passed trivially and do not calibrate performance at n = 18. A 48-failure score therefore carries no evidence of closeness. The auditor enumerated all 11,552 single-gate replacements of the 48-failure candidate. The candidate is a local minimum for single-gate replacement. Four replacements tied the score and the other 11,548 scored worse.”

The writeup attributes the two 170-second, clean-upstream SorterHunter reruns to the auditor and records the one and two other 77-gate classes seen in the first second. It gives the actual size ranges for each rerun and scopes extrapolation to the shared restart and escape settings. It reports the auditor's 171-second planted mid-window saving and 8- to 18-second tail queries. It explains why a single insertion can inflate `MaxPositionDistance`. The independent audit section records the full baseline simulation, counts and starts confirmed from configs and logs, and the repair and SAT controls. The follow-ups now lead with SorterHunter restart and escape changes, full-size repair controls with systematic neighbourhoods, and longer mid-window SAT budgets or a stronger encoding plus broader tail coverage. They call for reporting CPU seconds and retaining UNSAT certificates.

Added Claude Opus 5.5 as auditor and GPT-6.2 Sol for corrections in the attempt disclosure. All original entries remain. The required home-path grep printed nothing and exited 1 (no matches). The audit identified no licence issue. Both declarations remain false. No search was run, and no attempt was submitted.

**Title** — Record-started SorterHunter, sequential window SAT and deletion repair, 120 min budget, no 76-gate sorter

**Claim** — A failed search within a 120-minute wall budget: 36 SorterHunter runs from known 77- and 78-gate networks, 47 unresolved larger-window SAT queries, and fixed-length repair. No SorterHunter run produced a valid network smaller than its input. The only 77-gate networks the runs printed are the two 77-gate inputs (the published record and round 1's network), so the best valid size, 77, is the input, which ties the record. The repository verifier rejects the best measured 76-gate candidate, which fails 48 of 262144 inputs. This writeup is not machine-checked.

`bun install` succeeded. `bun run check` passed type checking and ran 434 passing tests, one skipped actionlint test and zero failures. Repository-wide validation exited 1 and reported only the 12 draft attempts' unconfirmed declarations. `git diff --check` passed.

`bun frontier check attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4` exited 0.

```text
$ bun src/cli.ts check "attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun frontier validate attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4` exited 1.

```text
$ bun src/cli.ts validate "attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4"
attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

Used the task-specific handoff filename `correct-sortnet18-r2.md`. The audit's numbers matched the brief. The replacement wording names SorterHunter in correction 1 to scope “no run” and gives the exact enumerated neighbourhood in correction 5.

## Concerns

None.

## Follow-ups

None.
