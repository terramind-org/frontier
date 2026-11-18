Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c5` from the swarm branch, recovered failed-push material from commit `77d53c67` (cherry-picked as `dfd23eb2`), and committed this measured handoff; made no attempt submission, declaration change, push, PR, or merge.
- Verified recovery before continuation. McKay source `r55_42some.g6` SHA-256 is `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`; selected matrix `ramsey_c8_alternate42.txt` SHA-256 is `557b03cb5670af1e1cef2378f13cfb44121e1d46d98df5ef50c30729d43fc28c`. Re-running the selector reproduced byte-identical matrix and probe JSON. The seed is K5-free and degree-sequence distinct from Exoo, as recorded in `ramsey_c8_alternate_probe.json`.
- Installed Bun 1.4.4 and dependencies per `AGENTS.md`. Frontier baseline validation of the Exoo matrix passed: `diagnose` says valid, value 42, ties best known; a disposable scaffold (declarations remained false) also passed `bun frontier check` as a valid 42-vertex witness. Baseline logs are retained. No 43-vertex candidate was found, so candidate `diagnose`/`check` was inapplicable.
- Recompiled the recovered deterministic encoder, ran its exhaustive CNF/scanner control (262,144 assignments; 18 variables/clauses), and passed its planted 39-to-42 reconstruction control (CNF satisfied, K5-free scan, byte-identical matrix reconstruction). Script SHA-256: `7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`.
- Resumed only the alternate McKay seed with `taskset -c 0 /tmp/frontier-ramsey-venv/bin/python .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_delete3_reinsert4.py .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_alternate42.txt --start 827 --seconds 1740 --per-core 8 --out .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_alternate_resume_result.json`. PySAT Glucose4 1.9.dev23 completed 4,893 labelled triples, indices 827–5,719 inclusive, in 1740.2654106419996 seconds: 4,893 UNSAT, 0 timeout, 0 SAT, 9,834,116 decisions. First record `[827,[1,2,10],22586,1827]`; last `[5719,[8,16,37],22682,1926]`; exact next cursor is 5,720. The raw result JSON SHA-256 is `cade942bded649563cc4f9bd7d78bedaf1d6ccfca108f821cb8fd9e837a57e77`.
- Combined with the recovered prefix, alternate indices 0–5,719 are now classified UNSAT (5,720 total); indices 5,720–11,479 remain unvisited. The completed Exoo route was not repeated.

## Deviations

- The first timing wrapper invocation used unavailable `/usr/bin/time`; it did not launch the solver (exit 127, retained in stderr). The actual search was immediately re-run without that wrapper and recorded its own monotonic elapsed time in the result JSON.
- A disposable baseline scaffold remains untracked under `attempts/` with declarations false, so it cannot enter the commit or be submitted. It exists only to document the local Frontier baseline check.

## Concerns

- This excludes only four-vertex insertions over the tested frozen 39-vertex cores. It does not determine `R(5,5)`.
- The alternate suffix from cursor 5,720 is unvisited, not UNSAT. Rerun any future timeouts rather than classifying them as exhausted.
- No candidate exists for Frontier validation; publication stays pending human approval.

## Follow-ups

1. Resume `ramsey_c8_alternate42.txt` with the identical command and `--start 5720`; retain this run's raw JSON rather than merging its unvisited suffix into UNSAT.
2. If a SAT instance appears, create a disposable witness with its 43 rows and run Frontier `diagnose` and `check` before making any claim.
3. After this alternate route is exhausted, pivot to another McKay graph with a recorded nonisomorphism certificate.
