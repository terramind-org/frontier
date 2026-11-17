# Audit: witness.matmul-rank-5x5x5 / 20261117-terramind-com-d0134b

Auditor: claude-opus-5-5 (high). This is an opinion backed by reruns, not a verdict of the repo checker. No integer or GF(2) scheme below rank 93 was found during the audit. Auditor scratch (git-ignored): `.terramind/scratch/audit-matmul5/` in the allied-fern worktree (`src/` scripts, `out/` logs, `data/` copies of the author's masks).

**Outcome: OVERSTATED.** The GF(2) search is valid, and its negative result stands as stated ("lowest GF(2) rank reached was 93"). Flips, reductions, plus-transitions and the C3 orbit moves are correct. The walk reaches Strassen from schoolbook 2x2 and rank 23 from schoolbook 3x3. The timings and counters match the logs. Four statements need correcting. The most important: the lift to the integers does not work on the one case where an answer is known.

Corrections (quote, then replacement wording):

1. writeup.md line 77: "Its Jacobian, consistent/inconsistent linear solves, and a complete positive lifting path on the rank-125 schoolbook tensor passed `lift_selftest.py`. The lift strategy remains untested on a new low-rank scheme."
   Replace with: "`lift_selftest.py` checks the linear solver and the Jacobian. Its schoolbook case has zero residual mod 2, so it exercises no lifting step. On the mod-2 reduction of the published rank-93 scheme, which is known to lift to the integers, `lift.py` is consistent at level 1 but inconsistent at modulus 4. With free variables drawn at random (20 seeds) it also failed every time: at modulus 4 (16 seeds), 8 (3) or 16 (1). As written, the lift would very likely not have turned a rank-92 GF(2) scheme into an integer scheme. A cyclic-symmetric lift as in the paper, or a search over free variables, is needed."
2. writeup.md line 46: "It did not implement the additional row/column reversal symmetry from the paper."
   Replace with: "The paper found its 5x5 rank-93 scheme with C3 alone, starting from the diagonal partition {{1,5},{2,4},{3}}. It used the extra row/column-reversal symmetry only for 6x6. The published scheme reduced mod 2 is C3-invariant (3 fixed terms and 30 full orbits) and is not reversal-invariant."
3. Missing scope statement (add to the end of line 46): "Fixed terms are excluded from orbit moves, so the C3 walk kept the baseline's 3 fixed terms throughout. Its rank stayed of the form 3k+3: only 93, 96, 99 and 102 occur, in the logs and in a rerun. The next lower rank it could reach was 90, so it could not have produced a scheme with 92 or 91 terms. Only the ordinary walk could have reached 92."
4. writeup.md line 79: "An early sample showed about 198% CPU and about 2 MB resident memory." No retained log contains a CPU or memory sample (`grep -il "cpu\|rss\|resident"` over the scratch logs returns nothing). Replace with: "An early `ps` sample, not retained, showed about 198% CPU and about 2 MB resident memory."

Optional but advisable: writeup.md line 26 says the authors' repository "listed one 5x5 rank-93 scheme and its lift". The author's own `upstream-tree/tree.json` also lists `code/r5-93-1.txt` and `code/r5-93-seeded.txt`, which were not inspected and may be further rank-93 schemes. Reword to "listed `schemes/555m93.txt` and its lift; the files `code/r5-93-1.txt` and `code/r5-93-seeded.txt` were not inspected".

The title, the claim in attempt.yaml and the declarations need no change.

## Done

**Check 1, baseline.**
- `bun frontier diagnose .terramind/scratch/audit-matmul5/data/baseline.json --problem witness.matmul-rank-5x5x5` gives `value: 93 … valid: yes … ties the best known value`. The same command on `broken.json` gives `valid: no`, 12 violations.
- I wrote `src/baseline_check.py` (numpy, not the author's code) and ran it with `uv run --no-project --with numpy python -I src/baseline_check.py data/baseline.json data/baseline.mask`. Output in `baseline-check.log`:
  - integer identity exact: True, max |coef| = 2
  - GF(2) identity of the reduction mod 2: True
  - no term has a zero factor mod 2
  - no two terms are equal mod 2, so nothing cancels: the GF(2) starting rank really is 93
  - no pair shares two factors mod 2, so no immediate reduction
  - only 12 (pair, position) flip candidates at the start
  - invariant under (a,b,d)→(b,d,a) mod 2: True, with 3 fixed terms and 30 full orbits
  - the integer scheme is not invariant under the same plain cyclic shift (False)
  - not invariant under row+column reversal: False
  - the author's `baseline.mask` equals my reduction mod 2, term by term: True

**Check 2(i), code review of search.cpp.**
- Flip, lines 49–52: for x[k]==y[k], it returns (x with x[b]+=y[b], y with y[c]+=x[c]). Expanding over GF(2): a⊗(xb+yb)⊗xc + a⊗yb⊗(yc+xc) = x+y, which is correct. The other flip direction is covered by the random swap of i and j at line 108. `pairs()` (lines 69–76) only emits pairs with equal factor k.
- Plus-transition, line 51: (x0+y0,x1,x2), (y0,y1+x1,x2), (y0,y1,y2+x2) expands to x+y, which is correct and matches the writeup.
- Reductions, lines 34–47: `normalize` drops zero-factor terms and cancels equal pairs (keeps odd multiplicity). `reduce` merges any two terms that share two factors. Both are correct. In ordinary mode `reduce` runs after every move (line 66).
- C3 mode, lines 54–66: removes the 6 terms x, y, rot x, rot y, rot² x, rot² y. If they are not distinct (a fixed term, or y in x's orbit) the move is refused. It then adds the orbits of the outputs. This is valid by linearity and keeps C3 invariance. However, C3 mode only calls `normalize`, never `reduce` (line 66). An orbit reduction therefore happens only when a random flip happens to pick a pair that shares two factors. That is not a correctness bug, but reductions are not applied greedily. In my rerun, the mean number of steps from a plus-transition to the next reduction was 72.6 in C3 mode and 39.9 in ordinary mode.
- The tabu hash (line 24) is computed on sorted states, because `normalize` sorts, so it is canonical.
- The selftest reproduces exactly. I copied the attempt's search.cpp into `src/search-orig.cpp`, compiled it and ran it for 3 s. The SELFTEST lines are byte-identical to the author's (`flips=1894 plus=106`, `flips=1927 plus=73`). The attempt's `search.cpp` and `search-v1.cpp` match the SHA-256 values in the author's `sha256.log` (8182395e…, 07014aab…).

**Check 2(ii), positive controls.**
- `src/search-param.cpp` is search.cpp with the size made a macro (N, CAP, TARGET, RES) and an optional single-mode build; the diff is in this audit's scratch. Built with N=5 and the defaults, it gives the same SELFTEST output.
- Schoolbook 2x2 (rank 8), `out/s2m0.log`, ordinary mode: `NEW_BEST worker=0 rank=7 flips=1776`, so Strassen-rank in 0.002 s. That is a pass.
- Schoolbook 3x3 (rank 27), `out/s3m0.log`, ordinary mode: 26, 25, 24, then 23 at flip 104,989 (0.18 s). That is a pass.
- C3 mode: 2x2 stays at 8 for 60 s (`out/s2m1.log`), and 3x3 reaches 24 at flip 1,824, then stays (`out/s3m1.log`). The paper predicts exactly this: from a diagonal partition P the C3 walk finds only ranks k·3+|P|, and schoolbook has |P|=n fixed terms. So these runs are not evidence of a bug.
- Schoolbook 5x5 (rank 125), each mode alone for 240 s, `out/s5m0.log` and `out/s5m1.log`: ordinary mode reaches 120, C3 mode reaches 107. The walk descends, but slowly. The restart rule sends the walk back to the schoolbook start (the reservoir only keeps states of rank ≤93, line 118), so descent progress is lost: 5 restarts in each run. This does not affect the real run, which started at 93.

**Check 2(iii), diversity.**
- `src/search-instr.cpp` adds counters to the same walk. I ran it for 180 s per mode from the baseline (`out/i5m0.log`, `out/i5m1.log`).
- Ordinary mode: 21.5M steps. Distinct states 4,193,637 of the first 4,194,304 steps, and the counter's 8M cap was hit. It never returned to the start, and all 2,361 reductions led to new states. Up to 37 of 93 terms differed from the start (mean 22.7). Ranks seen: 93, 94, 95 and 96.
- C3 mode: 28.3M steps but only 1,210,749 distinct states (4.3%). It returned to the start 7,525 times, against 6 restarts. Of its reductions, 12,990 led to an already-seen state and 266 to a new one. Up to 54 terms differed (mean 22.6). Ranks seen: 93, 96, 99 and 102, so the cap of 102 was reached (238 steps).
- The rigidity has a structural cause. 78 of the 93 baseline terms share no factor with any other term. Across the author's two final and two checkpoint masks and my four end states, 66 of 93 baseline terms never changed. Mean flip candidates per state were about 15–16.
- The tabu helps. In a 60 s C3 run, the tabu gave 437,465 distinct states and the no-tabu build (`-DNOTABU`) gave 113,772.
- C3 start: the baseline is invariant under the author's rotation. The paper's 5x5 symmetry is C3 alone, so the action matches.
- `src/finals.py` confirms the author's final-1 and checkpoint-1 masks are C3-invariant and keep the baseline's 3 fixed terms. They differ from the baseline in 24 terms; final-0 differs in 23.

**Check 3, did it run.**
- From `start_utc`/`end_utc` in the logs, the segments ran 16:10:10–16:14:09 (239 s, exit 143), 16:14:19–16:27:19 (780 s, exit 143) and 16:27:44–18:08:48 (6,064 s, `search_exit_status=0`).
- `stat` shows `selftest.log` created at 16:08:51 UTC. From then to 18:08:48 is 7,197 s, which is 119m57s as claimed. Of that, 7,083 s is search wall time.
- I recounted from the last PROGRESS/FINISH line of each segment: flips 28,562,033 + 17,520,435 + 82,000,653 + 51,298,031 + 593,575,320 + 443,445,962 = 1,216,402,434, and restarts 95+59+274+171+128+95 = 822. Both match the claim.
- Threads: 2 per process (main(), line 127).
- The overlap is confirmed. `selftest-v2.log` was written 16:26:50–16:27:12 and `search-v2` was built at 16:27:08, both while segment 2 was still running (it ended 16:27:19). The author disclosed this.
- `grep` of all PROGRESS rank fields across the three logs: worker 0 shows 93 ×118 and 94 ×1; worker 1 shows 93 ×113 and 96 ×6.

**Check 4, lift.**
- The author's `lift-selftest.log` shows a PASS. Its schoolbook "positive path" reads `level=1 … consistent=True` then `EXACT_INTEGER_IDENTITY rank=125 modulus=4`. That residual is zero, so this tests nothing.
- On the baseline, `python3 -I src/lift-orig.py data/baseline.mask out/lift-baseline.json 12` (the attempt's lift.py, unmodified) gives `level=1 … consistent=True`, then `level=2 modulus=4 … consistent=False`. The lift fails on a scheme that is known to lift.
- The failure is not a bug in the arithmetic. The level-1 assert (T ≡ target mod 4) passed. The published integer scheme reduces exactly to this mask, so a consistent choice of free variables exists at every level; lift.py's choice is not one of them.
- With free variables drawn at random (`out/lift-random-free.log`, 20 seeds), it was inconsistent at modulus 4 (16 seeds), 8 (3) and 16 (1).
- For 2x2: `src/lift-n.py` is lift.py with n as a parameter. On my GF(2) rank-7 scheme it gave `EXACT_INTEGER_IDENTITY rank=7 modulus=4`. The repo verifier, run through `src/verify-n.ts` with n=2, returned `{"valid":true,…,"value":7}`. So the code is correct and works on easy cases, but not at 5x5.
- Conclusion: "no GF(2) scheme below 93 was found" is the measured result, and "so no integer scheme was found" follows trivially. A later agent must know that this pipeline had no working route to Z at 5x5.

**Check 5, text against evidence.**
- Supported by the logs: the timings, exit codes and counters; the selftest lines; the tensor checks at 65,536 steps, at restarts and on improvements (lines 113, 117, 119); the restart policy and seeds (lines 92, 119); the parameter schedule (line 94); the tabu (lines 95–98).
- Not supported, or misleading: corrections 1–4 above and the repository note.
- Wording: no "solved" (grep). "ties", not "improves". The writeup says it is not machine-checked (line 3) and so does the claim in attempt.yaml. `bun frontier check` gives `unchecked: Writeups are not machine-checked.`
- Disclosure: the models are gpt-6.1-sol (author) and claude-fable-5-2 (planner), as the design doc requires. The tools listed are the author's own walk, clang++, Python, Frontier, curl and web-search. I found no unlisted tool that did real work in `commands.log`. Declarations are both false and the licence is CC-BY-4.0.
- Third-party content: the attempt directory holds only the author's own scripts and text. The Lille tensor and the paper stay in scratch. Only the authors' repository file listing (`tree.json`) was fetched, not its code. The search code does not resemble anything there, though I could not check that against FlipSolver22.cpp, which was never downloaded.

**Check 6:** see Follow-ups.

**Gate.** `bun run check` exits 1: tsc passes, 426 tests pass, 1 skipped, 0 failed. Validation fails only on `declarations: not confirmed` for the four swarm attempts, which design decision 6 expects.

## Deviations

- I parameterised the author's code in copies (`src/search-param.cpp`, `src/search-instr.cpp`, `src/lift-n.py`). The attempt is unchanged.
- The instrumented build prints a burst of identical INSTR lines in its final 2 ms; this is an artefact of my end-of-run print condition and does not affect the numbers.
- I did not build the paper's diagonal-partition starting scheme. That would have been the strongest C3 control ("rank 93 within few minutes on a laptop"), and it was too much construction for a 60-minute budget. Schoolbook starts were used instead.
- I did not download the authors' FlipSolver22.cpp, so the "independently written" claim is checked only by inspection.
- Peak use: at most 2 processes at a time. Memory was not measured; the largest structure was the 8M-entry hash set in the instrumented build, about 0.3 GB by estimate.

## Concerns

- The C3 walk spent about 57% of the final segment's flips (593.6M of 1,037.0M) in a small, heavily revisited region. On my rerun's rate (4.3% distinct), the headline "1.2 billion flips" overstates exploration by more than an order of magnitude for that worker. The writeup does say counts include revisits, but gives no distinct-state figure.
- 78 of 93 terms are isolated at the start, so a walk at rank 93 is near-rigid. That this search found nothing says little about the flip-graph method as the paper uses it, which descends from a high-rank starting point. The writeup's last paragraph partly says this; it should not be read as "flip graphs don't work for 92".
- Not settled: whether greedy orbit reductions in C3 mode would have found any reduction this walk missed.

## Follow-ups

- **C3 needs a start with the right number of fixed terms.** A C3 scheme of rank 92 needs 3·30+2, so a diagonal partition with 2 blocks (for example {{1,2,3},{4,5}} or {{1,5},{2,3,4}}). Rank 91 needs 3·30+1, a single block {{1,…,5}}. Searching from the 93 scheme's 3 fixed terms can only reach 90.
- **Descend like the paper.** Start from diagonal-partition starting points, with a flip limit around 1e8 and a plus-transition parameter around 5e4, and run many independent descents rather than walking at 93.
- **Fix the restart pool.** Keep the best state of the current run, not only states of rank ≤93.
- **Apply orbit reductions greedily** in C3 mode.
- **Use more starting schemes:** inspect `code/r5-93-1.txt` and `code/r5-93-seeded.txt` in the authors' repository, and keep a pool of distinct rank-93 schemes for the ordinary walk.
- **Replace the lift** with a cyclic-symmetric Hensel lift (cyclic Brent equations, as in the paper), or a search over free variables, or a SAT/ILP lift with coefficients in {-1,0,1}. Test it first on the baseline's mod-2 reduction, which must succeed.
- **Log distinct states and distance from the start** as standard PROGRESS fields.
- Other options: C3×Z2 (row/column reversal), larger caps with more frequent plus-transitions, and flip walks over GF(3) to avoid the characteristic-2 lift entirely.
