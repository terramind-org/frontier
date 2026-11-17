# Capped LKH (no full-path run completed) and large windows, scheduled 2 h, no 5904; kernel completion controls timed out

The shortest valid word retained is the published 5905-character input. This writeup is not machine-checked.

## Measured

### Reference objects and controls

On 2026-11-17 UTC, the [record thread](https://groups.google.com/g/superpermutators/c/D5sKkV2jBuc) still reported 5905. The [record API](https://superpermutations.com/api/records) reported upper bound 5905 and lower bound 5899. No shorter n=7 construction was found in those sources. The lower-bound proof was not rerun.

The two distinct published words were reused from the preserved round-one evidence. Frontier accepted the baseline as a valid 5905 tie. Its permutation path contains all 5040 permutations exactly once, with edge weights 1:4254, 2:716, 3:64, 4:5. Reconstructing its word from overlaps reproduces it exactly. The inner checker rejects a deleted-character copy; Frontier also rejects that 5904-character copy and lists six missing permutations.

The driver recorded these calibration results before its production phase:

- Full open paths from lexicographic n=5 starts reached 153 for seeds 1, 2, 3. Settings: MOVE_TYPE 5, MAX_CANDIDATES 20, MAX_TRIALS 5000, RUNS 5, external cap 60 s.
- The n=6 lexicographic seed-1 control reached 878, missing the benchmark target 872, with candidates 20, trials 20000, runs 10 and cap 220 s. A known 872 path damaged by five scattered swaps reached 873 at candidates 30 and cap 60 s. That control also failed.
- A known 872 path damaged by one adjacent swap, initially length 878, returned to 872 for each of seeds 1, 2, 3 at candidates 30, trials 20000, runs 10 and cap 60 s.
- Fixed-end n=5 lexicographic controls reached 153 for seeds 1, 2, 3 at candidates 30, trials 20000, runs 10 and cap 20 s.
- A 1000-permutation n=7 segment, with an adjacent swap in its initial order, returned from segment length 1183 to its original 1176. The reconstructed full word is a Frontier-accepted 5905 tie. Its seed was 71 and cap 60 s.

Later Frontier rechecks accepted all nine retained n=5/n=6 benchmark words at 153 or 872, and the reconstructed n=7 control at 5905. These controls demonstrate the stated repairs. The requested broader all-seed n=6 calibration was not achieved.

### LKH calls

The production settings were MOVE_TYPE 5, MAX_CANDIDATES 30, MAX_TRIALS 20000 and RUNS 10. The logs record 10 completed runs in 80 calls. Nine finished in 1000-permutation windows and one in a 1500-permutation window. No call on a window of 2000 permutations or more, and none of the four full-path calls, completed its first run.

The auditor read 93 to 106 CPU s of preprocessing per full-path call in the archived logs. In a full-path rerun, 116 trials took 59.8 CPU s, with a median of 0.41 CPU s per trial. Using about 0.45 CPU s per trial, the auditor estimated at most about 1000 trials of run 1 per original full-path call at full CPU share. One full run of 20000 trials would take about 2.5 CPU hours plus preprocessing at that rate.

Wall-clock caps applied to solver subprocesses on a machine shared with other searches. The author's resource log sampled the two LKH processes at 63% and 26% CPU. During the audit reruns, the machine's load average ranged from 55 to 77 on 14 cores. LKH's own clock counts user CPU time, so wall-clock-to-trial ratios are unreliable. Input generation and diagnosis also consumed the overall budget. Every invocation reached its external wall cap, returned code -15, and has timeout=true in the per-call log. No optimality certificate was obtained.

Four full ATSP calls used all 5040 permutations plus a zero-cost dummy node for an open path, twice from each published word, with a 600 s cap per call. All four returned their starting word. The directed edge cost is 7 minus the longest suffix/prefix overlap. Segment calls merge the two fixed ends into one node, keeping their outgoing/incoming costs separate.

There were 76 segment calls, each capped at 120 s or the remaining budget. Their sizes were 1000 (12 calls), 1500 (18), 2000 (16), 2500 (21), and 3000 (9). A randomly selected weight-3 or weight-4 edge lay within each selected window. The initial RNG seeds were 20261118 and 20261119. Every solver seed and window is in the logs.

After the failed kernel controls freed a core, a second LKH worker began with the two published starts in reversed order. After repeated unchanged returns, it switched at a completed-call boundary to initial-order perturbations, with RNG seed 20261120. This phase made 29 calls: eight unchanged-order references, seven adjacent-swap starts, seven block-swap starts, and seven starts with a shuffled 100-permutation region. Both window endpoints stayed fixed.

The auditor found that the second worker's scratch copies of `baseline.json` and `sol2.json` were swapped relative to the primary worker's copies. Use that swapped pair to interpret `start_word` in `second/*`. The auditor used the second worker's files for the exact replays and confirmed the logged trajectories and returns.

Across both workers there were 23 distinct full initial words, including the two published inputs. The 21 disturbed starts reached lengths up to 6444. Twenty returned tours that reconstruct the original published word; one timed out without an output tour.

In total, 80 LKH invocations returned 79 tours. Every returned tour was converted to a full word and immediately passed to `bun frontier diagnose`. All were valid 5905 ties. The separate overlap implementation in `replay.py` replayed all 79 archived tours and checked their node sets, endpoints, word hashes, lengths, acceptance decisions and heavy-edge counts. There are only two distinct returned words. Returned permutation orders have distance zero from their respective published starts. The best tour still has 69 edges of weight at least three, versus 69 at the start.

The driver counts distinct returned words. Distinct intermediate tours inside LKH remain unmeasured. The repaired starts reached the existing record.

### Kernel controls and the dropped stage

PermutationChains reproduced six n=5 words of length 153 and the published score-15 kernel's four words of length 5905. The n=7 baseline call completed with return code 0 in 0.790 s; all four words passed Frontier diagnosis.

Three published score-10 kernels were then tested for fresh 5906 completions:

- `666466646646664666`: symmPairs fullSymm, cap 900 s.
- `666646664466646666`: symmPairs fullSymm branchMostFree, cap 300 s.
- `66466466466644666466466466`: the same options, cap 217.801 s, limited by the preflight deadline.

All three timed out, with return code -15, timeout=true, and no output word. Their combined subprocess time was 1417.884 s. Frontier independently accepted one published 5906 word for each of these kernels. A fresh completion through this pipeline was not reproduced within the caps.

The auditor found no search-entry message in the three stdout logs. Output was block-buffered and one log ends mid-word, so whether any of the 5906 control calls reached the search phase is unknown.

The complete n=7 completion-call breakdown is: score 10, three timeouts; score 15, one completed call yielding four baseline ties; score 20, zero calls. Every call has a classification. These calls tested reference kernels only.

A modified KernelFinder passed a separate bridge-generation control. With both ends fixed, no guided move ordering, seed 73 and a nine-symbol middle removed from a known score-20 kernel, it reconstructed that kernel in a 2870-node search and emitted two kernels. This control checks the target-state and suffix-reservation bookkeeping. A score-20 completion remains unobserved.

At 19:31:29 UTC the 5906 completion control had failed. The binding preflight rule required fixing or dropping a stage that failed calibration. The completion stage was dropped. No score-20 bridged kernels were tested for completion, the seven fruitful seeds were not used for a new population search, and the four historical score-15 timeouts did not receive the planned long reruns. The unused kernel-search branch in `kernel_runs.py` is not evidence of execution.

### Timing, exits and retained evidence

The scheduled window was 2026-11-17 19:06:31.155 UTC to 21:06:31.155 UTC, including failed launches and calibration. The first numerical calibration began at 19:06:50.750 UTC. Production LKH calls ran from 19:23:10.583 to 21:06:28.455 UTC. Both final search drivers exited 0 before the deadline. The old second driver was deliberately stopped with signal 15 at 20:04:15.541 UTC, after iteration 7 and with zero solver children, before the perturbed phase began.

The deadline helper found no solver still running at 21:06:31.388 UTC. The archive helper exited 0 at 21:06:36.169 UTC. There were at most two solver processes at once. A late resource snapshot recorded two solver RSS values of 13856 and 6608 KiB and 302156 KiB of scratch data. These are sampled values. Peak usage remains unmeasured.

The calibration jobs ended with status 2 for the failed broad n=6 controls and status 0 for the adjacent-swap controls. The kernel preflight ended with status 2 after its failed controls. The initial recorded launcher failed with status 1 because its interpreter lacked NumPy; the working interpreter was Python 3.11.8 with NumPy 2.2.6.

Evidence is preserved in worktree `equal-nectar`, under `.terramind/scratch/superperm7-r2/`: `budget.json`, `provenance.json`, calibration JSONL files, `kernel.jsonl`, both LKH JSONL logs, `archive/`, `replay-final.log`, and `report-stats.json`. All returned tours and words are archived. One no-tour timeout, second-worker iteration 17, retained its structured status but lost stdout before the collector was fixed. Later no-tour calls retain their traces too. The archive restart and phase switch have separate records.

## Inferred and not established

These runs show bounded heuristic outcomes and successful repairs of several deliberately weakened starts. They establish no lower bound and exclude no 5904-character word. They do not establish local optimality under all rearrangements, or absence of a completion for any kernel. The broader n=6 failures limit claims about calibration from arbitrary starts.

The disturbed-start controls show that LK repairs block-structured damage back to the published word. From fully random window interiors, the auditor's reruns ended 1 to 9 cost units above the corresponding record segments. The auditor's three lexicographic n=6 controls reached lengths 879, 880 and 880, and the author's reached 878. Across the four from-scratch runs, zero reached the optimum of 872. The original n=7 LKH calls tested local repair around the published words.

The record-seeded LKH line continued after narrower positive controls passed. That departs from the requested broad n=6 calibration. The 5906 completion control produced no fresh completion before the 25-minute preflight limit.

## Independent audit

The auditor independently encoded the full-path and fixed-end problems, replayed two disturbed starts trial for trial, and ran a full-path timing control, random-interior windows and n=5 and n=6 calibrations. The audit confirmed that both published words passed Frontier diagnosis, a deleted-character copy failed, and all 79 archived returns reproduced one of the two published words. Their two hashes account for every returned word. The title, claim, run counts and timing language were corrected using those reruns and the archived logs. The audit is an opinion backed by reruns. The writeup is not machine-checked.

## Follow-ups

1. **Method.** Require LKH to reach 872 from scratch at n=6 on all four seeds before spending more time at n=7. Test population recombination and candidate-set settings during calibration.
2. **Method.** Save the ascent and reuse it through `PI_FILE` and `CANDIDATE_FILE`. Set a CPU-time limit and use `RUNS = 1` with a different seed per process. Keep `Run k:` lines in the logs to count completed runs.
3. **Method.** Use random-interior windows of 600 to 1000 permutations with several seeds per window. The record-seeded windows tested here only returned the published word.
4. **Method.** Slide exact windows of 100 to 300 permutations with fixed ends over the 69 edges of weight at least three in each published word. Use ATSP branch-and-cut or a CP-SAT circuit model to obtain a certificate for each window finished to optimality.
5. **Method.** Time the documented 5906 kernel `666466646646664666` once with `symmPairs fullSymm`, unbuffered output and a cap of up to four hours on one core. Log entry into the search phase and each completion before sizing a kernel population search. The four historical score-15 reruns and score-20 bridge completion tests remain open.

## Sources, reproduction and licensing

The LKH source is [cerebis/LKH3](https://github.com/cerebis/LKH3), commit `9a51de3161f2746e969f7a2e33220f637da64e54`, built with its makefile. KernelFinder and PermutationChains are from [superpermutators/superperm](https://github.com/superpermutators/superperm), commit `1922a3486a1a06040230b3e69f365a46e79ab2f2`, compiled with `cc -O3`. The prior search and its corrections are in `../20261117-terramind-com-6e8591/`.

The supplied Python and TypeScript files are the drivers, controls, replay and supervision code. Run them from a scratch copy. Attempt directories are immutable. They expect the two reference JSON words, downloaded source trees/binaries, and a `budget.json` carrying the UTC start, its Unix time as `start_epoch`, and `deadline = start_epoch + 7200`. The kernel-search fixtures stayed in scratch because that branch was not run. The timing helpers use macOS kqueue. With the retained evidence, `python3 -I replay.py <scratch>` reconstructs the returned tours, and `report_stats.py` aggregates the logs. LKH runs as an external binary. Third-party programs and reference objects are not bundled.

KernelFinder and PermutationChains are AGPL-3.0. Their modified source and the bridge builder are excluded from this CC BY 4.0 attempt. In scratch, KernelFinder's ordinary bookkeeping was retained while its search was replaced with bounded randomized DFS: reserve the fixed suffix's visited permutations, require the original suffix-entry state, and search between a fixed prefix and suffix with a score bound. The PermutationChains modification only records an exit code, source line and search-entry stage to a sidecar; its search decisions are unchanged. `branchMostFree` is an upstream option. These descriptions and the upstream commit identify the modifications without publishing derived code here.
