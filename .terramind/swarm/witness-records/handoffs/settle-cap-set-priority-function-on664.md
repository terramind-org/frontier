# Handoff: settle cap-set priority-function provenance

## Done

**Step 1: facts, with sources (all read on 18 Nov 2026).**

(a) Where the n = 8 priority function is published:
- **Nature paper, Fig. 4b.** Romera-Paredes et al., "Mathematical discoveries from program search with large language models", Nature 625, 468-475 (2024), https://www.nature.com/articles/s41586-023-06924-6 (doi 10.1038/s41586-023-06924-6). The body text says: "Moreover, we do not just discover the set of 512 eight-dimensional vectors in itself, but a program that generates it: we show this program in Fig. 4b." The Fig. 4 caption says: "b , The function ‘priority’ : Z_3^n → R discovered by FunSearch that results in a cap set of size 512 in n = 8 dimensions." I viewed the figure image (https://media.springernature.com/lw1200/springer-static/image/art%3A10.1038%2Fs41586-023-06924-6/MediaObjects/41586_2023_6924_Fig4_HTML.png). It prints the complete function as code: `score = n`, `score += n**2`, the three `*= 1.5` reflection tests, the two `*= 0.5` tests, the zero-position loop (`n * 0.5`, `0.5`, `n * 0.5 ** in_el`, `+= 1`) and the two final `*= 1.5` tests. The caption has no third-party credit line.
- **Supplementary Information** (https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-023-06924-6/MediaObjects/41586_2023_6924_MOESM1_ESM.pdf), Appendix E.2, refers to the function as "Figure 4 (b)" and does not reprint it. Supplementary Data 1 (https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-023-06924-6/MediaObjects/41586_2023_6924_MOESM2_ESM.zip) is a snapshot of the repository, including `code/cap_set/cap_set.ipynb`, `code/LICENSE` and a README with the same licence section.
- **Repository** github.com/google-deepmind/funsearch, commit cc53f274237d7ab05c19df939edbc1f9616a7c19 (HEAD on 18 Nov 2026). The function is in `cap_set/cap_set.ipynb`, code cell 6 ("Discovered function that builds a 512-cap in n = 8 dimensions"). The 512-cap data is in `cap_set/n8_size512.txt`.
- I checked equivalence mechanically: `funsearch_priority(v, 8, BASE)` from the attempt's greedy.py and the notebook's `priority(v, 8)` return identical values on all 3^8 = 6561 vectors (0 differences). The Fig. 4b text is the same as the notebook function.

