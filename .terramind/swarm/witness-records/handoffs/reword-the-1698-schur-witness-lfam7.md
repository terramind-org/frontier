## Done

**Step 0: the prior public bound, confirmed independently before citing it.** All three conditions hold, so the corrections were applied.

- (a) Zenodo record 23670665 (DOI 10.5281/zenodo.23670665, version 1; concept DOI 10.5281/zenodo.23670664). Title: "A sum-free 7-colouring of {1, ..., 1698}: S(7) >= 1698 and R_7(3) >= 1700". Creator as the record gives it: "Özdemir, Kerem". Licence: cc-by-4.0. Zenodo `created` 2026-10-26T16:20:42 UTC, `publication_date` 2026-10-26. DataCite (concept DOI): Issued 2026-10-26, registered 2026-10-26T16:20:48 UTC, same creator, rights CC BY 4.0. Version 2 (record 23673962) was created 2026-10-26T18:56:35 UTC and lists `S7_1698.txt` with the same MD5 (4abdb5543cee2ef4d4844da762480944). The downloaded `S7_1698.txt` has SHA-256 `33f2f6c39fcf21dc32b13336ac481fbc175126fe73f6074b7632e5d8d47809e7`, which matches the audit. The record's description says its colouring is symmetric under c(x) = c(1699 - x) and was found by local search seeded from Rowley's 1696 colouring. The date is before 17 November 2026.
- (b) The file holds 1698 labels in 1..7. I converted it to `{"colors": [...]}` by subtracting one. From the repo root, `bun frontier diagnose <scratch>/converted/zenodo1698.json --problem witness.schur-7` printed:

  ```text
  problem:  witness.schur-7 (verifier schur)
  value:    1698 (best known 1696, higher is better)
  valid:    yes
  result:   beats the best known value
  ```

  My own counter also found 0 violations for both colourings. Its first version had an off-by-one in the sum index and reported 7,471. I fixed it and checked the fix against our witness (0) before trusting it. Sorted class sizes: deposit 146, 150, 168, 204, 206, 302, 522; ours 146, 164, 182, 194, 234, 364, 414.
- (c) I took the minimum Hamming distance to our `witness.json` over all 5,040 colour relabellings. It is **172**, matching the audit and reached at the identity relabelling. The two are different partitions.

**witness.json SHA-256:** before, `a3bd293ccede7f6c09530333b54e84f3c2feca3104cf323fdcaca479e7d34da5`. After, `a3bd293ccede7f6c09530333b54e84f3c2feca3104cf323fdcaca479e7d34da5`. Unchanged.

**Corrections (old wording, then new wording):**

