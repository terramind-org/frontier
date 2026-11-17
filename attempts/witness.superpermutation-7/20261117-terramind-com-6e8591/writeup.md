# Score-20 kernel search from an adaptive kernel pool plus LKH segment re-solves from the 5905 superpermutation (2 h): no 5904 found

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

On this construction the final length is 5908 − score/5. An earlier draft of this writeup misstated it as 5907 − score/5; the score-20 target below was right either way, so the slip did not misdirect the search. The relation follows from counting characters: a kernel covering C 1-cycles with L symbols spells a word of 4 + 8C + L characters, and each of the (720 − C)/5 attached 2-cycles adds five new 1-cycles and 41 characters, so the total is 4 + 8C + L + 41(720 − C)/5 = 5908 − (C − 5L)/5. PermutationChains.c uses the same target (5907 − (score/5 − 1)).
- Egan's 5906 kernels score 10 (for example `666466646646664666`).
- Teodorescu's kernel scores 15. We computed this: it is 75 symbols long and covers 390 1-cycles. That gives 5905.

So with this construction a 5904 needs a kernel of score 20 (or 25 for 5903) that PermutationChains can complete. We are assuming this score-to-length relation holds for every kernel. PermutationChains printed "has score of 20" for our kernels and reported target sizes that fit it, but no score-20 kernel was completed, so the relation was never tested end to end at 5904.

## What was run

Hardware: 2 cores of a shared laptop. By the author's account the search began at 21:22 IST on 2026-11-17 with a short generator probe whose log was not kept, and ended at 23:20 IST, 118 minutes, within the 120-minute budget. The retained logs directly evidence 115 min 42 s of search, from the start of the LKH log (21:24:18 IST) to the last kernel log entry (23:20:00 IST).

How each process ended: v3 and v4 printed terminal `end` lines; v1 and v2 have no terminal status in the retained logs; the LKH line was stopped by hand, by the author's account, and its log has no `end` line. No process exit codes were recorded.

### Line 1: LKH-3 large-neighbourhood search on the permutation path (`lns_lkh.py`)

- Each iteration picks a random weight-≥3 step. It cuts a segment of K = 200 to 1200 permutations around that step (shorter at the path ends; the logged range is 30 to 1200).
- Both ends of the segment are kept fixed. The segment is re-solved as an ATSP path: the two ends are merged into one node, so a tour equals a path, and the edge weight is 7 − (longest overlap).
- LKH-3 settings: the cerebis/LKH3 GitHub mirror, because LKH's own download site was unreachable from here. RUNS = 1, MAX_TRIALS = K, MAX_CANDIDATES = 8, MOVE_TYPE = 5, TIME_LIMIT = 60 s. The initial tour is the current order, and the seed comes from an RNG seeded with 20261117.
- An equal-or-better segment is accepted. The script writes any strictly shorter word to a JSON file; it does not call the repo checker itself, so such a word would have needed a separate `bun frontier diagnose` run. No shorter word was written.
- It ran from 21:24 IST for 2,427 logged seconds (about 40 min, 847 segments) and was then stopped on purpose, by the author's account, so its core could run a second kernel search.
- **Result (measured):** 0 strict improvements in 847 segments. The count of weight-≥3 steps stayed at 69 throughout.

### Line 2: score-20 kernel search plus PermutationChains (`kernel_driver.py`)

