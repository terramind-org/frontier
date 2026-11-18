Outcome: done

## Done

- Confirmed the cloud checkout at `/workspace/repo`, created branch `swarm/frontier-cloud-codex--extend-seven-dimensional-cap-con-qxvuf-c3`, installed Bun 1.4.4, and ran the prescribed practice scaffold/check separately. Lean is absent, so that placeholder practice proof reported that CI would check it, as expected.
- Read `witness.cap-set-f3-7`; it has no prior Frontier attempts. Checked the 2024 Gijswijt survey entry and the primary/reproducible sources around it. The currently recorded target is still 237, over the published lower bound 236.
- Retrieved FunSearch's published `n8_size512.txt` from the DeepMind repository (SHA-256 `8d6df45c3039b6a7ee1aae7216b100c3f4c075179dc6471f4f51b968a26d8905`). Exhaustively enumerated all 9,840 affine hyperplanes of its 512-cap. The largest section had only 208 points, at normal `(1,0,0,0,1,1,0,0)`, offset `1`; deleting coordinate 0 after solving for it gives an explicit bijection of that hyperplane to F3^7. Thus this route does not supply a 236-point baseline.
- Reconstructed the 236-point Calderbank--Fishburn cap from the published six-coordinate 2-(6,3,2) design: layers `1 x H`, `0 x {+/-e_i}`, and `-1 x H'`, where `H` and `H'` are the two Hill 112-caps. Its JSON SHA-256 is `5d4d0bb152f5eb637a555007ff4e26a73fe7de4f619f2e998c5a54fc189f22cf`.
- Ran the repository verifier on a disposable scaffold containing that construction: `bun frontier diagnose` returned valid, value 236, ties best known; `bun frontier check` returned verified valid witness, value 236. Declarations remained false and no attempt was retained in this branch.
- Ran one-core exact destroy/repair search around the 236-cap. Every deletion neighborhood of sizes 1, 2, and 3 was exhausted: 236, 27,730, and 2,162,940 deletion sets respectively. Repair candidates were tested using their exact blocker-pair constraints and branch-and-bound compatibility; no set above 236 occurred. Elapsed 116.984 s, seed 20261118. The outgoing-blocker-pair histogram had minimum 10 pairs (24 outside points), explaining why no direct small repair was available.
- Pivoted to `witness.ramsey-5-5`, as requested. Retrieved Exoo's `g55.42` directly from his Ramsey-colourings page (SHA-256 `36ba90fb6727c9a876ecc127d8acbe9b9bf07a5b0925364a1b2f46f6e15052aa`). Verified the file has 42 rows of 42 bits, is symmetric, and has a zero diagonal. Repository diagnose/check both accepted it as a valid 42-vertex witness tying the known value.
- Formulated exact extension of this *fixed* 42-vertex colouring: each monochromatic K4 gives a four-literal prohibition on the incident colours of a new vertex. There are 2,308 such constraints (1,132 colour-0, 1,176 colour-1). Complete DPLL/unit propagation returned UNSAT in 39 nodes and 0.029 s. This rules out a 43rd vertex only for Exoo's supplied colouring, not for all 42-vertex colourings.

## Deviations

- `rg` and the visible-terminal launcher were unavailable/broken in this cloud image, so I used direct file operations and foreground one-core Python instead. No search process was left running.
- The requested roughly-30-minute cap-search budget was not spent because the specified complete neighborhoods finished in 116.984 s; extending the same enumeration would add no coverage. The FunSearch-section enumeration and exact extension test both completed fully.
- Work used disposable `/tmp/frontier-capset-*` scaffolds and scratch scripts only. No `attempts/` directory, declarations change, push, submission, or PR was made.

## Concerns

- This is not a global nonexistence result. The cap search excludes only exchanges with at most three deleted points from this particular affine realization of the 236-cap. The Ramsey result excludes only adding one vertex while preserving Exoo's exact 42-vertex colouring.
- The historical 236 source was reconstructed from Bierbrauer--Edel's published construction description; the original Calderbank--Fishburn paper itself was not used for coordinates. The reconstruction was independently accepted by Frontier's checker.

## Follow-ups

1. For cap sets, use a larger exact neighborhood with an incremental blocker-cover solver (four-plus deletions) or search affine images/structured perturbations of the 236-cap; retain the 236 JSON hash above as a reproducible baseline.
2. For Ramsey, search over 42-vertex recolourings plus insertion, not just vertex extension; use incremental SAT with explicit K5 clauses and independently recheck every candidate with `bun frontier diagnose`.
3. If retaining experimental artifacts later, scaffold a fresh attempt, keep both declarations false pending human approval, and record the exact scripts, seed, and construction provenance.
