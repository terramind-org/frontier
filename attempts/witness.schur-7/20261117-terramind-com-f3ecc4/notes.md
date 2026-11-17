# A seven-colour Schur partition of 1..1698

`witness.json` colours 1..1698 with colours 0..6 so that no colour class contains x, y and x + y (x = y included).
`bun frontier diagnose` reports `value: 1698 (best known 1696)`, `valid: yes`, `beats the best known value`.
The published record is 1696 (Rowley, arXiv:2107.03560), so this is 2 more. Nothing here gives an upper bound on S(7).

SHA-256 of `witness.json`: `a3bd293ccede7f6c09530333b54e84f3c2feca3104cf323fdcaca479e7d34da5`.

## The construction

This is Rowley's own method, run one order higher. Rowley built his 1696 partition like this:

1. Fix a 6-colour sum-free partition of 1..536 (the base).
2. Put 537 in a seventh colour.
3. Mirror x -> 1697 - x.
4. Search the middle.

The witness keeps the same shape at N = 1698:

- 1..536 use colours 0..5. This is base `b1_0014`, which differs from Rowley's base in 28 of 536 positions: 7, 45, 67, 70, 72, 88, 156, 164, 191, 203, 207, 254, 330, 334, 337, 346, 373, 381, 393, 414, 449, 463, 465, 466, 467, 470, 492 and 530.
- 537 has colour 6, and colour 6 lies inside 537..1162.
- The colouring is fully symmetric: c(x) = c(1699 - x) for every x.

A full mirror needs N + 1 not divisible by 3. If N + 1 = 3t, then t + t = 2t = N + 1 - t forces a monochromatic triple. That rules out 1697 (1698 = 3 x 566) and allows 1698 (1699).

How the base was found:

- `b1_0008` was a 6-colour partition of 1..536 generated on its own. It was a SAT re-solve of Rowley's base with 282 of its 536 positions freed and at least 20 forced changes; it differs from Rowley's base in 20 positions.
- It passed the 1696 check: base fixed, 537 in colour 6, mirror x -> 1697 - x, middle solved.
- `b1_0014` is a joint re-solve of that 1696 structure. About 70% of `b1_0008`'s base positions were freed, at least 10 had to change, and the variables had a random renaming.
- With `b1_0014` fixed and 537 in colour 6, the symmetric instance at N = 1698 was SAT at the root: 0 conflicts in 0.35 s, CaDiCaL 3.1.0, seed 781351734.

`reproduce.py` replays that call. It gave a colouring identical to `witness.json`.

## Method and parameters

Everything ran in scratch, on at most 2 cores at a time. All solver calls used the CaDiCaL 3.1.0 binary (commit 6b3d70b) with a wall-clock `-t` limit. Status comes from the return code (10 SAT, 20 UNSAT, 0 time limit), never from console text. Every call is logged with its seed, conflicts and seconds.

The encoding (`schur.py`):

- one variable per (representative, colour);
- exactly-one per integer;
- one clause per x <= y, x + y <= N and colour;
- mirrors are variable identifications;
- fixed and forbidden colours are unit clauses.

Each call renames the variables by a seeded random permutation and runs CaDiCaL with `--seed`, `--shuffle` and `--shufflerandom`.

Lines and their runs:

