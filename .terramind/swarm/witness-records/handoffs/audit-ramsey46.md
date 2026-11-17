Outcome: OVERSTATED. The search is valid and every exact result I re-derived holds. All 7,176 fixed cores are UNSAT under my own encoder and a different solver. The four DRUP traces verify with drat-trim. The one-vertex star minimum is 20 (14 colour-0 K4 + 6 colour-1 K6). The C36 and C37 circulant minima are 72 and 111. I found no bug that voids a stated result and no colouring on 36 vertices. Three things need correcting. (a) The one-vertex non-extension of the known 35-vertex colourings is prior art, published on arXiv in November 2024, and the writeup does not cite it. (b) The "12 violations at 36" is printed without the attempt's own calibration. That calibration shows the annealer that found 12 failed to repair any of 37 deliberately damaged valid 35-vertex colourings, so 12 says nothing about closeness. (c) The handoff calls the attempt's own DRUP checker "independent". No public colouring on 36 vertices exists: R(4,6) >= 36 is still the best published lower bound. This audit is an opinion backed by reruns, not a verdict of the repo checker.

## Done

References: `P` = `attempts/witness.ramsey-4-6/20261117-terramind-com-41765d/`; `A` = the author's scratch, `.terramind/scratch/ramsey46/` in worktree `dead-butte` (read only); `Q` = `.terramind/scratch/audit-ramsey46/` in this worktree (my scripts and outputs). Fresh Python 3.12 venv in `Q` with python-sat 1.9.dev22 and networkx 3.7. drat-trim was compiled from its GitHub source (MIT licence) with Apple clang 21. I downloaded every input myself into its own directory. Every audit process has exited. Peak use was 2 cores; the full re-derivation took about 10 minutes of wall time on 2 cores.

