Outcome: OVERSTATED. The stated numbers are true: best cap 512 (a tie), the symmetric-model results, SAT UNKNOWN, the products and the timings. But the round-2 headline, a plateau walk, did not happen. The 512 walk never moved off the FunSearch cap. Its only equal-size alternatives were two coordinate negations planted by its own control move. All four "research" 512-caps are linear images of the FunSearch cap. Also, the walk's 35-second CP-SAT maximisation missed known equal-size refills that a SAT query finds in 1 to 3 seconds. I found no bug that voids a stated result, and no cap above 512. This audit is an opinion backed by reruns, not a verdict of the repo checker.

## Done

References: `P` = `attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40/`; `A` = the author's scratch, `.terramind/scratch/capset8-r2/` in worktree `tame-aurora` (read only); `Q` = `.terramind/scratch/audit-capset8-r2/` in this worktree (my scripts and outputs). I made a fresh Python 3.12 venv in `Q` with NumPy 2.5.5, OR-Tools 9.15.6755, python-sat and pynauty. pynauty was needed only to import the author's module. My own equivalence and stabilizer code (`Q/capaudit.py`) does not use it. Every audit process has exited. Peak use was 2 cores.

### Check 1 (standard): baseline
- `A/baseline.json` equals, as a set, the 512 rows of the downloaded FunSearch file `A/download-baseline/n8_size512.txt` (`Q/partA.out`, line "baseline == funsearch file as set: True").
- My own checker (`Q/capaudit.py`, which enumerates pairs and third points; nothing from `search.py`) says it is a cap. Its outside blocking histogram matches round 1's exactly, minimum 4: `{4:16, 8:16, …, 80:8, 256:1}`.
- `bun frontier diagnose A/baseline.json --problem witness.cap-set-f3-8`: `value: 512 (best known 512…) valid: yes result: ties the best known value`. `A/broken.json`: `value: 513 … valid: no violations (14)` (`Q/diagnose.out`).

### Problem check 1: did the walk leave the FunSearch cap's class?
Coordinates are numbered 0 to 7 throughout, as in the code.
- **What "signed-coordinate class" means.** `P/search/search.py:36-49` builds a coloured graph: 512 point vertices, then for each coordinate one coordinate vertex and three value vertices. Value 0 has its own colour; values 1 and 2 share a colour. Its automorphisms are coordinate permutations combined with independent negations x_d → −x_d. That is the hyperoctahedral group (order 8!·2^8), all linear maps fixing 0. Translations and general GL(8,3) elements are **not** included. It is a subgroup of AGL(8,3), so one signed class implies one affine class. The converse fails: a translate of the cap would get a new certificate.
- **The walk never moved.** `search.py:266-268` replaces the current cap only on a gain or a new canonical certificate. Recount from `A/plateau.jsonl`: all 223 exchange rows have the same `start_hash` (`1f7146…`, the baseline). So every call was a neighbourhood of the FunSearch cap itself.
- **Where the alternatives came from.** I replayed the walk's RNG (`Q/replay_plateau.py`, using the plateau's own source snapshot `A/plateau.search-source.py`). All 244 calls match the log in mode, |R| and the SHA-256 of R (`Q/replay.out`: "matching log 244 mismatch 0").
  - The two non-baseline labelled 512-caps (`1c4b2e…`, `30b34a…`) were returned by **coordinate-flip** calls 7 (coordinate 2) and 43 (coordinate 3).
  - That mode builds R as the baseline minus its own image under one coordinate negation (`search.py:237-240`). The code comment calls it "a control, not a new symmetry class".
  - Random and targeted removals produced no different 512-cap at all.
