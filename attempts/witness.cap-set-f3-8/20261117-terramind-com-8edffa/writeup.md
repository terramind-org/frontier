# Exchange search and priority-function variants from the FunSearch 512-cap in F_3^8 (2 h budget, no 513-point cap found)

**Outcome: no cap set with more than 512 points was found.** This is the record of a failed search within a 2-hour
budget. It is a writeup and is never machine-checked; the numbers below come from my own search logs, except where
it says the repo verifier (`bun frontier diagnose`) was used or where it cites the independent audit described at
the end.

## Setup

- Starting object: `cap_set/n8_size512.txt` from the public google-deepmind/funsearch repository, encoded as
  `{"points": [...]}`. `bun frontier diagnose ... --problem witness.cap-set-f3-8` reports it valid, value 512,
  "ties the best known value".
- Points are encoded as integers 0..6560 (base 3, first coordinate most significant). A 6561 x 6561 table
  `T[a, b] = -(a + b)` gives the third point of every line, so "x is blocked" means some pair {a, b} of the cap has
  a + b + x = 0.
- Solver: OR-Tools CP-SAT 9.15, one worker per process. Two processes ran at a time (the 2-core limit). NumPy did
  the greedy builder and the freed-set computations.
- Wall clock: first search process started 21:25:04 IST, the last one exited on its own time limit at about
  23:19 IST, so about 114 minutes of the 120-minute budget. Two runs (A1, B1 below) were interrupted; their exit
  statuses and final counters were not preserved. The scripts are in `search/` (`capcore.py` shared helpers,
  `complete.py` completeness count, `lns.py` exchange search, `greedy.py` program search and products, `run_b.sh`
  the schedule of the second core). The current copies are the final versions; A1 ran before the FMAX skip was added.

## Step 1: completeness of the 512-cap

Every one of the 6049 outside points completes at least 4 lines through pairs of the cap, so the cap is complete
and no point can be added. Distribution (number of blocking pairs: number of outside points):

`4: 16, 8: 16, 10: 64, 11: 192, 12: 32, 13: 384, 14: 192, 15: 128, 17: 192, 18: 672, 19: 128, 20: 256, 21: 512,
22: 384, 23: 1152, 24: 512, 25: 256, 26: 256, 28: 192, 30: 128, 32: 256, 40: 16, 44: 32, 48: 56, 56: 16, 80: 8,
256: 1`

The single point with 256 blocking pairs is the origin: the cap is symmetric under x -> -x and does not contain 0.
No outside point has count 1, 2 or 3. For any outside point, its blocking pairs are pairwise disjoint (for fixed x
the partner of a is determined), so freeing even one outside point needs at least 4 cap points removed.

## Step 2: exchange / large-neighbourhood search (`lns.py`)

Each step removes a set R of cap points, computes the freed set F (R plus every outside point none of whose blocking
pairs lies entirely in the kept part), models max |S| over S in F with (kept + S) a cap exactly (pair constraints for
two freed points whose third point is kept, triple constraints for lines inside F; hint S = R), then runs
time-limited CP-SAT. Only an OPTIMAL status certifies the neighbourhood optimum; a FEASIBLE status gives only an
incumbent. Net gain is |S| - |R|. Neighbourhoods, drawn at random each step:

- **targeted**: 1 to 3 outside points of low blocking count; remove one endpoint of each of their blocking pairs,
  mostly the endpoint that blocks more low-count points (k between 4 and about 33);
- **random**: k cap points sampled with weight proportional to how many low-count outside points they help block,
  k growing over the run from KMIN to KMAX;
- **subspace**: the cap points of a random affine subspace of codimension 1 to 3;
- **hyperplanes**: the cap points in a union of 1 to 4 random affine hyperplanes.

A gain of 0 with S different from R would be accepted as a plateau move with probability PLATEAU (0.5, or 1.0 in
two runs). Neighbourhoods with |F| > FMAX = 1400 were skipped, because building those models took minutes each.

Runs (all from the FunSearch cap unless stated; counts are from the last logged snapshot of each run):