1. Title. Old: "Many 6-colour bases + Rowley mirror one order up (SAT, 2 h): 7-colour Schur partition of 1..1698". New: see the full title below. It keeps method and budget as rules item 5 requires, and says it ties the public bound.
2. Claim. Old: "...2 more than the published 1696 (Rowley 2021)... It was found by CaDiCaL in a 2 h search over 60 generated bases. No partition of 1..1699 was found...". New: the auditor's replacement claim word for word (in ASCII arrows), plus "It is not a new record." Full text below.
3. notes.md, line by line against the audit:
   - Lines 1-5. Old heading "A seven-colour Schur partition of 1..1698"; old line 5 "The published record is 1696 ..., so this is 2 more." New heading "... that ties the public bound". New text: the diagnose comparison is against the catalog's 1696 only; a public bound of 1698 already existed; "This witness ties that bound with a different partition. It is not a new record. The exact value of S(7) remains unknown".
   - Line 11. Old: "This is Rowley's own method, run one order higher." New: "This uses Rowley's construction with a different six-colour base." The four steps now read "Reflect the base and the pivot by x -> 1697 - x" and "Tree-search the middle". New sentence: "The workbook holds a fully symmetric example that Rowley selected. The run here used SAT with full reflection x -> 1699 - x at N = 1698".
   - Line 24. Old: "...That rules out 1697 ... and allows 1698". New: "The divisibility obstruction rules out full reflection at N = 1697 ... For N = 1698 (N + 1 = 1699) the obstruction does not apply."
   - Line 29. Old: "mirror x -> 1697 - x, middle solved". New: "a 1696 completion with the base and pivot reflected (... 1..537 reflected by x -> 1697 - x, the middle searched by SAT without a symmetry constraint)". Added the audit's base facts: 375 positions freed, and the two bases differ by 16. Line 31 now says "0 conflicts and 0 decisions".
   - Line 33 (`reproduce.py`). Added: it takes only the first 536 entries of its first input, reconstructs the middle and suffix, and uses the second input only for comparison. The audit repeated it with `witness.json` as both inputs and got the same SHA-256.
   - Line 37. Old: "on at most 2 cores at a time. All solver calls used the CaDiCaL 3.1.0 binary ... Every call is logged with its seed, conflicts and seconds." New: "normally two processes at a time, with a brief third-process overlap during breakout calibration. CPU time and peak memory were not measured. The main SAT runs used the CaDiCaL 3.1.0 binary...; an early calibration used PySAT's CaDiCaL 1.9.5... Completed calls have status records with seed, conflicts and seconds; duplicate generation summaries and interrupted calls have less detail."
   - Line 47. Old: "Each call renames the variables ... and runs CaDiCaL with --seed, --shuffle and --shufflerandom." New: the `schur.py` binary wrapper does that, and "The final cube runner in `cnc.py` passes a seed without those flags." Checked in `cnc.py:36`.
   - Line 53. Old: "Validation: base fixed, 537 in colour 6, mirror x -> 1697 - x". New: "a 1696 completion with the base and pivot reflected". Line 54. Old: "Every third passing base". New: "Passing bases number 1, 4, 7 and so on, and any base 120 or more positions from Rowley's". Checked in `bases.py`: `npass % 3 == 1`.
   - Lines 55 and 73. Old: "Cubes split on ... (16 cubes)"; "It timed out at 90 s for F = 350 and F = 300". New: "Each split proposed 16 cubes ... Only calibration samples were run". The calibration line now reads "The first F = 300 run logged five time limits at 52 to 60 s, and the later known-positive cube hit the 90 s limit at F = 350 and F = 300."
   - Line 63. Old: "five calls of 600 s". New: "five calls with a 600 s solver limit".
   - Line 70. Old: "Rowley's base, 537 in colour 6, mirror x -> 1697 - x. SAT at 1696". New: "Rowley's base with base and pivot reflected (x -> 1697 - x). A 1696 completion: SAT...".
   - Line 79. Old: "60 distinct bases were generated ... 55 reproduced a mirrored 1696 completion". New: "The many-bases line generated 60 distinct base vectors by the end ...; the push line separately produced one additional base, `p4_0001`. 55 of the 60 gave a 1696 completion with the base and pivot reflected".
   - Lines 84-93 (mode table). Kept: the audit says these counts match the logs.
   - Line 94. Old: "That covers bases `b1_0014` and `p4_0001` and the targets 1699, 1700 and 1701." New: "Both bases ... were tested at 1699 and 1700; only `b1_0014` was tested at 1701. ... Soft push modes varied the colour-6 exclusion cutoff with the prefix length and left 537 free." "timed out" became "hit their time limit".
   - Lines 95-100. Old: "time limit, 600 s" on each line. New: a header "(600 s solver limit; measured elapsed times of the time-limited calls were slightly above 600 s)" and the lines say only "time limit".
   - Line 101. Old: "Best 5 violations (run A, 4,449,280 steps) and 6 violations (run B, ...)". New: these are counts recounted on the saved best vectors, and the step counts include weight-increase iterations. Added: "A low count is not a sign that a 1699 partition is close", with the audit's (3, 14) breakout calibration as the reason.
   - Line 103. Old: "The 1698 colouring was found at 19:34:16 UTC." New: "CaDiCaL found the witness at 19:34:16 UTC, about nine minutes into the run, from the fourth distinct base generated." The pause is now "around 20:30 to 20:42 UTC", and the bases and long-call logs contain results from that interval.
   - Lines 107-109. Old: "Unit propagation alone rejects Rowley-style bases ... for most bases"; "appears to need a base prefix unlike Rowley's below 200 ..."; "cannot be extended ... because every colour then has a pair summing to N + 1. That is why top windows failed." New, in the audit's terms: in `shift1697` and `sym1698` with the full base fixed, every tested instance was rejected at the root except the witness. The F >= 200 result applies only to the specific templates and prefix vectors tried. Fixed reflection pairs block each colour at 1699 for the 300- and 500-position windows of `p4_0001`. At 700 and 900 the solver also said UNSAT at the root, but direct fixed pairs block only six and zero colours, so that argument does not explain those two.
   - Line 117. Old: "No calls longer than 600 s." New: "No solver time limit above 600 s."
   - Line 142 (Files). Added what a full historical replay would still need (the workbook and extraction step, pinned dependencies, the original controller arguments and logs, the two earlier `push.py` versions).
   - Removed every phrase that presents 1698 as a first or a record. `grep -n -i -E "\bfirst\b|record|solved"` on notes.md now finds only technical uses ("first 536 entries", "first search process", "records exit status") and the sentence "It is not a new record."