- **All are images of the FunSearch cap.** My own backtracking search (`Q/capaudit.py:find_signed_perm`) finds explicit maps from the baseline:
  - `1c4b2e…` is negation of coordinate 6. The same set comes from negating coordinate 2.
  - `30b34a…` is negation of coordinate 5 (equivalently 3).
  - `exact_8_all_512.json` (the "fourth") is x2 moved to position 6, x6 moved to position 2 and negated, and x5 and x7 negated. It is disjoint from the baseline, but still a linear image.
  - `exact_8_half_512.json`, `exact_8_few_512.json`, `restored512.json` and `best-smaller-512.json` (the other448 regrowth) are **identical** to the baseline.

  All have the same blocking histogram and the same spectrum over all 9,840 affine hyperplanes (3,280 parallel classes; sizes 96…208 as in `Q/partA.out`). So the walk moved between copies of one cap and explored no new 512-cap.
- **What the writeup says.** It reports "1 signed-coordinate class" but calls the three caps "Research walks retained" (`P/writeup.md:15`). It says "General affine equivalence was not computed" (`:20`) and "does not settle affine equivalence" (`:187`). That equivalence follows directly from the signed class. Nowhere does it say that the walk stayed on its start, or that both alternatives came from the planted reflection move. Corrections are below.

### Problem check 2: solution exclusion and solver power
- **The encoding is correct at the set level.** `search.py:66` adds `sum(x[R]) <= |R|-1`, which forbids any refill containing all of R. For a complete cap the only such equal-size refill is R itself. The no-good at `:68-71` applies the same idea to retained labelled caps.
- **Calibration control reproduced.** I re-ran `sp.exchange(a, a − flip5(a), 45, seed, exclude=True)` with the author's engine for seeds 102, 1 and 2. Each returned FEASIBLE 512, a different set, equal to the coordinate-5 image. Without exclusion, the same neighbourhood with a 20-second limit restores the original. This was an inline command against a copy of the plateau source in `Q/replay/`; its output is quoted here.
- **Outcome counts for the plateau walk** (`A/plateau.jsonl`, recounted):
  - 2 calls returned a different 512-cap (both planted reflections, FEASIBLE);
  - 0 returned the original;
  - 211 returned smaller caps: random 100 (OPTIMAL 511: 78; FEASIBLE 511: 22), targeted 81 (OPTIMAL 503/505/509 with a forced low-blocker point), flip 30 (FEASIBLE 511);
  - 9 INFEASIBLE (empty removals, coordinates 0 and 4 are in the stabilizer);
  - 1 UNKNOWN;
  - 21 skipped above 2,200 candidates.

  Neighbourhoods: 186 distinct of 223. Of the 78 OPTIMAL random calls, 37 freed at most 10 points beyond R, so they were nearly trivial.
- **Power failure inside the run.** The baseline has three distinct single-negation images (`Q/partA.out`: negating coordinate 1 or 7, 2 or 6, or 3 or 5 gives three distinct images; negating 0 or 4 fixes the cap). The coordinate-1/7 image `39bd27…` was never found and never made tabu. So in 9 calls (1, 37, 73, 91, 109, 121, 151, 169, 235) a valid different 512 refill was available, and every one returned FEASIBLE 511 at the 35-second limit (`Q/partB.out`).
  - Rerunning call 1 with the author's engine: 35 s gives FEASIBLE 511 again; 120 s finds the planted 512.
  - Call 37 still gives 511 after 120 s.
  - My independent model (`Q/own_exchange.py`, own freed set and clauses) posed as a Glucose4 decision ("at least |R|, not all of R") returns SAT with a valid 512 image in 1.3 s and 2.5 s. My CP-SAT maximisation on 2 workers needs the full 120 s.

  Conclusion: the 35-second maximisation (LP bound ~670 against 512) cannot reliably find equal-size moves when F ≥ ~336. All 52 FEASIBLE-511 results carry no information about whether a different 512 exists. This is a power limit, not a bug: the writeup never claims those neighbourhoods have no alternative ("remain uncharacterized", `:121`). It does make the walk's "no new class" outcome weak evidence.