- **Many bases (`bases.py`, seed 1, one core, 19:25:35 to 21:23:18 UTC, exit 0).**
  - Base generation: joint (random fractions or windows of a source base freed, or a short base 1..m with m in {300..500}, solved inside Rowley's 1696 structure), or alone (a 6-colour partition of 1..536 only). Each new base must differ from its source in at least D freed positions (sequential-counter cardinality from python-sat).
  - Validation: base fixed, 537 in colour 6, mirror x -> 1697 - x, N = 1696, 90 s.
  - Modes for each passing base: `shift1697` (base mirrored by x -> 1698 - x, middle free) and `sym1698` (full mirror x -> 1699 - x). Every third passing base, and any base 120 or more positions from Rowley's, also got `free1697` (base fixed, everything above free), `partial1697` (mirror only on 567..848) and `sym1698soft400` / `sym1699soft400` (only 1..400 of the base fixed, 401..536 free without colour 6). Limit 75 s each.
- **Cube-and-conquer (`cnc.py`), calibration only, 19:25:42 to 19:41:27 UTC.** Fixed prefixes 1..F of Rowley's colouring at N = 1696. Cubes split on the free integers with the fewest allowed colours (16 cubes).
- **Push (`push.py`, three runs, seeds 2, 3 and 4, 19:42:48 to 20:02:29 UTC).** Targets N = 1699 to 1701 from the 1698 base, and new bases that reach 1698. Each run was stopped by SIGTERM to restart with a changed mode list, so only the last version is included. Modes:
  - symmetric or near-symmetric (mirror dropped within 40 of (N + 1)/3);
  - base fixed on 1..F with colour 6 kept off 1..m;
  - top windows of the 1698 colouring;
  - base fixed with everything above free.

  Limits were 45 to 90 s.
- **Long calls (`longq.py`, seed 5, 20:02:29 to 20:52:22 UTC, exit 0).** One 1698 calibration, then five calls of 600 s at N = 1699, 1700 and 1701.
- **Local search (`breakout.cpp` via `ls_runs.sh`, 20:52:56 to 21:18:57 UTC, exit 0).** Clause-weighting breakout at N = 1699, with 1% random-walk moves and 780 s per run. Run A (seed 11) started from the 1698 colouring; run B (seed 12) from the 1697 colouring.

## Calibration (logs in scratch)

- **Checker.** Rowley's colouring (extracted from the arXiv ancillary spreadsheet, SHA-256 c50cf981…6fbb) has 0 violations. A copy with 2 given the colour of 1 has 19. The repo verifier accepts the first at 1696 and rejects the second.
- **Small known answers, with the binary.** K = 3: N = 13 SAT, N = 14 UNSAT. K = 4: N = 44 SAT, N = 45 UNSAT (221 s). The SAT models had 0 violations.
- **Rowley's base, 537 in colour 6, mirror x -> 1697 - x.** SAT at 1696, decoded 0 violations, accepted by `diagnose`. It differs from Rowley's colouring in 182 positions.
- **Planted refill.** 300 middle positions of Rowley's colouring freed at 1696: SAT, accepted by `diagnose`.
- **Full mirror x -> 1698 - x at 1697.** UNSAT at the root, as the divisibility argument predicts.
- **Cube-and-conquer at N = 1696.** The cube that agrees with Rowley's colouring was SAT in 29 s with F = 446 and in 33 s with F = 400. It timed out at 90 s for F = 350 and F = 300. A long cube run at F <= 350 would therefore not be calibrated.
- **Long-call 1698 control** (1..150 of the base fixed, colour 6 off 1..300): SAT, 0 conflicts.
- **Breakout.** It repairs the 1698 colouring with 60 or 400 random positions recoloured (2,409 and 9,475 starting violations) to 0 violations in under 1 s.

## Measured

- **Bases.** 60 distinct bases were generated (2 duplicates discarded), 20 to 60 positions from Rowley's base. 55 reproduced a mirrored 1696 completion that decoded with 0 violations:
  - all 51 joint bases;
  - 4 of the 9 alone bases (5 were UNSAT).
- **Modes over the 55 passing bases:**

  | Mode | SAT | UNSAT | Timeout (75 s) | Notes |
  |---|---|---|---|---|
  | `shift1697` | 0 | 55 | 0 | all UNSAT with 1 conflict |
  | `sym1698` | 1 (`b1_0014`) | 54 | 0 | all UNSAT with 1 conflict |
  | `free1697` | 1 (`b1_0014`, 4,318 conflicts) | 0 | 18 | |
  | `partial1697` | 0 | 19 | 0 | |
  | `sym1698soft400` | 3 (`b1_0014`, `b1_0134`, `b1_0182`) | 16 | 0 | |
  | `sym1699soft400` | 0 | 19 | 0 | |

  The three 1698 colourings are distinct (SHA-256 prefixes a3bd293c, 36b53ef4, e8e370c7), and `diagnose` accepts all three.
- **Push at 1699 to 1701.** Every symmetric or near-symmetric call fixing 1..200 or more of a base was UNSAT within 9 s. That covers bases `b1_0014` and `p4_0001` and the targets 1699, 1700 and 1701. Top windows of 300 to 900 freed positions at 1699 were UNSAT at the root. Calls fixing only 1..150, and the base-fixed calls with everything above free, timed out (75 or 90 s).
- **Long calls:**
  - `sym1699_F150_m300`: time limit, 600 s, 3,916,191 conflicts;
  - `free1699_base536`: time limit, 600 s;
  - `sym1699_F100_m300`: time limit, 600 s;
  - `near1700_F150_m300`: time limit, 600 s;
  - `sym1701_F150_m300`: UNSAT, 532 s, 3,242,387 conflicts.
- **Local search at 1699.** Best 5 violations (run A, 4,449,280 steps) and 6 violations (run B, 9,018,368 steps).
- **UNSAT evidence.** No DRAT or LRAT proofs were kept. UNSAT results are solver statistics only.
- **Timing.** The first search process started at 19:25:35 UTC and the last ended at 21:23:18 UTC (117 min 43 s). The 1698 colouring was found at 19:34:16 UTC. The searches ran unattended for about 10 minutes (20:31 to 20:42 UTC) while the author was paused at a usage limit. That pause was inside the budget, and nothing ran past it.

## Inferred, not proved

- Unit propagation alone rejects Rowley-style bases near Rowley's own at the shifted mirror x -> 1698 - x (N = 1697) and at x -> 1699 - x (N = 1698) for most bases. A few bases pass at 1698, so the base matters. Fixing the full base made `b1_0014` the only success; leaving 401..536 free found three.
- The symmetric pivot-537 structure at 1699 to 1701 appears to need a base prefix unlike Rowley's below 200: fixing 1..200 was always UNSAT quickly. This is an observation on two bases, not a proof.
- A colouring symmetric under x -> N + 1 - x cannot be extended to N + 1 by recolouring only high integers, because every colour then has a pair summing to N + 1. That is why top windows failed.

## Not covered

- No cube-and-conquer run at N >= 1697: core 2 went to pushing N once 1698 was found.
- No base far from Rowley's (all within 60 positions).
- No independent bases built from symmetric templates.
- No proofs for the UNSAT results.
- No calls longer than 600 s.

## What a later attempt should try

- Symmetric N = 1699 (x -> 1700 - x) with only a short prefix fixed, or none, using cube-and-conquer with long cubes. The 600 s calls at F = 100 and 150 were undecided.
- Bases whose low part (1..200) differs from Rowley's.
- Near-symmetric constructions at 1700, since 1701 = 3 x 567.
- Non-symmetric extensions that free low integers as well as high ones.

## Files

- `schur.py`: encoder, solver wrapper, checker.
- `extract.py`: baseline from the spreadsheet.
- `calib.py`, `calib_bin.py`: calibration.
- `bases.py`: many-bases line.
- `cnc.py`: cube-and-conquer.
- `push.py`: last version of the push line.
- `longq.py`: long calls.
- `blocked.py`: arithmetic check of fixed-pair blocking.
- `breakout.cpp`, `ls_runs.sh`: local search.
- `run.sh`: process wrapper that records exit status.
- `indep_check.py`, `indep_check2.py`: two independent brute-force checkers.
- `summarize.py`: log counts.
- `reproduce.py`: replays the 1698 call.

The CaDiCaL binary is expected at `bin/cadical-src/build/cadical` relative to the scripts. Build it from github.com/arminbiere/cadical at commit 6b3d70b.
