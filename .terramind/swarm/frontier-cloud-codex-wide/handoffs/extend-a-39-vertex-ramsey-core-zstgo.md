Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c6` from the recovered `22d8d26e` continuation; made no attempt submission, declaration change, push, PR, or merge.
- Revalidated recovery before searching. The McKay source is SHA-256 `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`, selected matrix is SHA-256 `557b03cb5670af1e1cef2378f13cfb44121e1d46d98df5ef50c30729d43fc28c`, and the selector evidence remains `ramsey_c8_alternate_probe.json`: source line 0 of 328, K5-free, degree-sequence distinct from Exoo. The lexicographic ordering has 11,480 triples; index 5,719 is `[8,16,37]` and resumed index 5,720 is `[8,16,38]`.
- Re-ran the independent exhaustive CNF/scanner equivalence control (262,144 assignments, 18 variables/clauses) and planted 39-to-42 reconstruction control before the sweep. Both passed; the latter has 12,180 clauses, satisfies the CNF, scans K5-free, and reconstructs the fixture byte-for-byte. The retained zero-search control result is `ramsey_c8_alternate_c6_control.json`, SHA-256 `e4d856a8d09000c9895e5754511384b411966721dbe6609df6ee3bf8db07e755`.
- Ran the recovered encoder SHA-256 `7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f` on exactly one `taskset -c 0` core: `/tmp/frontier-ramsey-venv/bin/python .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_delete3_reinsert4.py .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_alternate42.txt --start 5720 --seconds 1740 --per-core 8 --out .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_alternate_c6_result.json`.
- The 1,740.2842150609995-second suffix run classified indices 5,720–10,563 inclusive as 4,844 UNSAT, with 0 timeouts and 0 SAT, totalling 9,605,962 Glucose4 decisions. The first record is `[5720,[8,16,38],22730,2222]`; the last is `[10563,[23,27,32],22604,1416]`. Raw result SHA-256: `2ae17f07d95f4495f25f5cf2f5f5a433716045c9f1b3c937f98b3c0d34c31da3`; stdout and empty stderr are retained alongside it.
- Combined alternate coverage is now indices 0–10,563 UNSAT (10,564 cases). The exact next cursor is 10,564; indices 10,564–11,479 are unvisited, not UNSAT. The exhausted Exoo route was not repeated. There was no SAT graph, so Frontier candidate `diagnose` and `check` were inapplicable.

## Deviations

- The visible-terminal integration returned an IPC error before launching the search. The run was immediately started through the managed shell session instead; it retained the specified `taskset -c 0`, exact command, 1,740-second cap, raw stdout/stderr, and exit status 0.

## Concerns

- This covers only labelled four-vertex reinsertion over the frozen 39-vertex cores produced by the selected alternate 42-vertex McKay graph. It does not determine `R(5,5)`.
- The remaining 916 triples (indices 10,564–11,479) have not been visited. Do not label them UNSAT; re-run any future timeout separately.
- No candidate arose for independent Frontier validation. Declarations and publication remain pending human approval.

## Follow-ups

1. Resume the saved alternate fixture with the identical encoder and `--start 10564`; retain per-index raw JSON and a separate timeout class.
2. If a SAT instance appears, first materialize its 43-row graph in a disposable witness and run Frontier `diagnose` and `check` before making any claim.
3. If this seed exhausts with no candidate, select another McKay graph only after recording a nonisomorphism certificate and fixture/order hashes.
