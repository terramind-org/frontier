## Done

Edited only `attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/{writeup.md,attempt.yaml}`. No search was run, and `search/` was not touched. I ran `bun install`. I checked each replacement against the author's original logs (`grotesque-beach/.terramind/scratch/capset8`: `search_B1.out:11105-11119`, `runs/B/greedy_8.log:1-6,2675-2689`) and the audit's rerun outputs (`defeated-canopy/.terramind/scratch/audit-capset8`: `priority.out`, `hyperplanes.out`, `plateau.out`).

### The ten audit corrections (old wording -> new wording)
1. **Solve counts.** Old claim: "about 8,700 exact CP-SAT re-solves after removing up to 332 of its points ... all gave net gain 0". Old "Do not repeat": "net gain 0 in about 8,700 exact solves". New (Step 2 and claim): "The logged snapshots total 8,789 successful solves across the FunSearch cap (7,605), its affine copy (1,064) and the 400-point product cap (120). Of these, 8,625 proved optimal and 164 returned only feasible incumbents; none recorded an improvement. The largest removal certified optimal was 332; that is not the largest removal attempted (A1 has a FEASIBLE solve at |R| = 419, |F| = 3,874). A1 and B1 have no final record, so their counts are lower bounds at interruption." The run table now also gives A1's 9 and B1's 3 non-optimal solves and B1's 49 skips (audit Done 3).
2. **Exactness.** Old: "solves max |S| ... exactly, with CP-SAT". New: "models max |S| ... exactly (...; hint S = R), then runs time-limited CP-SAT. Only an OPTIMAL status certifies the neighbourhood optimum; a FEASIBLE status gives only an incumbent."
3. **S = R.** Removed "on every solve CP-SAT returned exactly S = R ..." and "the optimum was always exactly the removed set". New: "No gain or accepted plateau move was logged. Certified solves established the original cardinality as optimal; uniqueness was not tested, and returned-set identity was not logged." This is followed by the PLATEAU 0.5 vs 1.0 distinction (`lns.py:188`) and the audit's plateau example: R = baseline minus the second cap, |R| = 128, |F| = 256; adding "not all of R" returns the second 512-cap. "Equal-size alternatives therefore exist nearby."
4. **Freed-set sizes.** Removed "removing all cap points of an affine hyperplane (108 to 208 points) freed only 10 to 18 outside points, removing 200 random cap points freed 5 to 9, and removing 300 freed about 170". New: "Freed-set sizes vary substantially by hyperplane. For x1 = 0, R = 192 and F = 600, freeing 408 outside points; for x4 = 0, R = 160 and F = 160, freeing none." I deleted the random-removal figures rather than recasting them, because no per-solve record supports them. In their place I added that `lns.py` logs only about one sampled row a minute (146 rows) and never the contents of R or F, so the full distributions, the rate of repeated neighbourhoods and the fraction of F = R solves cannot be reconstructed.
5. **Noise.** Old: "tie-break noise up to 1% of the priority range: still 512; noise of 10% or more: at most 336". New: "random tie-break noise of 1e-9, 0.001 and 0.01 times the maximum absolute priority, five trials each: still 512. Five sampled trials at each of two larger noise scales, 0.1 and 0.5 times the maximum absolute priority, reached at most 336 in the seed-8 rerun. This is a sampled observation, not a bound for larger noise." "Range" also became "maximum absolute priority", which is what `greedy.py:103-107` computes. The 336 is in the original log at `greedy_8.log:5`.
6. **Lost run.** Old: "whose results were lost to a path bug after the run". New: "whose candidate coordinates were not saved because the baseline lookup failed; stdout preserves variant counts and top sizes" (`search_B1.out:11110-11119`).
7. **Histogram tail.** Old: "and a tail down to 425". New: "The printed histogram shows only the 15 largest size bins, ending at 425; smaller sizes were omitted."
8. **Affine image.** Old: "so it is very probably an affine image of it (not checked)". New: "It is an affine image of the FunSearch cap: the linear map negating the sixth coordinate, (x1, ..., x5, x6, x7, x8) -> (x1, ..., x5, -x6, x7, x8), sends one onto the other (exact set equality, checked in the audit)."
9. **Why it stalled.** Removed "strict local optimum under every neighbourhood tried", "refill to exactly the same points" and "Local search near it is the wrong tool", plus "came out at 448 or less, and the exchange search could not grow them either". New: "These sampled, time-limited exchanges found no improvement. This does not establish strict local optimality or rule out other local-search strategies. ... A priority variant produced an affine copy at 512. Exchange search was run from the FunSearch cap, that copy and the 400-cap; the two saved 448-caps were not exchange-searched in this attempt. The search never deliberately looked for equal-size alternatives, and the audit's plateau example above shows they exist."
10. **"Do not repeat"** became "Observed limits of these runs". Its bullets now report outcomes only: 8,669 successful solves from the two 512-caps (7,605 + 1,064), with no gain recorded and all hinted with the removed set; "the sampled perturbations reached at most 512, with 452 the largest logged smaller result"; CP-SAT from scratch in F_3^5/F_3^6 stayed at 39/79 in about 5 to 6 minutes. The advice "take the 45- and 112-caps from the literature instead" stays as an Untried item.

