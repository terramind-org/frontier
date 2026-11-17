# 18-input sorting network: SorterHunter and window SAT, 2 h, no 76-gate network found

This is a writeup of a failed search. It is not machine-checked, and it contains no witness. No network with fewer than 77 gates was found.

## What is shown

- The published 77-gate, 12-layer network for 18 inputs (Dobbelaere's list, id `N18L77D12`) was copied from the page and encoded as `{"comparators": [...]}`. `bun frontier diagnose` on it reported `valid: yes`, value 77, "ties the best known value".
- Two independent runs of SorterHunter (the heuristic that produced the record) each ran with the record's first layers as a fixed prefix. Run B reached a valid 77-gate network after about 10 minutes (`logs/network_77_found_by_SorterHunter_seedB.json`; `diagnose`: valid, value 77, ties the record). Neither run produced anything shorter in its full run time. That is the best value reached: **77, which ties the record and does not beat it.**
- For 76 gates, the fewest unsorted zero-one inputs I reached was 63 out of 262144. Both the record network and the network found by run B reach 63 when the single best gate is deleted. This is a lower-quality proxy only, since SorterHunter itself never targets a 76-gate non-sorter.
- A window re-synthesis by SAT (CaDiCaL) found no gate saving. For each window, "no replacement with one gate fewer exists" was proved UNSAT with the prefix and suffix of the record fixed. The windows covered are listed below.

## Method

**1. SorterHunter** (https://github.com/bertdobbelaere/SorterHunter, MIT, `--tool SorterHunter:search`), built with clang++ -O3 -march=native, one line added (`setvbuf(stdout, NULL, _IOLBF, 0)`) so output reaches the log while it runs. Symmetric mode (the record is mirror-symmetric under `(i,j) -> (17-j, 17-i)`), `EscapeRate=1000`, `MaxMutations=2`, mutation weights remove 1, swap 1, replace 0, cross 1, swap-intersecting 2, replace-half 1 (the sample config's values). Configs are in `scripts/cfgA.txt` and `scripts/cfgB.txt`.
- Run A: seed 101, fixed prefix of the record's first 2 layers (17 gates), `RestartRate=50000000`. Ran 1 h 59 min 58 s. Best: 78 gates; it also printed a 79-gate network at 11 layers. Stuck at 78 for the last 100+ minutes.
- Run B: seed 22, fixed prefix of the record's first 3 layers (21 gates), `RestartRate=20000000`. Started after the first SAT phase (about 1 h into the budget), ran 1 h 02 min. Best: 77 gates (12 layers) after at most 10 min, then no further improvement.
- Both were stopped by SIGTERM at the end of the budget (no exit code of their own; they never terminate). Each was limited by contention with other jobs on the shared machine (about 60 to 90% of one core).
- An attempt to start SorterHunter from the record via `InitialNetwork` did not work: after mirror-expansion it started from 90 gates, not 77, so it was dropped. I did not find out why (probably how self-mirrored gates or the prefix are handled in symmetric mode).

**2. Window SAT** (`scripts/window_sat.py`, python-sat's CaDiCaL 1.5.3, `--tool CaDiCaL:SAT solver`). For a window `[s, s+w)` of the record's 77-gate sequence, gates `[0, s)` are the fixed prefix and gates `[s+w, 77)` the fixed suffix. The question is whether `w-1` gates, chosen from all 153 pairs for each position, make prefix + window + suffix a sorter. Encoding: one choice variable per (position, pair) with exactly-one per position; per distinct zero-one vector that leaves the prefix, value variables per wire per position, with 6 clauses per (position, pair) and an "untouched wire keeps its value" rule; the fixed suffix is propagated gate by gate and the final wires must be sorted. Counterexample-guided: start from 100 vectors (60 the suffix alone cannot sort, 40 random), solve, run the candidate on all distinct prefix outputs (numpy), add up to 30 failing vectors, repeat. A candidate that passes would be re-tested with `bun frontier diagnose`. A gate directly repeating the previous one is forbidden (symmetry break); this loses nothing since a repeated gate is redundant.
Sanity checks on the encoder: replacing a 5-gate window at `s=70` with 5 gates is SAT, with 4 gates is UNSAT.

Windows proved UNSAT (a real negative result: no `w-1`-gate replacement of that window with that prefix and suffix; counts are of distinct `s`):
- `w=8`: 11 windows, `s` = 29, 33, ..., 69 (step 4). `s=17` and `s=25` timed out (240 s, 200 s).
- `w=9`: 25 windows, every `s` from 44 to 68. `s=43` timed out at 150 s.
- `w=10`: 21 windows, every `s` from 47 to 67. `s=42` timed out at 200 s.
- `w=12`: `s=65` timed out at 200 s (not UNSAT, not SAT). Larger windows (14 to 28) were never run, because `w=12` already timed out.
Logs: `logs/scan_*.txt` (one JSON line per window; the four files are four launches of `scripts/scan.py` with the parameters edited between them, and `scripts/scan.py` is the last version, `w` in {9, 11, 10}; `w=11` never started because the scan was killed to give the core to SorterHunter run B).

## Wall clock and exit status

First search process started 21:19:15 IST; the budget ended 23:19. Core 1: SorterHunter run A for the whole 2 h. Core 2: window SAT for about 1 h, then SorterHunter run B for 1 h. The SAT driver and both SorterHunter runs were killed by me (SIGTERM) at the end; no process crashed.

## Why it stalled

The record is already a SorterHunter result and run B reproduces it in 10 minutes, so the space reachable by this heuristic with this prefix is exhausted quickly at 77; going to 76 needs a very different network or much longer runs than 1 to 2 core-hours. The SAT windows are tiny relative to a 77-gate network: windows beyond about 10 gates time out within 200 s because the number of distinct prefix vectors (hundreds to thousands) and 153 pair choices per position make the instances large. Every window up to 10 gates that finished was UNSAT, so the record is locally optimal against one-window replacement.

## What a later attempt should not repeat

- Run SorterHunter with the record's first 2 or 3 layers fixed, symmetric, `EscapeRate=1000`, for 1 to 2 core-hours: both seeds stop at 77 or 78.
- Window SAT with a window of at most 10 contiguous gates of the record at any offset 43 or later: all UNSAT.
- Do not use `InitialNetwork` in symmetric mode without checking the starting length first.

## What remains untried

- Windows of 11 or more gates (needs a better encoding: fewer candidate pairs, layered gate-position encoding, or symmetric windows using the mirror symmetry of the record), and windows not contiguous in the sequence (reorder commuting gates first).
- Windows starting before gate 43 (more distinct vectors; solves took 100+ s already at `s=44`).
- SAT that fixes a prefix and leaves the whole rest free (the brief's line 4): not run beyond the window form, because the free tail would be 50+ gates.
- Many seeds, more cores and longer SorterHunter runs, different prefixes (not the record's), greedy prefixes, and asymmetric mode.
- Using the other 78-gate, 11-layer record network or other published 18-input networks as the starting point.

## Reproduction

`scripts/` has everything run (no binaries). SorterHunter was built from the public repository at its master as cloned on 2026-11-17 with the one-line `setvbuf` change above. `python-sat` and `numpy` were installed in a local `uv` virtualenv.
