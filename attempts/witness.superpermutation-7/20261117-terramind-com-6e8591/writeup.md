# Score-20 kernel search plus LKH segment re-solves from the 5905 superpermutation (2 h): no 5904 found

**Outcome.** No superpermutation on 7 symbols shorter than 5905 was found. The best valid string in hand at the end is the 5905-character baseline posted by Andrei Teodorescu. It ties the record, and it is his result, not ours. This writeup is not machine-checked.

## Record status, read on 2026-11-17

- The group thread "n=7 superpermutation of length 5905" (https://groups.google.com/g/superpermutators/c/D5sKkV2jBuc) posts four 5905-character words. As the thread itself notes, sol3 and sol4 are reversed relabellings of sol1 and sol2. No later post visible in the thread claims a shorter string.
- The group's thread list, as far as the page showed it, has no n = 7 construction shorter than 5905. It does carry lower-bound claims ("s(7) >= 5,899, proved in Lean", 8 Oct 2026).
- The almanac API (https://superpermutations.com/api/records) lists n = 7 with `upper_bound` 5905 and `lower_bound` 5899. Its record W-0021 credits Teodorescu, and its note gives his kernel: `4666446666-6666466636666-666646646666-666646646666-6666366646666-6666446664`.

We did not check the 5899 lower bound. If it holds, the gap is 5899 to 5904.

## Baseline (measured)

- `5905_7_sol1.txt` and `5905_7_sol2.txt` from the thread were stripped to their digits. Each is 5905 characters, and `bun frontier diagnose ... --problem witness.superpermutation-7` reports each one "valid: yes, ties the best known value".
- Structure of sol1 (from `analyze.py`): 5040 permutation windows, all distinct. The 5039 steps between them have weights 1 ×4254, 2 ×716, 3 ×64 and 4 ×5, so 69 steps weigh 3 or more. Length = 7 + Σweights = 5905. sol2 has the same weight counts.
- Running Egan's `PermutationChains 7 nsk<kernel>` on Teodorescu's kernel, with no symmetry options, reproduced 4 solutions of length 5905 in under a second.

## Background

A Houston kernel is a chain of complete 1-cycles. Each digit d is a run of d 1-cycles joined by weight-2 edges. Adjacent digits are joined by a weight-3 edge, and a `-` marks a weight-4 edge. KernelFinder.c defines a kernel's score as (1-cycles covered) − 5 × (symbols, dashes included). PermutationChains then tries to cover the remaining 1-cycles with trees of 2-cycles.

On this construction the final length is 5907 − score/5:
- Egan's 5906 kernels score 10 (for example `666466646646664666`).
- Teodorescu's kernel scores 15. We computed this: it is 75 symbols long and covers 390 1-cycles. That gives 5905.

So with this construction a 5904 needs a kernel of score 20 (or 25 for 5903) that PermutationChains can complete.

Why the relation holds, as we understand it:
- A complete 2-cycle tree adds the same number of characters for every 5 new 1-cycles it covers.
- The kernel's score counts how many characters its own weight-3 and weight-4 joins save against that rate.
- So the score must be a multiple of 5 (n − 2) for the remaining 1-cycles to be covered exactly, and each 5 points of score is one character saved.

This is an **assumption** read from Egan's and Houston's descriptions and checked on two data points: score 10 gives 5906 and score 15 gives 5905. It also assumes a 5904 would come from this kernel-plus-trees construction at all. A string outside that class is not ruled out by anything here. PermutationChains printed "has score of 20" for our kernels and reported target sizes that fit it, but no score-20 kernel was completed, so the relation was never tested end to end at 5904.

## What was run

Hardware: 2 cores of a shared laptop. The search wall clock ran from 21:22 to 23:20 IST on 2026-11-17, which is 118 minutes and within the 120-minute budget. Every search process ended by its own time limit: the drivers printed their `end` lines, and the LKH line was stopped by hand as described below.

From about 22:52 to 23:05 the two kernel drivers ran unattended while the agent was paused at a usage limit. They kept their own deadline, exited at 23:20 inside the budget, and did not overrun. Nothing was found in that interval. The only candidate files on disk are the 5905 words described below.

### Line 1: LKH-3 large-neighbourhood search on the permutation path (`lns_lkh.py`)

- Each iteration picks a random weight-≥3 step. It cuts a segment of K = 200 to 1200 permutations around that step (shorter at the path ends; the logged range is 30 to 1200).
- Both ends of the segment are kept fixed. The segment is re-solved as an ATSP path: the two ends are merged into one node, so a tour equals a path, and the edge weight is 7 − (longest overlap).
- LKH-3 settings: the cerebis/LKH3 GitHub mirror, because the author's host was unreachable from here. RUNS = 1, MAX_TRIALS = K, MAX_CANDIDATES = 8, MOVE_TYPE = 5, TIME_LIMIT = 60 s. The initial tour is the current order, and the seed comes from an RNG seeded with 20261117.
- An equal-or-better segment is accepted. Any strictly shorter word would have been written out and checked.
- It ran 21:24 to 22:05 (about 40 min, 847 segments) and was then stopped on purpose so its core could run a second kernel search.
- **Result (measured):** 0 strict improvements in 847 segments. The count of weight-≥3 steps stayed at 69 throughout.

### Line 2: score-20 kernel search plus PermutationChains (`kernelwalk_search.c`, `kernel_driver.py`)

- `kernelwalk` is Egan's KernelFinder.c with its exhaustive `search()` and `main()` replaced. The replacement is a randomised depth-first search. Moves are ordered by a weighted random race: digit 6 has weight 8, digit 5 weight 3, `-` weight 1, and lower digits 0.5. The search restarts after a node budget of 2·10⁴, 2·10⁵ or 2·10⁶ nodes, with 5 restarts per batch. It can start from a fixed kernel prefix.
- From scratch, this random DFS found almost no high-score kernels: 0 kernels of score ≥10 in 3·10⁶ nodes. So every batch instead keeps a prefix of a base kernel, cut at a random point, and re-completes the tail. The target score is 20 or 25, or 15 in a 15–30% share of batches. Max length is the base length + 5 to 35.
- Each new kernel goes to `PermutationChains 7 nsk<kernel>` with no symmetry options, as in the 5905 find, with a 60 s timeout. Most kernels end at once with "Exclusion of 2-cycle N is unviable". A kernel that reaches "Searching for solutions of size …" is counted as viable.
- The base pool starts as {Teodorescu's kernel, its reversal}. Every viable kernel joins the pool in both orientations.
- Four driver runs, in order:
  - v1: seed 20261117, no pool, 10 min.
  - v2: seed 20261118, with the pool, 9 min.
  - v3: seed 20261119, pool seeded from v1 and v2, 21:45 to 23:20.
  - v4: seed 777, pool seeded from v1 to v3, on the core freed from LKH, 22:04 to 23:20.

**Results (measured):**

| run | kernels tested | unviable | viable (reached tree search) | solutions |
|---|---|---|---|---|
| v1 | 3,095 | 2,740 | 0 | 0 |
| v2 | 29,693 | 21,830 | 273 | 1 kernel (Teodorescu's own, 4 words, all 5905) |
| v3 | 201,427 | 154,266 | 2,174 | 0 |
| v4 | 167,899 | 128,804 | 1,890 | 0 |

- About 402,000 kernel tests in total, with some overlap between the parallel runs.
- Distinct kernels logged from v2 on: 379,285 (242,492 of score 15, 135,932 of score 20, 861 of score 25).
- Distinct viable kernels: 4,162, of which 3,856 score 15, 306 score 20 and none score 25.
- Every viable score-20 kernel ended its PermutationChains search at once, with no solution.
- The only solutions found were Teodorescu's 4 words of length 5905, re-found when his own full kernel came up as a tail completion. `diagnose`: "ties the best known value".
- None of the other 3,855 viable score-15 kernels had a completion either.

## Self-tests (measured, `selftest.py`, `selftest_n5*.py`)

1. **Validity check.** The validity check inside the LNS (all 5040 permutation windows distinct) accepts the 5905 baseline. It rejects a copy with character 3000 changed, and a copy with character 3000 deleted. `bun frontier diagnose` also rejects both copies, with 6 missing permutations each.
2. **Path round trip.** Rebuilding the word from its permutation path gives back the baseline exactly.
3. **n = 7 segment repair.** In the window [2000, 2300] of the baseline path, a 40-permutation stretch was reversed, which raised the window's cost from 351 to 548. The LKH segment re-solve brought it back to 351. The rebuilt 5905 word is valid.
4. **n = 5 known optimum.** We started from the padded lexicographic path (597 characters, ends 12345 and 54321 fixed).
   - With the settings used in the n = 7 run (RUNS = 1, MAX_CANDIDATES = 8), 13 seeds reached 154 or 155 and **never the known minimum 153**.
   - The known 153 word has those same two ends, so 153 is reachable under this encoding.
   - With stronger settings, every probe reached 153 (repo verifier: valid, value 153): MAX_CANDIDATES 20, MAX_TRIALS 5000, RUNS 5, with or without an initial tour; and MOVE_TYPE 3, MAX_CANDIDATES 10, RUNS 10.
   - **So the LKH line as run on n = 7 was under-powered**, and its 847 null segments are weak evidence.
5. **Kernel-line recovery (`selftest_recover.sh`, log `selftest_recover.out`).** Teodorescu's score-15 kernel was cut after its first c symbols, and `kernelwalk` re-completed the tail (target 15, max length 75, one restart of 5·10⁷ nodes, seed 1).
   - His exact kernel was among the emitted kernels for c = 72, 70, 65, 60, 55 and 50, but not for c = 45 or 40.
   - PermutationChains on that kernel returns 4 solutions. These are byte-identical to the four posted words sol1 to sol4, and `diagnose` rates them valid, 5905, ties.
   - During the search, driver v2 hit the same kernel by chance, and its 4 output words are again identical to sol1 to sol4 (`selftest_score15_compare.out`).
   - A fresh 60 s run of the final driver at target 15 (`selftest_score15.out`) found 61 viable kernels but did not hit his kernel again. So the rediscovery in the search was a random hit, not a guaranteed one.
   - **What this shows:** the generator can reach a known completable kernel from a prefix of up to 25 missing symbols, and the PermutationChains step converts it into valid words checked by the repo verifier.
   - **What it does not show:** that the pipeline can find a *better* answer than its start. We have no small case where the kernel line went from a longer string to a shorter one.

## What we measured and what we inferred

- **Measured:** everything in the results and self-test sections above. That covers the counts, the null results and the n = 5 behaviour.
- **Inferred, not shown:**
  - That score-20 kernels near Teodorescu's are rarely viable. 306 viable out of about 136,000 score-20 kernels tested is a property of our generator's neighbourhood, not of all kernels.
  - That PermutationChains's search for a viable kernel is exhaustive within its own class of solutions (2-cycle trees anchored on the kernel). This is from reading its readme and seeing it finish in about 0.01 s. We did not audit its code.
  - That length = 5907 − score/5 for these kernels.

**Not shown:** that no 5904 exists, that no score-20 kernel has a completion, or anything about strings outside the kernel-plus-trees and segment-re-solve neighbourhoods.

## Do not repeat

- Re-completing tails (or heads, by reversal) of Teodorescu's kernel to score 20 with a weighted random DFS. About 136,000 such kernels, all with Teodorescu's prefix or suffix, gave 306 viable kernels and no completions.
- LKH segment re-solves with RUNS = 1 and MAX_CANDIDATES = 8. These do not reach the optimum even at n = 5.

## Untried

- Replacing the middle of a kernel while keeping both ends. This needs a kernel DFS that must hit a target state.
- Score-20 kernels unrelated to Teodorescu's, for example from KernelFinder run exhaustively at higher lengths.
- Running PermutationChains with `coverFirst`, or with the anchor options.
- Segment re-solves with the stronger LKH settings found above (RUNS ≥ 5, MAX_CANDIDATES ≥ 10), and a full 5040-node ATSP from the baseline tour.
- Using Teodorescu's second distinct word (sol2) as an LNS start.
- Starting kernel pools from Egan's seven fruitful score-10 palindromic kernels.

## Files

All of these are our own code.
- `analyze.py`: path and weight analysis.
- `lns_lkh.py`: the LKH segment LNS.
- `kernel_driver.py`: the kernel line driver.
- `kernelwalk_search.c` and `build_kernelwalk.py`: our replacement search and main for KernelFinder.
- `selftest.py`, `selftest_n5.py`, `selftest_n5_params.py`, `selftest_recover.sh`, `verify_n5.ts`: the self-tests.

Greg Egan's KernelFinder.c and PermutationChains.c (github.com/superpermutators/superperm, commit 1922a34) are AGPL-3.0 and are not included here. `build_kernelwalk.py` rebuilds `kernelwalk.c` from KernelFinder.c plus `kernelwalk_search.c`, and the result is byte-identical to the binary's source used here. PermutationChains was compiled unmodified with `cc -O3`.