- **Re-solves of the walk's random neighbourhoods** (`Q/partC.out`, Glucose4 decision, 40 s each, tabu as at that call):
  - all 23 FEASIBLE/UNKNOWN ones (F 622 to 2,027) came back UNKNOWN, so no missed different 512-cap was found and none was ruled out;
  - of 8 sampled OPTIMAL-511 ones, 6 are UNSAT (agreeing) and 2 are UNKNOWN at 40 s (F 605 and 622). There was no disagreement.

### Problem check 3: symmetric models
- **Group.** My own backtracking (`Q/partA.out`) finds the baseline's stabilizer in the signed-permutation group with order **512**: 16 distinct coordinate permutations and 32 pure sign changes. Global negation is already inside it. The author's pynauty count (`A/exact-all.jsonl`, `order_mantissa 512`) agrees.
- **Orbits.** ⟨stabilizer, −I⟩ has **124 orbits** on F_3^8. Sizes: 1×1, 2×2, 4×7, 8×14, 16×21, 32×30, 64×28, 128×16, 256×5. The baseline is a union of orbits.
- **My own model** (`Q/partD.py`) maps all 7,173,360 lines to orbit triples: 23,678 distinct, the author's constraint count exactly. CP-SAT with no hint: **OPTIMAL 512, bound 512**, in 0.36 s. A separate feasibility model for weight ≥ 513 is **INFEASIBLE** (0.27 s). Enumerating every orbit-union of weight ≥ 512 gives exactly **8** solutions, all signed images of the FunSearch cap (`Q/partD.out`).
- **What the 512 bound means.** It holds only for caps invariant under the FunSearch cap's own stabilizer. "Few" (1,220 orbits) and "half" (300) are subgroups of that same stabilizer (`exact_sym.py:36-38`), so every symmetric model was biased toward the FunSearch cap's symmetry. The writeup keeps the bound restricted (`:70`) and reports the FEASIBLE bounds 3,872 and 1,392 as solver bounds.
- **Incumbents.** `diagnose` accepts `exact_8_all_512` (ties), `exact_8_few_508` (508), `exact_8_few_512` and `exact_8_half_512` (ties). But the half and few-warm 512 incumbents are byte-for-byte the hint (the baseline), under a constraint of at least 512. "The warm retry recovered 512 from the complete hint" (`:75`) means only that the hint was returned.

### Problem check 4: literature products (`Q/partE.out`, own code)
- `A/hill112.json` is a 112-point affine cap in F_3^6, closed under negation and without 0.
- Its 56 projective points have no linearly dependent triple (own rank computation over F_3), so they form a 56-cap in PG(5,3). Their weights are 40 points of weight 3 and 16 of weight 6, matching the stated construction.
- `A/hill45.json` is a 45-point affine cap in F_3^5.
- `hill-product448` is exactly hill112 × {1,2}²; `hill-product405` is exactly hill45 × {(x, y, x²+y²)}, a 9-cap. `diagnose`: 448 and 405 valid, below the record.
- `best-smaller-449.json` is a valid cap by my O(n²) check and by `diagnose` (449, valid). It shares only 115 points with the 448 product. The 448 product is complete (minimum blocking 1, `A/product-build.jsonl`), so the gain was a real exchange gain: 13 equal-size moves, then 449 at 19:39:24. The growing code works.
- A positive control that should be stated: `start448-other` shares **432 of its 448 points** with the FunSearch cap (inline command in `Q` with `capaudit.py`; start448 shares 320). Its "growth to the original 512-cap" (`:5`) is a recovery from a near-copy. The other 448 shares 320 and stayed at 448.