| run | seed | params | wall clock | steps | successful CP-SAT solves (not proven optimal) | best net gain | largest R re-solved to proven optimality |
|---|---|---|---|---|---|---|---|
| A1 | 11 | defaults, no FMAX | about 10 min, interrupted | 93 | 93 (9) | 0 | random 61, subspace 172, hyperplanes 293 |
| A | 12 | KMIN 40, KMAX 470, TMAX 60 | 104 min, ended on time limit | 7395 | 6265 (91), 1130 skipped | 0 | random 332, targeted 33, subspace 208, hyperplanes 310 |
| B1 | 41 | PLATEAU 1.0, KMIN 150, KMAX 500, TMAX 90 | about 5 min, interrupted with the B1 schedule | 309 | 260 (3), 49 skipped | 0 | random 186, hyperplanes 296 |
| B_variant | 21 | defaults, from the second 512-cap below | 20 min, ended on time limit | 1246 | 1064 (18), 182 skipped | 0 | random 324, hyperplanes 312 |
| B_product | 31 | KMIN 40, KMAX 380, from the 400-point product cap | 15 min, ended on time limit | 177 | 120 (21), 57 skipped | 0 | random 111, subspace 52 |
| B_baseline | 41 | PLATEAU 1.0, KMIN 150, KMAX 500, TMAX 90 | 38 min, ended on time limit | 1167 | 987 (22), 180 skipped | 0 | random 332, hyperplanes 302 |

The logged snapshots total 8,789 successful solves across the FunSearch cap (7,605), its affine copy (1,064) and
the 400-point product cap (120). Of these, 8,625 proved optimal and 164 returned only feasible incumbents; none
recorded an improvement. The largest removal certified optimal was 332; that is not the largest removal attempted
(A1 has a FEASIBLE solve at |R| = 419, |F| = 3,874). A1 and B1 have no final record, so their counts are lower
bounds at interruption.

**Best net gain observed for k-removal: 0, in every neighbourhood type and every run.** No gain or accepted plateau
move was logged. Certified solves established the original cardinality as optimal; uniqueness was not tested, and
returned-set identity was not logged. With PLATEAU 0.5, zero accepted moves does not show that no different
equal-size set was returned; in the two PLATEAU 1.0 runs, where any different equal-size set would have been
accepted, none was up to their last logged snapshot. The hint S = R starts
CP-SAT on the removed set, so equal-size alternatives can stay hidden: the audit took R = (FunSearch cap minus the
second 512-cap below), |R| = 128, |F| = 256; the same model returned the FunSearch cap, and adding the single
constraint "not all of R" made it return the second 512-cap, valid at 512 (a tie). Equal-size alternatives
therefore exist nearby.

Freed-set sizes vary substantially by hyperplane. For x1 = 0, R = 192 and F = 600, freeing 408 outside points; for
x4 = 0, R = 160 and F = 160, freeing none. `lns.py` logs a sampled row only about once a minute (146 rows in all)
and never the contents of R or F, so the full |R| and |F| distributions, the rate of repeated neighbourhoods and the
fraction of solves with F = R cannot be reconstructed.

## Step 3: program search around the FunSearch priority (`greedy.py`)

The FunSearch greedy builder (add the unblocked point of highest priority, repeat) with the published n = 8
priority function, its eight constants exposed (the exponent of n, the reflection multipliers, the zero-position
multipliers, the per-nonzero increment):

- published constants: 512 (the FunSearch cap); random tie-break noise of 1e-9, 0.001 and 0.01 times the maximum
  absolute priority, five trials each: still 512. Five sampled trials at each of two larger noise scales, 0.1 and
  0.5 times the maximum absolute priority, reached at most 336 in the seed-8 rerun. This is a sampled observation,
  not a bound for larger noise;
- 74,659 random log-normal perturbations of 1 to 3 constants (60,552 in a first 15-minute run, seed 7, whose
  candidate coordinates were not saved because the baseline lookup failed; stdout preserves variant counts and top
  sizes; 14,107 in a 6-minute rerun, seed 8): the sampled perturbations reached at most 512, reached by many
  variants, with 452 the largest logged smaller result (seed 7 only; its coordinates were not saved, so it was never
  checked by the verifier), then 448;
- 151,858 priorities from other families (118,959 in seed 7, 32,899 in seed 8; random combinations of weight,
  number of reflections v_i = v_{8-i}, full-weight-and-reflection, first coordinate zero, and counts of zeros of two
  random linear forms): none beat 512.

