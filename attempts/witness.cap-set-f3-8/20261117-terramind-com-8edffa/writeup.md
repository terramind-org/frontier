# Exchange search and priority-function variants from the FunSearch 512-cap in F_3^8 (2 h, no 513-point cap found)

**Outcome: no cap set with more than 512 points was found.** This is the record of a failed 2-hour search. It is a
writeup and is never machine-checked; the numbers below come from my own search logs, except where it says the
repo verifier (`bun frontier diagnose`) was used.

## Setup

- Starting object: `cap_set/n8_size512.txt` from the public google-deepmind/funsearch repository, encoded as
  `{"points": [...]}`. `bun frontier diagnose ... --problem witness.cap-set-f3-8` reports it valid, value 512,
  "ties the best known value".
- Points are encoded as integers 0..6560 (base 3, first coordinate most significant). A 6561 x 6561 table
  `T[a, b] = -(a + b)` gives the third point of every line, so "x is blocked" means some pair {a, b} of the cap has
  a + b + x = 0.
- Solver: OR-Tools CP-SAT 9.15, one worker per process. Two processes ran at a time (the 2-core limit).
- Wall clock: first search process started 21:25:04 IST, the last one exited on its own time limit at about
  23:19 IST, so about 114 minutes of the 120-minute budget. The scripts are in `search/` (`capcore.py` shared
  helpers, `complete.py` completeness count, `lns.py` exchange search, `greedy.py` program search and products,
  `run_b.sh` the schedule of the second core).

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
pairs lies entirely in the kept part), and solves max |S| over S in F with (kept + S) a cap, exactly, with CP-SAT
(pair constraints for two freed points whose third point is kept, triple constraints for lines inside F; hint
S = R). Net gain is |S| - |R|. Neighbourhoods, drawn at random each step:

- **targeted**: 1 to 3 outside points of low blocking count; remove one endpoint of each of their blocking pairs,
  mostly the endpoint that blocks more low-count points (k between 4 and about 33);
- **random**: k cap points sampled with weight proportional to how many low-count outside points they help block,
  k growing over the run from KMIN to KMAX;
- **subspace**: the cap points of a random affine subspace of codimension 1 to 3;
- **hyperplanes**: the cap points in a union of 1 to 4 random affine hyperplanes.

A gain of 0 with S different from R would be accepted as a plateau move with probability PLATEAU (0.5, or 1.0 in
one run). Neighbourhoods with |F| > FMAX = 1400 were skipped, because building those models took minutes each.

Runs (all from the FunSearch cap unless stated):

| run | seed | params | wall clock | steps | CP-SAT solves | best net gain | largest R re-solved to proven optimality |
|---|---|---|---|---|---|---|---|
| A1 | 11 | defaults, no FMAX | 10 min, killed by me | 93 | 93 | 0 | random 61, subspace 172, hyperplanes 293 |
| A | 12 | KMIN 40, KMAX 470, TMAX 60 | 104 min, ended on time limit | 7395 | 6265 (91 not proven optimal), 1130 skipped | 0 | random 332, targeted 33, subspace 208, hyperplanes 310 |
| B1 | 41 | PLATEAU 1.0, KMIN 150, KMAX 500, TMAX 90 | 5 min, killed with the B1 schedule | 309 | 260 | 0 | random 186, hyperplanes 296 |
| B_variant | 21 | defaults, from the second 512-cap below | 20 min, ended on time limit | 1246 | 1064 (18 not proven optimal) | 0 | random 324, hyperplanes 312 |
| B_product | 31 | KMIN 40, KMAX 380, from the 400-point product cap | 15 min, ended on time limit | 177 | 120 (21 not proven optimal) | 0 | random 111, subspace 52 |
| B_baseline | 41 | PLATEAU 1.0, KMIN 150, KMAX 500, TMAX 90 | 38 min, ended on time limit | 1167 | 987 (22 not proven optimal) | 0 | random 332, hyperplanes 302 |

