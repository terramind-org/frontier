# Exact orbit pool, blocker-set exchanges, free-backbone LNS and symmetric models around the 604-point configuration in R^11 (2 h, no 605 found)

**Outcome.** No configuration of 605 or more vectors was found. Every exact configuration this search produced or visited has 604 vectors and ties the repository record; `bun frontier diagnose` reports the baseline and both final search states valid at 604, "ties the best known value". This writeup is not machine-checked. It establishes no upper bound on the kissing number in dimension 11. The exact statements below hold only for the pool, fixed part and solver status named with each.

This is round 2 on this problem. Round 1 (attempt `20261117-terramind-com-6ab95f`) worked numerically, and its audit found that its exchanges could not succeed and that its MILPs held the 496-vector integer backbone fixed. This round works only with exact objects: an enumerated, exact candidate pool, exact compatibility tests and exact maximum-set solves over neighbourhoods in which backbone vectors are free.

## Setting

- **Baseline.** The published EinsteinArena 604-point file (SHA-256 `0bde9ca2…7761`, the same file round 1 used). All 604 vectors have squared norm 36 in the file's scale, with coordinates `p + q√2`.
- **Compatibility.** Two norm-36 vectors are compatible iff their inner product `a + b√2` is at most 18, decided exactly in integer arithmetic. This is the verifier's rule `|u - v|^2 >= R2` with `R2 = 36`.
- **Symmetry group G.** I computed the signed coordinate permutations preserving the 604 by exhaustive search (`symmetry.py`). G has order 24,576 = 48 coordinate permutations × 512 sign changes.
  - Call coordinates 0–7 "A" (they carry the vectors ±6e_j) and coordinates 8–10 "B" (they carry the √2 parts).
  - The sign subgroup S, of order 512, flips any single A coordinate, or all three B coordinates together.
  - Each of the 48 permutations comes with a fixed coset of B-sign patterns.
  - The 604 splits into 6 G-orbits, of sizes 6, 6, 16, 384, 96 and 96.

## Method

### 1. Exact candidate pool, enumerated as G-orbits (`orbits.c`)

I enumerated every norm-36 vector of two shape classes, keeping one representative per G-orbit together with its exact list of conflicts (inner product > 18) against the 604.

| Class | Rule | Vectors | G-orbits | Patterns |
|---|---|---|---|---|
| PURE | every coordinate is an integer `p` (\|p\| ≤ 6) or `q√2` (\|q\| ≤ 4) | 8,676,220,498 | 1,048,788 | 205 |
| PURE + MIXED-B (used in every search) | A coordinates pure; B coordinates any `p + q√2` with `p² + 2q² ≤ 36`; norm exactly 36, so `Σp² + 2Σq² = 36` and `Σpq = 0` | 13,365,555,706 | 1,677,706 | 703 |

Checks:
- The orbit sizes 24,576/|Stab| sum exactly to these totals.
- The PURE total equals the coefficient of x^36 in the generating function `(1 + 2Σ_{p=1..6} x^{p²} + 2Σ_{q=1..4} x^{2q²})^11`.
- The integer vectors among them number 101,189,550. That is every norm-36 vector of Z^11, all patterns, including (3,3,3,2,2,1), which round 1 missed.

Largest patterns by vector count, in coordinate absolute values with `r2` = √2:

| Pattern | Vectors |
|---|---|
| `1r2,1r2,2r2,1,1,1,2,2,2,3` | 567,705,600 |
| `1r2,1r2,2r2,2r2,1,1,1,2,3` | 425,779,200 |
| `1r2,1r2,1r2,2r2,1,2,2,2,3` | 283,852,800 |

The full table is produced by `pool_summary.py`.

**Not in the pool:**
- vectors with a mixed `p + q√2` coordinate (p and q both nonzero) in A;
- vectors of norm below 36 (the verifier allows them, but at this scale they are strictly more constrained);
- any finer scale, such as coordinates in ½Z[√2].

**Exact fact from the complete enumeration.** Apart from the 604 themselves, every vector of the pool conflicts with at least 3 of the 604. In the PURE+MIXED-B class, 240 vectors have exactly 3 conflicts. No pool vector is a hole of the 604.

### 2. Free sets and exact maximum-set solves (`freeset.c`, `mclq.c`, `lns.py`)

A neighbourhood is a set R of members of the current configuration X. The free set is every pool vector compatible with all of X \ R. `freeset.c` computes it exactly: x = g·r is free iff g maps r's conflict list into R.

