Outcome: OVERSTATED. The exchange search passes positive controls and its constraints are correct on inspection and independent reruns. The recorded failure to find an improvement is credible. Several numerical summaries and conclusions need correction before filing; the required replacements are quoted under Done 5. I found no valid cap larger than 512. This audit is an opinion backed by reruns, not a verdict of the repo checker.

## Done

All commands ran from `/Users/agrim/.terramind/worktrees/frontier/defeated-canopy`. References below use these prefixes:

- `P` = `attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/` in this checkout.
- `A` = `/Users/agrim/.terramind/worktrees/frontier/grotesque-beach/.terramind/scratch/capset8/`, read only throughout.
- `Q` = `.terramind/scratch/audit-capset8/` in this checkout. Rerun scripts and complete output remain there.

Read the binding design, including decisions 9 and 10, and the author's handoff. Ran `bun install`; made an independent Python 3.12 venv with `uv venv --python 3.12 Q/venv` and `uv pip install --python Q/venv/bin/python ortools numpy`. Installed OR-Tools 9.15.6755 and NumPy 2.5.5. Numerical reruns used one solver worker and one BLAS thread per process. No attempt or problem file was edited, no review or submission was run, and every audit process has exited.

### 1. Baseline, second cap, completeness and encoding

`bun frontier show witness.cap-set-f3-8` reports target greater than 512, dimension 8, and verifier `capset`. Ran `bun frontier diagnose <file> --problem witness.cap-set-f3-8` separately on `A/baseline.json`, `A/runs/B/variant1_512.json`, `A/runs/B/product0_400.json`, and `A/runs/B/variant2_448.json`. Outputs: respectively valid at 512, 512, 400 and 448; the two 512s tie, and the smaller caps do not reach the best known value.

Ran `Q/venv/bin/python Q/audit.py > Q/audit.out`. Its independent counter enumerates unordered pairs in coordinate arrays and accumulates `-(a+b) mod 3`; it does not call `capcore.block_counts`. Both 512s are complete and give exactly this full outside-point blocking distribution (`Q/audit.out:1,3`):

```text
4:16, 8:16, 10:64, 11:192, 12:32, 13:384, 14:192, 15:128,
17:192, 18:672, 19:128, 20:256, 21:512, 22:384, 23:1152,
24:512, 25:256, 26:256, 28:192, 30:128, 32:256, 40:16,
44:32, 48:56, 56:16, 80:8, 256:1
```

These counts cover all 6,049 outside points. The origin is outside, the cap is closed under negation, and the two caps share 384 points (`Q/audit.out:7`). For the 400-cap the distribution is exactly `{3:2400, 10:40, 18:3600, 60:120, 200:1}` (`Q/audit.out:5`). The saved 448-cap is also complete, but has 448 outside points blocked only once (`Q/audit.out:6`).

Read `P/search/capcore.py:5-58` and `src/check/witness/capset.ts:25-62`. Both encode the first coordinate as the most significant trit, and both compute the same coordinatewise third point. An independent check of 100,000 random table entries and all 6,561 diagonal entries passed (`Q/audit.out:8`); int16 safely represents indices through 6,560.

### 2. The exchange step can find gains; no search-invalidating bug found

Read `P/search/lns.py` line by line. `freed` at lines 45-52 excludes exactly the kept points and points blocked by a kept pair. For distinct kept points, `inK[T[K]].any(axis=0)` is the blocking condition; diagonal terms only concern kept points already excluded. There is no omission of addable outside points. Independent coordinate-pair enumeration agreed with the author's freed sets for removals of 0, 5, 40, 150 and 300 points from each of the baseline, product and saved 448-cap (`Q/audit.out:9-23`).

The model at `lns.py:55-86` has the necessary pair clauses when the third point is kept, every triple clause within F exactly once, and objective max cardinality. A line involving two kept points was already excluded by `freed`. Hints at lines 75-77 do not constrain variables. FEASIBLE is accepted as an incumbent at lines 83-86, but only OPTIMAL updates the proven-removal maximum at lines 176-179; nonoptimal incumbents are separately counted. The implementation does not silently label FEASIBLE as OPTIMAL.

The positive controls execute the author's extracted, unchanged `freed` and `solve` functions; extraction avoids the script's top-level search loop:

- Deleted five baseline points, then removed 0, 8 or 40 additional points from the remaining 507. All three tests returned the exact original 512-cap, net gain 5, status OPTIMAL, with F sizes 5, 13 and 45 (`Q/audit.out:24-26`). `diagnose` on `Q/recovered0_512.json`, `Q/recovered8_512.json` and `Q/recovered40_512.json` reports valid 512, ties.
- Parameterised only the in-memory dimension/table globals. From a greedy six-point cap in dimension 3, removal of all points returned 9, gain 3, OPTIMAL. From a greedy 16-point cap in dimension 4, removal of all points returned 20, gain 4, FEASIBLE within 30 seconds (`Q/audit.out:27-28`). The latter demonstrates a gain, not a solver certificate of maximality.
- Added the third point of a baseline pair to make a broken 513-point object. `diagnose Q/broken513.json` reports `valid: no`, 19 collinear triples, including points 0, 1 and 512. Thus the repo verifier accepts the record object and rejects a broken copy.

I also built a separate exchange model using coordinate-pair enumeration and independent freed sets. Five tests per starting cap used low-count targeting, random removals of 150 or 250, and a removal-150 model forbidding restoration of all of R. For the 400-cap: two targeted models proved zero gain; the three larger tests remained FEASIBLE, with gains 0, 0 and -1 under the exclusion constraint. For the 448-cap: targeted models proved zero gain and found different equal-size caps; larger tests returned zero-gain FEASIBLE incumbents. For the baseline: targeted/random tests proved zero gain, and the exclusion test proved a loss of one for that particular F (`Q/audit.out:29-43`). No larger cap was found. These short tests support plausibility, not a broad impossibility claim about 400 or 448.

Ran `Q/venv/bin/python Q/plateau.py` to test whether hint restoration indicates rigidity. Set R to baseline minus the second cap, so |R|=128, |F|=256 and the kept intersection has size 384. The original model returned the baseline. Adding just `sum(x[pos[r]] for r in R) <= 127` made the same model return the distinct second 512-cap. Both returned FEASIBLE within the 20-second solve limits (`Q/plateau.out:1-2`). `diagnose Q/plateau_excludeTrue_512.json` reports valid 512, ties. An equal-size move exists nearby; the original hint does not help discover it.

### 3. The searches ran; counts and evidence limits

Ran `Q/venv/bin/python Q/logaudit.py > Q/logaudit.out`, parsing the original log literals rather than trusting the table. The six rows reproduce the writeup's step/solve snapshots:

- A1: last logged step 93; 93 successful solves, 9 nonoptimal, 84 proven. Source `A/runs/A1/lns_11.log:9`. No final `done` record; these are lower bounds at interruption.
- A: 7,395 steps; 6,265 successful solves, 91 nonoptimal, 6,174 proven; 1,130 FMAX skips. Source `A/runs/A/lns_12.log:82`.
- B1: last logged step 309; 260 successful solves, 3 nonoptimal, 257 proven; 49 FMAX skips. Source `A/runs/B1_baseline_partial/lns_41.log:4`. Again an interrupted snapshot.
- B_variant: 1,246 steps; 1,064 successful solves, 18 nonoptimal, 1,046 proven; 182 skips. Source `A/runs/B_variant/lns_21.log:17`.
- B_product: 177 steps; 120 successful solves, 21 nonoptimal, 99 proven; 57 skips. Source `A/runs/B_product/lns_31.log:13`.
- B_baseline: 1,167 steps; 987 successful solves, 22 nonoptimal, 965 proven; 180 skips. Source `A/runs/B_baseline/lns_41.log:25`.

Totals at those snapshots: 8,789 successful solves, 164 not proven optimal, 8,625 proven optimal; 1,598 logged FMAX skips after the cap was introduced. By kind: targeted 1,550, random 4,118, subspace 1,537, hyperplanes 1,584. All improvement and accepted-plateau counters remain zero. Among these, 7,605 solves started at the original baseline, 1,064 at its affine copy, and 120 at the product. The optimum-certified largest removals in the writeup match the log dictionaries; 332 is the maximum certified removal, not the maximum attempted removal. A1 contains a FEASIBLE solve at R=419, F=3,874 (`A/runs/A1/lns_11.log:4`).

