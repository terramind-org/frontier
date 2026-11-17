## Done

Created exactly one attempt: `attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f`, kind `writeup`.

Committed and pushed on the assigned worker branch. [PR #15](https://github.com/terramind-org/frontier/pull/15) targets `swarm/witness-records`.

Title: "Hole/exchange and all-point Lp search from 604 points, 2 h, no 605 found".

The repository record is 604. The published baseline and three finite-pool results were accepted at 604 and tie it. No configuration beat it. The best saved numerical 605-point configuration had maximum pairwise cosine **0.5072124712612411**, positive overlap **0.007212471261241138**, and minimum angle **59.52166841688265 degrees**. Its scale-10^12 integer export was rejected with **12,485 violations**.

The shared search window started at 2026-11-17 16:09:52 UTC. The budget guard sent SIGTERM at 18:09:51.995739 UTC, after **7199.995739 seconds**. The main launcher's recorded wait status is **145**, following earlier stop/resume operations; the final all-point profile exited **0** at the shared deadline. The earlier all-point profiles were intentionally stopped with status 143 when changing parameters. No search process remains running.

The last main progress record contains 161,415 hole trials, 53,805 backbone LP calls, 1,322,820 exchanges with k=1..6, and 723 all-point squared-overlap restarts. The final Lp profile completed 61 restart cycles and 713,909 evaluations with p through 256. Each retained hole had 51 initial blockers. The finite-pool MILPs returned 108 extensions; the full 19,034-direction model remains unresolved.

Verbatim `bun frontier check attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f` output:

```text
$ bun src/cli.ts check "attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun frontier validate <attempt>` reports only unconfirmed declarations, as required. `bun run check` passed typechecking and ran **426 passing tests, one skipped actionlint test, zero failures**. Its final validation step exits 1 only for the same false declarations. Both declaration fields remain false. No Frontier submission or review command was run.

Evidence is retained at **`/Users/agrim/.terramind/worktrees/frontier/ridiculous-shoal/.terramind/scratch/kissing11/`**. `commands.log` records commands; `run-index.json` records log creation times, source hashes, seeds and exit statuses. Raw search logs are `search.out`, `structure.out`, `expanded.out`, `integer-pool.out`, `integer-subset.out`, `dominance.out`, `relax.out`, `relax-high.out` and `relax-wide.out`. Final metrics are in `best-objective.json` and `evidence-summary.json`; the stop is recorded in `budget-stop.json`. Verifier and gate output is retained in the corresponding `*-diagnose.log`, `attempt-check.log`, `attempt-validate.log` and `full-check.log` files. Eleven source scripts are copied into the attempt, with no binaries or data dumps.

Checker self-test: **exact baseline ACCEPT; duplicate REJECT; numerical baseline ACCEPT; duplicate REJECT**. The repository independently accepts the baseline and rejects the deliberately duplicated copy. Gradient tests passed, and independent einsum recomputation agreed with the final Gram matrix within 4.44e-16.

## Deviations

Added finite-coordinate-pool MILPs, a dominance pass and all-point Lp continuation to the planned hole/exchange method. Polar vertices were sampled; deep holes were not exhaustively enumerated. The Lp profiles were upgraded from p<=16 to p<=64 and then p<=256 with larger perturbations after plateaus, all within the original deadline.

The initial full integer-pool run was stopped with status 143 after its model grew too large. A guarded 5,000-direction subset rerun exited 0 and returned a verifier-accepted 604-point tie. A later memory-bounded dominance pass deleted zero vertices and skipped its MILP.

## Concerns

The aborted full integer-pool run was not memory-bounded. Its observed RSS was 1,882,752 KiB, but its dense Gram matrix and temporary allocations could have exceeded the 3 GB cap. Peak memory was not captured, so compliance for that run cannot be asserted. Its original source is archived as `integer_pool_initial.py` for audit and should not be rerun under this budget.

The main launcher recorded wait status 145 rather than normal completion after its earlier stop/resume operations. The independent guard records the final SIGTERM and elapsed wall clock. Main trial counts are its last logged counts. The final Lp profile has a normal deadline summary and exit 0.

This writeup is unchecked. Numerical MILP optima are not formal upper-bound certificates, and the search does not exclude a valid 605-point configuration.

GitHub CI on PR #15 did not start either job. Its annotations report failed account payments or a spending limit requiring an increase; both jobs have zero executed steps. CI therefore adds no validation evidence. Once that account block is cleared, the swarm design still expects the false declarations and handoff outside `attempts/` to block the PR workflow.

## Follow-ups

Rank backbone-compatible candidate directions by blocker count before choosing small exchanges; the retained minimum-maximum-cosine holes each had 51 blockers. Try larger or less rigid backbone neighborhoods. Optimize the full 19,034-direction pool with memory-bounded clique constraints, and explore mixed p+q*sqrt(2) coordinates systematically.

The closing task should rerun `bun frontier check attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f` after merging this worker branch into the swarm branch. Keep declarations false and leave any eventual Frontier submission to the lead and requester.