The rerun saw 2 distinct 512-caps and 146 distinct 448-caps. The printed histogram shows only the 15 largest size
bins, ending at 425; smaller sizes were omitted. The second 512-cap shares 384 points with the FunSearch cap and has
exactly the same completeness distribution as above. It is an affine image of the FunSearch cap: the linear map
negating the sixth coordinate, (x1, ..., x5, x6, x7, x8) -> (x1, ..., x5, -x6, x7, x8), sends one onto the other
(exact set equality, checked in the audit). The repo verifier reports it valid at 512 (ties). The exchange search
from it (B_variant) also gained nothing.

## Step 4: product starting points

CP-SAT, one worker, from scratch: caps of the best known sizes 4 (F_3^2), 9 (F_3^3) and 20 (F_3^4), but only 39 in
F_3^5 (best known 45) and 79 in F_3^6 (best known 112) in its 4.8 and 6 minutes. These are incumbents; CP-SAT proved
optimality only in dimensions 2 and 3. I did not have explicit coordinates of the 45- and 112-caps and did not build
them from the literature. Products: 4 x 79 = 316, 9 x 39 = 351, 20 x 20 = 400; greedy completion added no point to
any of them. The 400-cap is complete (every outside point completes at least 3 lines: `3: 2400, 10: 40, 18: 3600,
60: 120, 200: 1`), and 15 minutes of exchange search from it (B_product) gained nothing. Doubling constructions were
not tried.

## Why it stalled

These sampled, time-limited exchanges found no improvement. This does not establish strict local optimality or rule
out other local-search strategies. The FunSearch cap is complete with minimum blocking count 4, so freeing even one
outside point needs at least 4 removals, and every certified neighbourhood optimum equalled the removed size. A
priority variant produced an affine copy at 512. Exchange search was run from the FunSearch cap, that copy and the
400-cap; the two saved 448-caps were not exchange-searched in this attempt. The search never deliberately looked for
equal-size alternatives, and the audit's plateau example above shows they exist.

## Observed limits of these runs

- Exchange search (remove k, re-solve the freed set) around the FunSearch 512-cap and its affine copy with k up to
  about 330 certified optimal, hyperplane sections and unions, or low-count targeting: 8,669 successful solves from
  those two caps in the logged snapshots, no gain recorded; all of them hinted with the removed set.
- Random perturbation of the published priority function's constants: the sampled perturbations reached at most
  512, with 452 the largest logged smaller result.
- CP-SAT from scratch in F_3^5 and F_3^6, with one worker and about 5 to 6 minutes each, stayed at 39 and 79, below
  the known 45 and 112, so the products built from them reached only 400.

## Untried

- Plateau walks that exclude the current set (a solution-exclusion constraint, or a secondary diversity objective)
  so that equal-size alternatives are explored instead of the hint being restored; the 128-point removal above is a
  known plateau move to test against.
- Exchange search from the two 448-caps the seed-8 rerun saved (their files are not part of this attempt); the one
  the audit examined is complete but has 448 outside points blocked only once.
- Products and doublings that start from the actual 45-cap in F_3^5 and the 112-cap in F_3^6 (and Edel-type
  constructions that gave the old 496 record), followed by exchange search.
- Neighbourhoods that free a whole affine subspace (remove the cap points of a codimension-2 or -3 subspace and also
  every cap point that blocks a point inside it), i.e. re-optimising a region together with its boundary, which
  frees far more candidates than the rules above.
- Exploiting the cap's symmetry group (search only for caps invariant under a subgroup, which shrinks the problem
  enough for exact solving over the whole space).
- An LLM-in-the-loop program search in the style of FunSearch, which needs far more than 2 hours.

## Independent audit

A second model (GPT-6.1 Sol) audited this attempt before submission. It re-derived the completeness distribution
with an independent counter, confirmed that the exchange step finds gains when they exist (from a 507-point
punctured copy it recovered the 512-cap, and it found gains in dimensions 3 and 4), recounted the solve counts from
the original log lines, verified the sixth-coordinate affine map between the two 512-caps, and found several
summaries and conclusions overstated. The text above was corrected accordingly. The audit is an opinion backed by
reruns, not a check by the repo verifier, and it found no valid cap larger than 512.
