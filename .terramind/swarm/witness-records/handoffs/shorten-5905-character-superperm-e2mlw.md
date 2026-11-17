# Handoff: superperm7 (witness.superpermutation-7)

## Done
- **Attempt directory:** `attempts/witness.superpermutation-7/20261117-terramind-com-6e8591/`
  - Kind: writeup.
  - Title: "Score-20 kernel search (Teodorescu-kernel tails + PermutationChains) and LKH segment re-solves, 2 h, no 5904 found".
  - Declarations are left false. Nothing was submitted, and no fork or PR to main was made.
- **Verbatim output of `bun frontier check attempts/witness.superpermutation-7/20261117-terramind-com-6e8591`:**
  ```
  $ bun src/cli.ts check "attempts/witness.superpermutation-7/20261117-terramind-com-6e8591"
  note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
  unchecked: Writeups are not machine-checked.
  ```
- **`bun frontier validate <dir>`:** its only complaint is "declarations: not confirmed" (exit 1, expected).
- **`bun run check`:** tsc passed, then 426 tests passed and 0 failed. The validate step then failed only on the same declarations line, which is expected (design decision 6).
- **Result:**
  - The record is 5905. The best value reached is 5905: the baseline, which is Teodorescu's word, re-found by the pipeline. The verifier says it **ties**. No string of 5904 or less was found, so nothing beats the record.
  - Search wall clock was 21:22 to 23:20 IST (118 min of the 120-min budget).
  - Exit status: both kernel drivers ended on their own time limit, printing `end {...}` with exit 0. I stopped the LKH LNS at 22:05 on purpose (see Deviations). `ps` showed no search process left at 23:20.
- **Record status (re-read 2026-11-17):** no shorter n = 7 string has been posted. The group thread and thread list show none, and superpermutations.com/api/records gives upper bound 5905, lower bound 5899.
- **Kernel line totals:** about 402k kernel tests and 4,162 distinct viable kernels (3,856 of score 15, 306 of score 20). There were 0 completions apart from Teodorescu's own kernel, which gave his 4 words of 5905.
- **LKH line totals:** 847 segment re-solves, 0 improvements. The count of weight-≥3 edges stayed at 69, the same as the baseline (69 = 64 × w3 + 5 × w4).

### Evidence (for the audit)
- **Scratch directory, kept:** `/Users/agrim/.terramind/worktrees/frontier/definite-haven/.terramind/scratch/superperm7/`
  - Baseline: `baseline.json` (sol1), `sol1..4.json`. Raw downloads are in `dl/` (thread attachments), `dl2/` (almanac `records.json`, `llms.txt`), `dl3/lkh` (cerebis/LKH3 clone) and `dl4/sp` (superpermutators/superperm @ 1922a34).
  - Logs: `search_lkh.out`, `search_kernels_v1.out`, `search_kernels_v2.out`, `search_kernels.out` (v3) and `search_kernels2.out` (v4). Per-kernel outcome logs are `runs/kernels/kernels.log` and `runs/kernels2/kernels.log`.
  - Self-test logs: `selftest.out` and `selftest_n5.out`. Their artefacts are in `runs/selftest/`.
  - Source: `src/`. The full `kernelwalk.c` that was compiled is there too, but it contains AGPL code, so it is not in the attempt.
- **Commands** (repo root unless stated; `S=.terramind/scratch/superperm7`):
  - `bun frontier diagnose $S/baseline.json --problem witness.superpermutation-7` gives "valid: yes, ties". The same holds for `sol2.json`.
  - Builds, run in `$S`:
    - `cc -O3 -o bin/PermutationChains dl4/sp/PermutationChains/PermutationChains.c`
    - `cc -O3 -o bin/kernelwalk src/kernelwalk.c -lm`
    - `make` in `build-lkh` (a copy of `dl3/lkh`)
  - LKH line, in `$S`: `nohup python3 -I src/lns_lkh.py baseline.json build-lkh/LKH runs/lkh 6300 20261117 > search_lkh.out` (PID 74416, started 21:24:18, killed 22:04:48).
  - Kernel line, in `$S`: `python3 -I src/kernel_driver.py bin runs/kernels <secs> <seed> <repo> [targets] [seed-file]`, run four times:
    - v1: seed 20261117, 21:26 to 21:36.
    - v2: seed 20261118, 21:36 to 21:45.
    - v3: seed 20261119, targets 20,20,20,25, pool from `runs/kernels/seed_v2.txt`, 21:45 to 23:20.
    - v4: dir `runs/kernels2`, seed 777, targets 20,20,25, pool from `seed_v3.txt`, 22:04 to 23:20.
  - Self-tests, in `$S`:
    - `python3 -I src/selftest.py baseline.json build-lkh/LKH runs/selftest`
    - `python3 -I src/selftest_n5.py build-lkh/LKH runs/selftest`
    - `python3 -I src/selftest_n5_params.py build-lkh/LKH runs/selftest`
    - `bun <attempt>/verify_n5.ts <json>`, which runs the repo verifier with n = 5.
