## Done

Outcome: **OVERSTATED**. The recorded score-20 search is valid as a bounded failed search, but the statements quoted in check 5 need correction. This audit is an opinion backed by reruns, not a Frontier checker verdict. No shorter word was found in this audit.

Evidence paths used below:

- `A` = `attempts/witness.superpermutation-7/20261117-terramind-com-6e8591` in this worktree.
- `S` = `/Users/agrim/.terramind/worktrees/frontier/definite-haven/.terramind/scratch/superperm7` (author's preserved scratch, read only).
- `D` = `/Users/agrim/.terramind/worktrees/frontier/mechanical-haven/.terramind/scratch/audit-superperm7` (audit commands, outputs and candidates).
- `PC` = `S/dl4/sp/PermutationChains/PermutationChains.c`; `KF` = `S/dl4/sp/KernelFinder/KernelFinder.c`. Upstream checkout is clean at `1922a3486a1a06040230b3e69f365a46e79ab2f2` (`git rev-parse HEAD`, `git status --short`).

**1. Baseline and record.** Ran `bun install`, `bun frontier show witness.superpermutation-7`, and `bun frontier diagnose S/baseline.json --problem witness.superpermutation-7` and the same command on `S/sol2.json`. Both diagnoses say value 5905, valid yes, ties the best known value (`D/diagnose-baseline.log`, `D/diagnose-sol2.log`). My independent `python3 D/analyze_evidence.py` counted 5040 distinct permutation windows in each, with weights 4254 of 1, 716 of 2, 64 of 3 and 5 of 4; `7 + 4254 + 1432 + 192 + 20 = 5905`. Thus 69 edges have weight at least 3. `selftest.py` and fresh repo diagnoses reject both changed/deleted-character copies, each with six missing permutations (`D/selftest.py.log`, `D/diagnose-broken-*.log`).

The visible [5905 thread](https://groups.google.com/g/superpermutators/c/D5sKkV2jBuc) agrees on the kernel and the two reversal/relabelling pairs. The [visible group list](https://groups.google.com/g/superpermutators) showed no newer n=7 upper-bound claim. A fresh `curl -L --fail --max-time 15 -sS https://superpermutations.com/api/records` saved to `D/records-current.json` reports n=7 lower 5899, upper 5905, W-0021, agreeing with `S/dl2/records.json`. The [lower-bound post](https://groups.google.com/g/superpermutators/c/dmBTmhy0a1A) describes a Lean proof with compiler-trusted evaluations. I did not rerun that proof; 5899 remains attributed, not certified by this audit.

**2. Kernel pipeline, classifier, score and diversity.** Ran `python3 -I D/rerun.py`, `python3 -I D/positives.py` and `python3 -I D/final_kernel_checks.py`.

The unchanged `A/kernel_driver.py`, with only the generator subprocess replaced by a deterministic known-kernel fixture, accepted Teodorescu's kernel, reported one solution-bearing kernel, searched=1, timeout=0, and converted/diagnosed all four generated words as valid 5905 ties (`D/injected/driver.log:2-24`). This tests the actual classification, solution-file discovery, conversion and repo-diagnose path. `PermutationChains 5` also returned its documented six solutions, all independently checked by `bun A/verify_n5.ts D/pc5/word*.json` as valid 153 (`D/pc5/pc.log`, `D/pc5/diagnose.log`).

All seven published fruitful 5906 kernels were fed through the original driver's exact `PermutationChains 7 nsk<kernel>` invocation. All hit its 60-second timeout, without a reported solution. Separate `symmPairs fullSymm` probes also timed out at 45 seconds each (`D/positives.log`; fixtures and full outputs under `D/known1` through `D/known7`). In particular both `666466646646664666` and the original Egan kernel `666646664466646666` timed out. This does not refute their published completions. I independently validated all 83 published words in `S/dl4/sp/superpermutations/7/7_5906`, and ran repo `diagnose` on one word per kernel: seven valid 5906 words, each worse than today's record (`D/published5906/*.log`, `D/final-kernel-checks.log`). The pipeline can say yes at 5905 and n=5; a fresh 5906 completion was not reproduced within these caps.

Reran 356 stratified historical rows: 70 explicit unviable, 70 `excludeMultiContacts`, 70 excluded-partial-cycle, 70 tree-search, one known successful kernel, 70 unable-to-add-cycle, and all five truncated timeout rows. Defaults reproduced 280 nonzero early exits, 70 clean searches without a solution, one successful search, five timeouts. Ran 168 additional probes with `coverFirst`, `lastAnchor`, or `lastAnchor fixedPointAnchor`: no formerly excluded/unknown sample produced a solution (`D/selected.json`, `D/sample-reruns.jsonl`; defaults capped at 4 seconds for this sample).

The complete historical logs contain 89,782 rows outside the driver's two ordinary text classifications: 84,272 `addPartialTCtoPC(...) attempting to add an excluded 2-cycle`, 5,100 `excludeMultiContacts() Abandoning exclusion...`, 405 `Unable to add 2-cycle...`, and five truncated outputs. These are about 22.5% of the 399,019 preserved per-kernel rows. The hard exits are in `PC:2199-2200`, `2219-2220` and `4467-4468`. `coverFirst` begins only at `PC:4589`, after those initialization failures; anchor restrictions cannot broaden the default anywhere-anchor class (`PC:4498-4513`, upstream `Readme.txt` Options). The sample found no option-based rescue. These observations do not prove the initialization/pruning code correct.

Most decisively, reran **all 306 distinct historically classified score-20 kernels**: all returned exit 0, reached search, and reported no solution. Total subprocess time 2.354 seconds, maximum 0.02092 seconds (`D/all-score20.jsonl`, `D/final-kernel-checks.log`). None of the five historical timeouts was score 20; all were score 15, four distinct strings (`S/runs/kernels/kernels.log:40083,159951,163152`; `S/runs/kernels2/kernels.log:82687,146736`). This supports the narrow score-20 non-completion result despite the classifier's poor handling of errors and timeouts.

The score definition is correct: `C - 5L`, where C is the digit sum and L includes dashes (`KF:19-22`, `PC:2713`). The stated length formula is wrong by one. `PC:4551-4553` gives `5907 - (score/5 - 1) = 5908 - score/5`, also matching [Houston's original formula](https://groups.google.com/g/superpermutators/c/VRwU2OIuRhM). Independently: the kernel word has length `4 + 8C + L`; each attached full 2-cycle adds five new 1-cycles and 41 characters. There are `(720-C)/5` attachments, giving `4 + 8C + L + 41(720-C)/5 = 5908 - (C-5L)/5`. Score 10 therefore gives 5906; score 15 gives 5905; **score 20 still correctly targets 5904**. The typo did not misdirect the search.

`python3 D/analyze_evidence.py` plus the orientation-aware literal-end comparison saved in `D/diversity.json` found 379,285 distinct kernels, lengths 34-117, median 81. Of these, 322,883 share no first or last character with the original kernel in either orientation; only 15,253 share a literal end of at least 15 characters. For 377,343, more than 15 characters lie outside the longest such shared end. Thus the adaptive pool genuinely drifted beyond direct head/tail variants of the original. A fresh compiled generator probe emitted 3351 kernels, 2192 distinct, including nine score-20 emissions. A separate unseeded target-10, max-length-110, 3-million-node-budget probe emitted zero (`D/final-kernel-checks.log`). This reproduces one bounded scratch-start failure, not the undocumented parameters of the author's earlier probe.

**3. LKH correctness and stronger rerun.** Reran `selftest.py`, `selftest_n5.py` and `selftest_n5_params.py`. The 13 original-setting seeds reached only 154/155, best 154. Each of the three stronger probes reached 153; reconstructed their returned tours and checked them with the repo verifier: all valid 153 (`D/selftest*.log`, `D/verify-n5-strong.log`). The damaged n=7 segment went from 351 to 548 and back to 351; its reconstructed word was valid 5905.

`A/lns_lkh.py:13-17` implements the true minimum overlap cost, 1-7, for distinct permutations. The merged node's outgoing edges use the fixed start and incoming edges the fixed end (`:31-40`); rotating the returned tour to that node fixes both ends (`:75-77`). The original main loop checks the returned permutation multiset (`:102`), but does **not** automatically revalidate a shorter word with the repo checker (`:109-114`).

Additional one-core run: `python3 -I D/strong_lns.py S/baseline.json S/build-lkh/LKH D/strong 1200 20261117`, with RUNS=5, MAX_CANDIDATES=20, MAX_TRIALS=5000, MOVE_TYPE=5, TIME_LIMIT=60. It finished **36 segment re-solves in 1261 logged seconds**, best 5905, zero strict improvements. Every returned tour passed added fixed-end and 5040-permutation coverage assertions; heavy-edge counts remained 69 (`D/strong.log`, final line `end best 5905 iterations 36`). The time limit is checked between segment calls, so actual elapsed time can exceed 1200 seconds. This is another bounded heuristic failure, not evidence that a shorter path is absent.

**4. Runtime and counts.** `python3 D/analyze_evidence.py` recounted the following, using file birth/mtime in UTC converted to IST and elapsed batch markers:

- v1: 21:26:32.974 to 21:36:17.526 IST; 585 logged seconds; 3095 tested, 2740 unviable, zero searched. No `end` line (`S/search_kernels_v1.out:1,3819`).
- v2: 21:36:18.843 to 21:45:44.966; 566 seconds; 29693 tested, 21830 unviable, 273 searched, one solution-bearing kernel. No `end` line (`S/search_kernels_v2.out:1,1872`); four valid ties at lines 70-92.
- v3: 21:45:46.791 to 23:20:00.921; 5654 seconds; 201427 tested, 154266 unviable, 2174 searched, three timeouts; terminal `end` (`S/search_kernels.out:15278-15279`).
- v4: 22:04:48.472 to 23:20:00.551; 4512 seconds; 167899 tested, 128804 unviable, 1890 searched, two timeouts; terminal `end` (`S/search_kernels2.out:13271-13272`).
- LKH: 21:24:18.949 to 22:04:46.136; final elapsed 2427 seconds, exactly 847 logged re-solves, lengths always 5905, heavy always 69, segment sizes 30-1200. No `end` line (`S/search_lkh.out:1-848`).

Total 402,114 kernel tests. The 399,019 preserved per-kernel rows omit v1, but their union has exactly the claimed 379,285 strings, score distribution 242492/135932/861 for 15/20/25. The union of the stdout viable lists is exactly 4162: 3856 score 15, 306 score 20. Logs show zero additional solution-bearing kernels. During the pause, v3 counters rise from 163404 at 23:00:04 to 177420 at 23:10:01 and 198299 at 23:19:00 (`S/search_kernels.out:12886,13659,15033`); v4 rises from 133755 to 146735 to 164772 (`S/search_kernels2.out:10400,11435,12990`). Both reach their terminal lines. Process exit codes and a 21:22 initial probe are not preserved in these logs. Directly evidenced search coverage is 115m42s from the first LKH file to the last kernel file; 118 minutes relies on that unlogged probe.

**5. Text and disclosure.** The tie, lack of a new record, unverified-writeup status, headline counts and n=5 warning are supported. `A/attempt.yaml:27-39` lists the author, planner, LKH, PermutationChains and KernelFinder. Both declarations remain false (`:43-45`). Required corrections:

- `writeup.md:23,87`: "5907 − score/5" -> **"5908 − score/5"**. Keep the score-20 target; correct its derivation as above.
- `attempt.yaml:6`: "built by re-completing the head or tail of Teodorescu's score-15 kernel" -> **"generated by repeated head/tail completion from an adaptive pool initially seeded by Teodorescu's kernel and its reversal"**. The title's method label should likewise identify the adaptive pool.
- `writeup.md:85,93`: "score-20 kernels near Teodorescu's" and "all with Teodorescu's prefix or suffix" -> **"all descended through the adaptive pool from that initial seed; most no longer share a literal end with it"**. Remove the broad discouragement of direct-tail search based on this inaccurate description.
- `writeup.md:31`: "Every search process ended by its own time limit: the drivers printed their `end` lines" -> **"v3 and v4 printed terminal `end` lines; v1/v2 have no terminal status in the retained logs; LKH was reportedly stopped manually."** State the 21:22 start as an author's account of an unlogged probe, not measured log evidence.
- `writeup.md:38`: "Any strictly shorter word would have been written out and checked" -> **"The script writes shorter words; it requires a separate repo-diagnose invocation."** No automated checker call exists in that script.
- `writeup.md:68`: "None of the other 3,855 viable score-15 kernels had a completion either" -> **"No completion was reported for the other 3,855 classified score-15 kernels in those invocations."** Completion impossibility is an inference about upstream search correctness, not a measurement.
- `writeup.md:83`: "Measured: everything in the results and self-test sections above" -> **"The logs measure classifications, reported solutions, elapsed counters and heuristic outcomes. They do not certify nonexistence of completions or historical process exit status."** Explicitly disclose the five timeouts and 89,782 unclassified retained rows.
- `writeup.md:94`: "These do not reach the optimum even at n = 5" -> **"These settings missed 153 on the 13 tested fixed-end n=5 seeds."** That observation does not establish an inability to reach 153 on another seed.
- `writeup.md:107`: "All of these are our own code" -> **"These files include a replacement coupled to Egan's internals and text identical to upstream code; licensing needs maintainer review."** See check 6.

**6. Licence risk, reported for the maintainer.** `KF` is in an AGPL-3.0 repository (`S/dl4/sp/LICENSE:1-2`). The attempt omits the bulk upstream program, but literal matching found `A/kernelwalk_search.c:31-34` identical to `KF:531-534`:

```c
int ekl;
if (palindromic1) ekl = 2*currentKernelLength;
else if (palindromic2) ekl = 2*currentKernelLength-1;
else ekl = currentKernelLength;
```

The replacement also invokes upstream `addStep`, `removeStep`, `printKernel`, `CHECK_MEM`, permutation tables and global state (`A/kernelwalk_search.c:23,58-62,74,87-105,113`). `A/build_kernelwalk.py:15-20` explicitly extracts the upstream prefix and initialization block, then writes `head + part1 + setup + part2`. Running that builder produced a source file byte-identical to `S/src/kernelwalk.c`: SHA-256 `87fcc3c173fc7467cf12d54c41e7e6d5bfb8dbbfca96441767899393d0688b89` for both. It compiled and generated kernels in my rerun.

This is concrete evidence of a tightly coupled modification and some identical text. A maintainer should treat the replacement as a potential derivative work when reviewing the CC BY 4.0 rights declaration. Excluding the bulk upstream file does not settle that question. I make no legal determination about the small matching block or licence compatibility; rights must remain false until the submitter resolves it.

**7. Untried work and repository gate.** Source inspection of `A/kernel_driver.py:35-44` and `A/lns_lkh.py:95-101` confirms that the original search neither bridges a changed middle to two fixed kernel ends nor re-solves the entire n=7 path. It starts LKH from sol1, and the kernel pool from Teodorescu, not the seven 5906 seeds. The stronger settings were tried only during this audit. The original approach also excludes repeated permutation occurrences and does not explore nonstandard weight-3 transitions discussed in the 5905 thread. These remain specific alternatives, not discredited methods.

Ran `bun run check`: typecheck succeeded; 426 tests passed, one actionlint test skipped, zero failed; final validation exited 1 solely for false declarations in the cap-set, sorting-network and superpermutation attempts (`D/repository-check.log`). Left those declarations untouched. `bun frontier check A` returned `unchecked: Writeups are not machine-checked.` (`D/attempt-check.log`). No Lean files or checker code changed, so no Lean gate was needed.

## Deviations

The requested fresh 5906 completions could not be confirmed under the exact driver's 60-second limit; all seven tests timed out. The 45-second symmetry probes were also inconclusive. Published 5906 witnesses were validated separately. This audit therefore cannot claim every known positive completed through the search pipeline.

Known-kernel injection was necessary to test the unchanged driver's success path deterministically. Early shell-generator fixtures expired before testing Teodorescu's input; those are retained but excluded from the positive evidence. An initial shorter n=7 probe used RUNS=5/candidates=20 with the original trial count before the final timed run adopted MAX_TRIALS=5000; its separate log is `D/strong-preliminary.log` and is excluded from the final count. Self-test imports briefly created bytecode under the attempt; only that audit-generated cache was removed, and tracked attempt files remained unchanged.

PR #19 targets `swarm/witness-records`. Its GitHub Actions validation never started: `gh api repos/terramind-org/frontier/check-runs/134268233499/annotations` reports "The job was not started because recent account payments have failed or your spending limit needs to be increased." No CI code result is available; the local gate above is the available test evidence.

The repository gate cannot pass full validation with the intentionally false declarations. No attempt, problem, verdict or review was edited. Only the requested reports are committed; scratch evidence stays ignored.

## Concerns

The full correctness/exhaustiveness of upstream PermutationChains is not established by positive tests or the fast returns. Its include/exclude branches (`PC:2632-2664`) support the intended exhaustive interpretation, but this audit did not prove all pruning and state updates correct. Treat its non-completions as tool outcomes within its class.

Five historical score-15 calls timed out and four distinct timed-out kernels remain unresolved. The driver's stdout-only classifier neither records return codes nor separates all early failures (`A/kernel_driver.py:57-71`); buffered console text can hide the fact that a timed-out call reached search. The retained v1/v2 logs do not preserve exit codes or their exact historical source revisions. The copyright/licence question above is still open. No global lower bound or exclusion of 5904 follows from this audit.

## Follow-ups

Correct the quoted text before offering this attempt for submission, and resolve the rights question without changing either declaration automatically. Save complete stdout/stderr, return code, timeout flag and monotonic start/end for each future kernel call; use structured statuses instead of keyword matching.

Give the four unresolved score-15 kernels longer, recorded runs. Establish a practical known-5906 positive regression with the documented symmetry settings and an adequate cap, then compare it with the unrestricted run. Use all seven fruitful kernels as new seeds. Explore middle bridges, independent score-20 generation and kernels admitting repeated permutations or different weight-3 transitions. For LKH, retain the n=5-tested settings, try sol2 and a full-path ATSP, and diagnose every shorter word immediately. Budget these as fresh experiments; the present data cannot exclude them.
