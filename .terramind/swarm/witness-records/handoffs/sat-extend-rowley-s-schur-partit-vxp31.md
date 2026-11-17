## Done

Integration PR: https://github.com/terramind-org/frontier/pull/16, targeting `swarm/witness-records`. Attempt commit: `a8274fd4`.

Created and checked `attempts/witness.schur-7/20261117-terramind-com-c8ca32/`, kind `writeup`.

Title: **Rowley-seeded SAT windows and tabu, 2 h, no extension; best 5 conflicts**.

The accepted baseline ties the published record of 1696. No accepted improvement was found. The best observed colouring at N=1697 has five monochromatic triples, confirmed by repository diagnosis. CaDiCaL reported UNSAT with Rowley's first 446 colours fixed and all later colours free: a top window of 1250 baseline entries, plus the new endpoint. Its N=1696 control was SAT and repository-accepted. Larger windows remain unresolved.

Search ran 2026-11-17 16:09:00 to 18:08:50 UTC, approximately 119 minutes 50 seconds. Final SAT controller and clean local search exited 0. Timeouts were recorded as 124; intentionally interrupted earlier phases used SIGTERM/143. The final clean local run made 112,873,492 moves over 113 restarts.

Verbatim `bun frontier check` output:

```
$ bun src/cli.ts check "attempts/witness.schur-7/20261117-terramind-com-c8ca32"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Path-specific validation reports only the unconfirmed declarations. Both declarations remain false. `bun run check` passed TypeScript and ran 426 passing tests, one skipped actionlint test, and zero failures; it exited 1 at validation solely because the declarations are false. No submit command was run.

Evidence is retained at `/Users/agrim/.terramind/worktrees/frontier/parental-glacier/.terramind/scratch/schur7/` (about 48 MB). Main logs: `search.out`, `sat.log`, `stage2.log`, `windows.log`, `windows2.log`, `windows3.log`, `local.log`, `local2.log`, `local3.log`, `stage-transition.log`, `monitor.log`, and the per-job logs/requests. `commands.txt` and `environment.log` record commands and versions. `candidate-audit.jsonl` covers all 688 saved colouring files: 395 accepted, 293 invalid, zero errors, zero improvements, maximum accepted length 1696. Source-only search/audit scripts are included in the attempt.

Checker self-tests passed: baseline accepted; deliberately broken baseline rejected with 19 violations including 1+1=2; four known SAT/UNSAT encoding cases passed; 50 local move costs agreed with full enumeration. The three supplied product templates produced repository-accepted lengths 1293, 1456 and 1664. Five six-colour-prefix requests produced two unique variants, whose reflected length-1696 controls failed; those trials are excluded from the conditional-extension conclusions.

## Deviations

I exceeded the two-core allowance for roughly 14 minutes after retrying a delayed terminal launch, leaving two identical local searches plus SAT. Observed aggregate CPU was about 220 percent. Both local instances were stopped and one clean instance restarted. The mixed `local2.log` is retained and excluded from clean-run move counts. The five-conflict candidate came from the later single-process run.

uv used its normal shared package cache during setup; the virtual environment and research data are in the required scratch directory. After execution, historical-PID identity guards were added to the two pause wrappers, and the extractor was made to emit the same `baseline.txt` conversion originally run inline. The SAT encoding and experimental parameters were unchanged.

## Concerns

This is an unchecked writeup. UNSAT claims concern the stated frozen colours and have positive controls, but no DRAT certificates were retained. Unrestricted 1697 and larger free sets timed out. Historical controllers have absolute deadlines; pause wrappers refuse their old PIDs. Replay individual saved requests through `sat.py child` rather than running those controllers unchanged. The mixed duplicate-process interval cannot support reliable aggregate iteration counts.

GitHub Actions did not start the PR jobs because the account has a payment or spending-limit block, according to both failing check annotations. CI has not validated the attempt. Once that account block is cleared, the integration PR is still expected to fail attempt-policy validation because declarations are false and the handoff is outside the attempt directory, as specified by the swarm design. The skipped actionlint test remains an environment limitation.

## Follow-ups

Audit the retained evidence and rerun the completed 1250-window case with proof logging. Change the fixed prefix before repeating that exact search. Try additional six-colour bases that first reproduce a length-1696 completion, weighted local search, and new product-template parameters. The lead should address the separate GitHub Actions account block, integrate this attempt, and include it in the final six-attempt checker run; declarations and submission remain for later human approval.
