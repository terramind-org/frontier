# Audit: witness.kissing-number-11 attempt 20261117-terramind-com-6ab95f

Auditor: claude-opus-5-5 (independent of the author, gpt-6.1-sol). This is an opinion backed by reruns, not a verdict of the repository checker. No 605-point configuration accepted by `bun frontier diagnose` was found during the audit.

All audit scripts, inputs and outputs are in `.terramind/scratch/audit-kissing11/` in the auditor worktree (`bin/` holds my scripts; `data/` holds byte copies of the author's files). Environment: Python 3.12, NumPy 2.5.5, SciPy 1.18.1 (uv venv), BLAS threads 1, at most 2 processes at once. Audit wall clock: 18:20 to 18:45 UTC on 17 Nov.

## Done

Report: `.terramind/swarm/witness-records/handoffs/audit-kissing11.md` (same content).

### Outcome

**OVERSTATED.** The search is valid. Each stage can say yes on a punctured instance with a known answer, the export path is correct, and every count in the writeup matches the logs. No bug voids a stated negative result. Four statements must be corrected, though, and three more should be.

**Must correct:**

1. **The headline number reads as closeness to 605.**
   - Where: the `claim` in attempt.yaml (lines 6-11), and writeup.md lines 3-6, which give "maximum pairwise cosine 0.5072124712612411 … minimum angle 59.52166841688265 degrees" as the lead result with no context.
   - Why it misleads: the figure measures the cost of squeezing one point into the jammed 604, not distance to a valid 605.
     - One 34-second Lp schedule (`relax.py`'s own loss and p schedule) from the baseline plus one random point reaches 0.5072137 (`relax-605.out`, seed 51). The author's two-hour best is 0.5072125.
     - The same optimiser from random starts reaches only 0.5434 to 0.5442 at N = 603, 604 and 605, and 0.5128 even at N = 438 (`relax-random-small.out`, `relax-random604.out`, `relax-605.out`).
   - Corrected claim: "Failed two-hour local search around the published 604-point configuration; no valid 605-point configuration was found. The best numerical 605-point configuration (the 604 with one point inserted, all points relaxed) had maximum pairwise cosine 0.50721 (required <= 0.5). One 34-second relaxation from the baseline plus a random point reaches the same value, so this figure is not evidence that 605 is close to reachable. Its integer export was rejected. Exact configurations validated only at 604, tying the repository record. This writeup is not machine-checked and establishes no upper bound."
   - Add the same qualification after writeup.md line 8.

2. **The exchange count suggests a broad search; the phase could not succeed.**
   - Where: writeup.md lines 56-61, "The log records 1,322,820 exchange trials. None improved the best maximum cosine."
   - Why: every exchange started from one of the 64 retained holes. All 64 have the same form, (±1, ±1, ±1, 0, …)/√3 (8 supports × 8 signs), and an identical inner-product profile against the 604. Each has exactly 51 points at cosine 1/√3 (`holes.npz`, my recount).
   - A k ≤ 6 exchange removes at most 6 of those 51 blockers. My replay of `search.py` lines 159-174 on the real holes (`bin/exchange_real.py`, 1,200 trials) converged in a median of 16 to 34 L-BFGS iterations, always to maximum cosine ≥ 0.578 (median about 0.587).
   - Add after line 61: "Every exchange started from one of 64 holes of a single type, each with 51 points at cosine 1/√3. Removing at most six of them could not clear the rest, so this phase was structurally unable to succeed; the trial count measures repetition, not breadth."

3. **The "full integer pool" is not full.**
   - Where: writeup.md line 90, "The full integer pool had 19,034 directions" (and "the full 19,034-direction model" in the handoff).
   - Why: `integer_pool.py` lines 34-35 enumerate eight hand-picked norm-36 integer patterns. My enumeration of every norm-36 integer pattern in Z^11 (`bin/int_patterns.py`) finds 16,286 integer directions compatible with the backbone. The pool has 14,750 of them and misses all 1,536 of pattern (3,3,3,2,2,1).
   - Corrected: "An enlarged pool had 19,034 directions: the 4,284 earlier ones plus the integer vectors of eight selected norm-36 patterns. It omits the 1,536 backbone-compatible integer vectors of pattern (3,3,3,2,2,1)."

4. **The memory statement understates what the log shows.**
   - Where: writeup.md lines 90-94, "Its initial dense model was stopped without a result because its allocation pattern could exceed the 3 GB memory cap … Resource compliance for that aborted run cannot be asserted."
   - Why: `integer-pool.out` ends with `MODEL 19034 vertices 34171904 edges`, so `integer_pool_initial.py` had already evaluated `x@x.T>.5+1e-12`. That means a float64 Gram matrix of 19,034² × 8 B = 2.90 GB and its Boolean result (0.36 GB) were live at the same moment: at least 3.26 GB. The run was stopped after that allocation, during model build or solve.
   - Corrected: "Its log shows it had already formed the dense 19,034-square float64 Gram matrix (2.90 GB) with its Boolean comparison (0.36 GB), so it very likely exceeded the 3 GB memory cap before it was stopped. The sampled RSS of 1,882,752 KiB is not a peak."

**Should correct (accurate but incomplete):**

5. **The MILP bound depends on the fixed backbone.** writeup.md lines 84-88, "Conflict-graph MILPs reported an optimum of 108 extension points for each pool … They do not bound configurations outside those pools." Every model holds the 496 integer backbone fixed (`structure.py` lines 23-24 and 95-104; `integer_pool.py` lines 11 and 54-61). Add: "and only with the 496-vector backbone held fixed."
6. **Most of the time in the hole and relaxation phases added nothing.**
   - The hole phase found its best value, 1/√3, at 0.06 s (`search.out` line 32). The remaining 161k trials never improved it.
   - The final relaxation profile reached 0.507212471 at 220 s of its 3,575 s (`relax-wide.out`). The earlier profiles plateaued at 733 s of 1,840 s and 151 s of 1,400 s.
   - Say so after lines 54 and 72, so the trial and evaluation counts are not read as search breadth.
7. **Exit status 145 is a stop, not the termination.** writeup.md lines 106-107, "The main launcher's recorded wait status is 145." 145 = 128 + 17, and signal 17 is SIGSTOP on this macOS (`python3 -c "import signal;print(signal.Signals(17).name)"` → `SIGSTOP`). The recorded status most likely reflects a stopped job, so the main process's final termination status was never captured. Also state the time the main process spent paused, about 284 s: its own progress log has gaps 1060→1208 s and 1328→1464 s, which match the two integer-pool runs in `run-index.json`.

### Checks

#### Check 1: baseline

- **Diagnose results** (`bun frontier diagnose <f> --problem witness.kissing-number-11`):
  - Author's `baseline.json`: valid, 604, ties.
  - `broken.json`: invalid (vectors 0 and 603 equal).
  - `structured-best.json`, `expanded-best.json`, `integer-pool-best.json`: each valid, 604, ties.
- **Exact analysis with my own script** (`bin/exact.py`, exact integer Z[√2] arithmetic):
  - One norm: |v|² = 36 for all 604 vectors.
  - 496 integer vectors: 480 of pattern (3,3,3,3) and 16 of the form ±6e_j.
  - 108 vectors with a √2 part, in three patterns: 96, 6 and 6.
  - 22 distinct inner products, including −36 (302 antipodal pairs: the configuration is antipodal).
  - Maximum cosine exactly 1/2, minimum angle exactly 60°.
  - **19,704 tight pairs** (inner product exactly 18), matching writeup.md line 32.
- **Provenance.** The baseline is the published EinsteinArena file, not a reconstruction. I re-fetched `repos/togethercomputer/EinsteinArena-new-SOTA/contents/kissing-number/solutions/solution_n=604_d=11.json?ref=c388c6f…` and its SHA-256 is `0bde9ca2…7761`, identical to the author's.
- **Structure.** The 496 + 108 split is real.
- **The three finite-pool results** are distinct from the baseline but close to it. Each contains all 496 backbone vectors plus 2 of the baseline's extension vectors and 106 new ones. They are also distinct from each other as sets. Their equivalence under symmetry was not tested.

#### Check 2: can the search say yes?

**(i) Hole search.** I punctured the baseline (one extension vector removed: `p1ext`; one backbone vector removed: `p1back`). Then I ran the author's `search.py`, patched only so the hard-coded 605 becomes len(x) (`bin/search_audit.py`; the diff is in the command log).

- In both cases the hole stage found max cos 0.5000000000000006 within 0.12 s.
- The alphabet snap rebuilt the exact vector, and the run raised `SUCCESS` after `exact_valid` and the repository `diagnose` both accepted the 604.
- The added vector equals the removed one exactly.

With three scattered vectors removed (`p3`, 601 points), the verbatim hole code (`bin/hole_test.py`) found holes at ≤ 0.5 + 1e-9 in 35 of 600 trials, and hit all three removed vectors (24, 5 and 6 times). Claim (b) is not voided.

**(ii) Exchange.** I ran the verbatim `local_loss` and minimize call on `p3`, with directions set to a removed vector plus noise of 0.05, 0.15 or 0.3, k = 1..6 and 8 trials each (`bin/exchange_test.py`).

- It lands in the correct basin every time: best max cos 0.5 + 6e-10 to 3e-9.
- It passes the code's own `score < .5+1e-9` gate in only 4 of 144 trials. The squared-hinge loss leaves residual overlaps of about 1e-9.
- This is a latent false-negative in automatic success detection. It does not void claim (c): the real run's exchange stage never got below 0.577, far from the gate, and my replay above shows why.

**(iii) Relaxation** (verbatim `relax.py` loss and p = 2…256 schedule, `bin/relax_test.py`):

| Start | N | Best max cos | Time |
|---|---|---|---|
| Baseline with noise 0.003, 0.015 or 0.05 (start max cos up to 0.694) | 604 | 0.5 + 4e-14 to 0.5 + 1e-13 | 0.6 s |
| Random | 604 | 0.5434, 0.5441 | |
| Random | 603 | 0.5437, 0.5437 | |
| Random | 560 | 0.5365 | |
| Random | 500 | 0.5257 | |
| Random | 438 | 0.5128 | |
| Random | 605 | 0.5442 | |
| Baseline + random point | 605 | 0.507214 / 0.507490 / 0.507498 | about 33 s each |

The optimiser is a strong local polisher and no global method: from scratch it cannot even reach 438 at 60°. So 0.5072 at N = 605 says nothing about whether 605 exists.

**(iv) Objective** (`bin/npz_check.py` on `relax-wide-best605.npz`):

- 605 rows, all finite, norms in [1 − 2e-16, 1 + 2e-16].
- Maximum cosine 0.5072124712612411, matching the claim.
- 605 distinct rows at 1e-6 rounding; no pair with cosine above 0.9 (none above 0.99). No collapsed points.
- 12,485 pairs above 0.5, of which 7,810 are above 0.505.
- `best605.npz` (main search): maximum cosine 0.5574815076231908, as claimed.

#### Check 3: exactness path

`export_best.py` lines 18-19 scale by 10^12, round, and put everything in the p part (q = 0). This is correct when there is slack.

- A 300-point configuration relaxed to max cos 0.49, plus 1e-9 noise, exported by the same code: `diagnose` accepts it (valid, 300).
- The exact 604 baseline exported from floats with no noise is rejected with 19,590 violations. With 1e-9 or 1e-6 noise: 9,837 and 9,844 violations.
- The 604 baseline has zero slack: all 19,704 contacts are exactly tight. No numerical neighbour of it can be made exact by rounding, and a numerical 605 near it would need exact reconstruction (an alphabet snap such as `search.py` line 96) or strict slack.
- 12,485 violations for the 605 export equals exactly the number of numerical pairs above 0.5. Rounding added and removed nothing, so the count is what one expects and shows no export bug.

Note: `bun frontier diagnose` exits 0 even for an invalid witness (`broken.json` gives exit 0). The success gate in `search.py` line 114, `exact_valid(...) and result.returncode==0`, therefore rests entirely on `exact_valid`. The p1 runs above show that `exact_valid` works.

#### Check 4: MILP claims

**What the model is.**
- Pool: norm-36 directions in Z[√2]^11 with cosine ≤ 1/2 + 1e-12 against all 496 backbone vectors.
- Conflict edges: pairs with cosine above 1/2 + 1e-12.
- Model: maximise Σx subject to x_i + x_j ≤ 1 per edge, x binary, backbone fixed (`structure.py` lines 93-100; `integer_pool.py` lines 54-58).
- "108 extensions" = a maximum independent set of the pool's conflict graph. That is a correct encoding of the angle constraint for an extension of the fixed backbone. Float tolerance is safe: Gram entries are values a + b√2 over 36, separated far more than 1e-12.

**Solver status.** It distinguishes optimal from time-limited. All three logs report "HiGHS Status 7: Optimal", gap 0%, primal = dual = −108. I re-ran `structure.py` myself: pool 3,876, 739,284 edges, Optimal 108, 15 s, 867 MB RSS. The resulting 604 is accepted by `diagnose`.

**The "19,034 directions".** These are the expanded pool plus eight integer patterns. The aborted model printed 34,171,904 edges and has no solver output (`integer-pool.out`). The guarded run used a seeded 5,000-subset: Optimal 108 (`integer-subset.out`). See correction 3 for the missing pattern.

**`dominance.py`.**
- The rule is correct: delete v if an adjacent active u has N[u] ⊆ N[v].
- It is restricted to dominators from the old pool and to 128 tests per vertex.
- `dominance.out`: 0 deleted, 2,269,643 checks, MILP skipped (more than 5,000 vertices).

#### Check 5: did the search run?

**Timeline** (`run-index.json`, `launch-utc.txt`, `budget-stop.json`):

| Time (UTC) | Event |
|---|---|
| 16:09:52 | Launch |
| 16:09:55.19 | Main search header |
| 16:11:28 – 16:11:49 | `structure`, exit 0 |
| 16:13:28 – 16:14:38 | `expanded`, exit 0 |
| 16:15:44 – 16:46:37 | `relax`, exit 143 |
| 16:27:43 – 16:30:03 | `integer-pool` (initial), exit 143 |
| 16:32:07 – 16:34:19 | `integer-subset`, exit 0 |
| 16:46:42 – 17:10:12 | `relax-high`, exit 143 |
| 17:10:16 – 18:09:52 | `relax-wide`, exit 0; END summary 3,575.17 s |
| 17:17:00 – 17:17:27 | `dominance`, exit 0 |
| 18:09:51.995739 | Guard SIGTERM, 7,199.995739 s after launch |
| 18:09:52.048 | `search.exit` = 145 written |

**Main progress log.** 347 progress records; phase boundaries at 1,208 s (hole → exchange) and 5,393/5,412 s (exchange → full). The last record, at 7,195.24 s, has counts hole 161,415, lp 53,805, exchange 1,322,820 and full 723. These match claims (b) and (c).

**Lp profile.** 61 restarts and 713,909 evaluations, matching claim (d).

**Pauses and exit status.** The two pauses in the main log match the integer-pool runs. Exit 145 is discussed in correction 7.

**Cores.** At most two research processes at once, per timestamps, with BLAS threads set to 1 in the logged environment. HiGHS printed "Unrecognized options detected: {'threads': 1}" for `linprog` (`search.out`): the option was passed through to HiGHS, not confirmed applied.

**Memory.** `resource-notes.log` records 1,882,752 KiB (initial integer-pool run) and 1,198,976 KiB (subset run). For the initial run, see correction 4: by arithmetic it very likely exceeded 3 GB. My own heaviest run peaked at 0.87 GB RSS.

#### Check 6: text against evidence

**Matches the logs.** These all match: 19,704 contacts, 496/108, 480/16, 161,415 trials, 53,805 LP calls, 256 retained/64 distinct holes, 51 blockers, 1/√3, 1,322,820, 723, 0.5574815076231908, 61 restarts, 713,909 evaluations, gradient errors (p = 2: 1.18e-7; others ≤ 2.7e-11), 0.5072124712612411, 12,485, 7,199.995739 s, HiGHS 1.8.0, NumPy 2.2.6, SciPy 1.16.3.

**Unsupported or overstated statements.** Corrections 1-7 above.

**Wording rules.**
- No "solved" anywhere (`grep -i solved` over writeup.md and attempt.yaml: no hits).
- Ties are called ties, never improvements.
- The writeup states "not machine-checked" (line 10; claim line 10).
- `bun frontier check` on the attempt reports `unchecked: Writeups are not machine-checked.`

**Disclosure.**
- Models: gpt-6.1-sol (author), claude-fable-5-2 (planner).
- Tools: python3, numpy, scipy (L-BFGS-B, SLSQP, linprog/milp front end), highs (LP/MILP), frontier, gh.
- That covers every solver and optimiser seen in the scripts and logs.

**Declarations.** `rights: false`, `disclosure_complete: false` (attempt.yaml lines 58-60).

**Licence.**
- The attempt directory contains only the author's own scripts and prose. No third-party code is present, and no data is copied: the baseline stays in scratch and is cited by URL, commit and SHA-256.
- The upstream EinsteinArena repository declares no licence (`gh api repos/togethercomputer/EinsteinArena-new-SOTA --jq .license` → null). Since nothing from it is redistributed, the CC BY 4.0 attempt is unaffected. Its "source permits reuse" status is simply unstated upstream.

#### Check 7: not tried

See Follow-ups.

#### Repository gate

- `bun run check`: tsc passed; 426 pass, 1 skip, 0 fail. `validate` exits 1 only for the five swarm attempts' unconfirmed declarations, which is expected.
- `bun frontier check attempts/witness.kissing-number-11/20261117-terramind-com-6ab95f`: `unchecked: Writeups are not machine-checked.`

## Deviations

- **Patched copy of `search.py`.** To run the author's search on punctured 603/601 instances, I changed four hard-coded `605`s to `len(x)`/`-1` and renamed the output file `candidate.json`, in my copy `bin/search_audit.py`. Nothing else changed, and the author's files were not touched.
- **Copied functions instead of whole scripts.** The exchange and relaxation tests copy the author's functions verbatim into my harnesses (named by line in each file's docstring), because those functions are nested in or hard-wired to N = 605 in the originals.
- **Different library versions.** I used Python 3.12 / NumPy 2.5.5 / SciPy 1.18.1 rather than the author's 3.11.8 / 2.2.6 / 1.16.3.
- **Not rerun:**
  - The 19,034-vertex and 5,000-subset MILPs. The first is over the memory budget; the second needs 130 s and 1.2 GB. Only the 3,876-direction MILP was rerun; the others were judged from their logs.
  - The full two-hour search.

## Concerns

- I did not test whether the three finite-pool 604s, or the 64 holes, are equivalent under the symmetry group of the 604. The 64 holes share one inner-product profile, which is consistent with one orbit but does not prove it.
- The exchange stage's automatic success gate, 0.5 + 1e-9, would usually miss a real exchange solution: 4 of 144 hits on the known-answer instance. This does not affect this run, because its exchange best was ≥ 0.578. A future run reusing the code could still miss a real success unless someone reads `new_best` values near 0.5 by hand.
- `relax.py` has no exact export inside its loop. A numerically tight 605 would only appear as `best_max_dot_605` ≈ 0.5, and scale-and-round would then fail on its tight contacts (check 3).
- The gradient self-test in `relax.py` (lines 66-75) samples 20 of 6,655 coordinates. Most of those have zero gradient at the test state, so it is weak evidence, but my reruns with the same loss behave correctly (perturbed 604 → 0.5).
- The memory cap was very likely exceeded by the aborted run (correction 4). This is a process issue, not a result issue.

## Follow-ups

What a stronger re-run should do differently:

1. **Calibrate on a known instance first.** Puncture the 604 and require each stage to restore it. Lower the exchange success gate, or polish with the epigraph SLSQP or an LP before gating.
2. **Diversify holes.** All retained holes were one type, with 51 blockers. Rank candidate directions by blocker count. Then remove the whole blocker set (m about 51) or a cap or hemisphere and re-optimise m + 1 points, instead of k ≤ 6.
3. **Free the backbone in the MILP.** Solve the independent set over the 496 backbone vectors plus the pool, not over extensions of a fixed backbone. Use clique constraints or a dedicated independent-set solver rather than edge constraints.
4. **Complete the pools.** Add the 1,536 (3,3,3,2,2,1) integer directions, and enumerate mixed p + q√2 coordinates systematically.
5. **Use the symmetry group of the 604** to orbit-reduce holes and MILPs.
6. **Spend the budget on diversity, not restarts.** Every relaxation profile plateaued within minutes. Use different starting structures (other published 11-dimensional constructions, laminated or code-based configurations), not baseline plus one point.
7. **Add an exact reconstruction step to the relaxation loop**: snap to the Z[√2]/6 alphabet, or a PSLQ/LLL fit, before rounding.
8. **Record each process's peak memory** (`/usr/bin/time -l`) and its true exit status.

For the lead: send corrections 1-4 (and ideally 5-7) back to the author with `swarm_continue`. The search itself does not need rerunning.