**Best net gain observed for k-removal: 0, in every neighbourhood type and every run.** No plateau move was ever
made: on every solve CP-SAT returned exactly S = R (it starts from the hint, so this does not prove that no
alternative optimum exists, only that none was found). The neighbourhoods freed remarkably few new points: removing
all cap points of an affine hyperplane (108 to 208 points) freed only 10 to 18 outside points, removing 200 random
cap points freed 5 to 9, and removing 300 freed about 170. With up to 332 removed points re-solved to proven
optimality the optimum was always exactly the removed set.

## Step 3: program search around the FunSearch priority (`greedy.py`)

The FunSearch greedy builder (add the unblocked point of highest priority, repeat) with the published n = 8
priority function, its eight constants exposed (the exponent of n, the reflection multipliers, the zero-position
multipliers, the per-nonzero increment):

- published constants: 512 (the FunSearch cap); tie-break noise up to 1% of the priority range: still 512; noise of
  10% or more: at most 336;
- 74,659 random log-normal perturbations of 1 to 3 constants (60,552 in a first 15-minute run, seed 7, whose results
  were lost to a path bug after the run; 14,107 in a 6-minute rerun, seed 8): the best was 512, reached by many
  variants, and among distinct caps the next sizes were 452 (seed 7 only) and 448;
- 151,858 priorities from other families (random combinations of weight, number of reflections v_i = v_{8-i},
  full-weight-and-reflection, first coordinate zero, and counts of zeros of two random linear forms): none beat 512.

The rerun saw 2 distinct 512-caps, 146 distinct 448-caps and a tail down to 425. The second 512-cap shares 384
points with the FunSearch cap and has exactly the same completeness distribution as above, so it is very probably
an affine image of it (not checked). The repo verifier reports it valid at 512 (ties). The exchange search from it
(B_variant) also gained nothing.

## Step 4: product starting points

CP-SAT, one worker, from scratch: caps of the best known sizes 4 (F_3^2), 9 (F_3^3) and 20 (F_3^4), but only 39 in
F_3^5 (best known 45) and 79 in F_3^6 (best known 112) in its 4.8 and 6 minutes. I did not have explicit coordinates
of the 45- and 112-caps and did not build them from the literature. Products: 4 x 79 = 316, 9 x 39 = 351,
20 x 20 = 400; greedy completion added no point to any of them. The 400-cap is complete (every outside point
completes at least 3 lines: `3: 2400, 10: 40, 18: 3600, 60: 120, 200: 1`), and 15 minutes of exchange search from
it (B_product) gained nothing. Doubling constructions were not tried.

## Why it stalled

The 512-cap is a strict local optimum under every neighbourhood tried: it is complete with minimum blocking count 4,
and even large removals (a whole hyperplane section, or a third to two thirds of the cap) refill to exactly the same
points. Local search near it is the wrong tool. Starting points other than the FunSearch construction (product caps,
other priority functions) came out at 448 or less, and the exchange search could not grow them either.

## Do not repeat

- Exchange search (remove k, re-solve the freed set exactly) around the FunSearch 512-cap with k up to about 330,
  hyperplane sections and unions, or low-count targeting: net gain 0 in about 8,700 exact solves.
- Random perturbation of the published priority function's constants: it gives 512 or at most 452.
- Searching for caps in F_3^5 or F_3^6 from scratch with CP-SAT to build products: it is far below the known sizes in
  minutes; take the 45- and 112-caps from the literature instead.

## Untried

- Products and doublings that start from the actual 45-cap in F_3^5 and the 112-cap in F_3^6 (and Edel-type
  constructions that gave the old 496 record), followed by exchange search.
- Neighbourhoods that free a whole affine subspace (remove the cap points of a codimension-2 or -3 subspace and also
  every cap point that blocks a point inside it), i.e. re-optimising a region together with its boundary, which
  frees far more candidates than the rules above.
- Exploiting the cap's symmetry group (search only for caps invariant under a subgroup, which shrinks the problem
  enough for exact solving over the whole space).
- An LLM-in-the-loop program search in the style of FunSearch, which needs far more than 2 hours.
