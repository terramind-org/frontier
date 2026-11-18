Outcome: done

## Done

- Created `swarm/frontier-cloud-codex--extend-seven-dimensional-cap-con-qxvuf-c7`, read `AGENTS.md`, showed `witness.ramsey-5-5`, and retained the PR #59/#60 control work already on the inherited branch. No push, PR, submission, scaffold, or declaration change was made.
- Recovered Exoo's `g55.42` from `http://cs.indstate.edu/ge/RAMSEY/g55.42`; SHA-256 is `36ba90fb6727c9a876ecc127d8acbe9b9bf07a5b0925364a1b2f46f6e15052aa`. The prior control branch's Frontier diagnostic accepted the same 42-vertex fixture; this run used the independently implemented K5 scanner as a second control.
- Added `ramsey_c7_delete3_reinsert4.py` and raw `ramsey_c7_smoke.json` / `ramsey_c7_result.json` under `.terramind/swarm/frontier-cloud-codex/`. For each labelled unordered deleted triple it freezes Exoo's induced 39-core and permits all 162 incident edges of four new vertices (156 new--core plus 6 new--new).
- Encoder controls passed. Exhaustive direct scanner versus CNF equivalence on the 3-core/4-new test covered all 262,144 assignments (18 variables, 18 clauses), with no disagreement. Planting three Exoo vertices in the corresponding 39-core/3-new encoder satisfies all 12,285 clauses, reconstructs Exoo byte-for-byte, and is K5-free under the independent scanner.
- Ran one cloud CPU with PySAT Glucose4 1.9.dev23, Python recorded in the JSON, no random seed, lexical triple order, 8 seconds per core and a 1,740-second global budget. It resolved 7,795 distinct triples as UNSAT, found 0 SAT instances and 0 per-core timeouts (15,694,520 recorded decisions). The reproducible cursor is index 7,795: indices 0 through 7,794 are exhausted and the 3,685 unvisited triples begin with `[12, 33, 39]`. There were no timed-out cases to rotate across easy/hard strata.
- No 43-vertex graph was produced, so a Frontier candidate `diagnose`/`check` was inapplicable. `python3 -m py_compile` and `bun run check` passed (434 tests, 1 skipped, 0 failures).

## Deviations

- The fresh cloud worker did not retain PySAT; installed `python-sat` only under `/tmp/frontier-c7/pylib`. The committed experiment explicitly records that Glucose4 dependency and version, while the disposable install is not part of the repository.
- The global time budget ended before all 11,480 triples. This is reported as 7,795 UNSAT plus 3,685 unvisited, not an exclusion of the full 39-core neighbourhood.

## Concerns

- The negative result is local to the completed prefix of one labelled Exoo 42-colouring with a frozen 39-core and four replacements. It neither covers the unvisited suffix nor decides `R(5,5)`.
- A timeout never occurred in this slice, but unvisited cases have not been inferred UNSAT. Resume must begin at triple index 7,795 with the same fixture hash and ordering.

## Follow-ups

1. Resume `ramsey_c7_delete3_reinsert4.py` from `--start 7795` with the same fixture and append/merge case records carefully; validate any SAT graph using Frontier `diagnose` and `check` in a disposable scaffold while keeping declarations false.
2. After all triples are covered, rerun any future timeouts with larger deterministic slices before calling the frozen-core neighbourhood exhausted.
3. Only pivot to a separately published 42-colouring after checking it is inequivalent to Exoo under relabelling and colour swap.
