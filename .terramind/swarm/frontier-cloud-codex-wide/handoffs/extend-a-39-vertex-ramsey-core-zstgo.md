Outcome: done

## Done

- Created branch `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c4`, read `AGENTS.md`, made no attempt scaffold, submission, declaration change, push, or PR. All committed material is reproducibility scratch and this handoff.
- Recreated the exact prior Exoo route in `ramsey_c8_delete3_reinsert4.py`, using `itertools.combinations(range(42), 3)` order, fixture `g55.42` fetched from Exoo's primary construction page, SHA-256 `36ba90fb6727c9a876ecc127d8acbe9b9bf07a5b0925364a1b2f46f6e15052aa`, PySAT Glucose4 `1.9.dev23`, one CPU pinned by `taskset -c 0`, no random seed, and an 8-second cap per core. Raw stdout/stderr and JSON are retained under `.terramind/swarm/frontier-cloud-codex-wide/`.
- Positive controls passed in both runs: exhaustive CNF/scanner equivalence over all 262,144 assignments of the 3-core/4-new test (18 variables and 18 clauses); and a planted 39-to-42 reconstruction satisfying the CNF, scanning K5-free, and matching the input matrix byte-for-byte. Python compilation of both scripts passed.
- The requested resume command was `taskset -c 0 /tmp/frontier-ramsey-venv/bin/python .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_delete3_reinsert4.py .terramind/swarm/frontier-cloud-codex-wide/g55.42 --start 7795 --seconds 1740 --per-core 8 --out .terramind/swarm/frontier-cloud-codex-wide/ramsey_c8_result.json`. It completed in 1315.601317371 seconds: all 3,685 previously unvisited triples, indices 7,795 through 11,479, were UNSAT; zero timed out; zero were SAT; 7,377,643 decisions; final cursor 11,480. The boundary records are `[7795, [12, 33, 39], 22616, 2418]` and `[11479, [39, 40, 41], 22700, 1897]`. Together with commit `c8076d2c`, all 11,480 labelled Exoo delete-three/four-reinsert instances are now covered with zero SAT and zero timeout.
- Pivoted after exhaustively completing the Exoo route. Brendan McKay's primary `r55_42some.g6` dataset (328 graphs, downloaded SHA-256 `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`) supplied an inequivalent seed: its first graph has a different sorted degree multiset from Exoo, a sufficient certificate of nonisomorphism, and independently scans K5-free. `ramsey_c8_alternate_probe.py`, its raw JSON/log, and matrix fixture retain that evidence.
- The bounded alternate sweep ran from index 0 with the same exact encoding and controls for 300.0014067970001 seconds. It classified indices 0 through 826 as 827 UNSAT, zero timeout, zero SAT, 1,695,243 decisions, with resume cursor 827 / triple `[1, 2, 10]`. No 43-vertex candidate existed in either route, so Frontier `diagnose`/`check` on a candidate was inapplicable.

## Deviations

- This fresh checkout has no `bun` executable (`command -v bun` is empty), so `bun frontier show`, `bun frontier diagnose`, `bun frontier check`, and the repository's Bun test command could not be run. I did not replace them with an unsupported checker. The Python encoder controls and direct K5 scanner are supplementary evidence only, not a Frontier verdict.
- The first route finished before its 1,740-second global cap. The remaining 300 seconds were deliberately spent on the required inequivalent-colouring pivot rather than idling. The alternate route is an initial 827-case prefix, not an exhausted neighbourhood.

## Concerns

- The completed Exoo result rules out only 43-vertex extensions formed by freezing an induced 39-vertex core of that labelled 42-vertex colouring and freely reinserting four vertices. It is not a determination of `R(5,5)`.
- The alternate graph sweep remains unvisited from index 827 onward; it must resume with the saved alternate fixture, its SHA-256, the same lexicographic order, and `--start 827`. Do not call it UNSAT until those cases are visited, and rerun any future timeout before treating an instance as exhausted.
- No candidate exists to validate with Frontier, and no declarations were changed; publication remains pending human approval.

## Follow-ups

1. On an environment with Bun, run Frontier baseline `diagnose`/`check` on a disposable known 42-vertex witness before any candidate check, keeping declarations false; if a 43-vertex candidate appears, run Frontier `diagnose` and `check` immediately.
2. Resume the alternate route from `--start 827` for the remaining 10,653 triples, preserving the current raw outputs rather than merging unvisited cases into UNSAT.
3. Rotate through further degree-sequence-distinct records in `r55_42some.g6` only after the selected alternate prefix is completed, or document a stronger isomorphism test when degree multisets collide.
