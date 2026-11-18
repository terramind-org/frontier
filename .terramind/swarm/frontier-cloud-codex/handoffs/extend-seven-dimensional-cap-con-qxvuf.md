Outcome: done

## Done

- Created `swarm/frontier-cloud-codex--extend-seven-dimensional-cap-con-qxvuf-c6`, read `AGENTS.md`, showed `witness.ramsey-5-5`, and recovered the prior PR #59/#60 controls (`d602112b` and `320e21d5`) already present on this branch.
- Recovered Exoo's `g55.42` from `http://cs.indstate.edu/ge/RAMSEY/g55.42`; SHA-256 is the required `36ba90fb6727c9a876ecc127d8acbe9b9bf07a5b0925364a1b2f46f6e15052aa`. A JSON wrapper passes `bun frontier diagnose /tmp/frontier-c6/exoo.json --problem witness.ramsey-5-5` at value 42.
- Added `ramsey_c6_three_matching_insert.py`. It covers precisely the residual three-edge matchings after PR #60's vertex-cover-at-most-two scope: `15*C(42,6) = 78,686,790` labelled cases. It records every cursor in nine raw JSON slices.
- The filter is sound: it stores every monochromatic K5 created by each isolated flip, and rejects a matching only when one such K5 has no other flipped edge inside it. The remaining exact two- and three-minority K5 clauses are checked before a direct full two-colour K5 scan. The deterministic 8-vertex cross-check covered all 420 matching triples and found no false certificate rejection.
- Controls passed: the fixed Exoo 42 graph has an UNSAT 43rd-vertex insertion (2,308 clauses, 1,111 DPLL nodes); deleting vertex 41 and solving its 41-core recovers Exoo's incidence byte-for-byte (2,101 clauses, 2,273 nodes).
- Exhausted all 78,686,790 residual matchings with no timeout. The K5 certificate filter rejected 78,686,754. The remaining 36 passed a direct K5 scan and each had an UNSAT exact 43rd-vertex extension instance (47,364 DPLL nodes total); 0 SAT and 0 witness candidates. Slice wall time totals 205.041 seconds; the cursor ends at 78,686,790.
- Preserved executable source, controls, nine raw slice records, and `ramsey_c6_summary.json` under `.terramind/swarm/frontier-cloud-codex/`. `python3 -m py_compile` and `bun run check` passed (434 tests, 1 skipped, 0 failures). No scaffold, declaration change, submission, push, merge, or attempt PR was made.

## Deviations

- The terminal launcher failed, so the one-core search was executed as nine bounded foreground slices. It completed in 205.041 seconds rather than using the full 30-minute ceiling.
- No external SAT package was needed: the final 36 extension instances were resolved by the reproducible native unit-propagating DPLL.

## Concerns

- This is a local exclusion only: three old-edge flips forming a matching, plus one inserted vertex, around one labelled Exoo 42-colouring. It does not rule out other 42-colourings or decide `R(5,5)`.
- No 43-vertex graph was generated, so a full Frontier check of a candidate was inapplicable.

## Follow-ups

1. Pivot to selected 39-core/four-new-vertex SAT instances (three deleted Exoo vertices), with planted recovery and deterministic timeout rotation.
2. Expand the two-delete neighbourhood by permitting bounded recolouring of the frozen 40-core.
3. Any future 43-vertex graph must be wrapped as a disposable witness and pass both `bun frontier diagnose` and `bun frontier check`, with declarations left false pending human approval.
