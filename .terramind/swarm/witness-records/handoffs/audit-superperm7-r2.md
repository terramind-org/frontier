# Audit: superperm7-r2 (attempts/witness.superpermutation-7/20261117-terramind-com-4180d7)

Auditor: Claude Opus 5.5. Author: GPT-6.1 Sol. This audit is an opinion backed by reruns, not a verdict of the repo checker.
No object shorter than 5905 was found during the audit.

**Outcome: OVERSTATED.** The search is valid: the encoding is correct, my own code reproduces the author's LKH calls trial for trial, and every returned word checks out. No bug voids a negative result. But the title calls the LKH "strong", and the writeup says completed runs and trials were "unmeasured" when the logs measure them. Measured, the LKH line at n = 7 was a local repair around the published word, not a powered search. No full-path call finished even its first run, and the calibration that would show LKH can find optima from scratch fails at n = 6 (0 of 4 runs across the author's run and mine). The corrected wording is under check 5.

## Done

All reruns used the author's LKH-3.0.6 binary, copied to my scratch with the same SHA-256 (`9dbf6007…3af1`). My own independent encoding is in `.terramind/scratch/audit-superperm7-r2/enc.py`. Timings are LKH's own clock, which is **user CPU time**: `SRC/GetTime.c` uses `getrusage`. The machine load average was 55 to 77 on 14 cores during my reruns, so each wall-clock second gave less than one CPU second. The author's `resources.jsonl` sampled their LKH processes at 63% and 26% CPU.

### Standard check 1: baseline

- `bun frontier diagnose` on `baseline.json` and `sol2.json` returned `value: 5905 (best known 5905) / valid: yes / result: ties the best known value` for both.
- My own script found both words to be valid superpermutations with 5040 distinct permutations. Rebuilding each word from its permutation path reproduces it exactly. Path cost is 5898 = 5905 − 7, with edge weights {1: 4254, 2: 716, 3: 64, 4: 5}. There are **69** edges of weight ≥ 3, as the author says.
- A copy with one character deleted is rejected.
- The two published words share 4943 of 5039 edges and differ around positions 909 to 4238.

### Problem check 1: did LKH optimise at n = 7, or hand back its start?

I parsed every archived `stdout.log` (80 calls; `archive/{primary,second}/*/`, parser `parse_logs.py`). TRACE_LEVEL 1 prints `* k:` on each improving trial and `Run k:` when a run ends.

Every call used RUNS 10, MAX_TRIALS 20000, MAX_CANDIDATES 30, MOVE_TYPE 5, TIME_LIMIT = cap − 2, and INITIAL_TOUR_FILE = the start order. TIME_LIMIT is per run and counts CPU time from the start of the run, so it never ended a call: the external wall cap always did.

| Nodes (window size − 1) | Calls | Preprocessing (CPU s) | Calls that finished ≥ 1 run | Runs finished |
|---|---|---|---|---|
| 999 | 12 | 2.3 to 3.0 | 7 | 9 (32 to 62 s each) |
| 1499 | 18 | 4.9 to 7.0 | 1 | 1 (63 s) |
| 1999 | 16 | 9.8 to 16 | 0 | 0 |
| 2499 | 21 | 17.7 to 26.6 | 0 | 0 |
| 2999 | 8 (+1 with no stdout, `second/17`) | 28.6 to 32.1 | 0 | 0 |
| 5041 (full path) | 4 | **92.7 to 105.6** | **0** | **0** |

**Cost per trial near the record**, from the logged improvement times:
- 999 nodes: about 1.6 to 3 ms (20000 trials in 32 to 62 s).
- 1999 nodes: about 6.7 ms (`second/27`: trial 180 at 1.20 s).
- 2499 nodes: about 14 to 18 ms (`second/14`: trial 141 at 1.92 s; `second/19`: trial 240 at 4.29 s).
- 5041 nodes (my rerun `A_full`, TRACE_LEVEL 2, which prints every trial): **116 trials in 59.8 CPU s (median 0.41 s per trial)**. No further trial finished in the remaining wall time of the 330 s cap.

**Answer.** LKH did optimise. Trial 1 is a full 5-opt LK descent from the start. Every call ran further trials, and disturbed starts came down by up to 536 in cost.

- **Full path.** Each call spent about 95 CPU s in subgradient ascent (lower bound 5757, so a word of at least 5764: weaker than 5899). It then completed at most about 1000 trials of run 1 at 100% CPU, probably a few hundred at the measured CPU share. That is about 5% of one run, and 0.5% of the specified 10 × 20000.
- **What full-path trials look like.** In my rerun the trial local optima were path cost 5899 to 5996 (median 5941) against the start's 5898. A trial at this size lands 1 to 98 above the record and is never accepted.
- **Windows.** At ≥ 2000 nodes, calls completed thousands to about 16000 trials of run 1. At 1000 nodes they completed two runs or more.
- **Cap needed.** One full-path run of 20000 trials needs about 20000 × 0.45 ≈ **9000 CPU s (2.5 h on a dedicated core) plus about 95 s of preprocessing**. The specified 10 runs need about 25 CPU hours.