File birth times agree with the starts inferred from last elapsed times. A1 starts about 15:55:02 UTC; A starts 16:04:56 and ends 17:49:11; B_variant starts 16:32:34 and ends 16:52:36; B_product ends 17:08:19; B_baseline ends 17:46:37 (`Q/logaudit.out:6,12,24,30,36`). The envelope is about 114m09s, consistent with 21:25-23:19 IST and the 120-minute budget. The four completed runs have `done` records. The interrupted runs do not preserve exit statuses or final counters, so the claimed kill action and exact exit codes cannot be independently recovered.

The logs contain 146 sampled per-neighbourhood rows, not 8,789 detailed rows. Their R buckets are 0-39:4, 40-99:2, 100-199:11, 200-299:22, 300-399:104, 400-999:3. Their F buckets are 0-39:4, 40-99:2, 300-399:1, 400-999:46, 1000-1400:85, greater than 1400:8. Full sampled-value histograms are in `Q/logaudit.out` and `Q/logsummary.json`; these are time-biased samples, often of the expensive models. Actual full |R|/|F| distributions and duplicate-neighbourhood rates cannot be reconstructed because `lns.py:192-195` logs only about once a minute and never records R or F contents. The larger rows prove substantive models were attempted. They do not prove all neighbourhoods were distinct or quantify the fraction of trivial F=R solves.

`diff -q` reports identical current scratch and attempt copies of capcore.py, lns.py and greedy.py. The interrupted A1 logs predate the FMAX addition, so identical current copies do not establish preservation of every historical version.

### 4. Priority claims, affine equivalence and the lost run

Ran `Q/venv/bin/python Q/priority.py > Q/priority.out`, executing the published functions extracted from `greedy.py`, then 3,000 fixed-count perturbations and 3,000 family variants. The exposed BASE priority agrees with the downloaded FunSearch notebook's published function at all 6,561 inputs and constructs exactly the baseline (`Q/priority.out:1`). Five trials at each noise level give 512 for 1e-9, 0.001 and 0.01; at 0.1 the sizes are 330,336,313,330,312, and at 0.5 they are 279,279,287,283,288 (`Q/priority.out:2-6`).

The 3,000 perturbations give 568 occurrences of 512, 79 of 448, and smaller caps down to 256; there are two distinct 512s. The 3,000 family variants top out at 448 and reach down to 256 (`Q/priority.out:7-9`). This matches the reported high-end behaviour, but disproves interpreting 425 as the bottom of the tail. The original histogram is explicitly truncated to the 15 largest size bins at `P/search/greedy.py:142`.

Ran `Q/venv/bin/python Q/affine.py > Q/affine.out`. Exact set equality verifies this linear map from baseline to the second cap: `(x1,x2,x3,x4,x5,x6,x7,x8) -> (x1,x2,x3,x4,x5,-x6,x7,x8)` over F3. No translation is needed. Independent spectra of all 9,840 affine hyperplanes, including parallel-class intersection triples, also match (`Q/audit.out:2,4`). This settles the affine-image question.

The initial run was not entirely lost. `A/search_B1.out:11110` says `after 60552 parameter variants`, with top sizes 512,512,452,448; line 11111 says `after 118959 family variants`. Line 11119 records `FileNotFoundError: ... 'runs/baseline.json'`. The current code loads that baseline before saving ranked caps (`greedy.py:135-138`), so the missing results are coordinates and later products, while counts and top sizes survived in stdout. The rerun log has 14,107 parameter variants and 32,899 family variants (`A/runs/B/greedy_8.log:2675-2676`). The total 226,517 = 60,552 + 118,959 + 14,107 + 32,899 is supported. It includes the initial run's surviving size summaries, appropriately usable as observations but not as saved witnesses.

The small-dimension and product sizes 4,9,20,39,79 and 316,351,400 are explicitly logged at `A/runs/B/greedy_8.log:2682-2689`. They are incumbent sizes; bounds for dimensions 4,5,6 are 80,240,727, not certificates of optimality. The writeup does not claim those solver bounds are optimal sizes.

### 5. Required textual corrections and disclosure

