# 18-input sorting network: SorterHunter and window SAT, scheduled 2 h, no 76-gate network found

This is a writeup of a failed search. It is not machine-checked, and it contains no witness. No network with fewer than 77 gates was found.

## What is shown

- The published 77-gate, 12-layer network for 18 inputs (Dobbelaere's list, id `N18L77D12`) was copied from the page and encoded as `{"comparators": [...]}`. `bun frontier diagnose` on it reported `valid: yes`, value 77, "ties the best known value".
- Two runs of SorterHunter (the heuristic that produced the record), each with a different seed and a fixed prefix taken from the record's first layers, reported best sizes 78 (run A) and 77 (run B). Neither log contains a network below 77 gates. Run B printed a 77-gate, 14-layer sorter (`logs/sh_B_output.txt:100`) and later a 77-gate, 12-layer sorter (`logs/sh_B_output.txt:102`); its log has no timestamps, so it does not record when either first appeared. The saved file `logs/network_77_found_by_SorterHunter_seedB.json` is the 14-layer one (`diagnose`: valid, value 77, ties the record). It is a different network from the record, not a reordering of it. **The best value reached is 77, which ties the record and does not beat it.**
- For 76 gates, the fewest unsorted zero-one inputs reached was 63 out of 262144. Both the record network and the saved run-B network reach 63 when the single best gate is deleted. This is a weak proxy only, since SorterHunter itself never targets a 76-gate non-sorter.
- A window re-synthesis by SAT (CaDiCaL) found no gate saving. For each window listed below, "a replacement with one gate fewer exists" was answered UNSAT with the prefix and suffix of the record fixed. No UNSAT proof certificates were kept.

## Method

**1. SorterHunter** (https://github.com/bertdobbelaere/SorterHunter, MIT, `--tool SorterHunter:search`), built with clang++ -O3 -march=native, one line added (`setvbuf(stdout, NULL, _IOLBF, 0)`) so output reaches the log while it runs. Symmetric mode (the record is mirror-symmetric under `(i,j) -> (17-j, 17-i)`), `EscapeRate=1000`, `MaxMutations=2`, mutation weights remove 1, swap 1, replace 0, cross 1, swap-intersecting 2, replace-half 1 (the sample config's values). Configs are in `scripts/cfgA.txt` and `scripts/cfgB.txt`. Neither run used `InitialNetwork`, so both started from the fixed prefix plus a random core (the logs show first networks of 115 and 111 gates).
- Run A: seed 101, fixed prefix of the record's first 2 layers (17 gates), `RestartRate=50000000`. Best reported: 78 gates (`logs/sh_A_output.txt:110,112`); it also printed a 79-gate, 11-layer network (line 118).
- Run B: seed 22, fixed prefix of the record's first 3 layers (21 gates), `RestartRate=20000000`. Started after the first SAT phase. Best reported: 77 gates (lines 100 and 102 of `logs/sh_B_output.txt`, see above).
- Run durations, how they ended and machine load are the author's own observations during the session and are not independently verified: run A about 2 h (1 h 59 min 58 s), run B about 1 h 02 min, both ended by SIGTERM (the programs never terminate on their own), about 60 to 90% of one core each because of contention with other jobs, no further improvement after about 10 minutes for run B and "stuck at 78" for the last 100+ minutes of run A. What the retained files support: the last write to run A's output was 68 min 9 s after its start file was created, and the last write to run B's output was 56 min 2 s after its start file was created, B starting 58 min 1 s after A; `scripts/waitloop.sh` schedules a deadline of start plus 7200 s. A quiet log does not show when a process stopped, and the logs hold no timestamps or iteration counters (`Verbosity=1`).
- The first `InitialNetwork` trial was abandoned after SorterHunter reported an unexpected starting size (90 gates instead of 77). Its configuration and output were not kept, so the cause of that 90 is unknown. See "InitialNetwork in symmetric mode" below for what the audit established.

**2. Window SAT** (`scripts/window_sat.py`, python-sat's CaDiCaL 1.5.3, `--tool CaDiCaL:SAT solver`; NumPy for the exhaustive candidate check, `--tool NumPy:exhaustive candidate validation`). For a window `[s, s+w)` of the record's 77-gate sequence, gates `[0, s)` are the fixed prefix and gates `[s+w, 77)` the fixed suffix. The question is whether `w-1` gates, chosen from all 153 pairs for each position, make prefix + window + suffix a sorter. Encoding: one choice variable per (position, pair) with exactly-one per position; per distinct zero-one vector that leaves the prefix, value variables per wire per position, with 6 clauses per (position, pair) and an "untouched wire keeps its value" rule; the fixed suffix is propagated gate by gate and the final wires must be sorted. Counterexample-guided: start with up to 60 failing and 40 shuffled prefix-output indices, deduplicated (so the actual count can be lower; across the logged UNSAT windows, 30 to 118 vectors were encoded out of 30 to 1343 distinct prefix outputs), solve, run the candidate on all distinct prefix outputs (NumPy), add up to 30 failing vectors, repeat. A candidate that passes would be re-tested with `bun frontier diagnose`. A gate directly repeating the previous one is forbidden (symmetry break); the audit checked that for the prefixes of the logged UNSAT windows this excludes no genuine saving, since each has pairs already ordered on every reachable input that can pad a shorter replacement.
Sanity checks on the encoder: replacing a 5-gate window at `s=70` with 5 gates is SAT, with 4 gates is UNSAT.

Exact windows that returned UNSAT (no `w-1`-gate replacement of that window with that prefix and suffix; offsets are distinct values of `s`):
- `w=8`: 11 windows, `s` = 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69 (every fourth offset).
- `w=9`: 25 windows, every `s` from 44 to 68.
- `w=10`: 21 distinct windows, every `s` from 47 to 67 (the log has 26 UNSAT lines because `s` = 47, 52, 57, 62, 67 were run twice).

Exact windows that timed out (neither UNSAT nor SAT):
- `w=8` at `s=17` (240 s) and `s=25` (200 s).
- `w=9` at `s=43` (150 s).
- `w=10` at `s=42` (200 s).
- `w=12` at `s=65` (200 s).

Windows never run: no `w=11` window; `w=10` at `s` = 43 to 46; `w=9` at `s` below 43; `w=8` at offsets not in the list above (including `s` = 18 to 24 and 26 to 28, and the offsets between the sampled ones); most windows starting before gate 43 at any size; all windows of 13 to 28 gates; `w=12` anywhere except the one timeout. Larger sizes were not run after the single 12-gate timeout, and the logs give no timing evidence for them. The logs also do not isolate why a window times out; the encoding uses pairwise exactly-one clauses over all 153 pairs at every position, and a single timeout does not show that larger synthesis is impractical.

Logs: `logs/scan_*.txt` (one JSON line per window; they come from four launches of `scripts/scan.py` with parameters edited between launches, and `scripts/scan.py` is the last version, `w` in {9, 11, 10}; `w=11` never started because the scan was killed to give the core to SorterHunter run B).

## Wall clock and exit status

Planned: a scheduled 2 h budget. The first search process was started at 21:19:15 IST (file-creation time 15:49:15 UTC, `search_start.txt`), and `scripts/waitloop.sh` schedules the deadline at start plus 7200 s. Core 1 was assigned SorterHunter run A, core 2 the window SAT for about 1 h and then SorterHunter run B. As in the run-duration bullet above, the author's recollection is that the SAT driver and both SorterHunter runs were killed with SIGTERM at the end and that no process crashed. The retained files do not independently confirm the exact durations, exit signals, CPU share or absence of crashes after the last output; they show output over about 68 minutes (run A) and about 56 minutes (run B). The audit also reran both configurations for a few seconds each and saw them mutate, evaluate and restart (about 23.6 and 21.5 million iterations in 8 s), which shows the configurations work, not how long the original runs lasted.

## Why it stalled

These two seeded runs did not report a sorter below 77. They do not establish exhaustion of the reachable search space, or that a different runtime or a different network would be needed. The SAT scan covered only the windows listed above. Every logged shortening query that completed was UNSAT; this establishes that there is no one-gate saving for the enumerated windows with the prefix and suffix fixed, and unsampled windows remain open. The single tested 12-gate window timed out at 200 s; no timing evidence was kept for 11-gate or 14 to 28-gate windows.

## InitialNetwork in symmetric mode

The independent audit established what the abandoned 90-gate trial did not (the 90 itself remains unexplained, since its input was not kept): in symmetric mode SorterHunter mirrors every gate of `InitialNetwork` (a gate with `i + j = 17` is inserted once; `FixedPrefix` is copied literally and is not mirrored). Giving it the full 77-gate record therefore starts at 149 gates. Given the mutable core in compressed form, one representative of each mirror pair (`i + j <= 17`) after removing the fixed prefix's gates, the 77-gate record starts at 77 with no prefix, with the 17-gate prefix and with the 21-gate prefix, and exhaustive enumeration found zero failures for all three expansions. Asymmetric mode accepts the full record unchanged and also starts at 77. So `InitialNetwork` works when the mutable core is supplied that way; it was not tried that way in this attempt.

## What these runs do and do not rule out

- These two seeds (101 and 22) with these two record-derived symmetric prefixes (the first 2 and the first 3 layers) reported best sizes 78 and 77. Another seed, another initialization or a continuation could behave differently.
- The windows listed above are UNSAT as stated. The other windows are not covered by any result here.

## What remains untried

- Start SorterHunter from the record, and from the distinct run-B 77-gate network, with a correctly compressed `InitialNetwork` (see above), in symmetric mode, and in asymmetric mode with the full network. This is the most direct search that was not actually run.
- Window SAT beyond the listed windows: the unrun and timed-out windows named above (no 11-gate window was run; `w=10` at `s` = 43 to 46; `w=8` at `s=17, 25`, `w=9` at `s=43`, `w=10` at `s=42` timed out; most windows before offset 43 are untested), larger windows (the one 12-gate window timed out), windows that are not contiguous in the sequence (reorder commuting gates first), mirror-linked windows, and a fixed prefix with the whole remaining tail free. A different encoding (sequential or cardinality at-most-one, layered gate positions) could be compared instead of concluding from one timeout.
- More seeds, more cores and longer SorterHunter runs, different prefixes (not the record's), greedy prefixes, and asymmetric mode.
- The 78-gate, 11-layer network and other published 18-input networks as starting points.

## Independent audit

A second model (GPT-6.1 Sol) audited this attempt. It reran controls on the SAT encoder: a planted redundant gate was found and removed; an 8-input bubble sort was shortened; the windows of an optimal 8-input network came back UNSAT; and three of the reported windows (`s=69,w=8`; `s=68,w=9`; `s=67,w=10`) were re-solved UNSAT. It also recomputed the single-deletion count (63 for both the record and the saved run-B network). It found the measured results reproducible and several conclusions and runtime statements overstated, and this text was corrected accordingly. The audit is an opinion backed by reruns, not a check by the repository verifier, and no UNSAT proof certificates were kept.

## Reproduction

`scripts/` holds the final versions of `window_sat.py`, `scan.py`, `best_from_sh.py` and `waitloop.sh`, and the two main configs `cfgA.txt` and `cfgB.txt` (no binaries). Not included: the earlier scan configurations (the parameters of `scan.py` were edited between launches), the failed `InitialNetwork` input, the baseline file (`baseline.json`, the record as copied from the page), and the SorterHunter source revision and build (it was cloned from the public repository's master on 2026-11-17 and given the one-line `setvbuf` change above; no commit hash or build log was kept). `python-sat` and `numpy` were installed in a local `uv` virtualenv with no lock file kept. Exact historical reproduction needs the author's scratch directory and further provenance.
