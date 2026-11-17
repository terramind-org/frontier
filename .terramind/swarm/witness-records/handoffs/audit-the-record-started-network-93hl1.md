# Audit: record-started sorting-network search (round 2), witness.sorting-network-size-18

Attempt audited: `attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4/` (writeup, author GPT-6.1 Sol). Auditor: Claude Opus 5.5. This audit is an opinion backed by reruns. It is not a verdict of the repository checker. Author scratch was read in worktree `novel-shelf`, `.terramind/scratch/sortnet18-r2/` (abbreviated `AS/` below), and was not modified. My scratch is `.terramind/scratch/audit-sortnet18-r2/` in worktree `comfortable-ember` (abbreviated `MS/`). No object beating the record was found.

## Done

**Outcome: OVERSTATED.** The search ran as described and every count I recounted matches the logs. Five statements need correcting (quoted below with the corrected wording). The most important: the only 77-gate networks the 36 SorterHunter runs printed are the starting inputs themselves. Read as written, "the smallest valid network visited has 77 gates" suggests the search reached 77. Two calibrations the writeup lacks: the repair heuristic cannot fix a record with **one** wrong gate at n = 18 in 4 to 5 minutes, and a planted saving in a 12-gate mid-network window needs 171 s, more than the 110-s SAT budget per query.

### Standard check 1: baseline
- `AS/baseline.json` is identical, as an ordered list, to upstream `Networks/Sorters/Sort_18_77_12.json` at SorterHunter `a18ee17` (`MS/classes.py`, comparison printed `True`).
- My own NumPy simulation of all 2^18 inputs finds 0 failures. `bun frontier diagnose MS/baseline.json --problem witness.sorting-network-size-18` printed `value: 77 (best known 77, lower is better)`, `valid: yes`, `result: ties the best known value`.

