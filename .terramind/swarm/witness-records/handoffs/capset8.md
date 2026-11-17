## Done
- Attempt directory: `attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/`, kind `writeup`, title "CP-SAT exchange search and FunSearch priority variants from the 512-cap, 2 h, no 513-point cap found". It holds `writeup.md`, `attempt.yaml` (claim written, declarations left `false` exactly as `new` wrote them) and the search source in `search/` (capcore.py, complete.py, lns.py, greedy.py, run_b.sh; all under 9 KB, no data).
- Verbatim output of `bun frontier check attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa`:
  ```
  $ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
  note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
  unchecked: Writeups are not machine-checked.
  ```
- `bun frontier validate <dir>` complains only that the declarations are not confirmed. `bun run check`: tsc clean, 426 pass / 1 skip / 0 fail, then validate fails on the same declarations message only.
- Result: record 512. Best value reached 512: the FunSearch cap (repo verifier: valid, "ties the best known value") and a second, distinct 512-cap from a perturbed priority function (repo verifier: valid, ties). Nothing beats the record, and no 513-point cap was found. Best net gain for k-removal: 0 in every neighbourhood and every run, over about 8,700 exact CP-SAT re-solves with up to 332 points removed. Completeness: every outside point completes at least 4 lines (16 points have count 4). Priority-function variants (about 226,500) gave at most 512. Product caps gave at most 400 (20 x 20), which is complete and did not grow.
- Wall clock: first search process started 21:25:04 IST, last one exited on its own time limit at about 23:19, so about 114 of the 120 minutes, on 2 cores. Exit status: the final runs A (104 min), B_variant, B_product and B_baseline all ended normally on their time limits. Run A1 was killed by me at 10 min to add a size cap, and the first B schedule crashed after its 15-minute program search on a path bug (details under Deviations).

## Deviations
- Restarts inside the budget: the first exchange-search process (A1) spent most of its time building CP-SAT models for freed sets of more than 3,000 points, so I killed it at 10 min, added FMAX = 1400 (skip bigger freed sets) and restarted (A, 104 min). The first program-search run crashed after its 15-minute variant loop on a wrong baseline path, so its caps were never saved (its logged sizes are reported). I reran it for 6 minutes. The budget clock was not reset for either.
- Step 3 of the brief asked for k = 1..8. I used k from 4 (the minimum blocking count) to about 330, plus hyperplane and subspace neighbourhoods, because small k frees almost nothing.
- Products: I had no explicit coordinates for the 45-cap (F_3^5) or the 112-cap (F_3^6). CP-SAT found only 39 and 79 in the time given, so the products started from 400 rather than from 405/448. Doublings were not tried. The writeup says so.
- python-sat was installed but not used, so only OR-Tools CP-SAT is disclosed as a tool.
- The swarm brief names the handoff `handoffs/capset8.md` and the handoff section names `handoffs/grow-funsearch-cap-set-past-512-6889k.md`. I wrote the second and a copy at the first, with identical content.

## Concerns
- "No plateau move found" is weak evidence. CP-SAT starts from the hint S = R and returned it every time, so alternative optima of equal size could exist in those neighbourhoods. The writeup states this.
- About 91 + 18 + 21 + 22 + 9 solves (out of about 8,700) hit the time limit without proving optimality. They found no gain but do not prove there is none.
- The second 512-cap probably comes from the FunSearch cap by an affine map (same completeness profile, 384 common points). This was not checked.
- As the design doc expects, the PR into the swarm branch will fail the `pr` workflow's validate step (declarations false, handoff file outside `attempts/`).

## Follow-ups
- Start from the literature 45- and 112-caps (products and Edel-type doublings, which gave the old 496 record), then run the exchange search.
- Region-plus-boundary neighbourhoods: remove a codim-2/3 subspace section together with every cap point blocking points inside it, so that many more candidates are freed.
- Symmetric-cap search: fix a subgroup of the cap's automorphism group and solve exactly over orbits.
