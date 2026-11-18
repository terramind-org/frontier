## Done

Filed one writeup at `attempts/witness.schur-7/20261118-terramind-com-7e1f64/`. Its title is "Six-colour bases and prefix SAT, eight hours, no partition of 1..1699 found."

The run generated 146,739 distinct bases. Of those, 135,498 reached 1696 and 59,372 reached 1698. The cumulative 1698 yield rose from 36.1% after hour one to 40.5% at the end. Frontier diagnosis accepted 1698 against the catalogued reference of 1696. The search threshold was 1699 and remained unmet.

The supervisor ran from 2026-11-17 21:13:02 UTC to 2026-11-18 05:13:01 UTC. Both base workers, the SAT worker and the local-search worker exited with status 0 at the final cutoff. Peak sampled worker RSS was 4.22 GiB. Scratch occupied 1.1 GiB at the end.

The `uncomfortable-grotto` worktree retains `.terramind/scratch/schur7-r3/`. The hourly record is `progress.md`, the counts are in `logs/summary.json`, and the exact restricted UNSAT cases at 1699 are indexed in `logs/unsat-1699.jsonl.gz` with their checkpoints in `checkpoints.sqlite`. The independent enumeration and Frontier diagnosis accepted the baseline and the reproduced 1698 control and rejected their broken copies. SAT controls returned SAT at 13 and UNSAT at 14 with three colours, and SAT at 44 and UNSAT at 45 with four. The retained evidence includes three independently checked LRAT results.

`bun frontier check` printed:

```text
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun run check` passed typechecking and ran 434 passing tests, one skipped test and zero failures. The full gate and standalone attempt validation exited 1 solely on unconfirmed declarations.

## Deviations

The exact wall-clock-limited calls used the CaDiCaL executable. The incremental calls through python-sat used conflict budgets within the common cutoff. The run resumed after planned configuration changes and one corrected cube-dispatch error. Five late 1698 completions reached the checkpoint before their pivot and window sweeps could run.

## Concerns

The UNSAT results apply to the indexed restrictions. At 1699, the cube search closed the tested 500- and 460-position prefixes. Shorter-prefix roots had timeouts. The best local candidate had two monochromatic triples and failed the tested exact repairs.

## Follow-ups

Audit the restricted UNSAT results against the archived requests. If extending the search, start from the open shorter-prefix branches or a different base family.