4. New section "Prior public bound". It gives the DOI, title, creator, licence, the Zenodo and DataCite dates, and what the deposit states. It says the certificate passes the Frontier verifier after label conversion, that ours was found independently on 17 Nov without knowledge of it, the Hamming distance of 172 and the differing class sizes, and that the catalog still lists 1696. It quotes the checker's line verbatim and says the checker compares against the catalog only.
5. New section "Ramsey consequence", attributed to the audit: colouring edge ij of K_1699 by the class of |i - j| gives R_7(3) >= 1700, the same bound the October deposit states.
6. New section "Provenance and rights". It cites arXiv:2107.03560 and its ancillary workbook URL and SHA-256 directly. The base descends from the workbook's 1..536 prefix (labels shifted to 0..5), modified at the 28 listed positions. arXiv distributes the paper under its non-exclusive distribution licence, not CC BY 4.0, although the catalog labels the reference CC BY 4.0. The witness is a new colouring vector, not a copy of the workbook. These are stated as facts for the submitter to weigh, and the section does not decide the question.
7. Follow-ups section ("What a later attempt should try"). The audit's leads come first, each labelled: the 537-element six-colour bases with pivot 538 (method); the October 1698 partition as a repair seed (method); cube-and-conquer with shorter prefixes or more diverse low positions (method, time relevant only to the short-prefix timeouts); keep instance specifications and proof certificates. The two original leads not covered by these follow.
8. Disclosure: added `gpt-6.2-sol` / `openai` / `auditor` in the existing YAML shape. No corrections entry, since I am the author model. See Deviations for the python-sat role.
9. New section "Independent audit". It says the auditor wrote its own checker first, replayed the completion to the identical SHA-256, built a separate SAT encoder that reproduced the witness, reran representative positive and negative instances, recounted the logs, and ran the literature search that found the earlier bound. It lists the corrected statements and calls the audit an opinion backed by reruns, not a repository-verifier check.

