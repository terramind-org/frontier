# C3-symmetric flip-graph descents from diagonal-partition starts, 2 h, no rank-92 scheme found

This writeup is not machine-checked. It reports a bounded search that did not beat the record. It gives no lower bound and no proof that a scheme with 92 or fewer terms does not exist.

## Summary

The record is a rank-93 scheme for 5x5 matrix multiplication (Moosbauer and Poole, arXiv:2502.04514). It was found by a flip-graph search over GF(2) restricted to schemes invariant under the cyclic action (a, b, c) -> (b, c, a), descending from a "diagonal partition" starting point. A C3-invariant scheme from a start with |P| diagonal blocks has rank 3k + |P| (k = number of full orbits) unless an orbit collapses to a fixed term. Rank 93 = 3·30 + 3 came from a 3-block partition. So rank 92 needs a 2-block start (3·30 + 2) and rank 91 a 1-block start (3·30 + 1). A previous attempt on this problem walked at rank 93 from the published scheme and kept its 3 fixed terms, so it could not reach 92. This attempt descends from 2-block and 1-block starts.

Measured outcome, all over GF(2), in a 120-minute run on 2 cores:

| start (block sizes) | target | descents | lowest rank | descents ending at the lowest |
| --- | --- | --- | --- | --- |
| {4,1}, e.g. {{1,2,3,4},{5}} | 92 | 237 fresh + 44 restarts from rank-95 states | 95 (= 3·31 + 2) | 20 of 237 fresh |
| {3,2}, e.g. {{1,2,3},{4,5}} | 92 | 113 | 98 (= 3·32 + 2) | 29 |
| {5}, i.e. {{1,2,3,4,5}} | 91 | 108 new (see "Runs" for one crash and one replay) | 97 (= 3·32 + 1) | 23 |
| {2,2,1}, the paper's {{1,5},{2,4},{3}} | 90 | 116 | 93 (= 3·30 + 3) | 8 |

No GF(2) scheme of rank 92 or less was found from any start, so nothing went to the lift at a rank that could beat the record, and no witness exists. The calibration below shows that the search reproduces the paper's rank 93 from the paper's own start, and that the lift turns those GF(2) schemes into integer schemes the repository verifier accepts at 93. Within this budget the best 2-block descents ({4,1}, rank 95) ended one orbit (3 terms) above 92, the 1-block descents two orbits above 91, and the 3-block descents one orbit above 90.

Partitions with the same block sizes give isomorphic searches. Relabelling the indices by a permutation σ (simultaneous conjugation of all three factors by the permutation matrix) is a symmetry of the matrix multiplication tensor that commutes with the cyclic action and maps the starting point of P to that of σ(P). So {{1,2,3},{4,5}}, {{1,5},{2,3,4}} and {{1,2},{3,4,5}} are the same search. Only the block-size types {3,2}, {4,1} and {5} are distinct 2- and 1-block starts, and those are what was searched.

## Method

`c3flip.cpp` is written from the paper's description (Definition 6, Theorem 4, Algorithm 1, Section 8), not from the authors' code, which was not downloaded.