### Problem check 2: disturbed starts

**Exact replays** (`jobC_disturbed.py`, runs `authorx15` and `authorx14`): I reproduced the author's `second/15` (shuffle_100, 1499 nodes, seed 410315366) and `second/14` (block_swaps, 2499 nodes). The author's trajectories came back exactly:
- `second/15`: trial 1 at 1766, trial 7 at 1754 (the original).
- `second/14`: trial 1 at 2932, trial 141 at 2926 (the original).

Both returned the original order (distance 0). Note: the second worker's scratch has `second/baseline.json` and `second/sol2.json` **swapped** relative to the primary (`shasum` confirms). `start_word` in `second/*` therefore indexes the swapped pair. My first replay missed this and applied the same perturbations to the other published word; those runs also returned the original (`author15`: start 2290, returned 1754, equal to the original).

**Starts the original is not obviously nearest to** (120 s wall each):

| Start | Nodes | Start cost | Original cost | Returned | Same as original? |
|---|---|---|---|---|---|
| Two far-apart 2-cycle blocks swapped (window 1400 to 2900 of word 1) | 1499 | 1769 | 1754 | 1754 at trial 1 | yes |
| Order of 12 middle 2-cycle blocks reversed (distance 476) | 1499 | 1798 | 1754 | 1755 at trial 2, 1754 at trial 9251 (51 CPU s) | yes |
| Fully random interior | 999 | 6745 | 1168 | **1169** | no (distance 126) |
| Fully random interior | 1499 | 10145 | 1754 | **1763** | no (distance 560) |
| Fully random interior | 1999 | 13499 | 2339 | **2341** | no (distance 378) |

**Reading.** Starts that keep the 2-cycle blocks intact fall straight back into the published word: the block swap is undone in the very first LK descent. With no structure left, LKH ends 1 to 9 above the record segment within these caps. The author's 20 of 21 repairs therefore show that the published word is a strong attractor for LK. They do not show that LKH, as configured, would find a different and better word nearby.

### Problem check 3: calibration (my rerun `jobB_cal.py` used the n = 7 production settings: cands 30, trials 20000, runs 10)

- **n = 5, lexicographic start, 60 s wall:** 153 on seeds 1, 2 and 3, first reached at trials 13, 86 and 8 (0.1 to 0.8 CPU s). No run of 20000 trials finished within 60 s.
- **n = 6, lexicographic start, 220 s wall:** **879, 880, 880** (seeds 1 to 3). The best path costs were 873, 874 and 874 (reached at trials 1768, 1011 and 2986, after 108, 62 and 172 CPU s); the optimum is 865 (word 872). At n = 6 from scratch a trial costs about 58 ms, against about 2.5 ms near the record at n = 7. The author's only broad n = 6 run (seed 1, cands 20, 220 s) gave 878; the writeup reports it truthfully as a failure.
- **Total: 0 of 4 runs reach 872 at n = 6 from scratch.** The author's passing controls are all warm starts: one adjacent swap from an 872 path, n = 5 with fixed ends, and an n = 7 window with an adjacent swap. These show repair, not search.
- **Implication for n = 7.** The configuration cannot find the n = 6 optimum (721 nodes) in 220 s, and its full-path n = 7 calls never got past about 5% of one run. No calibrated statement about the chance of finding a 5904 is possible from this attempt.

### Problem check 4: correctness of the reduction

I wrote my own encoding (`enc.py`): cost(a, b) = 7 − (longest proper suffix/prefix overlap); for a full path, node 0 is a dummy with zero in and out costs; for a window, node 0 is a merged fixed-end node that leaves as `seg[0]` and is entered as `seg[-1]`. The author's `lkh_search.py` `solve()` encodes the same thing:
- Rows use `starts = [p[0]] + p[1:-1]`, columns use `ends = [p[-1]] + p[1:-1]`.
- The match loop sets cost k when `a[k:] == b[:n-k]`, with default cost n.
- Tour mapping back to permutations keeps the window ends fixed (asserted in the code).

Two pieces of evidence that the encodings match:
- The replays above reproduce the author's per-trial costs exactly. That needs an identical matrix and start.
- Baseline path cost is 5898 = 5905 − 7, with 69 heavy edges, in my code.

I also re-checked all 79 archived returned words (`archive/*/*/word.json`) with my own coverage check: all 79 are valid, length 5905, one of the two published hashes, with 69 heavy edges each. All 79 `diagnose.log` files contain `valid:    yes`. `second/17` has no word, as the writeup says.