**Rules items 2 to 8.**
- Item 2: the auditor's measurements are listed in the "Independent audit" section and marked as the audit's, not the original run's. They cover generation-call counts, the 27th base's time, asymmetric positions in the validation outputs, the full-mirror recheck of the standalone bases, push-log counts and the longest UNSAT, the five restricted negative reruns with times and conflicts, the breakout calibration on (3, 14), and the controls.
- Item 3: there is no "exhausted", "locally optimal", "rigid", "does not work" or "do not repeat". The near-miss residues are framed as not closeness.
- Item 4: the audit's leads come first.
- Item 5: kind is still `witness`, and declarations are still `{ rights: false, disclosure_complete: false }`.
- Item 6: see 8 above.
- Item 7: `grep -rn -E "/Users/|/home/"` on the attempt directory finds nothing, before and after. The only personal names are scholarly citations (Rowley; the deposit's author). The audit found no copied third-party code or text, and the workbook's colour data is handled in the provenance section.
- Item 8: see 9 above.

**Title in full:** "Many 6-colour bases + Rowley's construction (SAT, 2 h): a symmetric 7-colour Schur partition of 1..1698; ties the public bound of 26 Oct 2026"

**Claim in full:** "Frontier's verifier accepts witness.json as a partition of 1..1698 into seven sum-free sets, including the case x = y. It exceeds the catalog's 1696 baseline from Rowley (2021) and ties the public lower bound reported in Zenodo DOI 10.5281/zenodo.23670665 on 26 October 2026. This partition differs from the Zenodo partition even after relabelling the colours. It uses Rowley's construction with a different six-colour base and is symmetric under x -> 1699 - x. The exact value of S(7) remains unknown. It is not a new record."

**Verification.** `bun install` succeeded and `git diff --check` passed. `bun run check`: `tsc --noEmit` passed, and tests gave 434 pass, 1 skip, 0 fail (435 tests, 34 files). Its validate step then exited 1 with only "declarations: not confirmed" lines, 13 of them, one per swarm attempt, as expected by design decision 6.

`bun frontier check attempts/witness.schur-7/20261117-terramind-com-f3ecc4` (exit 0):

```text
$ bun src/cli.ts check "attempts/witness.schur-7/20261117-terramind-com-f3ecc4"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
verified: Valid witness for witness.schur-7 with value 1698; beats the best known (1696, Rowley, arXiv:2107.03560).
```

`bun frontier validate attempts/witness.schur-7/20261117-terramind-com-f3ecc4` (exit 1, declarations only):

```text
$ bun src/cli.ts validate "attempts/witness.schur-7/20261117-terramind-com-f3ecc4"
attempts/witness.schur-7/20261117-terramind-com-f3ecc4/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

- **Title.** It is longer than the brief's example. The brief's example drops the method ("many 6-colour bases", "SAT") and the budget ("2 h"), and rules item 5 requires both, so I kept them and added the brief's wording after them.
- **python-sat role.** Changed from "cardinality encoding" to "cardinality encoding and early calibration solving (bundled CaDiCaL 1.9.5)". The audit established that an early calibration solved with PySAT's CaDiCaL 1.9.5, and the notes now say so. The entry itself is kept.
- **Push windows.** In "Measured" I kept "top windows of the 1698 colourings" rather than the audit's "`p4_0001`". `push.py:69-72` builds windows from every pool colouring, and I cannot tell from the shipped files which bases the last push version ran windows on. The audit's `p4_0001`-specific blocking statement is kept in "Inferred, not proved".
- **Creator's name.** The brief asks for the creator here and in notes.md. It is the public author of a cited deposit (scholarly attribution, like Rowley), not a private name.
- **Handoff file.** Identical copies are committed at `handoffs/correct-schur7-r2.md` (the brief's name) and `handoffs/reword-the-1698-schur-witness-lfam7.md` (the swarm handoff name).

## Concerns

- **Rights.** arXiv distributes Rowley's paper under its non-exclusive distribution licence, but the catalog labels the reference CC BY 4.0. The witness's first 536 colours equal the workbook's except at 28 positions. Whether that matters for submitting under CC BY 4.0 is the submitter's call before `rights: true`. The notes state the facts and do not decide it.
- **Similar to the deposit.** The deposit is also symmetric under x -> 1699 - x and was also seeded from Rowley's 1696 colouring, so the two are close relatives: Hamming distance 172 of 1698 at the identity relabelling. The notes say so plainly. A reader could reasonably see the attempt as a second, independent instance of a known bound rather than as new information.
- **Catalog.** The catalog's 1696 means the checker will keep printing "beats the best known" for this witness, and on merge CI may show a status of `record-improved`. That would misrepresent a tie with a public bound. A separate maintainer change should update the baseline (problems/ is out of scope for this task).

## Follow-ups

- **Maintainer change:** update the `witness.schur-7` best-known value to 1698, citing the Zenodo DOI, and decide how a valid witness that ties the bound is recorded. Do this before this attempt is submitted, or the site will show it as an improvement.
