## Done

Created exactly one attempt: `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/`.

Kind: `writeup`. Title: "GF(2) ordinary and cyclic flip walks, 2 h, no rank below 93 found". Declarations remain `rights: false` and `disclosure_complete: false`. No Frontier submit command was run.

Verbatim output of `bun frontier check`:

```text
$ bun src/cli.ts check "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Result: published integer record 93; best GF(2) rank reached 93; best integer object validated 93, the published baseline. Frontier says that baseline ties the record. No improvement was found. The search occupied about 119m57s from its first smoke launch to final exit, including pauses. The final 6,064-second segment exited 0 and recorded 1,037,021,282 flips and 223 restarts. Across all three long segments, retained counters guarantee at least 1,216,402,434 flips and 822 restarts, including repeated states. The two deliberately interrupted earlier segments exited 143.

Evidence directory, retained locally:
`/Users/agrim/.terramind/worktrees/frontier/suitable-cloud/.terramind/scratch/matmul5/`.

The main logs are `search.out`, `search-segment1.out`, `search-segment2.out`, `selftest.log`, `selftest-v2.log`, `baseline-diagnose.log`, `broken-diagnose.log`, `audit.log`, `lift-selftest.log`, `commands.log`, `sha256.log`, `summary.json`, `attempt-check.log`, `attempt-validate.log`, and `full-gate.log`. Downloads, baseline, checkpoint and final masks remain there. Search and audit source files are copied into the attempt; binaries and data dumps are excluded.

Checker controls: Frontier accepted the integer baseline at 93 and rejected a deliberately corrupted copy with 12 violations. The C++ checker accepted the GF(2) baseline, rejected a changed baseline, and passed 2,000 transition tests per mode. Every logged checkpoint and final tensor passed. Independent Python checks accepted both final tensors and rejected the changed baseline. The conditional lift's linear-system controls, full Jacobian directional check and schoolbook positive path passed.

Validation: `bun frontier validate` reports only unconfirmed declarations, as required. `bun run check` passed typechecking and 426 tests, with one actionlint test skipped; it exited 1 only when validation reached the deliberately false declarations. No Lean checks were needed. The prose detector reported clean. Scratch used 892 KB at the last measurement.

Branch: `swarm/witness-records--flip-graph-walk-for-5x5-matmul-rr7cv`. Review target: `swarm/witness-records`.

## Deviations

The first native-shell background launch died before producing output. Successful runs used a persistent terminal with an event-driven log reader and were awaited through completion.

One restart corrected the cutoff to include the initial smoke search. A second switched from short schedules to longer walks with a 256-state tabu history. Both interrupted logs and the original source are preserved. Their final minute of counters was not captured, so combined counts are lower bounds.

Two threads limited each main search process, but OS-level CPU limits were not installed. Compilation and a short preflight overlapped the previous two-thread process briefly; the strict two-core ceiling was therefore not enforced during that overlap. Observed memory and disk use stayed far below their limits.

No lower-rank GF(2) candidate appeared, so lifting was not triggered on a search result. The included lift implements a zero-free-variable Hensel path and centered integer checks; rational reconstruction and alternate free-variable choices remain unimplemented.

## Concerns

This is a heuristic search with one published starting construction, rank cap 102, and restricted cyclic orbit moves. It gives no lower bound and does not rule out rank 92 over either field. The writeup itself is unchecked. Lifting a genuinely new low-rank scheme remains untested. Exact transition counts depend on machine load, and earlier restarts replayed some prefixes.

CI validation on the worker PR is expected to fail because declarations remain false and the handoff is outside `attempts/`, as specified by the design.

## Follow-ups

Try different starting decompositions and diagonal partitions, larger intermediate ranks, C3 combined with row/column reversal symmetry, and reductions involving larger groups of terms. Measure cycle frequency before repeating the short initial schedules. The closing task should rerun `bun frontier check` on this attempt after the lead merges it into the swarm branch.