### P8 / standard check 5: prior art (at the top because it changes the wording)
- Radziszowski, *Small Ramsey Numbers*, DS1 revision #18, 24 April 2026 (https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1, PDF fetched 18 Nov 2026). Table Ia gives R(4,6) as 36 to 41. Table Ib gives 40 as the upper bound and calls it "better but unpublished upper bounds (2024)". The lower bound is still 36, from Exoo 2012.
- Exoo's page (https://cs.indstate.edu/ge/RAMSEY/, fetched 18 Nov 2026) still lists `r4.6.35`. McKay's page (https://users.cecs.anu.edu.au/~bdm/data/ramsey.html) says "37 Ramsey(4,6,35)-graphs … There could be more, and there might even be some with 36-40 vertices."
- Web and arXiv search up to today found no colouring on 36 vertices and no claim R(4,6) >= 37.
- **Prior art the writeup omits:** A. M. Lehavi, "Ramsey Number Counterexample Checking and One Vertex Extension Linearly Bound by s and t", arXiv:2411.04267 (v1 6 Nov 2024, v4 26 Nov 2024). Its abstract says it verifies "R(4,6,36) … [is] empty given current sets R(4,6,35)". So the result at `P/writeup.md:52`, that no known 35-vertex colouring extends by one vertex, was already published. The fixed-core results with 2 to 4 new vertices on one colouring are not covered by that abstract.

### P1 / check 1: baseline
- `Q/dl-exoo/r4.6.35` has SHA-256 `37606d8d…d321`, identical to the author's input and to the hash in the writeup. `Q/dl-mckay/r46_35some.g6` has SHA-256 `89a39d9c…3fc3`, also identical. It has 37 lines.
- My brute-force counter in `Q/src/controls.py` finds 0 colour-0 K4 and 0 colour-1 K6 in the baseline. `bun frontier diagnose` on the author's restore control gives `value: 35 … valid: yes … ties the best known value`.
- **Is it the record object?** It is the file the catalogue cites as best known (Exoo's page, `r4.6.35`). It is **not** the colouring printed in Exoo's 2012 paper: the paper's Table 1 colouring has an automorphism group of order 4 with one fixed point (paper p. 2), while I count `Aut(r4.6.35) order 2` (networkx VF2, every automorphism enumerated). This agrees with the writeup.
- **How many are public?** 37 non-isomorphic colourings (McKay's collection; Exoo's `R46/` page lists the same 37). `Q/src/iso.py` shows `r4.6.35` is colour-preserving isomorphic to entry 35 (0-based) of McKay's file, and to no other entry. The fixed-core results therefore cover 1 of the 37 known colourings. `P/writeup.md:146` ("this particular 35") says so correctly. The claim in `attempt.yaml` says "of the downloaded 35-vertex colouring", which is accurate but does not say it is one of 37 (correction 1).

### P2 / checks 2 and 4: the 7,176 UNSAT results
- **What is fixed and what is free.** I read `P/search/search.py:63-77` (`extension`) line by line. The kept core is relabelled 0..m-1, and all C(m,2) core edges are fixed at their original colours. Every edge touching a new vertex m..35 is a free variable, including the edges among the new vertices. Variable counts are 35, 69, 102 and 134, matching C(36,2) − C(m,2). For each colour, each clique size and each j = 1..min(added, size), every (size−j)-clique of that colour in the core is combined with every j-subset of new vertices. One clause forces some free edge in it to the opposite colour: positive literals (colour 1) for colour-0 K4, negative literals for colour-1 K6. The colours are the right way round (literal +x means colour 1, as in the verifier `src/check/witness/ramsey.ts`). Monochromatic cliques entirely inside the core are asserted absent. The encoding is complete: a 36-vertex colouring containing the kept core as an induced sub-colouring exists iff the CNF is SAT.
- **Recount from logs.** Python over `A/all-extensions.log` and `A/results/delete-three.log` counted 1 / 35 / 595 / 6,545 UNSAT, 7,176 distinct case names, 0 UNKNOWN and 0 SAT (apart from the `recover35` control). Status comes from the solver's return value (`True/False/None` mapped at `search.py:99`), not from text. The largest conflict count was 1,204, well under the 30,000 cap, so no case was a timeout. The `delete-more` summary line reads `{"False": 6545}`.
- **My own encoder** (`Q/src/myenc.py`) is brute force over every vertex subset of size 4 or 6 that meets a new vertex; it shares no code with the author's encoder.
  - On a seeded random sample of 49 cores, all UNSAT under both MiniSat 2.2 and MapleChrono (`Q/mysample.log`). The sample covers the full core, 10 one-vertex deletions, 15 two-vertex deletions, 20 three-vertex deletions and the 4 DRUP cores.
  - I then ran **all 7,176 cores** with MiniSat 2.2 (`Q/sweep0.log`, `Q/sweep1.log`): `[((0,'UNSAT'),1), ((1,'UNSAT'),35), ((2,'UNSAT'),595), ((3,'UNSAT'),6545)] distinct 7176`. My encoder never returned SAT.
  - Per-case clause counts equal the author's logged counts in all 7,176 cases ("clause-count mismatches 0").
  - For the 4 DRUP cores, the author's CNF and mine are identical as sets of edge-literal clauses.
- **DRUP traces** (`Q/src/drup.py`). I regenerated the author's CNFs with the author's own encoder and ran drat-trim on `A/extension-proof-{1,2,3,4}.drup`: `s VERIFIED` for all four, with "67 of 81", "76 of 94", "251 of 317" and "571 of 730" lemmas in core. The proof SHA-256s are `90892bba…`, `6808efca…`, `14a10633…` and `221f73c2…`. The CNFs were deleted after hashing. The writeup's 80/93/316/729 additions are the author's checker's count without the final empty clause.
  - Coverage: the four traces certify 4 of the 7,176 formulas (0.06%). The rest rests on solver return codes: CaDiCaL for the author, MiniSat for me.
  - The checker the author used (`P/search/neighborhoods.py:30-58`) is the attempt's own code. It is not independent, contrary to the handoff (correction 4).

### P3: known-answer controls
- Author's pipeline (`extension` + `solve` from `P/search/search.py`, run in `Q/authorctl/`), target 35:
  - removing {34}, {33,34}, {32,33,34}, {0,1,2} and {10,20,30} and re-adding 1, 2 or 3 free vertices gave SAT every time, in 38 to 193 conflicts;
  - `bun frontier diagnose` on the 3-vertex restore said `valid: yes`, `ties the best known value`.
- My encoder: 12 restore controls (1, 2 or 3 vertices removed, 4 sets each) were all SAT, with 0 violations by my counter (`Q/controls.log`).
- These controls show the encoder can say yes. They are weak, though: the deleted vertices' own stars are always a solution.
- The smaller controls the author names:
  - 17 vertices is R(4,4), where Paley 17 is the unique extremal colouring.
  - 24 vertices is R(4,5), the extremal order since R(4,5) = 25.
  - The negative controls are K14 for R(3,5) = 14 and K18 for R(4,4) = 18.
  - They check that the clique encoders, annealers and enumerators work at all. They do not calibrate the 36-vertex case: 136 or 276 edges against 630, and the extremal sizes are already known there. The writeup itself admits the degree-strengthened negative controls have "limited power" (`P/writeup.md:13`).

### P4: the exact star minimum of 20
- My own branch and bound (`Q/src/starbb.c`) uses a static vertex order and an independently written incremental clique counter. Its cost is (#colour-0 triangles among vertices joined by colour 0) + (#colour-1 K5 among vertices joined by colour 1). That equals the number of colour-0 K4 plus colour-1 K6 through the new vertex, since the core has none.
- Control: on the 34-vertex core (vertex 34 deleted) it returns optimum 0.
- On the full 35-vertex core: `optimum 20 nodes 37195513`, 21 s on one core.
- Writing that star as a 36-vertex colouring, `bun frontier diagnose` reports `valid: no violations (20)`: 14 colour-0 K4 and 6 colour-1 K6, the same split as the author. The author's B&B log `A/results/star-published-36.log` reads `end nodes=1295109 covered=34359738368 optimum=20`.
- So 20 is the exact minimum number of violated forbidden cliques (one clause per clique), with all 595 old edges fixed and only the 35 new edges free. The author's RC2 run was killed (exit 143), and the writeup says so.

### P5: the 16 complete enumerations
- `A/results/*-enum.log` end lines: `visited` equals 2^k for all 16 families, and every job exited 0.
- I checked each of the 14 orbit maps for order 36 (`A/g36-*.orbits`, `A/n36-circle.orbits`) independently. In each map:
  - the number of edge orbits equals (35 + i)/2, where i is the number of involutions of the named group (1, 3, 7, 9, 15 or 19);
  - involution orbits have 18 edges, the others 36;
  - every orbit is a regular graph.
- The 14 maps match the 14 groups of order 36:
  - C36 and Dic9;
  - (C2×C2)⋊C9, D36 and C18×C2;
  - C3×(C3⋊C4), (C3×C3)⋊C4 with kernel C2, (C3×C3)⋊C4 faithful, and C12×C3;
  - S3×S3, C3×A4, C6×S3, C2×((C3×C3)⋊C2) and C6×C6.
  So "the cyclic group and 13 semidirect products" is all 14 groups. Three of them are direct products, that is, trivial actions.
- My own circulant enumerator (`Q/src/circ.c`) does not use the orbit maps. Controls: n = 17 gives min 0 and n = 18 gives min 27 for (4,4). It gives `n=36 … minimum_total=72` and `n=37 … minimum_total=111`, matching the table.
- What the 16 enumerations exclude: every 36-vertex colouring invariant under a regular action of a group of order 36 (Cayley colourings); circulant colourings at 37; and colourings at 37 invariant under a 36-cycle with one fixed point. They do not exclude non-Cayley vertex-transitive colourings or other cycle structures.
- The six-block 36-vertex family is UNKNOWN at 1,000,001 conflicts. The writeup says so (`P/writeup.md:93`, table row `n36-b6`), and neither the title nor the claim counts it as negative.
- I did not re-derive the symmetry-breaking constraints behind the "Strengthened SAT: UNSAT" entries for n36-b3 and n36-b4. My reading of `P/writeup.md:27`: fixing the lexicographically least rotation of each cross word to block 1 is sound, because each other block's rotation acts independently on its word to block 1.

### P6 / check 3: annealing
- The 12 at 36 (`A/aut-base-history.log`) came from seed 4636035 with induced-path weight `p4=0.02`, on the order-two orbit map. It first appeared at restart 2, step 455,973 of 3,000,000, about 28 s into a 94-second run.
  - The run saw 134,731 distinct fingerprints in 24 million proposals (0.56%).
  - Restarts 3 to 7 matched 12 and never went lower.
  - The writeup does not mention the p4 weight for this run (correction 2).
- **Planted control: the attempt has one, and does not report it as one.** The repair-and-grow sweep (`P/search/grow.py`, `A/growth.log`, `A/results/grow35-*.log`) damaged valid 35-vertex catalogue colourings by flipping 5 to 17 edges touching 3 vertices, then annealed them with the same annealer.
  - With `p4=0.025` (runs 00 to 36): **0 of 37 repaired**, including the 6 with only 5 flipped edges. Most stalled at 2 violations; others at 1, 12, 20, 23 or 25.
  - With `p4=0` (runs 37 to 73): 23 of 37 repaired. All 5- and 7-flip cases were repaired; 4 of 6 at 9 flips, 3 of 6 at 11, 3 of 5 at 13, 1 of 5 at 15 and 2 of 5 at 17.
  - The failed raw runs stalled at 7 and 17 to 24 violations, although a valid colouring sat 17 or fewer edges away.
  - The writeup reports "It recovered 23 valid graphs" (`P/writeup.md:109`) without the split, and does not use it to read the 12.
  - On this evidence, a count of 12 is no sign of being near a valid colouring. The p4-weighted setting that produced the 12 cannot even repair a 5-edge perturbation of a valid 35 (correction 2).
- Unrestricted random starts plateaued at 30 to 34 per batch (`A/results/local-random-raw-0{0,4,8}.log`, `best_total` 32, 30 and 34), with about 2.9 to 3.1 million distinct states per batch.

### P7: budget
- Wall time: 21:23:17 to 22:05:16 UTC on 17 Nov, 41:59 of 120 minutes.
- Logged subprocess jobs (single-threaded; `structured.log`, `unrestricted.log`, `supplemental.log`, `extra-lane.log`): 189 jobs, all exit 0, summing to 3,717 s (about 62 CPU-minutes over 2 lanes). The largest were orbit SAT (471 s), delete-three (255 s) and the two 2^27 enumerations (161 s and 164 s).
- Why it stopped: the handoff says work ended "once the remaining campaigns completed". The run stopped because the plan ran out, not because the budget did.
- Was any lane cut while improving? The unrestricted lane was interrupted (exit 130 at 21:37:15). Its random batches had plateaued at 30 to 34, far above the fixed-core start's 18, so that cut lost little.
- What should have used the remaining 78 minutes:
  - The fixed-core lane, which was fast and exact: the 6,545 three-deletion cases took 255 s. With the time left, it could have run the 5-new-vertex cores of the same colouring (C(35,4) = 52,360 formulas, 165 variables). Or it could have run 2- and 3-new-vertex cores of the other 36 catalogue colourings: 36 × 630 = 22,680 formulas, minutes by my own timings of about 0.15 s each.
  - Alternatively, the unresolved n36-b6 SAT instance, by cube-and-conquer.

### Check 6: disclosure, licence, privacy
- `attempt.yaml` lists the author (gpt-6.2-sol), the planner (claude-fable-5-2), python-sat, CaDiCaL 1.9.5, Glucose 4.2, RC2, clang++, Python 3.12 and frontier. Both declarations are `false`.
- Omissions:
  - `bun`, which runs `search/wait-log.ts`;
  - `uv`, which builds the venv (minor);
  - the auditor (claude-opus-5-5), to be added in the correction.
- `grep -rn -E "/Users/|/home/" P` found nothing. No personal names.
- The `search/` sources carry no third-party code, licence header or adaptation notice. They read as original; the writeup says "original to this attempt". The group classification link (GitHub smallgroups README) is a citation, not copied code. Downloaded graphs and binaries stay in scratch.

### Check 8: repo commands
```text
$ bun src/cli.ts check "attempts/witness.ramsey-4-6/20261117-terramind-com-41765d"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
$ bun src/cli.ts validate "attempts/witness.ramsey-4-6/20261117-terramind-com-41765d"
attempts/witness.ramsey-4-6/20261117-terramind-com-41765d/attempt.yaml: declarations: not confirmed. Show the declarations (…) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```
`bun run check`: tsc clean, `434 pass / 1 skip / 0 fail`. Validation exits 1 only on the 13 unconfirmed declarations on the swarm branch, as designed.

### Corrections (quote, then replacement)
1. Claim, `attempt.yaml`. Quote: "SAT returned UNSAT for all 7,176 tested fixed cores of the downloaded 35-vertex colouring."
   Replace: "SAT returned UNSAT for all 7,176 ways to keep 32 to 35 vertices of Exoo's published r4.6.35 colouring and add 1 to 4 free vertices. This is one of the 37 known 35-vertex colourings; an independent auditor re-derived all 7,176 with a separate encoder and solver."
2. `P/writeup.md:107` and the claim. Quote: "reached 12 colour-0 K₄'s and zero colour-1 K₆'s at 21:39:01 UTC, in restart 2" (and claim: "The lowest observed violation count at 36 was 12.").
   Add after the writeup sentence: "This run used an induced-path weight of 0.02. In the attempt's own planted control, the annealer with that weight (0.025) repaired none of 37 valid 35-vertex colourings damaged by 5 to 17 edge flips. Without it, failed repairs stalled at 7 to 24 violations. A count of 12 is therefore not evidence of being near a valid colouring."
   Append to the claim: "Violation counts are not calibrated as distance to a valid colouring."
3. `P/writeup.md:109`. Quote: "It recovered 23 valid graphs, all colour-preserving isomorphic to a graph in the input collection."
   Replace: "It recovered 23 of 74, all from the 37 runs without the induced-path weight: all 5- and 7-flip cases, and fewer as the flips grew. The 37 runs with weight 0.025 recovered none. All 23 are colour-preserving isomorphic to a graph in the input collection."
4. `P/writeup.md:48` (DRUP sentence), and the handoff. Quote: "A reverse-unit-propagation checker derived the empty clause from each trace, with 80, 93, 316 and 729 additions respectively." Handoff: "An independent checker replayed the four DRUP traces."
   Replace: "The attempt's own reverse-unit-propagation checker, which ignores deletions, derived the empty clause from each trace, with 80, 93, 316 and 729 additions. An auditor's drat-trim run also verified all four. These traces certify 4 of the 7,176 formulas; the others rest on solver return codes."
5. `P/writeup.md:52`. Quote: "The same fixed-core model returned UNSAT for every one-vertex extension, with 29 to 76 conflicts per graph."
   Add: "This reproduces a published result: arXiv:2411.04267 (Lehavi, 2024) reports that no colouring on 36 vertices arises as a one-vertex extension of the known set of 35-vertex colourings." Also add the reference to the opening references.
6. `P/writeup.md:5`. Quote: "The survey's revision 18 gives 40 as the upper bound in Table Ib."
   Replace: "The survey's revision 18 (24 April 2026) gives 36 to 41 in Table Ia and an unpublished upper bound of 40 in Table Ib."
7. `P/writeup.md:25` (optional precision). Quote: "For order 36 the regular actions cover the cyclic group and 13 semidirect products."
   Replace: "For order 36 the regular actions cover all 14 groups of order 36: the cyclic group and 13 others, three of them direct products."
8. Disclosure: add claude-opus-5-5 (anthropic, auditor) and `bun` (tool, deadline watcher). `uv` is optional.

## Deviations
- I did not re-run the annealing, orbit-SAT, canonical-block or catalogue-symmetry lanes. I read their logs and code. I re-derived only the exact results: the fixed cores, the DRUP traces, the star optimum and the two circulant minima.
- I did not re-derive the symmetry-breaking constraints behind the n36-b3, n36-b4, n37-b4 and n37-b6 "Strengthened SAT: UNSAT" entries, or the 12 non-cyclic group enumerations. For the groups, I checked the orbit maps against group theory instead.
- I did not verify that the order-four colouring the author used ("catalogue graph 36") has the group the writeup states.
- Lehavi's paper: I read only the abstract page, not how it built the R(4,6,35) set or whether that set is McKay's 37.

## Concerns
- The prior-art paper's "current sets R(4,6,35)" is unspecified in its abstract. If it used only McKay's 37, then it and this attempt cover the same one-vertex cases.
- The 2- to 4-vertex fixed-core results cover a single colouring, `r4.6.35`, one of 37 known. Nothing says a colouring on 36 vertices would contain a large part of it.
- Of the 7,176 UNSAT results, 7,172 rest on solver return codes. Two independent encoders and two solver families agree, which is strong but not a certificate.

## Follow-ups
- **Method first, then time.** The exact fixed-core lane is the productive one: cheap, calibrated by restore controls, and certifiable. A stronger re-run should:
  - extend it to all 37 known colourings at 2 to 4 new vertices: 37 × 7,176 = 265,512 formulas, a few hours at about 0.15 s each;
  - run 5 new vertices on r4.6.35: 52,360 formulas;
  - emit DRAT/LRAT for every case or a random 5% sample, checked with drat-trim.
- Settle the n36-b6 instance by cube-and-conquer (it is UNKNOWN at 1 M conflicts). That needs time, not a new idea.
- Drop or recalibrate the induced-path annealer before using its counts. The attempt's own control shows it cannot repair a 5-edge perturbation. Exoo's Method B (paper p. 2) steers toward new colourings; it is not a repair method.
- Generate new 34- and 35-vertex classes, which is the writeup's own follow-up. That is the only route not already covered by the fixed-core results and the prior art. Its lever is method, not time.