### Problem check 5: stages unable to succeed
- **Region stage.** `region_removal` (`search.py:91-107`) removes both endpoints of every cap pair whose third point lies in the region. A codimension-2 or -3 region contains 1/9 or 1/27 of the space, so almost every point of a 512-cap is in such a pair. With the 2,200-candidate cap (`:259`) no region model can run. All 24 were skipped in 4.4 s (`A/region.jsonl`).
- The writeup admits that none ran (`:83`), but `:82` is wrong in a detail: 23 of 24 removed 512 and freed 6,561, while one (codimension 3, coordinate-aligned) removed 464 and freed 6,012.
- It also frames the region stage as a sample ("finite logged sample", `:84`), when it was structurally unable to run.
- **Full-space SAT at 513.** It is UNKNOWN after 600 s with no symmetry breaking (`A/sat-region.jsonl`). Reported correctly. The SAT control at n=4 (20 from 12) passed.

### Check 3 (standard): did it run?
- Start and end files cover 19:07:18 to 20:51:40 (104 min 22 s). Exits are 0, except calibration 1 (dropped encoder) and other448 143 (SIGTERM, recorded in `A/interruptions.jsonl`). Peak RSS was 1.42 GB (exact-few `process_end`).
- **When the best was reached.**
  - The 512 walk: at its first state; it never moved.
  - other448: reached 512 2.4 min after its start.
  - product448: reached 449 7.7 min after its start, then nothing more in about 15 min, or in the 30-min continuation (`smaller`: 37 distinct 449-states, no gain).
  - smaller-early: 34 distinct 448-states, no gain.
- `P/search/search.py` is the final source. The plateau and other phases ran earlier versions (`A/*.search-source.py` differ in empty-removal handling, region removal and file writing). The writeup discloses this (`:131`), and the walk logic I replayed is the same.

### Check 5 (standard): required corrections (quote, then replacement)
1. `P/attempt.yaml:6` "Research walks retained three labelled 512-caps; a symmetry model adds a fourth, all in one signed-coordinate class with minimum outside blocking count four." → "The 512-cap walk never left its starting cap. Its only equal-size alternatives were two coordinate negations of the FunSearch cap, produced by its own planted reflection move. Its random and targeted removals found no other 512-cap. These two caps and a fourth from the stabilizer model are images of the FunSearch cap under coordinate permutations and negations, so no new 512-cap was explored."
2. `P/attempt.yaml:6` "A complete saved 448-cap grew to the original 512-cap" → "A complete saved 448-cap that shares 432 points with the FunSearch cap was regrown to it."
3. `P/writeup.md:15-20` "Research walks retained 3 distinct labelled 512-caps … General affine equivalence was not computed." → "The 512 walk never moved. Every one of its 223 calls started from the FunSearch cap, because it moves only to a new signed-coordinate class and found none. Its two other labelled 512-caps came from its coordinate-reflection control move. Signed coordinate permutations are linear maps, so all four retained 512-caps are affine images of the FunSearch cap. An audit confirmed identical hyperplane spectra and blocking distributions."
4. `P/writeup.md:42-45`: add the outcome counts. "Of the 213 non-empty calls, 2 returned a different 512-cap (both planted reflections), 211 returned 503 to 511, and 1 was UNKNOWN. In 9 calls a known different 512 refill (the reflection in coordinates 1 or 7) was available, and the 35-second solve returned 511 every time. FEASIBLE results therefore say nothing about whether an equal-size alternative exists."
5. `P/writeup.md:75` "The warm retry recovered 512 from the complete hint." → "The warm retry returned its hint, the baseline itself, and found nothing better."
6. `P/writeup.md:82-84` "All 24 eight-dimensional samples removed all 512 points and freed all 6,561 candidates … The 24 regions are a finite logged sample." → "23 of 24 samples removed all 512 points and freed all 6,561 candidates. One removed 464 and freed 6,012. With this boundary rule a codimension-2 or -3 region removes nearly the whole cap, so under the 2,200-candidate cap the stage could not run a single model."
7. `P/writeup.md:187` "It does not settle affine equivalence of the smaller caps." → keep, and add before it: "All retained 512-caps are affinely equivalent to the FunSearch cap."