- **Self-test results, recorded:**
  - The inner validity check ACCEPTS the 5905 baseline. It REJECTS one copy with character 3000 changed and one with it deleted, and `bun frontier diagnose` also rejects both (6 missing permutations each).
  - Path to word reproduces the baseline exactly.
  - n = 7: a corrupted window (cost 351 raised to 548) was re-solved by LKH back to 351, and the rebuilt word is valid at 5905.
  - n = 5, from the padded lexicographic path (597 characters, ends fixed):
    - With the settings used in the search (RUNS 1, MAX_CANDIDATES 8), 13 seeds reached only 154 or 155, **not the known 153**.
    - With RUNS 5 and MAX_CANDIDATES 20, or with MOVE_TYPE 3, MAX_CANDIDATES 10 and RUNS 10, all three probes reached 153 (repo verifier: valid, value 153).
  - So the LKH line was under-powered as run. The writeup says so.
  - Kernel-line recovery (`sh src/selftest_recover.sh`, log `selftest_recover.out`):
    - Teodorescu's score-15 kernel, cut after c symbols, is regenerated exactly by kernelwalk for c = 72, 70, 65, 60, 55 and 50, and not for c = 45 or 40 (5·10⁷ nodes, seed 1).
    - PermutationChains turns it into 4 words byte-identical to the posted sol1 to sol4 (`selftest_score15_compare.out`), rated valid, 5905, ties.
    - A fresh 60 s target-15 driver run (`selftest_score15.out`, 61 viable, 0 solutions) did not hit it, so the in-search rediscovery was a random hit.
    - This is a recovery test. It does not show the pipeline can find a better-than-start answer.
- **All candidate files** (`runs/*/cand_*.json`) are 5905 copies of the posted words, and `diagnose` says "ties" for each. Nothing shorter exists on disk.
- **Assumptions and inferences** are listed separately in writeup.md ("What we measured and what we inferred").

## Deviations
- **LKH line stopped after about 40 min (847 segments, flat) instead of running the full budget.** Its core went to a second kernel driver, because the kernel/2-cycle view is where both known records came from. The self-test made afterwards shows the LKH settings were too weak (see Concerns).
- **Kernel generation re-completes heads and tails of Teodorescu's kernel** rather than following the brief's "2-cycles as nodes" wording literally. Egan's PermutationChains is the 2-cycle-tree search over a kernel. Random DFS from scratch found no kernels of score ≥10 at all.
- **Licence:** Egan's KernelFinder.c and PermutationChains.c are AGPL-3.0. Attempts are CC BY 4.0, so the attempt holds only my own code. That is `kernelwalk_search.c`, my replacement `search()` and `main()` with a marker where KernelFinder's setup block is spliced in, plus `build_kernelwalk.py`, which rebuilds `kernelwalk.c` byte-identically from the upstream file. The compiled `kernelwalk.c` stays in scratch.
- **LKH source:** the author's host (webhotel4.ruc.dk) was unreachable, so the cerebis/LKH3 GitHub mirror was used.
- **Budget start:** taken as 21:22, the first kernelwalk probe. That is earlier than the first background process (21:24:18), which keeps the count conservative.
- **The searches ran unattended for part of the budget.** My turn ended at about 22:52 with the searches running, and I resumed at about 23:05 after a usage-limit pause. The drivers kept their own 23:20 deadline and exited inside the budget, with no overrun. On resuming I waited in the foreground, and `ps` confirmed nothing was left at 23:20 and again at 23:25. The writeup records this.
- **Added after the brief, at the lead's request:** self-tests and an Evidence section. The recovery self-test (`selftest_recover.sh`) is in the attempt.

## Concerns
- **The LKH line is weak evidence.** With RUNS 1 and MAX_CANDIDATES 8, it does not reach the n = 5 optimum. Its 847 null segments at n = 7 say little.
- **"Viable" is my own classification**, read from PermutationChains' console text ("Searching for solutions" or "unviable"). About 22% of tested kernels ended with neither string, because they hit other exclusion messages. Those were counted as tested, not viable.
- **Exhaustiveness is inferred, not audited.** I treat PermutationChains as exhaustive within its own solution class (trees anchored anywhere, no `coverFirst`) for each viable kernel; it finishes in about 0.01 s. I did not audit its code.
- **Length = 5907 − score/5 is assumed.** It is confirmed at score 15, where Teodorescu's kernel gives 5905 words, but never seen at score 20, because no score-20 kernel was completed.
- **The generated kernels are narrow.** All share a long prefix or suffix with Teodorescu's kernel. This says nothing about score-20 kernels far from it.
- **The handoff file is outside `attempts/`.** As design decision 6 expects, the PR's validate step will fail on it and on the false declarations.

## Follow-ups
- Re-run the LKH segment LNS with RUNS ≥ 5 and MAX_CANDIDATES ≥ 10 (shown to reach the n = 5 optimum). Then try a full 5041-node ATSP from the 5905 tour.
- Make kernel generation replace the middle while keeping both ends fixed (a DFS that must hit a target state), and start pools from Egan's seven fruitful score-10 kernels.
- Run KernelFinder exhaustively for score ≥20 at lengths 60 to 100, non-palindromic, under time limits, and feed the results to PermutationChains, also with `coverFirst` and the anchor options.
- Use sol2, Teodorescu's second distinct word, as a second LNS start.