One trap I hit and fixed in my own code, not the author's: swapping the in and out strings of the merged end node produces a wrong window instance. The author's code gets this right.

### Problem check 5: kernel line

The writeup says the 5906 positive control failed: three score-10 kernels, symmPairs fullSymm, caps 900, 300 and 217.8 s, all rc −15, no words. It says no score-20 kernel was completion-tested, and claims only that the bridge generator rebuilt a planted middle. This matches `kernel.jsonl` line for line, and no claim about score-20 completions is made.

Points the writeup does not make:
- **Search stage unknown.** None of the three `stdout.log` files contains "Searching for solutions". Stdout to a file is block-buffered and the last line is cut mid-word (`positive5906/stdout.log` ends "…selected orbi"). So it is not established whether PermutationChains reached its search phase or died in setup. Run it under a pty or with a flush to know.
- **No solution was lost.** PermutationChains appends each solution to `7_<len>_<options>.txt` as it finds it (source lines about 2370 to 2394), and no such file exists. One upstream quirk: the second `fopen` result is not assigned to `f` (about line 2386). It works by reuse of the freed FILE* (the baseline control did write its 4 words), but it is fragile.
- **No documented run time.** Upstream `superpermutations/7/7_5906/Readme.txt` says 1,572,390 palindromic score ≥ 10 kernels were searched with `PermutationChains 7 symmPairs fullSymm nsk<kernel>` and 7 were fruitful (`666466646646664666`: 53 solutions). It gives no run times. Egan's Superpermutations page gives none either; I checked the page. The PermutationChains Readme gives only "762 solutions in roughly half an hour" for `7 fullSymm limStab ffc`.
- **Sizing.** The cap for one 5906 completion is therefore unknown. Measure it once: run `666466646646664666` on one core with unbuffered output for up to 2 to 4 hours before sizing any kernel population search.

### Standard checks 2 and 3: can the search say yes; did it run?

- **Can it say yes?** Any returned word with `new < best` is diagnosed and saved as `best-<len>.json` (`lkh_search.py` lines 98 to 101). The gate can fire. Planted improvements at n = 7 were not tested, but repairs from 1183 → 1176 and 6745 → 1169 show it accepts better tours.
- **Did it run?** Wall times, rc −15 on all 80 calls and the timestamps match the writeup (19:23:10 to 21:06:28 UTC per `lkh.jsonl` and `second/lkh.jsonl`). There were 2 distinct returned words.

### Standard check 4: exact results

None claimed. The writeup correctly states no lower bound and no local-optimality certificate.

### Standard check 5: text against evidence (corrections)

1. **Title**, "Strong LKH full paths and large windows, scheduled 2 h, no 5904; kernel completion controls timed out", becomes: "Capped LKH (no full-path run completed) and large windows, scheduled 2 h, no 5904; kernel completion controls timed out".
2. **writeup.md, "LKH calls":** "These values specify limits; completed-run and trial totals remain unmeasured." becomes:
   > "These were limits that were not reached. The logs record 10 completed runs in 80 calls: nine in 1000-permutation windows and one in a 1500 window. No call of 2000 permutations or more, and none of the four full-path calls, completed its first run. A full-path call spent 93 to 106 CPU s in preprocessing and then, at about 0.45 CPU s per trial (auditor's rerun), completed at most about 1000 trials of run 1; one full run of 20000 trials needs about 2.5 CPU hours. Caps were wall-clock on a shared machine, while LKH's own times are CPU times."
3. **attempt.yaml claim:** after "four full ATSP calls", add "(none completed its first LKH run)".
4. **"Inferred and not established", add:**
   > "The disturbed-start controls show that LK repairs block-structured damage back to the published word. From fully random window interiors, the same settings ended 1 to 9 above the record segment cost (auditor's reruns), and from scratch they did not reach the n = 6 optimum 872 in 4 runs. So the n = 7 runs tested the neighbourhood of the published words, not the wider space."
5. **"Caps apply to solver subprocesses"** becomes "Wall-clock caps applied to solver subprocesses on a machine shared with other searches; sampled LKH CPU use was 26 to 63%".

Everything else in the writeup matches the logs, including the kernel section, the timing section and the evidence list. The writeup states it is not machine-checked and never says "solved".

### Standard check 6: disclosure, licence, privacy

- attempt.yaml lists gpt-6.1-sol (author), claude-fable-5-2 (planner), lkh-3, permutationchains, kernelfinder, numpy, python and clang. Declarations are both `false`.
- `grep -rn -E "/Users/|/home/"` on the attempt directory found nothing, and a search for personal names found nothing.
- The attempt files only call third-party binaries. No AGPL source from KernelFinder or PermutationChains is included: `grep` for licence, copyright and AGPL text found none, and the modified C stays in scratch, as the writeup says.