- New kernels come from `kernelwalk`, a modified KernelFinder described in "Kernel generator (not included)" below. Its source is not part of this attempt, so `kernel_driver.py` cannot be rerun from this directory alone.
- From scratch, this random search found almost no high-score kernels: in a probe whose log was not kept, 0 kernels of score ≥10 in 3·10⁶ nodes. So every batch instead takes a base kernel from a pool, keeps its prefix up to a random cut point, and re-completes the tail. The target score is 20 or 25, or 15 in a 15–30% share of batches. Max length is the base length + 5 to 35.
- Each new kernel goes to `PermutationChains 7 nsk<kernel>` with no symmetry options, as in the 5905 find, with a 60 s timeout. The driver classifies each call by keywords in its output: "unviable" counts as unviable, "Searching for solutions of size …" counts as viable (reached the tree search). It does not record return codes.
- The pool starts as {Teodorescu's kernel, its reversal}. Every viable kernel joins the pool in both orientations, so kernels were generated by repeated head/tail completion from an adaptive pool initially seeded by Teodorescu's kernel and its reversal.
- Four driver runs, in order:
  - v1: seed 20261117, no pool, 10 min.
  - v2: seed 20261118, with the pool, 9 min.
  - v3: seed 20261119, pool seeded from v1 and v2, 21:45 to 23:20.
  - v4: seed 777, pool seeded from v1 to v3, on the core freed from LKH, 22:04 to 23:20.

**Results (from the driver's counters and logs):**

| run | kernels tested | unviable | viable (reached tree search) | timeouts | solutions |
|---|---|---|---|---|---|
| v1 | 3,095 | 2,740 | 0 | 0 | 0 |
| v2 | 29,693 | 21,830 | 273 | 0 | 1 kernel (Teodorescu's own, 4 words, all 5905) |
| v3 | 201,427 | 154,266 | 2,174 | 3 | 0 |
| v4 | 167,899 | 128,804 | 1,890 | 2 | 0 |

- 402,114 kernel tests in total, with some overlap between the parallel runs.
- 399,019 per-kernel rows are preserved (v2 to v4; v1 kept no per-kernel log). They hold 379,285 distinct kernels: 242,492 of score 15, 135,932 of score 20, 861 of score 25. Lengths range from 34 to 117 symbols, median 81.
- The pool drifted far from its seed. Of the 379,285 distinct kernels, 322,883 share no first or last character with Teodorescu's kernel in either orientation, and only 15,253 share a literal end of 15 or more characters with it.
- 89,782 of the 399,019 rows (about 22.5%) ended in neither of the two classifications: 84,272 exits on "attempting to add an excluded 2-cycle", 5,100 "Abandoning exclusion" exits, 405 "Unable to add 2-cycle" exits, and 5 timeouts whose output was truncated. These are early exits or unfinished calls, not completions, but the driver did not count them as unviable.
- Five calls hit the 60 s timeout, on four distinct kernels, all of score 15. None of them was score 20.
- Distinct viable kernels: 4,162, of which 3,856 score 15, 306 score 20 and none score 25.
- Every viable score-20 kernel ended its PermutationChains search at once, with no solution reported.
- The only solutions found were Teodorescu's 4 words of length 5905, re-found when his own full kernel came up as a tail completion. `diagnose`: "ties the best known value".
- No completion was reported for the other 3,855 classified score-15 kernels in those invocations.

## Kernel generator (not included)

`kernelwalk` is a modification of Greg Egan's KernelFinder, from the superpermutators/superperm repository at commit 1922a3486a1a06040230b3e69f365a46e79ab2f2 (files `KernelFinder/KernelFinder.c` and `PermutationChains/PermutationChains.c`; the repository is AGPL-3.0). The modified source is kept by the submitter and is not published here, because it derives from AGPL-3.0 code and this attempt is published under CC BY 4.0. PermutationChains itself was compiled unmodified with `cc -O3`.

What the modification does, in words:
- It keeps KernelFinder's own bookkeeping for building a kernel one symbol at a time (adding and removing a digit or a dash, tracking visited permutations and the running score) and its permutation setup, and replaces the program's exhaustive search and its command-line entry point.
- The replacement search is a randomised depth-first search. At each node the candidate moves are the digits 2 to 6 and, after a digit, a dash. They are tried in a random order drawn as a weighted race: digit 6 has weight 8, digit 5 weight 3, the dash weight 1 and lower digits 0.5, so long runs are tried first most of the time.
- The search prunes a branch when the kernel reaches the maximum length, or when the remaining length cannot lift the score to the target. It prints every kernel it reaches that is longer than the fixed prefix, ends in a digit, has a score of at least the target, and has a score divisible by 5.
- Each run takes a target score, a maximum length, a node budget, a number of restarts, a random seed and an optional fixed prefix. A restart begins again from the prefix after the node budget is spent. The driver used node budgets of 2·10⁴, 2·10⁵ or 2·10⁶, 5 restarts per batch, and the prefix cut from a pool kernel (random cut point of at least 15 symbols, moved back off any trailing dash).
- The driver gives each generator call 120 s and passes at most 300 new kernels per batch on to PermutationChains.

## Self-tests (measured, `selftest.py`, `selftest_n5*.py`)

1. **Validity check.** The validity check inside the LNS (all 5040 permutation windows distinct) accepts the 5905 baseline. It rejects a copy with character 3000 changed, and a copy with character 3000 deleted. `bun frontier diagnose` also rejects both copies, with 6 missing permutations each.
2. **Path round trip.** Rebuilding the word from its permutation path gives back the baseline exactly.
3. **n = 7 segment repair.** In the window [2000, 2300] of the baseline path, a 40-permutation stretch was reversed, which raised the window's cost from 351 to 548. The LKH segment re-solve brought it back to 351. The rebuilt 5905 word is valid.
4. **n = 5 known optimum.** We started from the padded lexicographic path (597 characters, ends 12345 and 54321 fixed).
   - With the settings used in the n = 7 run (RUNS = 1, MAX_CANDIDATES = 8), 13 seeds reached 154 or 155 and **never the known minimum 153**.
   - The known 153 word has those same two ends, so 153 is reachable under this encoding.
   - With stronger settings, every probe reached 153 (repo verifier: valid, value 153): MAX_CANDIDATES 20, MAX_TRIALS 5000, RUNS 5, with or without an initial tour; and MOVE_TYPE 3, MAX_CANDIDATES 10, RUNS 10.
   - **So the LKH line as run on n = 7 was under-powered**, and its 847 null segments are weak evidence.

## Independent audit

A second model (GPT-6.1 Sol) audited this attempt before it was offered for submission. It re-validated the baseline with the repo verifier; drove the unchanged `kernel_driver.py` with Teodorescu's kernel injected in place of the generator, to confirm that the driver can report and convert a completion; re-ran all 306 score-20 kernels (all reached the tree search and reported no solution, at most 0.021 s each) and a stratified sample of 356 other logged kernels; re-ran the LKH line with stronger settings; and recounted the logs. It found nine statements in an earlier draft overstated and the length formula off by one, and the text above was corrected accordingly.

The audit could not reproduce a fresh 5906 completion through this pipeline: all seven published fruitful score-10 kernels hit the driver's 60 s limit without a solution, although their published 5906 words are valid. The same pipeline does reproduce Teodorescu's 5905 completions and the n = 5 completions. So "no completion reported" here means no completion within this pipeline's limits, which are known to miss at least the 5906 cases.

The audit is an opinion backed by reruns, not a check by the repo verifier.

## What the logs measure and what we inferred

- **Measured:** the logs measure classifications, reported solutions, elapsed counters and heuristic outcomes: the counts, timeouts and null results above, and the n = 5 behaviour in the self-tests. They do not certify that no completion exists for any kernel, and they do not record process exit status. Of the 402,114 kernel tests, 399,019 left a per-kernel row, and 89,782 of those rows (about 22.5%) fell outside both classifications. Five score-15 calls timed out (four distinct kernels), none of them score 20. All 306 score-20 kernels were re-run in the audit and reported no solution.
- **Inferred, not shown:**
  - That score-20 kernels are rarely viable. 306 viable out of about 136,000 score-20 kernels tested is a property of our generator and its adaptive pool, not of all kernels.
  - That PermutationChains's search for a viable kernel is exhaustive within its own class of solutions (2-cycle trees anchored on the kernel). This is from reading its readme and seeing it finish in about 0.01 s. We did not audit its code.
  - That length = 5908 − score/5 for these kernels. It is derived above and matches PermutationChains.c, but was never tested end to end at 5904.

**Not shown:** that no 5904 exists, that no score-20 kernel has a completion, or anything about strings outside the kernel-plus-trees and segment-re-solve neighbourhoods.

## Weak settings, not worth repeating as run

- LKH segment re-solves with RUNS = 1 and MAX_CANDIDATES = 8. These settings missed 153 on the 13 tested fixed-end n = 5 seeds.

## Follow-ups and untried

First, what the audit established:
- Re-run the LKH segment search with the n = 5-tested settings. The audit ran 36 segments with RUNS 5, MAX_CANDIDATES 20 (MAX_TRIALS 5000, MOVE_TYPE 5) for about 21 minutes, with no improvement; a longer run is untried. Diagnose every shorter word as soon as it is written.
- Give the four timed-out score-15 kernels longer runs.
- Seed the kernel pool from all seven published 5906 kernels.
- Bridge a changed middle between two fixed kernel ends. This needs a kernel search that must hit a target state.
- Record the return code, the timeout flag and the full output for each kernel call, instead of classifying by keyword matching.

Also untried:
- Score-20 kernels generated independently of this pool, for example from KernelFinder run exhaustively at higher lengths.
- Running PermutationChains with `coverFirst`. The audit's 168 option probes on sampled kernels found no solution; anchor options narrow rather than widen the search class.
- A full 5040-node ATSP from the baseline tour, and Teodorescu's second distinct word (sol2) as an LNS start.
- Kernels that admit repeated permutations or the different weight-3 transitions discussed in the 5905 thread.

## Files

These files were written for this attempt. A text comparison of each against the superpermutators/superperm repository at the commit named above and against the LKH-3 source tree used here found no copied text beyond generic idioms (a `__main__` guard, a two-line `if i == j: return 0`) and the TSPLIB keywords that LKH's input format requires.
- `analyze.py`: path and weight analysis.
- `lns_lkh.py`: the LKH segment LNS.
- `kernel_driver.py`: the kernel line driver. It calls the `kernelwalk` and `PermutationChains` binaries, neither of which is included.
- `selftest.py`, `selftest_n5.py`, `selftest_n5_params.py`, `verify_n5.ts`: the self-tests.

Greg Egan's KernelFinder.c and PermutationChains.c (github.com/superpermutators/superperm, commit 1922a34) are AGPL-3.0 and are not included here, and neither is the modified generator derived from KernelFinder.c (see "Kernel generator (not included)").