(b) Licences:
- **Paper** ("Rights and permissions", https://www.nature.com/articles/s41586-023-06924-6), verbatim: "Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/ ."
- **Repository README**, "License and disclaimer" (https://github.com/google-deepmind/funsearch/blob/cc53f274237d7ab05c19df939edbc1f9616a7c19/README.md), verbatim: "Copyright 2023 DeepMind Technologies Limited" / "All software is licensed under the Apache License, Version 2.0 (Apache 2.0); you may not use this file except in compliance with the Apache 2.0 license. You may obtain a copy of the Apache 2.0 license at: https://www.apache.org/licenses/LICENSE-2.0" / "All other materials are licensed under the Creative Commons Attribution 4.0 International License (CC-BY). You may obtain a copy of the CC-BY license at: https://creativecommons.org/licenses/by/4.0/legalcode". The `LICENSE` file is the Apache License 2.0 text (GitHub reports `apache-2.0`). The notebook's first cell repeats the same Apache 2.0 / CC-BY statement. So the notebook code is most naturally read as "software" under Apache 2.0, and the 512-cap data file as "other materials" under CC BY 4.0.

**Step 2: Case A applies.** The function's full text is printed in Fig. 4b of the open-access article, which is under CC BY 4.0, and Fig. 4 has no credit line that excludes it. The same function is also in Apache-2.0 notebook code. That is the mixed-evidence case, which the rule settles as Case A, citing the CC BY source. The function stays.

Changes (only these two files; attempt.yaml is unchanged):
- `attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/search/greedy.py`: a 9-line comment block above `funsearch_priority`. It names all twelve authors, the paper with its DOI, "Fig. 4b", CC BY 4.0 with its URL, and the changes: the eight constants are exposed as P (keys sq, r0, r1, z0, zl, zm, nz, r2), and the three consecutive reflection tests of the all-nonzero branch are written as one loop. With P = BASE (the published constants) it returns the published priority on every vector. The block also notes that the greedy builder follows the article's method (Fig. 2a) and is not copied. No code line changed.
- `.../writeup.md`: a new section "Third-party material" before "Independent audit", with the same attribution, licence, changes, the note on the greedy builder, and a statement that the starting 512-cap file was read at run time and is not part of the attempt. A new final section "Provenance" says the review was done after the closing check and what was done. Title, claim, results, numbers and disclosure list are unchanged. I was not added to `models`. Both declarations are still `false`.

**Step 3: other files.**
- `capcore.py`: no FunSearch code. It shares only the common base-3 indexing idiom with the notebook (`itertools.product((0, 1, 2), repeat=N)`, powers `3 ** np.arange(N - 1, -1, -1)`, so index = vector @ powers). That is a one-line convention, not copied expression. I noted it in the Provenance section.
- `greedy.py` `greedy()`: the same algorithm as the paper's skeleton (Fig. 2a, CC BY) and the notebook's `solve`: argmax priority, then mask blocked points with -inf. The code is different (a precomputed third-point table, a start set, no einsum). Attributed as method, not as copied code.
- `complete.py`, `lns.py`, `run_b.sh`: no FunSearch-derived or other third-party code found. `grep -i "funsearch|deepmind|copyright|apache"` matches only greedy.py. `run_b.sh` reads `baseline.json` at run time.
- The 512-cap data (`n8_size512.txt` / `baseline.json`) is NOT in the attempt. `git ls-files` lists only attempt.yaml, writeup.md and the five search files, and the attempt.yaml `files` list matches exactly.

**Step 5: verification.**
`bun frontier check attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa` (exit 0):
```
$ bun src/cli.ts check "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```
`bun frontier validate attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa` (exit 1, the only complaint is the declarations):
```
$ bun src/cli.ts validate "attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa"
attempts/witness.cap-set-f3-8/20261117-terramind-com-8edffa/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```
`bun run check`: tsc clean; `bun test` 434 pass, 1 skip, 0 fail. The validate step fails only on "declarations: not confirmed" for the seven swarm attempts, which is expected (design decision 6). greedy.py still parses, and the equivalence test above was re-run after the edit (0 differences). The script itself was not run: Case A changes only comments, and the task asks for a run only in Case B.

## Deviations

- The task names two handoff paths (`handoffs/capset8-provenance.md` in the task text, `handoffs/settle-cap-set-priority-function-on664.md` in the handoff instructions). I wrote the same content to both.
- I added one attribution line for the greedy builder (method from Fig. 2a), which step 2 did not ask for. It is method credit only, and both places are CC BY.

## Concerns

- The repository README places "software" under Apache 2.0. The CC BY coverage relied on here is the article's licence for Fig. 4b, which is printed as an image of code inside the CC BY article. The article's licence statement covers "images or other third party material ... unless indicated otherwise in a credit line", and Fig. 4 has no such line. That is the factual basis; whether it fully settles the rights declaration is for the human to judge (this is not legal advice).
- Attribution is given in the form CC BY asks for (credit, licence link, changes indicated). The original copyright notice "Copyright 2023 DeepMind Technologies Limited" is from the repository, not the paper. I did not add it because the attribution cites the CC BY paper, not the Apache code. The human may want to add it anyway.
- Other attempt files were judged by reading and grep, not by any automated similarity tool against all of GitHub.

## Follow-ups

- The second cap-set attempt on the swarm branch (`20261117-terramind-com-e28c40`) was not in scope and was not reviewed for provenance. If it ships Hill-cap or FunSearch-derived code (it has `hill_products.py` and `check_sym512.py`), it may need the same review.
