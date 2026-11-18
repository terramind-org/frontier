Outcome: done

## Done

- Created branch `swarm/frontier-cloud-codex--extend-seven-dimensional-cap-con-qxvuf-c4`, read `AGENTS.md`, and showed `witness.ramsey-5-5`. Primary sources still give the open interval `43 <= R(5,5) <= 46`: Exoo's 1989 42-vertex lower-bound graph and Angeltveit--McKay's 2026 upper-bound paper (DOI 10.1002/jgt.70029).
- Retrieved Exoo's `g55.42` from `http://cs.indstate.edu/ge/RAMSEY/g55.42`; SHA-256 is the requested `36ba90fb6727c9a876ecc127d8acbe9b9bf07a5b0925364a1b2f46f6e15052aa`. It has 42 symmetric zero-diagonal binary rows. `bun frontier diagnose /tmp/frontier-c4/baseline/witness.json --problem witness.ramsey-5-5` accepted it at value 42, tying the known value.
- Added reproducible one-core source `ramsey_c4_recolor_insert.py` and its raw JSON output `ramsey_c4_result.json` beside this handoff. The script represents a prospective 43rd vertex with 42 Boolean incident-edge variables; every monochromatic K4 produces an exact four-literal prohibition. It ran in 48.636 s on the cloud worker.
- Reproduced fixed-graph extension UNSAT, independently of the earlier run: 2,308 constraints (1,132 colour-0, 1,176 colour-1), 1,111 DPLL nodes, UNSAT. The higher node count reflects generic branch ordering; it has the same fixed-graph scope.
- Positive control: deleted vertex 41, generated the 2,101 K4 constraints of the 41-vertex core, and recovered a satisfying incident-edge vector in 2,273 DPLL nodes. It matched Exoo's deleted incidence vector byte-for-byte. The rebuilt 42-vertex JSON was accepted by `bun frontier diagnose`, value 42.
- Exhausted every one-edge recolouring: all 861 choices completed; 853 immediately create a monochromatic K5, and exact extension is UNSAT for each of the remaining 8 (9,120 aggregate DPLL nodes). No one-flip 42-graph extends to 43.
- Exhausted every two-edge recolouring: all 370,230 edge pairs accounted for; an exact K5-delta filter rejected 370,206, and all remaining 24 valid recolourings had UNSAT 43rd-vertex extensions (29,554 aggregate DPLL nodes). There were 0 SAT candidates and 0 timed-out/unstarted cases. Each of the 24 was directly rechecked for absence of a monochromatic K5 before DPLL.
- Verified the script compiles with `python3 -m py_compile`; `bun run check` passed (434 tests, 1 skipped, 0 failures). No attempt, declarations change, submission, push, or PR was made.

## Deviations

- The requested approximately 30-minute budget was not consumed: after the exact filter was corrected and independently asserted, the entire stated one- and two-flip scope ended in 48.636 s. Continuing would duplicate completed cases rather than increase coverage.
- `gh api user` returned no login in this cloud worker, so no disposable `frontier new` scaffold was created. The repository's witness diagnostic was run directly on both the sourced 42 graph and the planted recovery; no candidate of size 43 exists to check.

## Concerns

- This is not a global exclusion and does not decide R(5,5). It excludes only 43rd-vertex insertion after one or two edge flips of this single labelled Exoo 42-vertex graph.
- The two-flip K5 filter is exact for two flips: for every original K5 and target colour it records the one or two original mismatching edges required to become monochromatic, then validates every retained pair by a full K5 scan. The result remains conditioned on the supplied labelled graph, not its whole isomorphism class or other 42-vertex colourings.

## Follow-ups

1. Search three-edge recolouring plus insertion, preferably with an incremental SAT instance and the same direct K5 validation; this is the next radius not covered here.
2. Implement the requested two-vertex-delete/three-vertex-reinsert SAT neighbourhood for selected Exoo cores, with the 41-to-42 planted recovery retained as its control.
3. If a 43-vertex candidate appears, write it only in a fresh disposable scaffold and run both `bun frontier diagnose` and `bun frontier check`; keep declarations false pending human approval.
