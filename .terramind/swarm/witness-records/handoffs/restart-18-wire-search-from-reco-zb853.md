## Done

Review PR: https://github.com/terramind-org/frontier/pull/32 into `swarm/witness-records`.

Created exactly one new attempt: `attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4`, kind `writeup`, titled "Record-started SorterHunter, sequential window SAT and deletion repair, 120 min budget, no 76-gate sorter". Both declarations remain false. Nothing was submitted through Frontier.

The smallest valid network visited has 77 gates and ties the record. All 86 distinct printed ordered networks pass an independent exhaustive bitset check. The best measured 76-gate candidate fails 48 of 262144 inputs; the repository verifier rejects it. Repair evaluated 699445 candidates over 35 walks and counted 5464 distinct sampled ordered candidates. All 47 larger-window SAT queries remain unresolved: 38 internal timeout results and nine outer deadlines without an answer.

The scheduled UTC interval was 2026-11-17 19:07:41.384524 to 21:07:41.384524. Long SorterHunter runs began at 19:09:11.890452; the final child was reaped at 21:07:41.414048. Exit codes: all 36 SorterHunter children `-15`; SAT children 36 zeros and eleven `-15`s; repair `-15` after printing its budget result. No search process remains.

Controls passed: known record accepted and broken copy rejected; SorterHunter improved a padded 8-input network from 20 gates to 19; sequential-counter SAT removed a planted gate and returned UNSAT on all sixteen tested windows of an optimal 8-input network; the actual repair heuristic restored its 8-input control in 875 evaluations. The diversity estimator passed its known-distinct and duplicate controls.

Verbatim output of `bun frontier check`:

```text
$ bun src/cli.ts check "attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun run check` passed typechecking and reported 434 pass, 1 skip, 0 fail, 2481 expect() calls across 34 files. Its final validation exits 1 for the blockers below. Targeted validation of the new attempt exits 1 only for its unconfirmed declarations. Privacy scanning found no home paths or personal names in the new attempt.

Evidence remains in worktree `novel-shelf`, `.terramind/scratch/sortnet18-r2/`: `budget.json`, `build-manifest.json`, `calibration.log`, `hunter-lane.log`, all `hunt_*.cfg`, `hunt_*.log` and summaries, `sat-lane.log`, all `sat_*.log` and exit records, `repair.log`, `repair.exit.json`, `repair76.best.json`, diagnostic JSON and `evidence-summary.json`. The attempt includes our search source; third-party source, binaries and raw data remain in scratch.

## Deviations

The branch includes the required setup merge of `origin/main`. Its catalog updates are inherited from that merge; no catalog files were edited by this task.

Used two bounded visible-terminal process lanes rather than nohup. The operating system rejected the initial virtual-address-limit setup, so child RSS was sampled every five seconds with termination above 1300000 KiB. Highest sampled child RSS was 754800 KiB. The original wall deadline was retained after the setup retry.

Distinct-state reporting uses exact samples and, for the last 28 SorterHunter runs, full-candidate cardinality estimates. There is no exact global distinct-state union count. Weighted SAT failure counts and best non-sorting objects were retained starting at query 17; earlier transient models are excluded from the best-measured failure claim. No 75-gate repair ran.

## Concerns

The full repository gate also finds inherited local-path violations in the existing matrix-multiplication `writeup.md` and Schur `run.sh`. They are outside this task's ownership and remain untouched. Their correction tasks must be reconciled before approved attempts reach main. All existing and new unconfirmed declarations also block validation as required.

The 48-input failure score supplies no calibrated estimate of distance to a valid sorter. The research SAT calls supply no UNSAT exclusion result. Counts distinguish ordered gate lists, including commuting reorderings. Memory samples do not certify instantaneous maxima.

## Follow-ups

Independently audit this attempt from the preserved scratch before any submission. Preserve the 48-failure object for another repair search, and consider longer per-window SAT budgets. Reconcile the inherited privacy corrections on the swarm branch.
