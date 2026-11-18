Outcome: done

## Done

- Created `swarm/frontier-cloud-codex--extend-seven-dimensional-cap-con-qxvuf-c5`, read `AGENTS.md`, showed `witness.ramsey-5-5`, and fetched PR #59's head. PR #59 is the preceding c4 one/two-edge recolour-and-insert control (`d602112b`); it remains the baseline rather than a new result.
- Recovered Exoo's `g55.42` from `http://cs.indstate.edu/ge/RAMSEY/g55.42`; its SHA-256 is the requested `36ba90fb6727c9a876ecc127d8acbe9b9bf07a5b0925364a1b2f46f6e15052aa`. The JSON-wrapped graph was accepted by `bun frontier diagnose ... --problem witness.ramsey-5-5` at value 42.
- Added `ramsey_c5_delete2_reinsert3.py`: for every lexicographic unordered deletion pair it freezes the induced 40-core and encodes all 120 new-to-core and 3 new-to-new edges. For every potential K5 meeting the three new vertices it emits both exact colour-forbidding clauses. Thus each instance has 123 Boolean variables; the Exoo planted two-vertex recovery has 6,102 clauses.
- Controls passed. Exhaustive enumeration of all 262,144 assignments for a 5-core plus three new vertices agrees exactly between the clause encoder and a direct K5 scan. Deleting Exoo vertices 40 and 41 and re-inserting their original incidences satisfies the two-new-vertex encoding, reconstructs Exoo byte-for-byte, and is K5-free.
- Using PySAT Glucose4 1.9.dev23 with deterministic pair order and no seed, exhausted all 861 distinct pairs: 861 UNSAT, 0 SAT, 0 final timeouts. The initial 30.101-second pass solved indices 0--134 and timed out index 135; an explicit 110-second retry proved 135 UNSAT, and the 127.882-second resumed pass solved 136--860. No 43-vertex candidate exists in this exact labelled two-delete/three-insert neighbourhood, so there was no candidate to pass to `frontier check`.
- Preserved executable source, all three raw machine-readable run records, and `ramsey_c5_summary.json` under `.terramind/swarm/frontier-cloud-codex/`. `python3 -m py_compile` and `bun run check` passed (434 tests, 1 skipped, 0 failures). No scaffold, declarations change, submission, push, merge, or attempt PR was made.

## Deviations

- The exact sweep took about 278 seconds of solver wall time rather than the requested 30-minute ceiling, because Glucose exhausted every core quickly; extending the budget would only repeat the completed deterministic scope.
- The solver package was installed into disposable `/tmp/frontier-c5/pysat`, not the repository. The checked-in script retains its native deterministic DPLL fallback, but Glucose4 was the recorded backend for the full sweep.

## Concerns

- This is a local exclusion only: it fixes each induced 40-vertex subgraph of one labelled Exoo 42-colouring and tests three replacement vertices. It neither rules out other 42-vertex colourings nor decides `R(5,5)`.
- Although the planted control is a recovered 42-vertex graph and the baseline is Frontier-diagnosed, no 43-vertex graph was generated, so an authoritative `bun frontier check` of a 43 candidate was inapplicable.

## Follow-ups

1. Pivot to three-edge recolourings plus a single-vertex insertion using PR #59/c4 as the fixed baseline, retaining a direct final K5 scan for every candidate.
2. Expand the two-delete neighbourhood by permitting bounded recolouring of the 40-core, rather than treating it as frozen.
3. Any future 43-vertex graph must be wrapped as a disposable witness and pass both `bun frontier diagnose` and `bun frontier check`, with declarations left false pending human approval.