Wording: no "solved" claim (the grep hit is "unresolved"); ties are described as ties; `:3` and the claim say the writeup is not machine-checked. No statement presents a solver bound as a result.

### Check 6 (standard): disclosure, licence, privacy
- `attempt.yaml` lists gpt-6.1-sol (author), claude-fable-5-2 (planner), CP-SAT, NumPy, pynauty, python-sat Glucose4, Python, frontier and web-search; this matches the imports in the sources. Declarations are both `false` (`:56-57`).
- `grep -rn -E "/Users/|/home/" P` finds nothing; no personal names.
- The FunSearch cap is loaded at run time and not embedded. `hill_products.py` is original code citing a survey for the construction. I found no copied third-party code.

### Check 7 (standard): not tried
See Follow-ups.

### Check 8 (standard): repo commands, verbatim
```text
$ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
(exit 0)
$ bun src/cli.ts validate "attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40"
attempts/witness.cap-set-f3-8/20261117-terramind-com-e28c40/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```
Validation fails only on the deliberately false declarations.

The repo gate `bun run check` (`Q/repo-check.out`): TypeScript passes; tests report `434 pass`, `0 fail`, `Ran 435 tests across 34 files`. Validation exits 1 only because eight swarm attempts have `declarations: not confirmed`, as expected under design decision 6. This audit changes no code.

## Deviations
- The first try of my orbit-model script included an RC2 MaxSAT cross-check that did not finish in about 13 minutes. I killed it and replaced it with a second CP-SAT formulation (feasibility of weight ≥ 513, INFEASIBLE). The second solver is the same family, so the 124-orbit optimum is confirmed by two encodings of my own, not by two solvers.
- I did not re-solve all 78 OPTIMAL-511 random neighbourhoods, only every tenth (8). I re-solved all 23 FEASIBLE/UNKNOWN ones at 40 s each, not longer.
- The walk's 128 retained smaller caps in `A/visited/` were not each re-checked by me. I checked the 512s and the 448, 449, 405 and 508 objects named in claims.
- Wall clock was about 75 minutes, over the 60-minute guide, mostly from the stuck RC2 run.

## Concerns
- No cap above 512 was found by the author or by me.
- The walk's negative result is weaker than the table suggests: its solver could not reliably find equal-size moves that exist. A real plateau walk on this cap has still not been run.
- The 22 large random neighbourhoods (F ≈ 2,000) remain open. Neither the author's 35-second CP-SAT nor my 40-second Glucose run decided them.
- Every symmetric model used subgroups of the FunSearch cap's own stabilizer. Their outcome (the FunSearch cap is optimal among caps with its symmetry) is close to circular and says nothing about caps with other symmetry.

## Follow-ups
This names a new idea; method, not time, is the lever:
1. Find equal-size moves with a SAT decision query (at least |R|, not all of R), not with a 35-second maximisation. On F = 336 it finds known alternatives in 1 to 3 s where CP-SAT fails at 35 s.
2. Exclude the whole known class, not single labelled images. Add no-goods for all 2^8·8! signed images present in a neighbourhood, or require a changed affine invariant: the hyperplane-intersection spectrum (cheap: 3,280 forms).
3. Let the walk move to equal-size caps even within one class only when the invariant changes; track classes by an affine invariant, because the signed certificate is blind to translations.
4. Use symmetric models under groups that are not subgroups of the FunSearch stabilizer: stabilizers of the 448 product (hill112 × 4-cap), translation subgroups, or cyclic groups from known cap constructions. That tests other symmetric 512+ families.
5. Replace the region rule: keep only pairs with both endpoints inside the region, or cap the boundary at a random fraction, so F stays under the model limit.
6. Full-space SAT at 513 needs symmetry breaking (for example lex-leader on a few coordinate swaps) or cube-and-conquer. More time alone on the plain encoding is unlikely to help.

Whether a round 3 is worth it is the lead's call. If one runs, items 1 to 3 are cheap to add to the existing `search.py`.