- Representation: an n x n factor matrix is a bitmask (bit i·n + j = entry (i, j)), in trace form: the target tensor is the sum over i, j, k of E_ij ⊗ E_jk ⊗ E_ki. A scheme is a list of fixed terms X ⊗ X ⊗ X and a list of orbit representatives (a, b, c); the orbit is {(a,b,c), (b,c,a), (c,a,b)}. Rank = 3·(orbits) + (fixed terms).
- Starting point for a partition P (Definition 6): one fixed term (Σ_{i∈B} E_ii)^{⊗3} per block B; the standard terms E_ij ⊗ E_jk ⊗ E_ki with (i, j, k) not all equal, one representative per rotation class; and correction orbits E_ii ⊗ E_jj ⊗ E_kk for i, j, k in one block, not all equal. Start ranks: {2,2,1} 135, {3,2} 152, {4,1} 182, {5} 241. Each start is checked exactly against the target tensor before use.
- Orbit flip: two distinct orbits whose representatives, after rotation, share the first factor X: (X, b, c) + (X, b', c') -> (X, b, c + c') + (X, b + b', c') over GF(2). A pair is drawn by picking a uniformly random factor value that occurs at least twice, then two of its occurrences in different orbits. A factor that becomes zero deletes its orbit; this is how reductions happen (as in the paper, reductions are not searched for separately). An orbit whose representative becomes a ⊗ a ⊗ a is converted to a fixed term (coefficient 3 = 1 mod 2).
- Orbit plus-transition: (a, b, c) + (a', b', c') -> (a + a', b, c) + (a', b, c + c') + (a', b + b', c'), rank + 3, on two random orbits with random rotations (requires a ≠ a', b ≠ b', c ≠ c').
- Descent (Algorithm 1): random flips; a plus-transition every M flips, with the counter reset only when the descent reaches a new minimum rank (`--paper-plus`); the descent stops after L flips without a new minimum. Parameters were the paper's 5x5 values L = 1e8, M = 5e4, except one variant run with L = 2e8, M = 1e5. Each descent starts again from the diagonal start (independent descents), except in the "kicks" and "pool" runs described below.
- Checks: the full tensor identity is recomputed exactly over GF(2) at every new descent minimum, every 2^20 flips, and for every saved scheme. Every descent's best scheme is re-verified before it is reported, and the run aborts on any failure. None failed.
- Lift (`c3lift.py`): a C3-symmetric Hensel lift on the cyclic Brent equations (paper, Section 6). The unknowns are the orbit representatives' entries; the fixed terms are constants with entries 0/1. From modulus 2^m to 2^{m+1} it solves J(x0)·y = F(x_m)/2^m over GF(2), with J the Jacobian at the GF(2) solution, on one equation per rotation class of (p, q, r) (5,225 equations at n = 5). Variables that are odd mod 2 come first in the elimination order, so they tend to be pivots and the zero entries tend to stay free at 0. After each level the entries are taken in the symmetric range and tested as an exact integer scheme. The output is written in the verifier's JSON format and checked with `bun frontier diagnose`.
- Distinct states: each state has an order-independent 64-bit hash (sum of per-orbit hashes, each the minimum over the three rotations). The hash is inserted into a per-descent set every 128 flips. "distinct_within_descent" counts distinct sampled hashes. "Distinct best schemes" counts distinct hashes of descents' final best states.

## Calibration (before the long run, about 10 minutes, 19:08 to 19:16 UTC)

Measured:
- Self-test (`--selftest`): 20,000 random flips and plus-transitions from the 2x2 {{1,2}}, 3x3 {{1,2},{3}} and 5x5 {{1,5},{2,4},{3}} and {{1,2,3,4,5}} starts, with the full tensor identity and the factor index re-checked after every move: 0 failures. A copy with one bit flipped was rejected each time.
- 2x2 from {{1,2}}: 20 of 20 descents reached rank 7 (Strassen's rank, over GF(2)).
- 3x3 from {{1,2},{3}}: 20 of 20 descents reached 23 (the paper reports 23 for any 2-part partition). From {{1,2,3}}: 10 of 10 reached 25 (= 3·8 + 1).
- 5x5 from the paper's partition {{1,5},{2,4},{3}}:
  - The first descent rule I implemented reset the plus-transition counter after every reduction (my reading of the paper's prose). 150 s on 2 cores gave lowest 96 over 18 descents; with an extra greedy reduction scan, 99 over 4 descents; with M = 5e3, 96 over 10 descents.
  - With Algorithm 1 as printed (counter reset only at a new minimum), 1 of 10 descents reached 93, 31 s after the run started (final ranks {93: 1, 96: 1, 99: 3, 102: 4, 105: 1}). All later runs use this rule.
  - In the long run's last phase, the same start and settings gave 8 rank-93 schemes in 116 descents over 28.4 minutes on one core, the first 27 s in. Final ranks: {93: 8, 96: 5, 99: 43, 102: 48, 105: 7, 108: 4}, one descent cut by the time limit.
- Speed: about 6 to 10 million flips per second per core. The paper reports 1 to 6 billion flips per minute, about 17 to 100 million per second. The descent finds 93 from the paper's start within a minute, so its success rate per flip is not obviously worse than the paper's, but the throughput is lower.
- Lift, tested first on the published scheme: the Lille scheme reduced mod 2 is C3-invariant (3 fixed terms, 30 orbits; converted by `mask_to_c3.py`). `c3lift.py` lifted it on its first try at modulus 4 to an integer scheme with coefficients in {-1, 0, 1}, which `bun frontier diagnose` reports as `valid: yes`, value 93, ties the best known value. Further lifts:
  - all 19 distinct 3x3 rank-23 schemes from the calibration, verified with the repository verifier at n = 3 (`verify-n.ts`), all valid;
  - the 2x2 rank-7 scheme, valid;
  - a 5x5 {4,1} rank-95 scheme from the long run, valid at 95;
  - the 9 rank-93 schemes this search found from {{1,5},{2,4},{3}} (1 in calibration, 8 in the long run), all `valid: yes` at 93 with coefficients in {-1, 0, 1}.

  Every lift succeeded on its first try, at modulus 4 or 8.
- The 9 rank-93 schemes found here fall into at least 5 classes by the multiset of GF(2) ranks of their 279 factor matrices, which the symmetry group preserves: {1: 141, 2: 138} (the published scheme's multiset; equivalence to it was not tested), {1: 144, 2: 135}, {1: 141, 2: 135, 3: 3}, {1: 135, 2: 141, 3: 3}, {1: 129, 2: 144, 3: 6}. So the search finds rank-93 schemes not equivalent to the published one. They tie the record and are not submitted as witnesses.

## Runs (long run: 120 minutes from 19:16:13 to 21:16:14 UTC, at most 2 processes)

Each process is `c3flip` started by `launch.sh`, which records the UTC start, end and exit status. Times are from those status files.

| process | start (block type) | UTC | exit | notes |
| --- | --- | --- | --- | --- |
| p1-32 | {3,2} | 19:16:14 to 19:46:15 | 0 | first build (no plus cap) |
| p1-5 | {5} | 19:16:14 to 19:25:36 | 134 | crashed; see below |
| (idle) | | 19:25:36 to 19:37:30 | | crash noticed late |
| p1b-5-repro | {5}, same seed as p1-5, old uncapped rule | 19:37:30 to 19:52:04 | 143 | reproduced the crash cause, then stopped by me |
| p2-41 | {4,1} | 19:46:51 to 20:16:51 | 0 | |
| p2-32k | {3,2} with 20 kicks | 19:52:05 to 20:02:41 | 143 | stopped by me |
| p3-41pool | restarts from the five {4,1} rank-95 schemes | 20:02:43 to 20:12:22 | 143 | stopped by me |
| p3-41v | {4,1}, L = 2e8, M = 1e5 | 20:12:24 to 20:46:25 | 0 | |
| p3-5 | {5} | 20:17:35 to 20:47:36 | 0 | |
| p4-221 | {2,2,1} (paper's) | 20:47:48 to 21:16:14 | 0 | |
| p4-41 | {4,1} | 20:47:48 to 21:16:14 | 0 | |

Approximate core-minutes: {4,1} 102, {5} 54 (about 13 of them a replay of an earlier seed), {3,2} 41, {2,2,1} 28, idle 13. The 2- and 1-block starts took about 87% of the used time. Total about 9.9e10 flips, plus 1.0e9 in the new part of the replay run.

The searches ran unattended for part of the run. During one usage-limit pause, from about 20:38 to 20:45 UTC, the phase-3 processes kept running inside their planned windows. Nothing overran the budget, no planned phase was skipped, and the last phase was launched after the pause to end at the budget end.

**The {5} crash (p1-5).** It aborted with "delOcc: missing id" in descent d=33 (0-based; exit 134, SIGABRT). Cause: each factor value keeps a fixed-size list of at most 120 occurrences. Under Algorithm 1's rule, plus-transitions continue every M flips, and with no cap on the rank one descent ran away: plus-transitions outpaced reductions and the rank grew until a list overflowed. The occurrence was then missing from the index. Reproduced: rerunning seed 2001 with the same uncapped rule and a build that ends the descent cleanly on overflow gave the same first 33 descents, and descent 33 ended with `overflow=1` after 4.9 s (best 169 from start 241). Later builds cap plus-transitions at 30 orbits above the descent's best and end a descent on overflow. No later run overflowed. Descents completed before the crash were verified and are counted.

**Final ranks per run** (from the DESCENT lines; `summarize.py`):
- p1-32 {3,2}: {98: 28, 101: 69, 104: 10, 107: 2, 110: 1}, plus 1 cut by time. 28 distinct schemes at 98.
- p2-32k {3,2}, 20 "kicks" (on a stall, restart from the descent's own best state, up to 20 times): 2 descents in 10.6 min, {98: 1, 101: 1}. Only 17% of sampled states were distinct, against about 90% in fresh descents. Stopped.
- p2-41 {4,1}: {95: 7, 98: 35, 101: 19, 104: 18, 107: 3}, plus 1 cut.
- p3-41pool, restarts from the five rank-95 {4,1} schemes: all 44 descents ended at their own start scheme. Only 220,399 of 34.4 million sampled states were distinct (0.6%), so walks at 95 kept revisiting a small region. Stopped.
- p3-41v {4,1}, L = 2e8, M = 1e5: {95: 4, 98: 15, 101: 9, 102: 1, 104: 12, 107: 1}, plus 1 cut.
- p4-41 {4,1}: {95: 9, 98: 45, 101: 19, 104: 24, 107: 8, 110: 3, 113: 1, 114: 1}, plus 1 cut.
- p1-5 {5}: {97: 6, 100: 10, 103: 5, 104: 2, 106: 6, 109: 3}, plus 1 stuck (no flip available) and the crashed descent.
- p1b-5-repro {5}: descents d=0 to d=32 replay p1-5 exactly; d=33 is the overflowed descent; d=34 to d=38 are new: {97: 1, 100: 2, 103: 2}.
- p3-5 {5}: {97: 16, 100: 26, 101: 1, 103: 13, 104: 1, 106: 6, 109: 1, 110: 1, 113: 1}, plus 2 stuck and 1 cut.
- p4-221 {2,2,1}: as in Calibration.

Ranks such as 101 and 104 for {5}, and 102 and 114 for {4,1}, are off the 3k + |P| pattern. In those descents an orbit collapsed to a fixed term, which changes the number of fixed terms. This happened rarely.

## Measured

- No GF(2) scheme of rank 92 or less was reached from {3,2}, {4,1} or {5} starts. The auto-lift watcher (`autolift.sh`, every saved scheme below 93) never triggered.
- Lowest GF(2) ranks: {4,1} 95, {3,2} 98, {5} 97, {2,2,1} 93.
- The same code and settings reach the record rank 93 from the paper's {{1,5},{2,4},{3}} start in 7% of descents (8 of 115 completed), the first 27 s after start. Every rank-93 and rank-95 scheme tried lifted to a verifier-accepted integer scheme.
- From {4,1}, 20 of 237 fresh descents (8%) ended at 95, one orbit above 92. From {3,2}, the best was 98, two orbits above 92.

## Inferred

- The search is calibrated: from the paper's start it reproduces the paper's 93 within a minute, the paper's 23 at 3x3 and Strassen's 7 at 2x2. Its throughput is a few times lower than the paper reports, and every 2- and 1-block descent stopped at least one orbit above its target. So this run says little about whether a 2-block C3 scheme of rank 92 exists. It shows that, with the paper's parameters and about 100 core-minutes on {4,1}, the descents do not get there.
- At the level where these descents stop (93 for {2,2,1}, 95 for {4,1}), the walk is confined: in restarts from rank-95 states, 99.4% of sampled states were repeats, and kicks back to the best state cut the distinct fraction to 17%. More flips from the same states looks less promising than more independent descents or different starts.
- {4,1} is the most promising 2-block type seen here: 8% of its descents reach 95, against 0% for {3,2}. {5} reaches 97 but needs two more orbits for 91.

## Not covered

- C3 × Z2 symmetry (row/column reversal), which the paper used for 6x6.
- Starts other than diagonal partitions, and modified starts such as the paper's 6x6 trick of identifying diagonal orbits in 1-block results and re-partitioning.
- Partition types {3,1,1}, {2,1,1,1} and {1,1,1,1,1} (3- to 5-block starts can only give ranks 3k + 3 or more).
- Parameters other than (L, M) = (1e8, 5e4) and (2e8, 1e5). Runs longer than about 100 core-minutes per start type. Higher throughput.
- The authors' search code and their other published files were not used.

## What a later attempt could try

- Many more independent {4,1} descents at higher throughput (the paper's implementation is several times faster), and a sweep of M and L for the {4,1} and {5} starts.
- The paper's 6x6 method: search from the 1-block start and look in the low-rank results for orbits of diagonal matrices that suggest a better partition.
- C3 × Z2-invariant starts, and the other partition types.
- The lift here worked on every scheme tried, so the GF(2) search is now the limiting step.

## Files

- `c3flip.cpp`: the search. Build: `clang++ -O3 -march=native -std=c++17 -o c3flip c3flip.cpp`. Three builds were used in sequence. The phase-1 runs used the first build: no plus cap, no overflow guard, no `--kicks`/`--pool`; with `--paper-plus` and no `--plus-cap` the RNG path is the same. p2-41 used a build with the overflow guard, a default plus cap of 30 orbits and progress lines. Later runs used the file as shipped, which adds `--kicks` and `--pool`.
- `c3lift.py`: the C3-symmetric Hensel lift. Usage: `python3 -I c3lift.py <scheme.c3> <out.json> [tries] [max_level] [random_levels] [seed]`.
- `mask_to_c3.py`: converts a full-term GF(2) mask list to the C3 format, used on the published scheme.
- `factor_ranks.py`: the factor-rank invariant.
- `summarize.py`: per-run summaries from the logs.
- `launch.sh`: one search process with start, end and exit status.
- `autolift.sh`: lifts and diagnoses any saved scheme below 93.
- `tune.sh`: the calibration sweep; only its first half ran, and it was stopped after the paper-plus result.
- `verify-n.ts`: runs the repository matmul verifier at any n, for the 2x2 and 3x3 lift checks.

The published rank-93 scheme itself is not copied here.