The title's "2 h" can describe the allocated budget; actual runtime should remain explicitly about 114 minutes. The claim's no-improvement outcome, complete-cap assertion and priority-count order of magnitude are supported. The following statements need replacement:

- `P/attempt.yaml:6`, "about 8,700 exact CP-SAT re-solves after removing up to 332 of its points ... all gave net gain 0", and `P/writeup.md:106-107`, "net gain 0 in about 8,700 exact solves". Replace with: "The logged snapshots total 8,789 successful solves across the baseline, its affine copy and the 400-cap. Of these, 8,625 proved optimal and 164 returned only feasible incumbents; none recorded an improvement. The largest removal certified optimal was 332." The baseline alone accounts for 7,605, not the full total. Interrupted-run counts are lower bounds. Evidence: Done 3's original final/snapshot lines.
- `P/writeup.md:36-39`, "solves max |S| ... exactly", requires "models max |S| exactly, then runs time-limited CP-SAT; only OPTIMAL certifies the neighbourhood optimum." Evidence: `lns.py:79-86,176-179` and the 164 nonoptimal results.
- `P/writeup.md:62-67`, "on every solve CP-SAT returned exactly S = R" and "the optimum was always exactly the removed set". Replace with: "No gain or accepted plateau move was logged. Certified solves established the original cardinality as optimal; uniqueness was not tested, and returned-set identity was not logged." For PLATEAU=0.5, zero accepted moves does not establish zero proposed moves (`lns.py:188`). For PLATEAU=1 runs it does establish no different equal-size incumbent was accepted at logged checkpoints. `Q/plateau.out:2` demonstrates a valid equal-size alternative when the original set is excluded.
- `P/writeup.md:65-66`, "removing all cap points of an affine hyperplane (108 to 208 points) freed only 10 to 18 outside points". This is false as a general summary. Replace with: "Freed-set sizes vary substantially by hyperplane. For x1=0, R=192 and F=600, freeing 408 outside points; for x4=0, R=160 and F=160, freeing none." Independent command `Q/venv/bin/python Q/hyperplanes.py` prints these at `Q/hyperplanes.out:1,10`. Even the original `A/runs/A/lns_12.log:49` records R=160, F=429, freeing 269. Spectra also show sections of size 96 and 104 (`Q/audit.out:2`); the 108 lower endpoint is not a universal minimum. The adjacent "200 random ... 5 to 9" and "300 ... about 170" are unsupported as distributions of the original run because complete per-solve sizes are absent. Rephrase as specific sampled observations with seeds, or delete. My independent random-300 test did free 170 (`Q/audit.out:13`), which supports an example only.
- `P/writeup.md:75-76`, "noise of 10% or more: at most 336". Replace with: "Five sampled trials at each tested noise scale, 0.1 and 0.5 times max absolute priority, reached at most 336 in the seed-8 rerun." This is a sampled observation, not a bound for all larger noise scales; see `greedy.py:103-107` and `Q/priority.out:5-6`.
- `P/writeup.md:77-79`, "whose results were lost to a path bug after the run". Replace with: "whose candidate coordinates were not saved because the baseline lookup failed; stdout preserves variant counts and top sizes." Evidence: `A/search_B1.out:11110-11119`.
- `P/writeup.md:83`, "a tail down to 425". Replace with: "The printed histogram shows only the 15 largest size bins, ending at 425; smaller sizes were omitted." Evidence: `greedy.py:142`, original log line 2681 and `Q/priority.out:7-9`.
- `P/writeup.md:84-85`, "very probably an affine image of it (not checked)". Update with the checked sixth-coordinate negation map from Done 4. The earlier speculation was labelled honestly, but the question is now settled.
- `P/writeup.md:99-102`, "strict local optimum under every neighbourhood tried", "Local search near it is the wrong tool", and "Starting points other than the FunSearch construction ... came out at 448 or less, and the exchange search could not grow them either." Replace with: "These sampled, time-limited exchanges found no improvement. This does not establish strict local optimality or rule out other local-search strategies. A priority variant produced an affine copy at 512. Exchange search was run from that copy and the 400-cap; the saved 448-caps were not exchange-searched in this attempt." Evidence: six run starting sizes in Done 3, `run_b.sh:7-10`, and the explicit plateau reproduction. No original run starts at 448.
- `P/writeup.md:104-110`, "Do not repeat", especially "Random perturbation ... gives 512 or at most 452". Replace the heading with "Observed limits of these runs" and say "The sampled perturbations reached at most 512, with 452 the largest logged smaller result." The experiment supports reporting its outcome, not discouraging every variation of the method.

