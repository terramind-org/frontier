# Pivot 538 over the published 537-element six-colour bases, and the Zenodo 1698 partition as a seed: no partition of 1..1699

**Outcome.** No partition of 1..N into seven sum-free sets with N ≥ 1699 was found. The largest colouring this
search produced with pivot 538 has N = 1612. The search also rebuilt valid partitions of 1..1698 from the two known
1698 colourings, but these were calibration controls and only tie the public bound. This writeup is not
machine-checked and gives no upper bound on S(7).

## Prior public bound

- The catalog lists 1696 (Rowley, arXiv:2107.03560, 2021).
- A public Zenodo deposit already gives **S(7) ≥ 1698**: "A sum-free 7-colouring of {1, ..., 1698}: S(7) >= 1698 and
  R_7(3) >= 1700", DOI 10.5281/zenodo.23670665 (v1, 26 October 2026, CC BY 4.0). Its file `S7_1698.txt` has SHA-256
  `33f2f6c3…809e7`. My checker and `bun frontier diagnose` accept it at 1698 after relabelling colours 1..7 to 0..6.
- Another partition of 1..1698 is in this repo (attempt `20261117-terramind-com-f3ecc4`).
- Searched on 17 November 2026 (UTC): the arXiv listing for "Schur number" (newest first), a web search for
  S(7) ≥ 1699/1700/1701, the Zenodo version history, and the deposit author's announcement page. The round-2 audit
  of this problem also checked DS1 rev. 18, OEIS and Leaps in Bounds. No public value above 1698 was found.

The target for this search was therefore N ≥ 1699.

## Inputs (third-party data, cited and not copied)

- **537-element bases.** Chen, Zhu and Long, "A new lower bound for the sixth Schur number: S(6) ≥ 537",
  arXiv:2610.31362v1 (22 October 2026, CC BY 4.0). The ancillary file `solutions537.txt` lists 131 pairwise
  inequivalent six-colour sum-free partitions of 1..537, in five families: F1 (107), F2 (14), F3 (5), F4 (4) and
  F5 (1). Its SHA-256 `fcae1cd5…4631b6` matches the deposit's `SHA256SUMS`.
  - My checker (`check.py`) finds no monochromatic x + y = z in any of the 131 bases.
  - The 125 bases of families F1, F2 and F4 are symmetric under x → 538 − x, and their sixth colour spans 151..387.
    The F3 bases and the F5 base are not symmetric (F5.001 has 5 mismatches).
  - At F = 100, 121 of the 131 prefixes 1..F are distinct.
- **Zenodo 1698 partition.** Described above. It has pivot 537: colours 0..5 on 1..536, 537 in the seventh colour,
  which spans 537..1162. It has zero mismatches under x → 1699 − x. On 1..40 its prefix differs from every
  537-base by at least 31 positions, after relabelling colours by first appearance.

## Method

All encodings use one variable per (integer or mirror orbit, colour). They have exactly-one constraints, one clause
per x ≤ y, x + y ≤ N and colour (x = y included), and mirrors as variable identification. The encoder is `schur.py`
from attempt `f3ecc4`, copied unchanged. The **pivot-p template** at N:

- 1..p−1 take colours 0..5 only, and 1..F are fixed to the base;
- p takes colour 6;
- the mirror is either **full**, c(x) = c(N + 1 − x) for all x, or **partial**, imposed only for x ≤ p;
- colour 6 is also forbidden on the mirrored base.

A full mirror is impossible when 3 divides N + 1: with x = (N + 1)/3, x + x = 2x = N + 1 − x. So the full mirror was
used at 1699, 1701 and 1702, and the partial mirror at every N from 1699 to 1704.

Solvers: the CaDiCaL 3.1.0 binary (commit 6b3d70b) took one call per instance, with status taken from the return
code (10, 20, 0). PySAT's CaDiCaL 1.9.5 ran incrementally under assumptions with a **conflict budget**: PySAT's
interrupt timer did not fire in this setting (an 8 s cap ran for over 3 minutes), so the time caps were replaced by
conflict budgets. "LIMIT" below means the budget ran out and the instance is undecided.

Lines, in the order run:

- **(a) Pivot 538, core-guided descent (`sweep.py`).** For each base, start at F = 537. On UNSAT, the
  failed-assumption core gives the largest fixed position p it used, so every F ≥ p is UNSAT for that base, N and
  mode. Next try F = min(p − 1, F − 10). Stop at SAT or LIMIT (100,000 conflicts).
  - Full mirror at 1699 and 1701: 56 bases each, covering all five families.
  - Partial mirror at 1699 to 1704: 8 sampled bases (F1.001, F1.050, F1.100, F2.001, F2.007, F3.001, F4.001,
    F5.001).
  - Variants:
    - an N ladder from 1500 to 1690 with F = 537 on 4 bases;
    - the exact top N with F = 537 for all 131 bases (`a-maxN`);
    - the Rowley-family 1..536 prefixes (repo and Zenodo 1698 colourings) under pivot 538 (`a-hybrid`).
- **(b) Zenodo 1698 seed.**
  - (b1) Pivot-537 template with Zenodo 1..F fixed, same descent, at N = 1699 and 1701 full and 1699 to 1701
    partial.
  - (b1-free) Zenodo 1..F fixed for F = 1300, 1100, 900, 700 and 537, everything above free, no mirror, N = 1699 to
    1701, binary with 45 s each (`zenpre.py`).
  - (b2) Zenodo fixed except a freed window, extended to N = 1699 to 1701 with no mirror, binary with 45 s each
    (`zenwin.py`). Windows of 200, 400 and 600 positions were freed at the pivot [537, 537 + w), centred on 537, at the
    top, low [1, w], and as half-and-half pivot plus top or low plus top. That makes 54 instances.
- **(c) Cube-and-conquer (`cnc538.py`).** Each instance is split on the 4 free base positions with the fewest
  colours left after propagation, with every combination of their allowed colours as a cube.
  - Five instances, 8 cubes each, 700,000 conflicts per cube: the most-fixed undecided pivot-538 instances, plus
    the Zenodo pivot-537 instance at F = 56.
  - Two instances with all cubes run (16 and 36), 1.5 M conflicts per cube.
- **(d) Other bases.**
  - Suffix-fixed (`suffix.py`): only S..537 of the base fixed and 1..S−1 free, which allows new low parts. S = 141,
    200 and 300 were run on 10 bases. S = 400 to 520 were run on 7 bases. Each was tried at 1699 full, 1701 full and
    1700 partial, with 300,000 conflicts.
  - Joint (`joint.py`): the whole base free (F = 0), so the solver generates a new six-colour base together with
    its extension. Phases were set to one published base. Budget: 4 M conflicts.

Budget: the first search process started at 22:37:10 UTC on 17 November 2026 and the last one ended at 00:21:07 UTC on 18 November
(103 min 57 s of the 120 min budget). At most two solver processes ran at once, except for 4 s (22:41:06 to 22:41:10 UTC): the first sweep started before
the ladder (two binaries) was stopped, so four ran together (logged in `budget.txt`). All processes exited 0, except the runs stopped by SIGTERM listed in `budget.txt` (ladder, sweep v1 to v4),
each restarted with a changed configuration. The machine's load average was about 14 on 14 cores throughout. Search calls,
calibration excluded: 3,548 UNSAT, 199 undecided (conflict limit), 3 binary time limits, and 794 SAT. All 794 SAT
calls are at N ≤ 1612: 788 in the top-N line (a-maxN) and 6 in the N ladder at N = 1600. Their summed per-call
solver time was 9,147 s. CPU seconds per process were not measured.

## Calibration

- **Checker.** `check.py` gives 0 violations for both 1698 partitions and 21 for a copy of the Zenodo partition with
  2 given the colour of 1. `diagnose` agrees: valid, valid, invalid. All 131 bases are valid six-colourings of
  1..537.
- **Small known answers.** With the binary, K = 3 is SAT at N = 13 and UNSAT at N = 14.
- **Full-size positive controls with the binary.** The pivot-537 template with full mirror at N = 1698 was SAT with
  0 decoded violations using:
  - the repo witness's 1..F for F = 536, 400, 300, 200, 150 and 100, which reproduces that witness exactly;
  - the Zenodo partition's 1..F for the same F, which gives valid 1698 partitions 118 to 148 positions from the
    Zenodo one; `diagnose` accepts the F = 536 one.

  At F = 50, both timed out at 90 s.
- **Planted refill.** Zenodo positions 700..999 were freed at N = 1698. The result was SAT, and `diagnose` accepts it.
- **Divisibility.** The full mirror at N = 1697 was UNSAT at the root, as predicted.
- **Incremental path.** The pivot-537 template at 1698 was loaded once, with the repo and Zenodo prefixes (F = 536,
  300 and 150) as assumptions: SAT with 0 violations in every case.