### Items 2 to 6 of the brief
- **Item 2:** Untried now opens with (a) plateau walks that exclude the current set (solution exclusion or a diversity objective), with the 128-point removal as a known plateau move to test against, and (b) exchange search from the two 448-caps the seed-8 rerun saved. The four original items follow unchanged.
- **Item 3:** "about 114 minutes of the 120-minute budget" is kept. Setup now says "Two runs (A1, B1 below) were interrupted; their exit statuses and final counters were not preserved". In the table, "killed by me" became "interrupted" and "killed with the B1 schedule" became "interrupted with the B1 schedule". Setup also says that the `search/` copies are final versions and that A1 predates the FMAX skip (audit Done 3).
- **Item 4:** The attempt.yaml title is unchanged because no correction makes it inaccurate. The writeup H1 says "2 h budget" instead of "2 h". The claim is rewritten (below). `kind: writeup` and `declarations: { rights: false, disclosure_complete: false }` are unchanged.
- **Item 5:** Added `NumPy` (provider `tool`, role `greedy builder and freed-set computation`) and `gpt-6.1-sol` (provider `openai`, role `auditor`). The existing three entries are unchanged. Setup now also says "NumPy did the greedy builder and the freed-set computations".
- **Item 6:** Added an "Independent audit" section. It covers the independent completeness counter, the positive controls (punctured 507 back to 512; gains in dimensions 3 and 4), the recount from original log lines, the affine map, the overstated summaries and the corrected text. It says the audit is "an opinion backed by reruns, not a check by the repo verifier", and that the audit found no cap above 512. The report is not pasted.
- **Item 7:** No "solved" anywhere. Ties are called ties. The top of the writeup and the claim both say it is not machine-checked.

### New title (unchanged)
CP-SAT exchange search and FunSearch priority variants from the 512-cap, 2 h, no 513-point cap found

### New claim (in full)
No cap set in F_3^8 with more than 512 points was found. This writeup records a failed search within a 2-hour budget (about 114 minutes used) and is not machine-checked. The FunSearch 512-cap is complete (every outside point completes at least 4 lines). Exchange search removed cap points (random, targeted, hyperplane and subspace neighbourhoods), modelled the best refill exactly and ran time-limited CP-SAT: the logged snapshots total 8,789 successful solves across the FunSearch cap (7,605), its affine copy (1,064) and a 400-point product cap (120); 8,625 proved optimal and 164 returned only feasible incumbents; none recorded an improvement; the largest removal certified optimal was 332 points; counts for the two interrupted runs are lower bounds. Equal-size alternatives were not deliberately explored. About 226,000 variants of the FunSearch priority function reached at most 512; product caps reached 400. It does not establish that the 512-cap is a strict local optimum and claims nothing about whether a larger cap exists.

### Verbatim output
```
$ bun frontier check attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa
$ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
(exit 0)

$ bun frontier validate attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa
$ bun src/cli.ts validate "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```
Validate's only complaint is the declarations. The repo gate `bun run check` ran once: tsc clean; 426 pass, 1 skip, 0 fail across 34 files. It exits 1 only because validate rejects the intentionally false declarations of the four unsubmitted attempts (cap-set, matmul, sorting-network, superpermutation), as design decision 6 expects.

## Deviations
- Correction 4: I deleted the random-removal figures (200 -> 5 to 9, 300 -> about 170) instead of recasting them as seeded examples. No original log line ties them to a seed, and the audit's random-300 = 170 is the auditor's own example, not the author's run.
- I added a few facts the audit supports that the brief did not list, all narrowing rather than strengthening:
  - A1 and B1 non-optimal and skip counts in the table.
  - A1's FEASIBLE |R| = 419 solve.
  - The 146 sampled log rows and what cannot be reconstructed from them.
  - CP-SAT proved optimality only in dimensions 2 and 3 for the small-dimension caps (bounds 4 and 9 at `greedy_8.log:2682-2683`; dimension 4 bound 80).
  - The 452-cap's coordinates were never saved, so the verifier never checked it.
  - The 151,858 family count is split as 118,959 + 32,899.
  - The `search/` copies are final versions, and A1 predates FMAX.
- The writeup H1 "2 h" became "2 h budget". The attempt.yaml title is unchanged.
- The brief names the handoff both `correct-capset8.md` and `correct-the-cap-set-writeup-svxko.md`. Both files hold this identical text.

## Concerns
- The audit's suggested wording for correction 9 says "Exchange search was run from that copy and the 400-cap". Taken literally, that omits the baseline, which had 7,605 of the solves. I followed the brief's fuller wording (FunSearch cap, its copy, the 400-cap).
- The audit's plateau example used FEASIBLE solves (20 s limit), not OPTIMAL. It shows that an equal-size alternative exists, which is all the text claims. It does not certify anything about optimality.
- Nothing else in the audit looked wrong against the logs I read. The 336, 452, 60,552, 118,959, 14,107, 32,899, 425 and the dimension-2 to 6 sizes all match the original log lines.

## Follow-ups
None.
