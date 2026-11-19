# C3-symmetric flip-graph descents from diagonal-partition starts, 2 h, no rank-92 scheme found

This writeup is not machine-checked. It reports a bounded search that did not beat the record. It gives no lower bound and no proof that a scheme with 92 or fewer terms does not exist.

## Summary

The record is a rank-93 scheme for 5x5 matrix multiplication (Moosbauer and Poole, arXiv:2502.04514). It was found by a flip-graph search over GF(2) restricted to schemes invariant under the cyclic action (a, b, c) -> (b, c, a), descending from a "diagonal partition" starting point. A C3-invariant scheme consists of full orbits (3 terms each) and fixed terms X ⊗ X ⊗ X; the start for a partition P has one fixed term per block. While the fixed-term count remains unchanged, two blocks give ranks 3k + 2 and one block gives ranks 3k + 1 (k = number of full orbits). Collapses can change this count. For example, four and five fixed terms also permit 91 and 92 with 29 full orbits. Rank 93 = 3·30 + 3 came from a 3-block partition. A previous attempt on this problem walked at rank 93 from the published scheme and kept its 3 fixed terms throughout, so it stayed on ranks 3k + 3. This attempt descends from 2-block and 1-block starts, which give 92 = 3·30 + 2 and 91 = 3·30 + 1 if their fixed-term count stays unchanged.

Measured outcome, all over GF(2), in a 120-minute run on 2 cores:

| start (block sizes) | target | descents | lowest rank | descents ending at the lowest |
| --- | --- | --- | --- | --- |
| {4,1}, e.g. {{1,2,3,4},{5}} | 92 | 237 fresh reported (234 regular) + 44 reported restarts from rank-95 states (one more killed in progress) | 95 (= 3·31 + 2) | 20 of 234 regular fresh |
| {3,2}, e.g. {{1,2,3},{4,5}} | 92 | 113 reported (112 regular) | 98 (= 3·32 + 2) | 29 of 112 regular |
| {5}, i.e. {{1,2,3,4,5}} | 91 | 108 unique descents begun, 107 with a reported best, 103 regular (see "Runs" for one crash and one replay) | 97 (= 3·32 + 1) | 23 of 103 regular; three more reported 97 before stalling or being cut |
| {2,2,1}, the paper's {{1,5},{2,4},{3}} | 90 | 116 reported (115 regular) | 93 (= 3·30 + 3) | 8 of 115 regular |