- **Cube-and-conquer.** On the Zenodo prefix at F = 50 (pivot 537, 1698), the cube agreeing with the Zenodo
  colouring was SAT in 31.5 s (537k conflicts). `diagnose` accepts the result. Single binary calls had timed out at
  90 s on this instance.
- **Pivot-538 positive control.** With F = 537 and full mirror at N = 1612, all 131 bases are SAT. `diagnose`
  accepts the F1.001 colouring (value 1612). So the pivot-538 pipeline can say yes.
- **Proof checker.** lrat-check rejected the first proof truncated to half its lines ("NOT VERIFIED", rc 1).

## Measured

Pivot 538, line (a), F = largest fixed prefix:

| N | mirror | bases | SAT | smallest F proved UNSAT (min/median/max over bases) | undecided at F (min/max) |
|---|---|---|---|---|---|
| 1699 | full | 56 | 0 | 63 / 137 / 147 | 53 / 137 |
| 1701 | full | 56 | 0 | 63 / 137 / 147 | 53 / 137 |
| 1699 | partial | 8 | 0 | 63 / 141 / 143 | 53 / 133 |
| 1700 | partial | 8 | 0 | 63 / 141 / 143 | 53 / 133 |
| 1701 | partial | 8 | 0 | 63 / 142 / 143 | 53 / 133 |
| 1702 | partial | 8 | 0 | 63 / 142 / 143 | 53 / 133 |
| 1703 | partial | 8 | 0 | 63 / 143 / 147 | 53 / 137 |
| 1704 | partial | 8 | 0 | 63 / 141 / 143 | 53 / 133 |

The 63 and 53 are the asymmetric base F5.001. Each F1 to F4 base has its own threshold between 131 and 147.

Notes on line (a):

- **Full base fixed (F = 537).** All 131 bases are SAT at N = 1608, 1609, 1611 and 1612 (full mirror) and at 1612
  (partial). All are UNSAT at every tested N from 1613 to 1619. The 4-base ladder was UNSAT at every tested N from
  1620 to 1690 and from 1699 to 1704. Each of those calls was refuted with at most 3 conflicts. Note that 1612 = 3 · 537 + 1.
- **Root obstruction, traced by `propchain.py` for F1.001 at 1699.** Colour 6 holds 538 and its mirror N − 537.
  That bars (N − 537)/2 = 581 from colour 6, so 581 is forced to colour 0. That forces 15 integers between 584 and 621 into colour 6, and
  then N − 1075 = 624 has no colour left: the base blocks 0..5 and 538 + 624 = N − 537 blocks colour 6.
- **Rowley-family prefixes under pivot 538.** UNSAT for F ≥ 66 (repo) and F ≥ 70 (Zenodo), and undecided at
  F = 56 and 60.
- **Full cube coverage.** For F1.026 at F = 137 (1699, full mirror), all 16 cubes were UNSAT. That instance was
  undecided in the descent and is now refuted by the solver.

Zenodo seed, line (b):

- Pivot-537 template with Zenodo 1..F: UNSAT for F ≥ 66 at every one of 1699 full, 1701 full and 1699, 1700 and 1701
  partial. Undecided at F = 56 with 100k conflicts. With all 36 cubes run at F = 56 (1699 full), every cube was UNSAT.
- No mirror, Zenodo 1..F fixed: UNSAT within 3 conflicts for F = 1300, 1100, 900 and 700 at N = 1699, 1700 and 1701.
  Time limit (45 s) for F = 537.
- All 54 freed-window instances (b2): UNSAT at the root (1 conflict or fewer).

Cube-and-conquer, line (c): 40 of 40 cubes UNSAT on the five 8-cube instances. All cubes UNSAT on the two
full-coverage instances (16 of 16 and 36 of 36).

Other bases, line (d):

- **Suffix-fixed.** UNSAT within 8 conflicts for S = 141, 200 and 300 on all 10 bases and all 3 targets. For S = 400, 6 of
  7 bases were undecided at 300k conflicts. F5.001 was UNSAT at S = 400, 420 and 440 and undecided at 460.
- **Joint (whole base free).** All 7 calls were undecided at their budget:
  - 4 M conflicts: 1699 full (phases F1.001 and F5.001), 1700 partial (F1.001), 1701 full (F2.001) and 1702 full
    (F3.001), at 226 to 344 s each;
  - 15 M conflicts: 1699 full (F2.001) and 1701 full (F1.001), at 1,573 and 1,560 s.

