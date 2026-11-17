# Handoff: kissing11-r2 (blocker-set exchanges and free backbone)

## Done
- **Attempt directory:** `attempts/witness.kissing-number-11/20261117-terramind-com-27c376`.
  - Kind: `writeup`.
  - Title: "Exact G-orbit pool (13.4e9 norm-36 vectors), blocker-set exchanges, free-backbone LNS and symmetric models from the 604, 2 h, no 605 found".
  - Declarations left false. Nothing submitted.
  - `bun frontier check` output, verbatim: `note: checked anyway; before submit: declarations: not confirmed. …` then `unchecked: Writeups are not machine-checked.`
  - `bun frontier validate` on the attempt complains only that the declarations are not confirmed.
  - `bun run check`: tsc clean, 434 pass, 0 fail; `validate` fails only on the unconfirmed declarations of the swarm attempts.
- **Result:**
  - Record 604; best reached 604. No configuration of 605 or more vectors was produced at any point.
  - `diagnose` on the baseline and both final search states: valid, 604, "ties the best known value". Both final states equal the baseline as sets.
  - Search started 2026-11-17 19:39:05 UTC; budget end 21:39:05.
  - `run.py` (seed 1): 19:39:05–21:33:28, normal end.
  - `symmetric.py`: 19:39:05 to about 20:10:25, normal end.
  - Walk process (seed 2): 20:21:47–21:34:14, normal end.
  - `/usr/bin/time` reports no non-zero exit status. No search process was left after the budget.
  - The searches ran unattended across the usage-limit pause, ending about 20:45 UTC. Logs are continuous and nothing was restarted.
- **What was built:**
  - The symmetry group G of the 604 (order 24,576 = 48 permutations × 512 signs).
  - An exact pool enumerated as G-orbits:
    - PURE: 8,676,220,498 vectors / 1,048,788 orbits. This includes all 101,189,550 integer norm-36 vectors, including (3,3,3,2,2,1).
    - PURE + MIXED-B: 13,365,555,706 vectors / 1,677,706 orbits.
    - Both counts are checked against a generating function.
  - An exact free-set server and an exact bitset max-clique solver.
- **Exact results, with their scope:**
  - **Blocker-set exchange.** Fixed part: the 604 minus the 51 blockers of the deepest hole (cos 1/√3). Free set: 10,570 pool vectors. Solver status OPTIMAL. The maximum replacement is 51, so no 52 exists (one hole representative tested).
  - **Symmetric models.** Six models solved to proven optimum 604: S ⋊ P′ for |P′| = 48, 24, 16, 12, 8 and 6 (orders 24,576 to 3,072). They were re-solved without the 604 hint after the run, with the same result. The S model and the |P′| = 2, 3 and 4 models are FEASIBLE only, with incumbent 604 and bounds 27,402, 10,832, 6,388 and 2,964.
  - **Neighbourhood solves.** 2,164 cap and blocker neighbourhoods were attempted. 1,937 were solved to proven optimality and none gave |R| + 1; 226 were skipped (free set over 30,000) and 1 timed out. All 1,012 equal-size move searches completed (status OPTIMAL) with no alternative set, so only 1 distinct configuration was visited. Each statement holds only for that cap and pool.
  - **Holes.** Every non-604 pool vector conflicts with at least 3 of the 604 (complete enumeration).
- **Evidence:**
  - Worktree `homeless-peak`, scratch `.terramind/scratch/kissing11-r2/`.
  - Logs: `logs/calibrate.log`, `logs/run.log`, `logs/run-records.jsonl`, `logs/run-walk2.log`, `logs/run-walk2-records.jsonl`, `logs/symmetric.log`, `logs/symmetric-check.log`, `logs/symmetric-results.json`, `logs/records-summary.json`, `logs/pool-summary.json`, `logs/orbits-*.log`, `logs/final-diagnose.log`, `pids.txt`, `search-start-utc.txt`.
  - Data: `reps_*.txt` (orbit files), `holes.json`, `group.txt`, `act604.txt`, `out/`, `out-walk2/`, `calib/`.
- **Calibration:**
  - The exact checker accepts the baseline and rejects two broken copies.
  - Cap solves restored 604 exactly after removing 1 extension vector, 1 backbone vector and 3 scattered vectors (m = 30 and 50).
  - The blocker form restored the extension puncture and the 3-point puncture.
  - Move mode found a different equal-size set on two planted instances.
  - The symmetric optima reproduce without the hint.

## Deviations
- **Solver.** The neighbourhood MIS is solved as a maximum clique of the compatibility graph with my own C solver, not as a HiGHS MILP with clique cuts. The free-set conflict graphs are nearly complete, and an edge-formulation run stalled.
- **Pool.** Mixed p + q√2 coordinates are allowed only in the 3 B coordinates, not in A. Norms below 36 and finer scales are excluded. The writeup states this.
- **Symmetric models.** Solved with CP-SAT, 1 worker, 300 s each. Only one random subgroup per order was tried.
- **Calibration gaps.** The blocker-form calibration on backbone punctures (84 and 109 blockers, free sets of 310k and 4.6M) was killed as too large and is not calibrated. The move-mode test (`calib_move.py`, 20:27 UTC) and the symmetric no-hint recheck (21:37–21:41 UTC) ran during and after the run, not before it.
- **Neighbourhood cap.** Neighbourhoods with more than 30,000 free vectors were skipped, for memory.

## Concerns
- **Memory cap exceeded.** `symmetric.py` peaked at 4.77 GB RSS, over the 3 GB cap, from its 15M-edge list and CP-SAT. The post-run recheck peaked at 3.13 GB. During calibration, one `mclq` call reached about 5 GB before I killed it. All three are disclosed in the writeup.
- **Cores.** `holes.py` ran alongside calibration. For about 10 s at 20:27, a third process (`calib_move.py`) ran beside the two searches.
- **Hole classes.** The 51 hole classes are grouped by cosine profile and are numerical. They are not proven to be G-classes, and only one representative per class was used.
- **Misleading log line.** `symmetric.log` has a leftover line "spot-check vs scalar: False" that tests nothing (it is explained in the writeup). The real cross-check found 0 disagreements on 20,000 pairs.
- **Exactness depends on my code.** The exact results depend on the correctness of `orbits.c` (the group coset handling, where a bug was found and fixed before the run), `freeset.c` and `mclq.c`. Calibration covers restore and move cases, not an independent re-enumeration.
- **Long claim.** The claim is several sentences.

## Follow-ups
- A weighted max-clique or MaxSAT solver with clique covers for the 12,099-orbit S-model, to get a real bound.
- A sparse or external-memory clique solver for caps of 90–110 members, whose free sets exceed 30,000.
- Extending the pool to mixed coordinates in A, or to the ½Z[√2] scale.
- Symmetric models for subgroups not containing S.
- Seeding the walk from other 604-point configurations, since the baseline admitted no equal-size move in any solved cap.
