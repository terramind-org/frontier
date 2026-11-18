# A seven-colour Schur partition of 1..1698 that ties the public bound

`witness.json` colours 1..1698 with colours 0..6 so that no colour class contains x, y and x + y (x = y included).
`bun frontier diagnose` reports `value: 1698 (best known 1696)`, `valid: yes`, `beats the best known value`. That comparison is against the Frontier catalog's value, 1696 (Rowley, arXiv:2107.03560), and nothing else.

A public lower bound of 1698 already existed when this partition was found: a Zenodo deposit of 26 October 2026 (see "Prior public bound" below). This witness ties that bound with a different partition. It is not a new record. The exact value of S(7) remains unknown, and nothing here gives an upper bound on it.

SHA-256 of `witness.json`: `a3bd293ccede7f6c09530333b54e84f3c2feca3104cf323fdcaca479e7d34da5`.

## Prior public bound

- **The deposit.** Zenodo DOI [10.5281/zenodo.23670665](https://doi.org/10.5281/zenodo.23670665) (version 1; concept DOI 10.5281/zenodo.23670664), "A sum-free 7-colouring of {1, ..., 1698}: S(7) >= 1698 and R_7(3) >= 1700", by Kerem Özdemir, licence CC BY 4.0. Zenodo dates version 1 at 26 October 2026, 16:20:42 UTC, and DataCite gives the issue date 2026-10-26. It states S(7) >= 1698 and R_7(3) >= 1700. Its description says that colouring is also symmetric, c(x) = c(1699 - x), and was found by local search seeded from Rowley's 1696 colouring.
- **Its certificate passes the Frontier verifier.** `S7_1698.txt` (SHA-256 `33f2f6c39fcf21dc32b13336ac481fbc175126fe73f6074b7632e5d8d47809e7`) uses colours 1..7. Converted to `{"colors": [...]}` with colours 0..6, `bun frontier diagnose --problem witness.schur-7` reports `value: 1698`, `valid: yes`.
- **This partition is a different one.** It was found independently on 17 November 2026, without knowledge of the deposit. Over all 5,040 relabellings of the seven colours, the smallest Hamming distance between the two colourings is 172 positions. Their sorted class sizes also differ: 146, 164, 182, 194, 234, 364, 414 here, against 146, 150, 168, 204, 206, 302, 522 in the deposit.
- **Why the checker says "beats".** The Frontier catalog still lists 1696, so `bun frontier check` prints, verbatim:

  ```text
  verified: Valid witness for witness.schur-7 with value 1698; beats the best known (1696, Rowley, arXiv:2107.03560).
  ```

  The checker compares against the catalog only. Against the public literature this witness is a tie at 1698.

## Ramsey consequence

This consequence was derived by the independent audit (see below). Colour edge ij of the complete graph K_1699 on vertices 0..1698 by the colour class of |i - j|. A monochromatic triangle i < j < k would give two distances j - i and k - j whose sum k - i has the same colour, which the partition excludes. So the colouring gives a seven-edge-colouring of K_1699 with no monochromatic triangle, and R_7(3) >= 1700. That is the same bound the October deposit states.

## The construction

This uses Rowley's construction with a different six-colour base. In Rowley's paper (arXiv:2107.03560, §3) the 1696 partition is built like this:

1. Fix a 6-colour sum-free partition of 1..536 (the base).
2. Put 537 in a seventh colour (the pivot).
3. Reflect the base and the pivot by x -> 1697 - x.
4. Tree-search the middle.

The workbook holds a fully symmetric example that Rowley selected. The run here used SAT with full reflection x -> 1699 - x at N = 1698:

- 1..536 use colours 0..5. This is base `b1_0014`, which differs from Rowley's base in 28 of 536 positions: 7, 45, 67, 70, 72, 88, 156, 164, 191, 203, 207, 254, 330, 334, 337, 346, 373, 381, 393, 414, 449, 463, 465, 466, 467, 470, 492 and 530.
- 537 has colour 6, and colour 6 lies inside 537..1162.
- The colouring is fully symmetric: c(x) = c(1699 - x) for every x.

The divisibility obstruction rules out full reflection at N = 1697: if N + 1 = 3t, then t and 2t = N + 1 - t share a colour and t + t = 2t is a monochromatic triple, and 1698 = 3 x 566. For N = 1698 (N + 1 = 1699) the obstruction does not apply.

How the base was found:

- `b1_0008` was a 6-colour partition of 1..536 generated on its own. It was a SAT re-solve of Rowley's base with 282 of its 536 positions freed and at least 20 forced changes; it differs from Rowley's base in 20 positions.
- It passed the 1696 check: a 1696 completion with the base and pivot reflected (base fixed, 537 in colour 6, 1..537 reflected by x -> 1697 - x, the middle searched by SAT without a symmetry constraint).
- `b1_0014` is a joint re-solve of that 1696 structure. About 70% of `b1_0008`'s base positions (375) were freed, at least 10 had to change, and the variables had a random renaming. The two bases differ in 16 positions.
- With `b1_0014` fixed, 537 in colour 6 and full reflection x -> 1699 - x, the instance at N = 1698 was SAT at the root: 0 conflicts and 0 decisions in 0.35 s, CaDiCaL 3.1.0, seed 781351734.

`reproduce.py` replays that call. It takes only the first 536 entries of its first input as the base, reconstructs the middle and the suffix, and uses its second input solely for comparison. It gave a colouring identical to `witness.json`; the independent audit repeated this with `witness.json` as both inputs and got the same SHA-256.

## Provenance and rights

- The baseline is Rowley's 1696 colouring from the ancillary workbook of arXiv:2107.03560 (`https://arxiv.org/src/2107.03560v1/anc/Specimens_S_7____TFTs-4,5,6.xls`, SHA-256 `c50cf981c1c437557b261cb8a66e193ee2cf77a8a50b0ae70c986b1c1cbb6fbb`), read with `extract.py`.
- The six-colour base of this witness descends from the workbook's 1..536 prefix: with the workbook's colour labels shifted to 0..5, it equals that prefix except at the 28 positions listed above. Positions 537..1698 come from the SAT call and the reflection.
- arXiv distributes that paper under its non-exclusive distribution licence (`https://arxiv.org/licenses/nonexclusive-distrib/1.0/`), not under CC BY 4.0, although the Frontier catalog labels the reference CC BY 4.0.
- The witness is a new colouring vector, not a copy of the workbook. These are stated as facts for the submitter to weigh before confirming the rights declaration; this file does not decide that question.

## Method and parameters

Everything ran in scratch, normally two processes at a time, with a brief third-process overlap during breakout calibration. CPU time and peak memory were not measured. The main SAT runs used the CaDiCaL 3.1.0 binary (commit 6b3d70b) with a wall-clock `-t` limit; an early calibration used PySAT's CaDiCaL 1.9.5. Status comes from the return code (10 SAT, 20 UNSAT, 0 time limit), never from console text. Completed calls have status records with seed, conflicts and seconds; duplicate generation summaries and interrupted calls have less detail.

The encoding (`schur.py`):

- one variable per (representative, colour);
- exactly-one per integer;
- one clause per x <= y, x + y <= N and colour;
- mirrors are variable identifications;
- fixed and forbidden colours are unit clauses.

The binary wrapper in `schur.py` renames the variables by a seeded random permutation and runs CaDiCaL with `--seed`, `--shuffle` and `--shufflerandom`. The final cube runner in `cnc.py` passes a seed without those flags.

Lines and their runs:

- **Many bases (`bases.py`, seed 1, one process, 19:25:35 to 21:23:18 UTC, exit 0).**
  - Base generation: joint (random fractions or windows of a source base freed, or a short base 1..m with m in {300..500}, solved inside Rowley's 1696 structure), or alone (a 6-colour partition of 1..536 only). Each new base must differ from its source in at least D freed positions (sequential-counter cardinality from python-sat).
  - Validation: a 1696 completion with the base and pivot reflected (base fixed, 537 in colour 6, 1..537 reflected by x -> 1697 - x), 90 s.
  - Modes for each passing base: `shift1697` (base mirrored by x -> 1698 - x, middle free) and `sym1698` (full mirror x -> 1699 - x). Passing bases number 1, 4, 7 and so on, and any base 120 or more positions from Rowley's, also got `free1697` (base fixed, everything above free), `partial1697` (mirror only on 567..848) and `sym1698soft400` / `sym1699soft400` (only 1..400 of the base fixed, 401..536 free without colour 6). Limit 75 s each.
- **Cube-and-conquer (`cnc.py`), calibration only, 19:25:42 to 19:41:27 UTC.** Fixed prefixes 1..F of Rowley's colouring at N = 1696. Each split proposed 16 cubes, chosen on the free integers with the fewest allowed colours. Only calibration samples were run.
- **Push (`push.py`, three runs, seeds 2, 3 and 4, 19:42:48 to 20:02:29 UTC).** Targets N = 1699 to 1701 from the 1698 base, and new bases that reach 1698. Each run was stopped by SIGTERM to restart with a changed mode list, so only the last version of `push.py` is included. Modes:
  - symmetric or near-symmetric (mirror dropped within 40 of (N + 1)/3);
  - base fixed on 1..F with colour 6 kept off 1..m;
  - top windows of the 1698 colouring;
  - base fixed with everything above free.

  Limits were 45 to 90 s.
- **Long calls (`longq.py`, seed 5, 20:02:29 to 20:52:22 UTC, exit 0).** One 1698 calibration, then five calls with a 600 s solver limit at N = 1699, 1700 and 1701.
- **Local search (`breakout.cpp` via `ls_runs.sh`, 20:52:56 to 21:18:57 UTC, exit 0).** Clause-weighting breakout at N = 1699, with 1% random-walk moves and 780 s per run. Run A (seed 11) started from the 1698 colouring; run B (seed 12) from the 1697 colouring.

## Calibration (logs in scratch)

- **Checker.** Rowley's colouring (from the arXiv ancillary workbook) has 0 violations. A copy with 2 given the colour of 1 has 19. The repo verifier accepts the first at 1696 and rejects the second.
- **Small known answers, with the binary.** K = 3: N = 13 SAT, N = 14 UNSAT. K = 4: N = 44 SAT, N = 45 UNSAT (221 s). The SAT models had 0 violations.
- **Rowley's base with base and pivot reflected (x -> 1697 - x).** A 1696 completion: SAT, decoded 0 violations, accepted by `diagnose`. It differs from Rowley's colouring in 182 positions.
- **Planted refill.** 300 middle positions of Rowley's colouring freed at 1696: SAT, accepted by `diagnose`.
- **Full mirror x -> 1698 - x at 1697.** UNSAT at the root, as the divisibility argument predicts.
- **Cube-and-conquer at N = 1696.** The cube that agrees with Rowley's colouring was SAT in 29 s with F = 446 and in 33 s with F = 400. The first F = 300 run logged five time limits at 52 to 60 s, and the later known-positive cube hit the 90 s limit at F = 350 and F = 300. A long cube run at F <= 350 would therefore not be calibrated.
- **Long-call 1698 control** (1..150 of the base fixed, colour 6 off 1..300): SAT, 0 conflicts.
- **Breakout.** It repairs the 1698 colouring with 60 or 400 random positions recoloured (2,409 and 9,475 starting violations) to 0 violations in under 1 s.

## Measured

- **Bases.** The many-bases line generated 60 distinct base vectors by the end (2 duplicates discarded), 20 to 60 positions from Rowley's base; the push line separately produced one additional base, `p4_0001`. 55 of the 60 gave a 1696 completion with the base and pivot reflected that decoded with 0 violations:
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
- **Push at 1699 to 1701.** Both bases, `b1_0014` and `p4_0001`, were tested at 1699 and 1700; only `b1_0014` was tested at 1701. Every symmetric or near-symmetric call fixing 1..200 or more of a base was UNSAT within 9 s. Soft push modes varied the colour-6 exclusion cutoff with the prefix length and left 537 free. Top windows of 300 to 900 freed positions of the 1698 colourings at 1699 were UNSAT at the root. Calls fixing only 1..150, and the base-fixed calls with everything above free, hit their time limit (75 or 90 s).
- **Long calls** (600 s solver limit; measured elapsed times of the time-limited calls were slightly above 600 s):
  - `sym1699_F150_m300`: time limit, 3,916,191 conflicts;
  - `free1699_base536`: time limit;
  - `sym1699_F100_m300`: time limit;
  - `near1700_F150_m300`: time limit;
  - `sym1701_F150_m300`: UNSAT, 532 s, 3,242,387 conflicts.
- **Local search at 1699.** Recounted on the saved best vectors, run A's has 5 monochromatic triples and run B's has 6. The logged step counts (4,449,280 for run A, 9,018,368 for run B) include iterations spent increasing clause weights without a recolouring. A low count is not a sign that a 1699 partition is close: the audit's breakout run on the impossible K = 3, N = 14 instance also reached a single violation (see below).
- **UNSAT evidence.** No DRAT or LRAT proofs were kept. UNSAT results are solver statistics only.
- **Timing.** The first search process started at 19:25:35 UTC and the last ended at 21:23:18 UTC (117 min 43 s). CaDiCaL found the witness at 19:34:16 UTC, about nine minutes into the run, from the fourth distinct base generated. The searches ran unattended for about 10 minutes (around 20:30 to 20:42 UTC) while the author was paused at a usage limit; the bases and long-call logs contain results from that interval. The pause was inside the budget, and nothing ran past it.

## Inferred, not proved

- In the `shift1697` and `sym1698` modes, with the full base fixed, every tested instance was rejected at the root except `sym1698` on `b1_0014`, which gave this witness. Leaving 401..536 free (`sym1698soft400`) gave three distinct 1698 colourings, so the base matters.
- The F >= 200 push result applies only to the specific templates and prefix vectors tried (two bases, the targets listed above). It is an observation, not a proof.
- For the 300- and 500-position top windows of `p4_0001`, fixed reflection pairs block each colour at 1699. At window sizes 700 and 900, CaDiCaL also returned UNSAT at the root, but direct fixed pairs summing to 1699 block only six colours and zero colours respectively, so that argument does not explain those two.

## Not covered

- No cube-and-conquer run at N >= 1697: core 2 went to pushing N once 1698 was found.
- No base far from Rowley's (all within 60 positions).
- No independent bases built from symmetric templates.
- No proofs for the UNSAT results.
- No solver time limit above 600 s.

## What a later attempt should try

From the independent audit, first:

- **Method:** the recently published 537-element six-colour bases (arXiv:2610.31362, S(6) >= 537) with pivot 538, as a different construction.
- **Method:** the October 2026 deposit's 1698 partition as a distinct seed for repair search.
- **Method (time relevant only to the short-prefix timeouts):** cube-and-conquer with shorter prefixes, or with more diverse low positions, for the pivot-537 family. The 600 s calls at F = 100 and 150 were undecided.
- Keep instance specifications and proof certificates for any broad UNSAT statement.

From the original run:

- Near-symmetric constructions at 1700, since 1701 = 3 x 567.
- Non-symmetric extensions that free low integers as well as high ones.

## Independent audit

A second model from another family (gpt-6.2-sol) audited this attempt before submission. It wrote its own checker before reading the author's and found zero monochromatic triples in `witness.json`, including x = y. It replayed the completion with a CaDiCaL build at the same commit and got output with the identical SHA-256, built a separate SAT encoder that also reproduced the witness from the 1..536 prefix, reran representative positive and negative instances, recounted the logs, and ran the literature search that found the October 2026 deposit. Named statements in this file and in `attempt.yaml` were corrected to match its findings: the title and claim, the comparison with the public bound, the timing and breadth of the search, the description of the 1696 validation, the scope of each negative result and the provenance of the base. The audit is an opinion backed by reruns, not a check by the repository verifier.

Measurements made by the audit, not by the original run:

- **Search counts.** 196 generation calls in `bases.py` produced 60 new bases, 2 duplicates, 100 UNSAT and 34 time limits. The 27th distinct base was logged at 20:10:06 UTC. All 55 saved 1696 validation outputs are sum-free and have 2 to 10 asymmetric positions (`b1_0008` 4, `b1_0014` 2, the baseline control 4), so the 1696 check reflected only the base and pivot.
- **Standalone bases under full mirror.** A separate full-mirror recheck of the nine standalone bases returned SAT for the same four and UNSAT for the same five.
- **Push logs.** 31 UNSAT and 9 time-limited target calls (1699: 16/5, 1700: 10/3, 1701: 5/1); the longest logged UNSAT took 8.4 s.
- **Negative reruns.** Its own encoder confirmed UNSAT for the exact `b1_0014` `shift1697` restriction, the `p4_0001` fixed-base symmetric 1699, the `p4_0001` 900-position top window at 1699, symmetric 1699 with `p4_0001`'s 1..200 fixed, colour 6 forbidden on 201..350 and 537 free (0.95 s, 9,838 conflicts), and full-mirror 1701 with 1..150 fixed to `b1_0014`, colour 6 forbidden on 151..300 and 537 free (152.53 s, 2,090,030 conflicts). These are restricted instances, not general bounds.
- **Breakout calibration.** The copied breakout program repaired the saved 9,475-violation perturbation to zero in 426 steps; on the impossible K = 3, N = 14 instance it reached one violation and stopped at its 1 s limit.
- **Controls.** Its encoder returned SAT for a fully mirrored 1696 from the workbook prefix, SAT at (K, N) = (3, 13) and UNSAT at (3, 14); the shipped binary returned SAT at (4, 44).

## Files

- `schur.py`: encoder, solver wrapper, checker.
- `extract.py`: baseline from the workbook.
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

The CaDiCaL binary is expected at `bin/cadical-src/build/cadical` relative to the scripts. Build it from github.com/arminbiere/cadical at commit 6b3d70b. Replaying the base discovery and the negative runs would also need the workbook and extraction step, pinned Python dependencies, the original controller arguments and logs, and the two earlier versions of `push.py`, none of which are included.