**LRAT certificates.** CaDiCaL 3.1.0 `--lrat` was run on a kept DIMACS file, then lrat-check verified each proof.
The proofs were deleted after hashing.

| instance | conflicts | CNF SHA-256 (prefix) | proof bytes | lrat-check |
|---|---|---|---|---|
| P1: F1.001, F = 537, pivot 538, partial mirror, N = 1699 | 1 | b74e7b60 | 246,323 | VERIFIED |
| P2: F1.001, F = 141, pivot 538, full mirror, N = 1699 | 44,247 | 9be7d92f | 34,195,514 | VERIFIED |
| P3: Zenodo 1..150, pivot 537, full mirror, N = 1699 | 1 | 8489433d | 178,066 | VERIFIED |
| P4: Zenodo 1..66, pivot 537, full mirror, N = 1699 | 17,371 | 109da583 | 20,974,590 | VERIFIED |
| P5: F5.001, F = 63, pivot 538, full mirror, N = 1699 | 78,513 | 1e2b130e | 54,535,746 | VERIFIED |

Every other UNSAT is a solver statistic only.

## Inferred, not proved

- With these 131 bases fully fixed, the pivot-538 template stops at 1612 = 3 · 537 + 1, far below Rowley's 1696
  from a 536-base. The bases were found as partitions of 1..537. Nothing in their construction aims at a seven-colour
  extension, and their low parts (1..~140) differ from the Rowley-family prefix.
- In line (a), 1,214 of 1,244 UNSAT cores started at position 1, and the rest at 2 to 5. Fixing only the top of a base (S ≥ 141 up to 300)
  was also refuted at once. For the symmetric F1, F2 and F4 bases, fixing S..537 amounts to fixing 1..538 − S, so these
  are not independent checks. For those bases, the solver-level evidence says roughly the first 130 to 147 positions
  of each base already exclude the pivot-538 extension at N = 1699 to 1704.
- The Zenodo partition, like the repo's 1698 witness, has pivot 537 and a full mirror at 1699. Its first 56
  positions already exclude a pivot-537 mirrored extension to 1699, which is complete under cube coverage. Pushing a
  fully mirrored 1698 colouring to 1699 needs both its low part and its top changed, which matches the root failures
  of every window.

## Not covered

- Partial-mirror runs used only 8 of 131 bases. The full mirror at 1702 had no line-(a) runs, only one joint run.
- F below the LIMIT thresholds (about 53 to 137) for most bases. Only one pivot-538 instance and one Zenodo instance
  had all cubes run.
- Joint runs with the base free got at most 15 M conflicts each (7 calls).
- No bases built from new templates, and no pivot other than 537 and 538. No non-mirrored pivot-538 runs.
- UNSAT results other than P1 to P5 have no proofs.

## What a later attempt should try

- **Joint search for the base and the extension together.** Line (d) with longer budgets and cube-and-conquer: a
  six-colouring of 1..537 that admits pivot 538 at N ≥ 1699 must differ from all 131 published bases within its first
  ~140 positions.
- **Seed the low part from the Rowley family.** Use its first 50 to 60 positions, where pivot 538 was undecided, with
  a free middle base.
- **Non-symmetric constructions at 1700 and 1703,** where the full mirror is impossible.
- **Other pivots.**

## Files

All scripts are the author's own, except `schur.py`, which is copied unchanged from attempt `f3ecc4` (this
repository).

- `check.py`: independent sum-free checker.
- `lib538.py`: template builders and the logged binary runner.
- `sweep.py`: line (a) and (b1) descents. Versions v1 and v2 used a time interrupt and were stopped. v3 onwards used
  the conflict budget.
- `ladder.py`: the first binary ladder, stopped early.
- `calib538.py`, `calib538b.py`, `calib_incr.py`: calibration.
- `blocked538.py`, `zset.py`, `propchain.py`: arithmetic diagnosis of the root failures.
- `zenwin.py`, `zenpre.py`: line (b).
- `cnc538.py`: line (c).
- `suffix.py`, `joint.py`: line (d).
- `proofs.py`: LRAT certificates.
- `report.py`, `summ.py`: tables and progress summaries from the logs.

Logs and outputs stay in the author's scratch directory, which is not part of this attempt.