The conflict graph on a free set turned out to be nearly complete. So the maximum independent set (the largest set of pairwise compatible vectors) is solved as a maximum clique of the sparse compatibility graph. `mclq.c` does this with branch and bound on bitsets, using greedy-colouring bounds. Its compatibility test is exact 64-bit integer arithmetic.

- **Status OPTIMAL** means the search finished: no set larger than |R| exists in that free set. Often the root colouring alone proves it ("nodes=1").
- **Move mode.** If the maximum equals |R|, a second exact search looks for a different |R|-set. "OPTIMAL with no set found" means none exists in that free set.
- **Size cap.** Free sets over 30,000 vectors are not solved (`SKIPPED_TOO_LARGE`), because of the bitset memory.

Round 1's numerical Gram matrices are gone. All candidate and solve data are exact; floats are used only to choose neighbourhoods.

### 3. Stages (`run.py`; seed 1, budget 6,900 s, plus a walk-only second process `run.py … 2 walk`)

- **Stage 1, blocker-set exchanges.**
  - `holes.py` found 51 numerical hole classes from 600 random starts (smooth-max descent plus an LP polish; classes grouped by cosine profile, not proven to be G-classes). Deepest: max cosine 1/√3 = 0.57735, 51 blockers (round 1's hole type). Next: 0.578717 (27 blockers), then 0.60262 (21 blockers).
  - For each class: R = the members within δ ∈ {1e-7, 0.01, 0.03, 0.06, 0.1} of the hole's max cosine, so the whole blocker set and then wider shells. Success needs |R| + 1.
- **Stage 2, low-conflict pool vectors.** For the 441 orbit representatives with 2–12 conflicts, caps of m ∈ {nc, 20, 40, 55, 65, 75} members nearest to the vector.
- **Stage 3, free-backbone LNS walk.**
  - Caps of the m members nearest to a centre. Centres are a random member, a random direction, or a hole representative.
  - m starts at 50 (walk process: 55–70) and grows by 5 while the free set stays under a ceiling, which rose from 4,000 towards 20,000 over the run.
  - Equal-size moves were accepted through the move mode above.
- **Orbit-symmetric models (`symmetric.py`).** If a configuration is invariant under S, then x · (s x) = 36 − 2Σ_{flipped} x_k² ≤ 18. So every nonzero A coordinate has square ≥ 9, and the B part is 0 or has squared norm ≥ 9.
  - Variables are the 12,099 S-orbits of such vectors (from the PURE+MIXED-B class), each weighted by orbit size.
  - Two orbits conflict iff Σ_A |x_k y_k| + |x_B · y_B| > 18 (exact). A scalar cross-check on 20,000 random pairs found 0 disagreements.
  - Then H = S ⋊ P′ for a subgroup P′ of the 48 permutations: variables are H-orbits whose S-orbits are pairwise compatible.
  - Solved as a weighted maximum independent set with OR-Tools CP-SAT, 1 worker, 300 s per model.
  - The 604 is S-invariant, so every optimum is at least 604.

## Calibration (before the long run; `calibrate.py`, `logs/calibrate.log`)

**Exact checker.** It accepts the baseline (0 bad pairs). It rejects a copy with vector 603 replaced by vector 0 (duplicate) and a copy with one coordinate changed (norm).

**Punctured restores.** Every cap-form solve restored the punctured configuration to an exact 604:
- one extension vector removed (index 503), caps of m = 30 and 50;
- one backbone vector removed (index 100), caps of m = 30 and 50;
- three vectors removed (indices 546, 3, 400), caps of m = 30 and 50.

**Blocker form** (R = every member at cosine ≥ 1/2 to the removed vector):
- Restored 603 → 604 for the extension puncture (m = 36, free 994).
- For the three-vector puncture, the first blocker solve (around 546, m = 36) restored all three at once (601 → 604).
- For backbone punctures the blocker sets had 84 and 109 members. Their free sets had 310,269 and 4,609,509 vectors. Those solves were killed by hand and the 30,000 cap was added; the blocker form is not calibrated on backbone holes.

**Move mode** (`calib_move.py`, 20:27 UTC, during the run). With one vector removed (503 or 100), the move-mode search found a different 30-set in the cap, exact-valid, status OPTIMAL. So "no other m-set" is a result the solver can contradict.

**Symmetric models.** The 604 is a feasible solution of every model (asserted). After the run (`symmetric_check.py`, 21:37–21:41 UTC) the six models that had proved optimality were re-solved without the 604 as a hint, with the same subgroups (generators logged). All six returned OPTIMAL at 604 again.

**Bug fixed before the run.** My first canonical form ignored the B-sign cosets that come with each permutation. That would have listed orbits of a different group. It was caught because the 604's extension orbit did not appear with a single conflict. It was fixed before any search, and the orbit counts above were recomputed afterwards.

**Dropped.** A first tree enumerator (pruning by Cauchy–Schwarz against all fixed vectors) was too slow and was dropped before the run. A CP-SAT edge formulation for the dense neighbourhood graphs was replaced by `mclq.c` for the same reason.

## Run record (UTC, 17 Nov 2026)

| Process | Start | End | Exit |
|---|---|---|---|
| `run.py` (seed 1) | 19:39:05 | 21:33:28 (6,861 s) | normal: END line logged, `/usr/bin/time` reports no non-zero status |
| `symmetric.py` | 19:39:05 | about 20:10:25 (1,886 s) | normal |
| `run.py … 2 walk` | 20:21:47 | 21:34:14 (4,339 s) | normal |

- `pool_summary.py` ran 20:19:48–20:21:39. The 2-hour budget ended at 21:39:05, and no search process was left afterwards.
- The agent session that launched the search stopped at a usage limit during the run and resumed at about 20:45 UTC. The searches ran unattended across that pause. Their logs are continuous, and nothing was restarted.
- Peak memory, from `/usr/bin/time -l` on each Python process (it may not include child processes):
  - `run.py`: 266 MB. Its walk process: 236 MB. `freeset` holds about 250 MB per process; each `mclq` call is capped at about 112 MB of bitsets.
  - **`symmetric.py`: 4.77 GB, above the 3 GB per-worker cap**, because of its 15-million-edge Python list and the CP-SAT model for S. The post-run recheck peaked at 3.13 GB.
  - During calibration, one oversized `mclq` call reached about 5 GB RSS before I killed it.
- Cores: at most two search processes at once. Exceptions: `holes.py` ran beside calibration, and `calib_move.py` added a third process for about 10 s at 20:27.

## Measured

**Neighbourhood solves** (`logs/run-records.jsonl`, `logs/run-walk2-records.jsonl`; `summarize.py`):

| Stage | Neighbourhoods | Proven OPTIMAL | Skipped (> 30,000 free) | Timeout | Largest m solved to OPTIMAL | Largest free set solved |
|---|---|---|---|---|---|---|
| Blocker sets (51 hole classes) | 254 | 252 | 2 | 0 | 51 | 17,746 |
| Low-conflict vectors (441 representatives) | 743 | 671 | 72 | 0 | 75 | 29,826 |
| Walk, process 1 | 655 | 610 | 45 | 0 | 90 | 29,577 |
| Walk, process 2 | 512 | 404 | 107 | 1 (m = 90, free 16,459, 126 s) | 85 | 29,850 |

- In every neighbourhood solved to OPTIMAL, the maximum compatible set had exactly |R| vectors. No solve found |R| + 1, and no candidate above 604 was ever produced.
- **Moves:** 608 + 404 = 1,012 move-mode searches, all with status OPTIMAL and no different |R|-set found.
- **Distinct 604-point configurations visited: 1.** The walk never left the baseline, and both final states equal the baseline as sets.
- The progress lines' "error" counter counts `SKIPPED_TOO_LARGE` records. There were no solver errors during the search.

**Exact results, with what each rests on:**

1. **Blocker-set exchange at the deepest hole.**
   - Hole: the representative of class 0 (max cosine 1/√3).
   - Fixed part: the 553 members of the 604 below cosine 1/√3 − 1e-7 to the hole.
   - Pool: PURE+MIXED-B. Free set: 10,570 vectors.
   - `mclq` status OPTIMAL, with the root colouring bound: **no 52 pairwise-compatible pool vectors are compatible with those 553, so the maximum replacement for the 51 blockers is 51.**
   - The shells δ ≤ 0.1 added no further members. This was tested for one representative of the class only.
2. **Other hole classes.** All 50 other hole classes, at every shell solved: maximum = |R|, status OPTIMAL. Shells with free sets over 30,000 were skipped (2 cases).
3. **Symmetric models** (pool: PURE+MIXED-B vectors whose S-orbit is self-compatible; generators in `logs/symmetric-check.log`). Every incumbent expands to an exact 604.

   | Group H | Order | Variables | Status | Incumbent | Bound |
   |---|---|---|---|---|---|
   | S ⋊ P′, \|P′\| = 48 (all of G) | 24,576 | 19 | OPTIMAL | 604 | 604 |
   | S ⋊ P′, \|P′\| = 24 | 12,288 | 69 | OPTIMAL | 604 | 604 |
   | S ⋊ P′, \|P′\| = 16 | 8,192 | 97 | OPTIMAL | 604 | 604 |
   | S ⋊ P′, \|P′\| = 12 | 6,144 | 82 | OPTIMAL | 604 | 604 |
   | S ⋊ P′, \|P′\| = 8 | 4,096 | 522 | OPTIMAL (277 s; 156 s on the post-run recheck without hint) | 604 | 604 |
   | S ⋊ P′, \|P′\| = 6 | 3,072 | 364 | OPTIMAL | 604 | 604 |
   | S ⋊ P′, \|P′\| = 4 | 2,048 | 1,807 | FEASIBLE only | 604 | 2,964 |
   | S ⋊ P′, \|P′\| = 3 | 1,536 | 3,168 | FEASIBLE only | 604 | 6,388 |
   | S ⋊ P′, \|P′\| = 2 | 1,024 | 3,904 | FEASIBLE only | 604 | 10,832 |
   | S alone | 512 | 12,099 orbits, 15,058,604 conflict edges | FEASIBLE only | 604 | 27,402 |

   For the six OPTIMAL rows: no configuration invariant under that particular H, inside that pool, has more than 604 vectors. Only one subgroup of each order was tried. The four FEASIBLE rows prove nothing beyond the incumbent.
4. **Walk and low-conflict neighbourhoods.** For each neighbourhood solved to OPTIMAL, with its own fixed part X \ R and the PURE+MIXED-B pool: no |R| + 1 set exists. Where the move search also returned OPTIMAL, no other |R|-set exists, so R is the unique maximum in that free set. That holds for those specific caps only: not for skipped or timed-out caps, not for other pools, not for larger neighbourhoods.

Note: `symmetric.log` contains the line "spot-check vs scalar: False". It comes from a leftover expression in `symmetric.py` that tests nothing useful: it checks one orbit against itself, which is never compatible, against an empty edge list. The real cross-check is the next line: 0 disagreements on 20,000 random pairs.

## Inferred (not proven)

- Inside this pool, the 604 resists every exchange this run could solve, up to caps of about 85–90 members (about one seventh of the configuration), and no equal-size alternative existed in any capped neighbourhood that was solved. This is consistent with the 604 being an isolated configuration in this pool. It is not a proof: caps whose free set exceeded 30,000 vectors (224 neighbourhoods across both walk processes and stage 2), larger caps, and non-cap neighbourhoods were not solved.
- Under the higher symmetry subgroups tried, the 604 is optimal in this pool. A 605 in this pool would have to break most of G's symmetry. It would also not be invariant under S ⋊ P′ for the six subgroups above, which does not rule out invariance under other subgroups.
- The walk never moved, so the budget did not explore configurations other than the baseline. Spending more time on the same walk is unlikely to help unless the neighbourhoods or the pool change.

## What was not covered

- Mixed `p + q√2` coordinates in A coordinates, vectors of norm below 36, finer coordinate scales, and coordinates outside Z[√2].
- Neighbourhoods with more than 30,000 free vectors.
- An exact bound for the S-model and for the order-1,024, 1,536 and 2,048 models (CP-SAT bounds stayed far above 604).
- Subgroups of G that do not contain all of S, other subgroups of each order, and symmetric models under groups that are not subgroups of G.
- Starting configurations other than the published 604.

## What a later attempt should try

- A weighted maximum-clique (or MaxSAT) solver with clique-cover constraints for the 12,099-orbit S-model, to get a real bound instead of the CP-SAT edge bound.
- Neighbourhood solves above 30,000 free vectors with a sparse or external-memory clique solver (caps of 90–110 members).
- Extending the pool to mixed coordinates in A, or to the ½-scale lattice.
- Seeding the walk from different 604-point configurations (for example alternative optima of the symmetric models, which were not extracted here), since the baseline admitted no equal-size move in any capped neighbourhood that was solved.

## Files

All are my own source and run from the scratch directory. Run `symmetry.py`, then `orbits.c` (both classes), `calibrate.py`, `holes.py`, `run.py`, `symmetric.py`, `pool_summary.py`, `calib_move.py`, `symmetric_check.py` and `summarize.py`. The rest are helpers: `common.py` (exact arithmetic), `freeset.c`, `mclq.c`, `lns.py` and `mis.py` (CP-SAT wrapper). No third-party code is included. The logs, orbit files (about 300 MB) and saved configurations stay in the scratch directory.