### Problem check 1: was the record really the starting point?
Recomputed from every `AS/hunt_*.cfg` and `AS/hunt_*.log` (`MS/runs.py`, output `MS/runs.out`):
- **All 36 runs started where the writeup says.** The log of each run prints `Initial network size:` 77 for the 24 runs from `baseline` (Sort_18_77_12) and `round1` (round 1's 77-gate, depth-14 network), and 78 for the 12 runs from `depth11` (Sort_18_78_11). The configs show the stated grid: symmetric and asymmetric mode; prefixes of 0, 9 and 17 gates (0, 1 and 2 ASAP layers); symmetric cores compressed to the gates with i + j <= 17 (41, 36 and 32 gates for the record, expanding to 77). `campaign.py` re-expands each serialized core and checks the result on all inputs before launch, and `hunter.py` aborts on a size mismatch. No run started anywhere else.
- **The runs were short, and CPU-starved.** Each lasted 196.0 to 197.6 s of wall time (7,095 s in total). SorterHunter's own `t=` field (process CPU time from `clock()`) reports **33 to 178 CPU seconds per run, 3,717 CPU s in total (52% of wall time)**, so the hunter lane got about half a core on a shared machine. My own reruns on this machine also got 28 to 90% of a core. Each run printed 134 to 189 iteration heartbeats. SorterHunter prints a heartbeat at every 10% increase, so the last reported iteration is a lower bound, within 10% of the true count. Those last reports sum to 4,238,175,949, matching the writeup.
- **No run printed a 77-gate network other than its own start, and no 78-gate start printed a 77.** SorterHunter prints a network only when its (size, depth) pair improves that run's Pareto front (`checkImproved`, `SorterHunter.cpp` around line 505 of the patched source). Any 76 would therefore have been printed and diagnosed by `hunter.py`, so the success gate could fire. A new 77-gate network at the start's own depth or deeper would not be printed, so the logs cannot say whether one was visited. To find out, I rebuilt clean upstream SorterHunter with a counter of accepted networks at or below the start size, canonicalised up to commuting gates (`MS/sh/`), and reran configs 01 and 03 for 170 s each (`MS/a_01.log`, `MS/a_03.log`). Run 01 (symmetric, 9-gate prefix) found 1 other class at <= 77 and run 03 (asymmetric, no prefix) found 2. The start is mirror-symmetric up to commutation, so these are genuinely different 77-gate networks. **The last accepted network of at most 77 gates came before iteration 631,480 (0.32 CPU s) in run 01 and before iteration 36,184 (0.26 CPU s) in run 03. For the rest of each run the accepted network had 78 to 86 gates (run 01) or 79 to 95 gates (run 03).** The cause is the configuration: `RestartRate=0` with `EscapeRate` of 300 to 5000 inserts a gate every 300 to 5000 iterations at about 10^4 to 10^6 iterations per second (logged rates), and nothing returns the network to the start. The printed larger networks in the author's logs (79 to 87 gates) agree with this.

Per-run table, recomputed from the author's configs and logs:

| run | start | mode | prefix gates | core given | initial size | wall s | CPU s | last iteration report | heartbeats | printed (size,depth) after start |
|---|---|---|---|---|---|---|---|---|---|---|
| 00 | baseline | sym | 0 | 41 | 77 | 197.5 | 171 | 12,120,951 | 152 | (81,11) |
| 01 | baseline | sym | 9 | 36 | 77 | 197.5 | 178 | 255,919,149 | 184 | (82,11) (81,11) (80,11) |
| 02 | baseline | sym | 17 | 32 | 77 | 197.6 | 114 | 374,691,228 | 188 | (80,11) |
| 03 | baseline | asym | 0 | 77 | 77 | 197.4 | 105 | 4,673,148 | 142 | none |
| 04 | baseline | asym | 9 | 68 | 77 | 197.4 | 110 | 119,388,169 | 176 | none |
| 05 | baseline | asym | 17 | 60 | 77 | 197.4 | 117 | 412,160,351 | 189 | (79,11) |
| 06 | round1 | sym | 0 | 41 | 77 | 197.4 | 134 | 14,666,352 | 154 | (83,13) (81,13) |
| 07 | round1 | sym | 9 | 36 | 77 | 197.4 | 159 | 255,919,149 | 184 | (81,13) (80,13) (80,12) (79,13) (78,13) (79,12) (78,12) |
| 08 | round1 | sym | 17 | 32 | 77 | 197.4 | 139 | 255,919,149 | 184 | (81,13) (79,13) (80,12) (79,12) (80,11) (78,13) (78,12) |
| 09 | round1 | asym | 0 | 77 | 77 | 197.4 | 81 | 3,191,821 | 138 | (81,13) (80,13) (79,13) (78,13) |
| 10 | round1 | asym | 9 | 68 | 77 | 197.4 | 111 | 74,130,659 | 171 | (80,13) (81,12) (79,13) (80,12) (79,12) (78,13) (78,12) |
| 11 | round1 | asym | 17 | 60 | 77 | 197.4 | 38 | 98,667,908 | 174 | (79,13) (78,13) (80,12) (79,12) (78,12) |
| 12 | depth11 | sym | 0 | 40 | 78 | 197.4 | 107 | 10,017,314 | 150 | none |
| 13 | depth11 | sym | 9 | 35 | 78 | 197.3 | 116 | 131,326,986 | 177 | none |
| 14 | depth11 | sym | 17 | 31 | 78 | 197.3 | 114 | 211,503,428 | 182 | none |
| 15 | depth11 | asym | 0 | 78 | 78 | 197.3 | 114 | 5,140,463 | 143 | none |
| 16 | depth11 | asym | 9 | 69 | 78 | 197.3 | 94 | 89,698,098 | 173 | none |
| 17 | depth11 | asym | 17 | 61 | 78 | 197.4 | 83 | 158,905,654 | 179 | none |
| 18 | baseline | sym | 0 | 41 | 77 | 197.3 | 120 | 7,526,155 | 147 | none |
| 19 | baseline | sym | 9 | 36 | 77 | 197.3 | 88 | 89,698,098 | 173 | (82,11) |
| 20 | baseline | sym | 17 | 32 | 77 | 197.3 | 92 | 174,796,220 | 180 | (80,11) |
| 21 | baseline | asym | 0 | 77 | 77 | 197.3 | 57 | 2,180,055 | 134 | none |
| 22 | baseline | asym | 9 | 68 | 77 | 197.2 | 33 | 28,580,575 | 161 | none |
| 23 | baseline | asym | 17 | 60 | 77 | 197.2 | 44 | 81,543,725 | 172 | none |
| 24 | round1 | sym | 0 | 41 | 77 | 197.0 | 93 | 9,106,649 | 149 | (87,13) (85,13) |
| 25 | round1 | sym | 9 | 36 | 77 | 196.8 | 97 | 119,388,169 | 176 | (79,13) (84,12) (83,12) (82,12) (80,12) (79,12) (78,13) (78,12) |
| 26 | round1 | sym | 17 | 32 | 77 | 196.8 | 83 | 158,905,654 | 179 | (82,13) (81,13) (80,13) (79,13) (82,12) (81,12) (80,12) (79,12) (78,12) |
| 27 | round1 | asym | 0 | 77 | 77 | 196.7 | 109 | 3,862,105 | 140 | none |
| 28 | round1 | asym | 9 | 68 | 77 | 196.7 | 100 | 81,543,725 | 172 | (81,13) (80,13) (79,13) (81,12) (80,12) (79,12) (78,13) (78,12) |
| 29 | round1 | asym | 17 | 60 | 77 | 196.6 | 112 | 232,653,771 | 183 | (80,13) (80,12) (79,13) (79,12) (78,13) (78,12) (79,11) |
| 30 | depth11 | sym | 0 | 40 | 78 | 196.6 | 68 | 5,654,510 | 144 | none |
| 31 | depth11 | sym | 9 | 35 | 78 | 196.3 | 73 | 74,130,659 | 171 | none |
| 32 | depth11 | sym | 17 | 31 | 78 | 196.3 | 114 | 211,503,428 | 182 | none |
| 33 | depth11 | asym | 0 | 78 | 78 | 196.2 | 104 | 4,673,148 | 142 | none |
| 34 | depth11 | asym | 9 | 69 | 78 | 196.1 | 86 | 89,698,098 | 173 | none |
| 35 | depth11 | asym | 17 | 61 | 78 | 196.0 | 159 | 374,691,228 | 188 | none |

### Problem check 2: diversity
`MS/classes.py` puts the 86 printed networks in Cartier-Foata normal form (canonical up to reordering of commuting disjoint gates) and takes the smaller of a network and its mirror image. Result: **86 ordered sequences, 77 distinct up to commutation, 77 up to commutation plus mirror**. All 86 sort every input. By size, the classes are 77: 2, 78: 17, 79: 19, 80: 18, 81: 11, 82: 5, 83: 2, 84: 1, 85: 1, 87: 1. **The eight 77-gate sequences are four orderings each of the two 77-gate inputs**, and one 78-gate class (four orderings) is the `depth11` input. The new networks are 16 classes of 78 gates (all from `round1` starts, at depth 12 or 13) and larger ones. The HyperLogLog estimates (about 0.69 to 0.99 of the iteration count) show that almost every candidate is a new ordered sequence. That is expected while the network drifts upward in size, and it says nothing about diversity near 77.

### Problem check 3: the repair line
- Recount: `AS/repair76.best.json` (SHA-256 `b92b9928...cb32`) has 76 gates and **48** failing inputs by my NumPy simulation. `bun frontier diagnose` printed `value: 76`, `valid: no`, and three violations: 15 inputs with wire 0 above wire 1, 18 with wire 1 above wire 2, and 15 with wire 16 above wire 17.
- **Positive control at full size: failed.** I took the 77-gate record, replaced one gate, and ran the author's unchanged `repair.run` loop (`MS/ctl18.py`, seed 32003, same moves, temperatures and 20,000-step walks):
  - gate 40 changed from (16,17) to (9,10), 120,795 failing inputs: **300 s, 193,617 evaluations, 10 walks, best 317, no sorter**;
  - gate 60 changed from (2,4) to (5,9), 1,116 failing inputs: **240 s, 82,617 evaluations, 5 walks, best 43, no sorter**.
  Together that is 276,234 evaluations, 39% of the author's 699,445. A single wrong gate is repaired by one specific move. The random walk reached 43 failures at 77 gates from a record one gate away and still did not find it. So **a failure count in the 40s says nothing about distance to a sorter**.
- The 48-failure candidate is a strict local minimum for single-gate replacement. All 11,552 one-gate replacements score at least 48, and 4 tie (`MS/nbhd.py`, 6.8 s).
- The best score improved last at evaluation 377,888 (20:56:27 UTC). The remaining 321,557 evaluations (walks 20 to 35, about 11 minutes) brought no gain (`AS/repair.log`). The objective had stalled.
- Wording: the writeup does not present 48 as closeness. It says the significance is "uncalibrated" (`writeup.md:65`). Line 3 and the claim put the 48 in the headline next to the tie; see correction 5.

### Problem check 4: SAT
- The writeup states plainly that every query is unresolved and that the calls "supply no exclusion result" (`writeup.md:15`, `:55`, `:65`). It does not count timeouts as evidence. My recount from `AS/sat_*.log` and `.exit.json` gives 47 queries: 38 ending in `timeout`, 9 with no result; exit codes 36 zeros and 11 `-15`, 2 of which also printed `timeout`. All 9 unanswered queries were killed at 120.0 s by the **per-query** wrapper (110-s internal deadline plus 10 s). None was stopped by the campaign deadline. Conflicts per query ranged from 37,771 to 647,706.
- Encoder controls with the author's unchanged `window.py` (`MS/satctl.py`, `MS/satctl.log`):
  - redundant (0,17) planted at position 74 of the record, window s = 73, w = 3, target 2: SAT in 1.0 s, 77 gates, 0 failures;
  - gate 40 duplicated, window s = 39, w = 4, target 3: SAT in 0.9 s, 77 gates, 0 failures;
  - optimal 19-gate 8-input network (`Sort_8_19_6`), all 16 four-gate windows shortened to three: 16 of 16 UNSAT, 0.007 to 0.10 s each.
- **Where the wall is** (`MS/satwall.sh`; record, order 0; sequential-counter encoding; 300-s cap; seed 4242):

| window | result | time | conflicts | decisions | propagations | restarts | vectors | vars / clauses | peak RSS |
|---|---|---|---|---|---|---|---|---|---|
| s=41, w=11 -> 10 | timeout | 302 s | 1,418,432 | 4,274,176 | 958,369,034 | 63,379 | 65 | 19,350 / 238,922 | 303 MiB |
| s=66, w=11 -> 10 (tail) | **UNSAT** | 8.0 s | 97,071 | 234,702 | 43,168,427 | 1,972 | 29 | 8,972 / 32,741 | 264 MiB |
| s=41, w=12 -> 11 | timeout | 301 s | 784,752 | 3,218,014 | 607,844,672 | 37,421 | 76 | 23,617 / 370,262 | 418 MiB |
| s=65, w=12 -> 11 (tail) | **UNSAT** | 17.9 s | 216,013 | 450,584 | 90,295,591 | 6,361 | 28 | 9,601 / 39,235 | 251 MiB |

  - Planted saving at the hard offset: the record with gate 46 duplicated (78 gates), window s = 41, w = 12, target 11: **SAT in 171 s** (805,444 conflicts, 5 refinement rounds). The result has 77 gates, 0 failures, is the same class as the record, and `diagnose` says `valid: yes`.
  - So in the middle of the network, an 11- or 12-gate window does not finish in 5 minutes, and a known saving at w = 12 takes longer than the author's 110-s budget. A real one-gate saving in the windows the author sampled could have been missed for lack of time. At the tail, w = 11 and 12 finish in 8 to 18 s. The author's grid used offsets 0 to 41 only (every window ends at or before gate 55), so it **never sampled the cheap tail region** at these widths. The two tail UNSAT results above apply only to those exact windows, with the prefix and suffix fixed, and come without proof certificates.

### Problem check 5: time or method?
See Follow-ups. In short: for SorterHunter and repair, the lever is method, not time. For SAT it is time on mid windows and coverage of tail windows.

### Standard checks 2 to 4
- Stages that can say yes: SorterHunter (padded 8-input 20 -> 19, `AS/cal_hunter8.log`; and any 76 is always printed); SAT (planted controls above, including one at w = 12). The repair loop failed its full-size control (check 3). The author's 8-input repair control passes, but it is too easy to calibrate n = 18.
- Did the search run: start, end and exit times match `AS/budget.json`, `AS/hunt_*.summary.json`, `AS/sat_*.exit.json` and `AS/repair.log`. All 36 SorterHunter children exited -15 at their scheduled end. Instrumentation (`git diff` in `AS/upstream/SorterHunter`) adds only counting and printing (a hash register, a sample set every 65,536 iterations, line buffering). It adds no RNG call and changes no acceptance or mutation rule, as stated. The binary was rebuilt at 19:32:32 UTC, before run 08 started, which matches "first 8 runs without HLL".
- Exact results: none. The author's attempt has no UNSAT result.

### Standard check 5: text against evidence, corrections
1. `writeup.md:3` "The smallest valid network visited has 77 gates and ties the published record." and `attempt.yaml` claim "The best valid size is 77, which ties the record." -> "No run produced a valid network smaller than its input. The only 77-gate networks the runs printed are the two 77-gate inputs (the published record and round 1's network), so the best valid size, 77, is the input, which ties the record."
2. `writeup.md:9` "Eight distinct printed ordered sequences have 77 gates." -> "Eight distinct printed ordered sequences have 77 gates. They are four orderings each of the two 77-gate inputs. Up to commuting gates and mirror symmetry, the 86 printed networks form 77 classes: the 3 inputs, 16 new 78-gate classes and larger networks."
3. `writeup.md:11` "each lasting 196.0 to 197.6 seconds" -> add: "of wall time. SorterHunter's own CPU clock reports 33 to 178 s per run, 3,717 CPU s in total, about half a core on a shared machine."
4. `writeup.md:36`, after "`RestartRate=0` leaves the bounded wrapper in charge of restarting from the known inputs.", add: "Each input was therefore started 12 times in total (36 runs over 3 inputs). The logs do not record the size of the accepted network after the start. In audit reruns of two of these configurations, the accepted network left 77 gates within the first 0.32 CPU seconds and stayed at 78 to 95 gates for the rest of the run, so nearly all run time was spent far above 77."
5. `writeup.md:15` "nine stop at the outer deadline without a final solver answer" -> "nine were stopped by the per-query 120-second limit (110-second internal deadline plus 10 seconds) without a final solver answer". `writeup.md:67` "The next attempt should preserve the 48-failure candidate as another repair start" -> "An audit control showed that the same repair loop cannot restore the record with one wrong gate at n = 18 within 4 to 5 minutes (best 43 and 317 failures). A 48-failure score therefore carries no evidence of closeness, and the 48-failure candidate is a local minimum under all one-gate replacements."
No "solved", "record improved" or "locally optimal" wording was found. The writeup says it is not machine-checked (`writeup.md:3`, claim).

### Standard check 6: disclosure, licence, privacy
- `attempt.yaml` lists gpt-6.1-sol (author), claude-fable-5-2 (planner), SorterHunter, CaDiCaL, python-sat, NumPy, Python, Clang and Frontier. That is every tool I saw doing real work. Declarations are both `false`. When the corrections are applied, add `claude-opus-5-5:anthropic:auditor`, following the round-1 pattern.
- Licence: the eight scripts are the author's own code. `prepare.py` embeds two one-line anchor strings from MIT-licensed SorterHunter (an upstream `printf` line and a comment) as text to patch at, and writes the instrumentation shown in `hll_control.cpp`, which is also the author's code. No upstream source or binary is in the attempt. I found nothing incompatible with CC BY 4.0.
- A grep of the attempt directory for home-directory paths and the personal names checked by the swarm rules: no match (exit 1).

### Standard check 7: see Follow-ups.

### Standard check 8: repository checker, verbatim
```
$ bun src/cli.ts check "attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
(exit 0)
$ bun src/cli.ts validate "attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4"
attempts/witness.sorting-network-size-18/20261117-terramind-com-ef57c4/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
(exit 1: only the declarations, which must stay false)
```

## Deviations
- I did not rerun all 36 SorterHunter configurations. I reran 2 (01 and 03) for 170 s each with an audit counter, on a clean upstream build. "Left 77 within 0.32 CPU s" is measured on those two only, and extended to the rest by the shared `RestartRate=0` and escape settings.
- The full-size repair controls used 39% of the author's evaluation budget, spread over two damaged networks. They show failure within 4 to 5 minutes, not failure at 30 minutes.
- SAT wall: one seed, record order 0, two offsets per width (41 for the middle, 65/66 for the tail), as briefed. Mid-offset timeouts at 300 s do not locate the wall exactly, only that it is above 5 minutes there. I kept no DRAT proofs for the two tail UNSATs.
- Disk: my scratch holds only JSON, logs and a 120 KB binary. No CNF or proof files were written.

## Concerns
- The machine was oversubscribed during the author's campaign (SorterHunter got 52% of a core) and during this audit. Wall-clock budgets on this machine overstate the compute actually spent. Later attempts should report CPU seconds.
- `MaxPositionDistance` (`writeup.md:13`) counts positional differences. One insertion shifts every later position, so values of 64 to 111 do not show distance from the record. The writeup presents it only as a count, which is fine, but nobody should read it as "left the neighbourhood".
- Small 8-input controls (SorterHunter 20 -> 19, repair in 875 evaluations) pass trivially and cannot calibrate n = 18. Any later round should run its controls at n = 18.

## Follow-ups
Is time or method the lever? Method for SorterHunter and repair; time plus coverage for SAT.
- **SorterHunter: method, not time.** In the reruns the network leaves 77 within 0.32 CPU s and drifts to 78 to 95. A longer run of the same configuration spends more time there. Use `RestartRate` so that SorterHunter returns to the record every roughly 10^5 to 10^6 iterations, or lower the escape rate (for example `EscapeRate` far above 5000), so that a 2-hour budget gives thousands of excursions that start at 77 rather than 36. Log the accepted size and new classes at or below 77 (the audit counter in `MS/sh/SorterHunter.cpp` does this in a few lines). Check its output at n = 18: the reruns found 1 to 2 other 77-gate classes in the first second, so this is measurable.
- **Repair: method.** The random walk fails its one-wrong-gate control at n = 18. One-gate replacement neighbourhoods cost about 7 s to enumerate exactly (`MS/nbhd.py`), so use systematic 1- and 2-gate neighbourhoods (best-improvement or tabu) and a full-size control before any 76-gate search. Do not start from the 48-failure candidate on the strength of its score: it is a one-gate-replacement local minimum, and the controls show a 40s score carries no information.
- **SAT: time and coverage.** Mid windows of 11 to 12 gates need more than 5 minutes (a planted w = 12 saving took 171 s), so give fewer windows longer budgets there (for example 20 to 30 minutes), or use a stronger encoding (symmetry breaking on gate order in the window, or the layer encoding). Tail windows of 11 to 12 gates finish in 8 to 18 s, so a cheap sweep of tail offsets at w = 11 to 14 (and of reordered tails) is the obvious next coverage step. Keep proof certificates for any UNSAT that is reported.
- When the corrections task runs: apply the five corrections above and add `claude-opus-5-5:anthropic:auditor` to `models`.