Wording checks: `rg -n '\bsolved\b|improv|machine' P/writeup.md` finds no forbidden result claim; `writeup.md:3-5` and `attempt.yaml:6` explicitly say this writeup is not machine-checked. Ties are described as ties. `bun frontier check P` returns `unchecked: Writeups are not machine-checked.` Declarations remain `rights: false`, `disclosure_complete: false` at `attempt.yaml:34-35`.

The author and planner models and OR-Tools CP-SAT are disclosed (`attempt.yaml:20-29`), matching the supplied task/design. Python/NumPy also perform the custom greedy search (`greedy.py:10-14,29-86,108-142`), but are absent from the tool list. Add the custom Python/NumPy search as a tool before declaring disclosure complete. The author's handoff says python-sat was installed but unused; I found no import or call to it in the recorded search sources, so there is no demonstrated need to disclose it as a used solver. Model invocations themselves are not in numerical logs, so complete model/people provenance cannot be independently established from these files alone.

### 6. Stronger rerun and repository verification

The concrete missing experiment is deliberate plateau discovery. The existing second cap gives a tested 128-removal neighbourhood with a different size-512 completion. Use solution exclusion or a secondary diversity objective, and distinguish failure to improve from failure to explore equal-size alternatives. The saved 448-caps were not searched despite their one-blocker outside points; the independent tests already find valid equal-size moves there (`Q/audit.out:34-38`). Literature starting caps, region-plus-boundary removal, symmetry-orbit models and a real evolutionary program search are also absent from the retained sources (`writeup.md:112-121`; `run_b.sh:6-11`).

Ran the repository's full `bun run check` once in a visible terminal, saving `Q/repo-check.out`. TypeScript passed; tests report 426 pass, 1 skip, 0 fail across 34 files. The actionlint test is skipped. Validation then rejects the cap-set and sorting-network attempts' intentionally false declarations, so overall exit is 1 (`Q/repo-check.out:499-509`). These protected declarations were left unchanged. Lean checks were not needed because neither Lean nor the proof checker changed.

## Deviations

- Full per-solve |R|/|F| distributions, returned-set identities, duplicate-neighbourhood rates, historical source versions and interrupted-run exit statuses could not be recovered: the original logs do not contain them. Done 3 reports only what survives.
- The dimension-4 positive control finds 20 with FEASIBLE, not a solver proof of optimality. The initial audit assertion incorrectly required OPTIMAL; I corrected that test requirement and reran the entire audit script successfully. The original search code was untouched.
- Reran exact extracted priority functions with fixed trial counts rather than replaying both complete time-based priority schedules. This tests the same builder and distributions while leaving budget for the other checks. Did not rerun the historical 4.8/6-minute dimension-5/6 searches; surviving logs record their counts and the saved products validate.
- The brief requires `audit-capset8.md` and the generic handoff requires `audit-the-cap-set-attempt-inck0.md`. Both contain this identical report; no other tracked files change.

## Concerns

The surviving logs support a genuine failed search, but cannot establish every asserted solver-return identity or an exhaustive neighbourhood census. The initial 452-cap's coordinates were never saved, so its validity cannot be independently diagnosed; only the logged size and correctness of the builder support it (`A/search_B1.out:11110-11119`, `greedy.py:29-44`). My larger independent exchanges also ended with loose bounds; they say nothing decisive about possible improvements from those starting points. No valid cap above 512 was found.

## Follow-ups

Return the writeup to its author for the explicit corrections in Done 5 before showing it for submission. A further search should save one row per solve with hashes and sizes of R/F/S, solver status, incumbent, upper bound, wall time, and an explicit `S == R` flag; save complete histograms and every best witness before optional baseline comparisons. Add the punctured-cap positive controls and a known plateau control before a long run. For the next substantive search, test exclusion/diversity-guided plateau walks, the saved 448-caps, region-plus-boundary neighbourhoods, and the literature 45/112 starting caps. Treat the observed failure as evidence about these runs, not a prohibition on local search.