### Standard check 8: check and validate (verbatim)

```
$ bun src/cli.ts check "attempts/witness.superpermutation-7/20261117-terramind-com-4180d7"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
$ bun src/cli.ts validate "attempts/witness.superpermutation-7/20261117-terramind-com-4180d7"
attempts/witness.superpermutation-7/20261117-terramind-com-4180d7/attempt.yaml: declarations: not confirmed. ...
error: script "frontier" exited with code 1
```

Validate fails only on the declarations, which is expected (design decision 6).

## Deviations

- My first background launch of the disturbed-start job was killed when its shell exited, which cost about 8 minutes. I re-ran it in the foreground.
- My first two "author" replays used the wrong published word because of the swapped files in `second/`. I kept those runs as extra perturbation tests and added exact replays.
- The n = 6 calibration reruns used a 220 s wall cap, as the author did, on a heavily loaded machine (load 55 to 77). Longer caps were outside the 60-minute audit budget.
- I did not rerun PermutationChains: a 900 s+ control did not fit the budget.
- Per-trial costs at 2999 nodes were not measured, since no improving trial was logged there.
- The full-path trial rate comes from one rerun of 330 s wall, about 60 CPU s of trials.
- The design log calls this report `audit-superperm7-r2.md`, and the task names the handoff file `audit-the-strong-lkh-superpermut-7tyxp.md`. I wrote both, with the same findings.

## Concerns

- **Inflated per-trial times.** All timings, theirs and mine, come from a machine with load 55 to 77 on 14 cores. CPU-time figures are fine; wall-clock-to-trials ratios are not. The author's full-path calls probably completed only a few hundred trials each.
- **Unknown whether the kernel control was searching.** Whether the 5906 control reached its search phase is not known (buffered stdout). If PermutationChains spends most of 900 s in setup for nsk kernels, the kernel line needs a different cap than if it was deep in search.
- **The full-path stall.** In my full-path rerun no trial finished in about the last 170 s of wall time after trial 116. That is consistent with CPU starvation or with one very long LK trial; I could not tell which.
- **Hidden scratch swap.** The second worker's swapped `baseline.json`/`sol2.json` is not mentioned in the writeup. It does not change any result, since the replay used the second-worker files, but a reader replaying `second/*` with the primary files gets different instances.

## Follow-ups (for the planned 8 h, 4-core superpermutation run)

1. **Calibrate first.** Make LKH reach 872 at n = 6 from scratch on 4 of 4 seeds before spending n = 7 time:
   - Try POPULATION_SIZE 10 to 20 with RECOMBINATION GPX2 or IPT, RUNS ≥ 20, and a CPU TIME_LIMIT per run.
   - Try CANDIDATE_SET_TYPE POPMUSIC or a saved CANDIDATE_FILE/PI_FILE.
   - Each n = 6 run should take minutes. If 4 of 4 is not reached within about 30 min per seed, the full n = 7 path (7× larger, about 0.45 s per trial) is hopeless for LKH in 8 h. Then spend the run on method, not time.
2. **If LKH stays, sizing.**
   - Compute the ascent once and reuse it through PI_FILE and CANDIDATE_FILE (saves about 95 CPU s per call).
   - Use TIME_LIMIT in CPU seconds and RUNS 1 per process, with a different seed per process.
   - 8 h × 4 cores ≈ 115,000 CPU s, which fits about 12 full-path runs of 20000 trials, or about 2000 window runs at 1000 permutations (about 50 CPU s each).
   - Windows: use random-interior starts, not record-seeded ones. Record-seeded windows only repair back to the published word (check 2). Random-interior windows of 1000 still end 1 above the record, so prefer 600 to 1000 permutations with several runs each.
   - Log TRACE_LEVEL 1 `Run k:` lines so completed runs are counted.
3. **Better use of the time: exact windows.** Solve windows of 100 to 300 permutations exactly between fixed ends: ATSP branch-and-cut, OR-Tools CP-SAT circuit, or a 2-cycle-level model. Slide them over all 69 heavy edges of both published words. An exact "no saving in this window" is a certificate a later attempt can build on. A heuristic tie is not.
4. **Kernel line.** Time the documented 5906 control (`666466646646664666`, `symmPairs fullSymm`) once on one core for up to 4 h. Run it with unbuffered output, logging when the search phase is entered and when each solution appears. Size any score-20 bridged population from that number. Upstream's 1.57 M-kernel search implies most kernels fail fast, but the fruitful ones' times are not published.
5. **Time or method?** Method. Measured, the n = 7 LKH line was a local repair and is uncalibrated even at n = 6. Only an LKH configuration that passes check 1 above makes extra time worth anything.