Counting convention (from the independent audit's recount of the logs): "reported" counts descents with a `DESCENT` row, replay rows counted once; "regular" excludes stalls, overflows and time cuts. The decompositions in the "lowest rank" column are the full-orbit and fixed-term counts that the `DESCENT` rows log for those best states; the counts at intermediate states are not logged.

This run found no GF(2) scheme with at most 92 terms and produced no integer witness at that size. Nothing went to the lift at a rank that could beat the record. The run gives no lower bound. The negative result covers reported descent minima and saved schemes; see "Tracking limits" for what the code did not record. The calibration below shows that the search reproduces the paper's rank 93 from the paper's own start, and that the lift turns those GF(2) schemes into integer schemes the repository verifier accepts at 93. Within this budget the best 2-block descents ({4,1}, rank 95) ended 3 terms above 92, the 1-block descents 6 terms above 91, and the 3-block descents 3 terms above 90.

Partitions with the same block sizes give isomorphic searches. Relabelling the indices by a permutation σ (simultaneous conjugation of all three factors by the permutation matrix) is a symmetry of the matrix multiplication tensor that commutes with the cyclic action and maps the starting point of P to that of σ(P). So {{1,2,3},{4,5}}, {{1,5},{2,3,4}} and {{1,2},{3,4,5}} are the same search. Only the block-size types {3,2}, {4,1} and {5} are distinct 2- and 1-block starts, and those are what was searched. The independent audit checked this argument against the code's moves and compared the actual expanded {{1,2,3},{4,5}} and {{1,3,5},{2,4}} starts under the permutation (1→1, 2→3, 3→5, 4→2, 5→4). The same numerical seed need not produce conjugate paths, because insertion order and indexed choices can differ.

## Method

`c3flip.cpp` is written from the paper's description (Definition 6, Theorem 4, Algorithm 1, Section 8), not from the authors' code, which was not downloaded.

- Representation: an n x n factor matrix is a bitmask (bit i·n + j = entry (i, j)), in trace form: the target tensor is the sum over i, j, k of E_ij ⊗ E_jk ⊗ E_ki. A scheme is a list of fixed terms X ⊗ X ⊗ X and a list of orbit representatives (a, b, c); the orbit is {(a,b,c), (b,c,a), (c,a,b)}. Rank = 3·(orbits) + (fixed terms).
- Starting point for a partition P (Definition 6): one fixed term (Σ_{i∈B} E_ii)^{⊗3} per block B; the standard terms E_ij ⊗ E_jk ⊗ E_ki with (i, j, k) not all equal, one representative per rotation class; and correction orbits E_ii ⊗ E_jj ⊗ E_kk for i, j, k in one block, not all equal. Start ranks: {2,2,1} 135, {3,2} 152, {4,1} 182, {5} 241. Each start is checked exactly against the target tensor before use.
- Orbit flip: two distinct orbits whose representatives, after rotation, share the first factor X: (X, b, c) + (X, b', c') -> (X, b, c + c') + (X, b + b', c') over GF(2). A pair is drawn by picking a uniformly random factor value that occurs at least twice, then two of its occurrences in different orbits. After 64 failed draws the descent ends as "stuck"; this is not an exhaustive check that no eligible pair exists. A factor that becomes zero deletes its orbit; this is how reductions happen (as in the paper, reductions are not searched for separately, except in the optional greedy variant below). An orbit whose representative becomes a ⊗ a ⊗ a is converted to a fixed term (coefficient 3 = 1 mod 2).
- Orbit plus-transition: (a, b, c) + (a', b', c') -> (a + a', b, c) + (a', b, c + c') + (a', b + b', c'), on two random orbits with random rotations (requires a ≠ a', b ≠ b', c ≠ c'). A plus-transition usually adds a full orbit. Its output orbits can collapse, and fixed terms can cancel.
- Descent: the loop adapts Algorithm 1 with finite move-selection retries, a best-relative plus cap in later runs, and a best-state report at descent end. It records minima after flips and optional greedy reductions. It makes random flips and a plus-transition every M flips, with the counter reset only when the descent reaches a new minimum rank (`--paper-plus`), and stops after L flips without a new minimum. Duplicate full orbits remain in the list until a later reduction removes them; they are not cancelled when they appear. Default settings: L = 1e8, M = 5e4, the numerical values of the paper's 5x5 run; one variant run used L = 2e8, M = 1e5. This code counts one flip per orbit move, while the upstream C3 solver counts three, so the same numbers allow about three times as many orbit moves here. The printed Algorithm 1 has no rank-relative cap. The cap in the later builds (no plus-transition while the scheme has 30 or more orbits above the descent's best) removes paths from it, and skipped plus-transitions were not logged. Each descent starts again from the diagonal start (independent descents), except in the "kicks" and "pool" runs described below.
- Checks: the full tensor identity is recomputed exactly over GF(2) at every new descent minimum, every 2^20 flips, and for every saved scheme. Every descent's best scheme is re-verified before it is reported, and the run aborts on any failure. None failed.
- Lift (`c3lift.py`): a C3-symmetric Hensel lift on the cyclic Brent equations (paper, Section 6). The unknowns are the orbit representatives' entries; the fixed terms are constants with entries 0/1. From modulus 2^m to 2^{m+1} it solves J(x0)·y = −F(x_m)/2^m mod 2, with J the Jacobian at the GF(2) solution, on one equation per rotation class of (p, q, r) (5,225 equations at n = 5). The sign has no numerical effect in characteristic two. Variables that are odd mod 2 come first in the elimination order, so they tend to be pivots and the zero entries tend to stay free at 0. These fixed entries and zero-biased choices restrict the lifts it explores, so a failure at some level would not be a general obstruction. After each level the entries are taken in the symmetric range and tested as an exact integer scheme. That in-script test uses NumPy `int64` and can wrap at high levels; the repository verifier is the authoritative check. The output is written in the verifier's JSON format and checked with `bun frontier diagnose`.
- Distinct states: each state has an order-independent 64-bit hash (sum of per-orbit hashes, each the minimum over the three rotations). The hash is inserted into a per-descent set every 128 flips; the set stores at most four million hashes. "distinct_within_descent" counts distinct sampled hashes. Percentages of distinct states below are the sum over descents of within-descent distinct sampled hashes divided by the number of samples. "Distinct best schemes" counts distinct hashes of descents' final best states.

## Tracking limits

These limits come from the independent audit's reading of `c3flip.cpp` and its planted tests. They bound what the negative result covers.

- Rank after each kind of move is not recorded. The best-rank update runs after flips and greedy reductions but before the plus-transition, so a rank decrease caused by a plus-transition can go unrecorded (the audit planted a local example where a plus-transition turned six terms into five).
- Duplicate full orbits are not cancelled when they appear, so a state can hide a smaller reduced scheme until a later reduction removes the pair.
- Capacity handling: the overflow guard checks before, rather than after, the greedy batch or the plus call, and an overflowing move can still abort inside `renameOcc`.
- Skipped plus-transitions under the cap are not logged, so the cap's effect on the historical minima is unknown.
- A "stuck" descent ended after 64 failed draws, not after a check that no flip exists.

The audit found no evidence that the first two produced an unreported rank of at most 92 in these runs. The 57 saved C3 schemes it checked had no duplicate pair and a correct GF(2) tensor.

## Calibration (before the long run, about 10 minutes, 19:08 to 19:16 UTC)

Measured:
- Self-test (`--selftest`): 20,000 random flips and plus-transitions from the 2x2 {{1,2}}, 3x3 {{1,2},{3}} and 5x5 {{1,5},{2,4},{3}} and {{1,2,3,4,5}} starts, with the full tensor identity and the factor index re-checked after every move: 0 failures. A copy with one bit flipped was rejected each time.
- 2x2 from {{1,2}}: 20 of 20 descents reached rank 7 (Strassen's rank, over GF(2)).
- 3x3 from {{1,2},{3}}: 20 of 20 descents reached 23 (the paper reports 23 for any 2-part partition). From {{1,2,3}}: 10 of 10 reached 25 (= 3·8 + 1).
- The retained logs for these self-test and small-size runs are incomplete: the self-test pack is not fully retained, the 3x3 count survives as a summary, and the 2x2 log keeps only the last descent and the finish. The audit's reruns reproduced the 2x2 and 3x3 outcomes (see "Independent audit").
- 5x5 from the paper's partition {{1,5},{2,4},{3}}:
  - The first descent rule I implemented reset the plus-transition counter after every reduction (my reading of the paper's prose). The two 150-second calibration processes reported 14 rows for ordinary flips, including one time cut, and 4 rows for greedy, including one time cut. The respective minima were 96 and 99. With M = 5e3, 96 over 10 descents.
  - With Algorithm 1 as printed (counter reset only at a new minimum), 1 of 10 descents reached 93, 31 s after the run started (final ranks {93: 1, 96: 1, 99: 3, 102: 4, 105: 1}). All later runs use this rule.
  - In the long run's last phase, the same start and settings gave 8 rank-93 schemes in 116 descents over 28.4 minutes on one core, the first 27 s in. Final ranks: {93: 8, 96: 5, 99: 43, 102: 48, 105: 7, 108: 4}, one descent cut by the time limit.
- Speed: about 5.9 to 10.3 million flips per second per process in the completed phases. This build reached 93 from the same start in under a minute in the reported runs. The paper gives a laptop time and a throughput range across inputs and hardware. These figures alone cannot compare success per flip. The paper's flip counts are also in a different unit (three per orbit move); the audit's same-machine comparison with the upstream executable is under "Independent audit".
- Lift, tested first on the published scheme: the Lille scheme reduced mod 2 is C3-invariant (3 fixed terms, 30 orbits; converted by `mask_to_c3.py`). `c3lift.py` lifted it on its first try at modulus 4 to an integer scheme with coefficients in {-1, 0, 1}, which `bun frontier diagnose` reports as `valid: yes`, value 93, ties the best known value. Further lifts:
  - all 19 distinct 3x3 rank-23 schemes from the calibration, verified with the repository verifier at n = 3 (`verify-n.ts`), all valid;
  - the 2x2 rank-7 scheme, valid;
  - a 5x5 {4,1} rank-95 scheme from the long run, valid at 95;
  - the 9 rank-93 schemes this search found from {{1,5},{2,4},{3}} (1 in calibration, 8 in the long run), all `valid: yes` at 93 with coefficients in {-1, 0, 1}.

  Every lift succeeded on its first try, at modulus 4 or 8.
- Equivalence of the 9 rank-93 schemes to the published one. Seven of nine GF(2) schemes differ from the Lille baseline by the aggregate factor-rank invariant. An invariant that groups factor ranks by term distinguishes one more. All nine lifts differ from the exact Lille scheme by rational factor-rank multiset. These comparisons establish inequivalence to that specific scheme in the corresponding field and leave prior discovery and equivalence within matching signatures open. (The aggregate GF(2) frequencies of factor ranks 1, 2, 3 are (141, 138, 0) twice, (144, 135, 0) twice, (141, 135, 3) twice, (135, 141, 3) twice and (129, 144, 6) once; Lille mod 2 has (141, 138, 0). With the per-term invariant the nine fall into at least six GF(2) symmetry classes. The per-term and rational comparisons are the audit's.) They tie the record and are not submitted as witnesses.

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

Approximate core-minutes: {4,1} 102, {5} 54 (about 13 of them a replay of an earlier seed), {3,2} 41, {2,2,1} 28, idle 13. The 2- and 1-block starts took about 87% of the used time. The audit's recount: 225.1 core-minutes of process time across the 120-minute schedule; summing new reported descent rows gives 100.42 billion flips, and work in descents killed before a `DESCENT` line is extra (at least 1.074 billion flips in the last kicks descent). Process timings confirm at most two search processes. The logs give sample counts but no exact unique-state totals, CPU utilisation or memory use.

The searches ran unattended for part of the run. During one usage-limit pause, from about 20:38 to 20:45 UTC, the phase-3 processes kept running inside their planned windows. Nothing overran the budget, no planned phase was skipped, and the last phase was launched after the pause to end at the budget end.

**The {5} crash (p1-5).** It aborted with "delOcc: missing id" in descent d=33 (0-based; exit 134, SIGABRT). Cause: each factor value keeps a fixed-size list of at most 120 occurrences. Under Algorithm 1's rule, plus-transitions continue every M flips, and with no cap on the rank one descent ran away: plus-transitions outpaced reductions and the rank grew until a list overflowed. The occurrence was then missing from the index. Reproduced: rerunning seed 2001 with the same uncapped rule and a build that ends the descent cleanly on overflow gave the same first 33 descents (the audit confirmed they match the original in rank, counts and hashes), and descent 33 ended with `overflow=1` after 4.9 s (best 169 from start 241). The audit counted 898 plus-transitions against 821 reductions in that descent before the overflow. Later builds cap plus-transitions at 30 orbits above the descent's best and end a descent on overflow. No later run overflowed; the guard's remaining gaps are under "Tracking limits". Descents completed before the crash were verified and are counted.

**Final ranks per run** (from the DESCENT lines; `summarize.py`):
- p1-32 {3,2}: {98: 28, 101: 69, 104: 10, 107: 2, 110: 1}, plus 1 cut by time. 28 distinct schemes at 98.
- p2-32k {3,2}, 20 "kicks" (on a stall, restart from the descent's own best state, up to 20 times): 2 descents in 10.6 min, {98: 1, 101: 1}. 16.5% of sampled states were distinct. This is a lower bound, because one kick descent filled the four-million-hash set. In fresh descents the same measure was 75% to 92% by start type in the audit's recount ({3,2} 74.7%, {5} 78.6%, {4,1} 86.6%, {2,2,1} 91.5%). Stopped.
- p2-41 {4,1}: {95: 7, 98: 35, 101: 19, 104: 18, 107: 3}, plus 1 cut.
- p3-41pool, restarts from the five rank-95 {4,1} schemes: all 44 reported descents ended at their own start scheme; one further descent was killed in progress. 220,399 distinct sampled hashes over 34.4 million samples (0.64%), so walks at 95 kept revisiting a small region. Stopped.
- p3-41v {4,1}, L = 2e8, M = 1e5: {95: 4, 98: 15, 101: 9, 102: 1, 104: 12, 107: 1}, plus 1 cut.
- p4-41 {4,1}: {95: 9, 98: 45, 101: 19, 104: 24, 107: 8, 110: 3, 113: 1, 114: 1}, plus 1 cut.
- p1-5 {5}: {97: 6, 100: 10, 103: 5, 104: 2, 106: 6, 109: 3}, plus 1 stuck (64 failed flip draws) and the crashed descent.
- p1b-5-repro {5}: descents d=0 to d=32 replay p1-5 exactly; d=33 is the overflowed descent; d=34 to d=38 are new: {97: 1, 100: 2, 103: 2}.
- p3-5 {5}: {97: 16, 100: 26, 101: 1, 103: 13, 104: 1, 106: 6, 109: 1, 110: 1, 113: 1}, plus 2 stuck and 1 cut.
- p4-221 {2,2,1}: as in Calibration.

Ranks such as 101 and 104 for {5}, and 102 and 114 for {4,1}, are off the 3k + |P| pattern. In those descents the fixed-term count changed (an orbit collapsed to a fixed term, or fixed terms cancelled). Off-pattern ranks were rare. They are only the visible cases: the count can also change while the rank stays on the pattern. In the audit's replay, the first {4,1} descent of p4-41 reached 107 with five fixed terms, and the 3-block calibration logged three fixed terms at its reported minima.

**When the best values appeared** (audit recount): the first reported 95 came at 19:52:25 UTC (5 min 34 s into the first {4,1} run), the first 98 at 19:16:51 (37 s after launch) and the first 97 at 19:17:14 (60 s after launch). None of the three minima improved after that. The final {4,1} phase still produced nine 95s, the last at 21:14:04.

## Measured

- No reported descent minimum or saved GF(2) scheme from {3,2}, {4,1} or {5} starts had rank 92 or less. The auto-lift watcher (`autolift.sh`, every saved scheme below 93) never triggered. "Tracking limits" lists what the code did not record.
- Lowest GF(2) ranks: {4,1} 95, {3,2} 98, {5} 97, {2,2,1} 93. The 95 and 97 reproduce endpoints already named in the upstream 5x5 run manager ([upstream cases, lines 296–308](https://github.com/jakobmoosbauer/symmetric-flips/blob/main/code/MatrixMult22.py#L296-L308)).
- The same code and settings reach the record rank 93 from the paper's {{1,5},{2,4},{3}} start in 7% of descents (8 of 115 regular), the first 27 s after start. Every rank-93 and rank-95 scheme tried lifted to a verifier-accepted integer scheme.
- From {4,1}, 20 of 234 regular fresh descents (8.5%) ended at 95, 3 terms above 92. From {3,2}, the best was 98, 6 terms above 92.

## Inferred

- The search reproduces known values: from the paper's start it reached 93 within a minute in the reported runs, 23 at 3x3 and Strassen's 7 at 2x2. Every 2- and 1-block descent's reported minimum stayed at least 3 terms above its target. So this run says little about whether a 2-block C3 scheme of rank 92 exists. It shows that, with these settings and about 100 core-minutes on {4,1}, the reported descent minima did not get there.
- The audit's extrapolation of the hit rate at 92 assumes the same conditional step from at most 95 to at most 92 as from at most 98 to at most 95. The regular {4,1} rows give 20/115 for the latter step and 20/234 for reaching 95. That model predicts about 1.49% per descent, or 67 descents per hit in expectation, and about a 3% chance of zero hits across 234 independent descents, which is what was observed. The settings also varied. With zero hits, the one-sided 95% binomial upper limit under i.i.d. sampling is 1.27% per descent, with no positive lower limit. The 67 is an extrapolation the observed data already strain; the expected time to 92 is unresolved.
- In restarts from the five rank-95 {4,1} states, 99.36% of sampled hashes were within-descent repeats, and kicks back to the best state cut the distinct fraction to 16.5% or more. More flips from the same states looks less promising than more independent descents or different starts.
- {4,1} is the most promising 2-block type seen here: 8.5% of its regular fresh descents reach 95, against 0% for {3,2}. {5} reaches 97 but needs 6 more terms for 91.

## Independent audit

A second model from another family (gpt-6.2-sol) audited this attempt before submission. It rebuilt `c3flip.cpp`, checked every start against an independently formed target tensor, drove the move functions through 24,000 randomized test steps across eight starts with an independent exact tensor check (all passed), recounted the historical logs, replayed controls, re-lifted schemes and re-ran `bun frontier diagnose` on 11 lifts. It confirmed the bounded result (95, 98 and 97 for the three target starts) and found that several statements went beyond the evidence; those statements are corrected above. The audit is an opinion backed by reruns, not a check by the repository verifier. Its measurements, all on its own machine and not part of the original run:

- 2x2 and 3x3 controls: from {{1,2}}, 20 short 2x2 runs reached the known optimum 7 and none reached 6. From {{1,2},{3}}, all 20 3x3 runs reached 23 with L = 300000, M = 1000. From the one-block 4x4 start {{1,2,3,4}} with this code, L = 3e6, M = 3000 gave sixteen 49s and four 52s in 20 runs (this code has no reversal moves); the upstream 4x4 C3 × Z2 case with its defaults gave 20 of 20 rank-49 schemes.
- 5x5 calibration replay: two fresh 600-second processes from {{1,5},{2,4},{3}} with the default settings and cap 30 completed 57 and 58 descents (plus one time cut each) and hit 93 four and three times; the first hits came after 256 s and after 5 s. Completed ranks: {93: 7, 96: 7, 99: 47, 102: 47, 105: 4, 108: 3}. About 14.10 and 13.95 million orbit flips per wall second per process; peak memory 119 and 103 MiB. All seven rank-93 schemes passed an independent GF(2) check, and the earliest one lifted at modulus 4 to an exact integer tie.
- Negative replay: the first three {4,1} descents of p4-41 (seed 9001, logged settings) reproduced best ranks 107, 95 and 98 with the same hashes and flip counts.
- Upstream comparison: the upstream 5x5 executable reached 93 once in 12 runs with its public case file, at about 17.59 million orbit flips per second end to end, about 1.25 times this code's per-worker rate in the two-process replay. Its schedule differs (it reschedules plus moves after reductions and stops at the target), so the yields are not directly comparable.
- Low-rank yield per core-hour in the original logs: the default {4,1} setting gave 16 rank-95 rows in 3,506 core-seconds (16.4 per hour); the doubled L = 2e8, M = 1e5 run gave 4 in 2,041 core-seconds (7.1 per hour).
- Integer checks: the baseline lift, all nine rank-93 lifts and the rank-95 lift were diagnosed by the repository verifier (93 ties the best known value; 95 does not reach it) and agree with an exact integer check and with their GF(2) schemes mod 2.

## Not covered

- C3 × Z2 symmetry (row/column reversal), which the paper used for 6x6. Reversal moves, which the upstream code has and this code does not.
- Starts other than diagonal partitions, and modified starts such as the paper's 6x6 trick of identifying diagonal orbits in 1-block results and re-partitioning.
- Partition types {3,1,1}, {2,1,1,1} and {1,1,1,1,1}. While the fixed-term count remains unchanged, two blocks give ranks 3k + 2 and one block gives ranks 3k + 1. Collapses can change this count. For example, four and five fixed terms also permit 91 and 92 with 29 full orbits.
- Parameters other than (L, M) = (1e8, 5e4) and (2e8, 1e5). Plus caps other than 30 (the uncapped first build aside), and the upstream starting-rank ceiling. Runs longer than about 100 core-minutes per start type. Higher throughput.
- The authors' search code and their other published files were not used.

## What a later attempt could try

The audit's leads come first.

- Method: fix the tracking omissions before any long run. Record the rank after each kind of move, cancel duplicate full orbits, fix capacity handling, log both full-orbit and fixed counts at minima, and log cap skips and stalls. Keep a baseline-versus-patched seed replay, because cancellation changes the transition graph.
- Time: a 32 core-hour run split as 24 core-hours on fresh {4,1}, 6.4 on {5} and 1.6 on fresh {3,2}, with L = 1e8, M = 5e4 as the control. In the first four {4,1} core-hours, use two for the control, one for M = 1e5 with the same L, and one for the upstream-normalized L ≈ 3.33e7, M ≈ 1.67e4. Keep the cap at 30 in those tests and log skips and stalls; compare a starting-rank ceiling once the occurrence index can grow safely. Let verified low-rank hits per core-hour guide the rest. At the original blended rate, 24 core-hours buys about 3,700 fresh descents. Skip unchanged rank-95 pool restarts, which returned just their five starts.
- Method: save {5} schemes through rank 100, including rank 97 (this run retained none at 97). For each split I = X + Y into disjoint nonempty diagonal masks, look for both full cyclic orbits of (X, X, Y) and (X, Y, Y). Over GF(2), those six terms plus the identity cube I^{⊗3} equal X^{⊗3} + Y^{⊗3}, so a rank-97 state containing this pattern would become rank 92 directly, after an exact check and a lift. Test all 15 unordered diagonal splits, then consider low-cost exact replacement searches on the diagonal subspace.
- Method: keep C3 × Z2 out of the main allocation until its full size-six orbit mechanics are reproduced at n = 4 (the upstream 4x4 case is a regression test), then measure a small n = 5 pilot. The published 5x5 result needed only C3.
- Time (throughput): profile factor-table probes, occurrence deletions and hash sampling before trying SIMD; compare the current `-O3 -march=native` build with LTO and profile-guided builds on identical seeds, requiring unchanged verified outcomes. The upstream executable's 17.59 million orbit flips per second on the audit's machine is the local reference.
- Method: the paper's 6x6 approach: search from the 1-block start and look in the low-rank results for orbits of diagonal matrices that suggest a better partition.
- Method: the other partition types listed under "Not covered".
- The lift here worked on every scheme tried, so the GF(2) search is now the limiting step.

## Files

- `c3flip.cpp`: the search. Build: `clang++ -O3 -march=native -std=c++17 -o c3flip c3flip.cpp`. Three builds were used in sequence. The phase-1 runs used the first build: no plus cap, no overflow guard, no `--kicks`/`--pool`. Pass an explicit high cap to the shipped code for an uncapped reproduction. Its default cap is 30. p2-41 used a build with the overflow guard, a default plus cap of 30 orbits and progress lines. Later runs used the file as shipped, which adds `--kicks` and `--pool`. A run from this directory, without the scratch layout: `./c3flip --n 5 --partition '1234|5' --L 1e8 --M 5e4 --paper-plus --plus-cap 30 --descents 1000000 --seconds 1800 --seed 1 --tag p41 --out out --save-at 96` (create `out/` first).
- `c3lift.py`: the C3-symmetric Hensel lift. Usage: `python3 -I c3lift.py <scheme.c3> <out.json> [tries] [max_level] [random_levels] [seed]`.
- `mask_to_c3.py`: converts a full-term GF(2) mask list to the C3 format, used on the published scheme.
- `factor_ranks.py`: the factor-rank invariant.
- `summarize.py`: per-run summaries from the logs.
- `launch.sh`, `autolift.sh`, `tune.sh`: a recipe for the original scratch layout, not standalone launchers. They `cd` to the parent of their own directory and expect `bin/c3flip`, `src/c3lift.py`, `logs/` and `out/` there; `autolift.sh` also expects that directory to sit at `.terramind/scratch/matmul5-r2/` in a repository clone and runs the lift with `uv`. `launch.sh` runs one search process with start, end and exit status; `autolift.sh` lifts and diagnoses any saved scheme below 93; `tune.sh` is the calibration sweep, of which only the first half ran, stopped after the paper-plus result.
- `verify-n.ts`: runs the repository matmul verifier at any n, for the 2x2 and 3x3 lift checks.

The published rank-93 scheme itself is not copied here.
