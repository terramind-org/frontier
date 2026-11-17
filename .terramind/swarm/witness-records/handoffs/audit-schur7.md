# Audit: witness.schur-7 attempt 20261117-terramind-com-c8ca32

Auditor: claude-opus-5-5. This audit is an opinion backed by reruns. It is not a verdict of the repo checker. No colouring of 1..N with N >= 1697 was found during the audit.

Outcome: OVERSTATED. The search is valid and its key negative result holds. I re-derived it with my own encoder and solver build, and lrat-check verified an LRAT certificate for it. Three passages must be corrected: the template passage and its follow-up describe a dead end as untried, and the reflected-placement passage and the SAT controls describe trivial checks as search. The corrected wording is under Concerns, items C1 to C3.

Auditor scratch (git-ignored): `.terramind/scratch/audit-schur7/` in the worktree `provincial-haven`. My scripts there are `enc.py` and `enc2.py` (DIMACS encoders), `decode.py` and `count.py` (my own colouring checker), and `probes.sh`. I wrote all of them and imported none of the author's code. Solver: CaDiCaL 3.1.0 (`6b3d70b9`), built from github.com/arminbiere/cadical. Proof checker: `lrat-check` and `drat-trim`, built from github.com/marijnheule/drat-trim. Python 3.12 with python-sat 1.9.dev22 and xlrd, in a fresh `uv venv`.

## Done

### 1. Baseline
- `bun frontier diagnose <author scratch>/baseline.json --problem witness.schur-7` returned `value: 1696`, `valid: yes`, `ties the best known value`, exit 0.
- I downloaded the ancillary file myself: `https://arxiv.org/src/2107.03560v1/anc/Specimens_S_7____TFTs-4,5,6.xls`. Its SHA256 is `c50cf981…6fbb`, identical to the author's file and to the hash in writeup.md. It is an Excel file, author "Fred Rowley", last saved 8 Jul 2021.
- My own reader takes the integer and subset columns from the sheet `S(7) >= 1696`. The integers are exactly 1..1696 and the labels are 1..7. After subtracting 1, the result is entry-for-entry equal to the author's `baseline.json`.
- `count.py` (my checker) reports `N 1696 violations 0`. Class sizes for colours 0..6: 204, 176, 318, 152, 148, 200, 498.
- Structure: colour 6 is a subset of 537..1160 with nothing at or below 536. The colouring is fully symmetric: c(i) = c(1697−i) for all 1696 integers. This matches the paper (rowley.txt lines 107–118).

### 2. Is the UNSAT real? Yes. It is now LRAT-certified.

**(i) Code reading of sat.py and windows3.py.**
- Exactly-one per free integer: sat.py:18–20.
- Every pair x ≤ y with x + y ≤ N, including x = y, is covered: sat.py:21–22 loops `x in 1..n//2`, `y in x..n-x`. When x = y, `vs` is the 2-set {x, 2x}.
- Simplification is sound:
  - A triple whose fixed members have two or more colours is skipped. It can never be monochromatic.
  - A triple that is all fixed and monochromatic adds the empty clause.
  - Otherwise the clause gets one negative literal per free member, for the single fixed colour, or for all 7 colours if no member is fixed.
- Indexing is consistently 1-based: `base[x-1]`, and `v(x,c)=(x-1)*k+c+1`.
- windows3.py:8 sets `free=range(1697-w,1697)`. For w = 1250 that is 447..1696.
- sat.py:12 adds `original_length+1..n`, which brings 1697 into the free set.
- The retained `finalwindow1250_n1697_round1.spec.json` has `effective_free` equal to 447..1697 exactly: 1251 integers, so 1..446 are fixed.
- There is no symmetry breaking. The `different` clause is not used in windows3. `set_phases` only sets preferences.
- The log `finalwindow1250_n1697_round1.log` reads `RESULT False seconds 405.48`, with 4,870,267 conflicts and 1,628,827 clauses. This matches the writeup.

**(ii) Independent rebuild.** `enc.py 1697 7 446 baseline.json` writes a plain CNF with a different encoding from the author's:
- at-least-one colour per integer, with no at-most-one clauses;
- every (x ≤ y, colour) triple clause, with nothing simplified away;
- positive and negative unit clauses fixing 1..446 to Rowley's colours.

The result has 11,879 variables and 5,044,483 clauses, which is 7 × 719,952 + 1697 + 7 × 446. Its SHA256 is `27a91e8b…b0da`. This formula is weaker than the author's, so its UNSAT is the stronger statement.

`cadical --lrat --binary=false cnf/n1697_f446.cnf proof_n1697_f446.lrat` returned `s UNSATISFIABLE` and `exit 20`, in 373.7 s wall (360.1 s process time), with 5,361,997 conflicts and 8,977,122 decisions.

`lrat-check cnf/n1697_f446.cnf proof_n1697_f446.lrat` returned `c VERIFIED`. Verification took 30.4 s, with 10,860,013 added and 10,263,118 deleted clauses and 127 MB peak RSS.

The checker's negative control: the same proof truncated to its first 2 GB returned `c NOT VERIFIED … Verification incomplete`, exit 1.

The proof stays in scratch: 2,147,056,325 bytes, SHA256 `3c59f0ff…06b1` (`proof_n1697_f446.sha256`).

So this statement is now certified for my CNF: "no 7-colour Schur colouring of 1..1697 agrees with Rowley's colouring on 1..446". Two parts of the chain are not formally verified: the 40-line encoder `enc.py`, and the fact that lrat-check itself is unverified C. No second solver was needed once the certificate checked.

**(iii) Known-answer controls.** All pass on both encoders.
- Mine: K=3, N=13 SAT (decoded, 0 violations); K=3, N=14 UNSAT; K=4, N=44 SAT (0 violations); K=4, N=45 UNSAT in 97.5 s.
- The author's sat.py child, run on a copy in `author/` with all integers free: the same four answers. K=4, N=45 was UNSAT in 69.2 s.
- The 7-colour control at N=1696 with 1..446 fixed was SAT in 8.4 s on my encoder, with no phase hints. The decoded colouring has 0 violations and `bun frontier diagnose` accepts it (`valid: yes`, ties). It differs from Rowley's colouring at 140 of the 1250 free positions, so this is a real positive control.
- The author's own 1696 control returned Rowley's colouring unchanged, with 0 of 1250 free positions different. sat.py:33,38 set the phases to the baseline, so that control only shows the encoding does not exclude the known solution. See C3.

**(iv) Plausibility and the boundary.**
- Unit propagation decides little. Eliminating colours by fixed pairs leaves 812 of the 1251 free integers with all 7 colours and 190 with 2 colours. Only one free integer is forced. The UNSAT needed about 5 million conflicts in both encodings. It is a real search result, not a trivially propagated one.
- Boundary probes: my CNF at N=1697, fixing only the first F colours. None of these runs produced a result line (`s` count 0 in each .out).

| F fixed | Result | Time | Conflicts |
|---|---|---|---|
| 446 | UNSAT, LRAT-verified | 373.7 s | 5,361,997 |
| 400 | unknown | 420 s limit | 3,320,937 |
| 300 | unknown | 600 s limit | 5,267,182 |
| 200 | unknown | 420 s limit | 3,063,520 |
| 100 | unknown | 300 s limit | 3,414,963 |

- What is proved: only the F = 446 statement, for the colours 1..446 of Rowley's ancillary partition. Smaller F is open at these limits.
- The author's 1001..1200 windows (UNSAT in windows.log and windows2.log) and stage-1 top windows of 32..1000 (sat.log) fix supersets of 1..446, so the certified result implies them. They are consistent and monotone: no smaller window is SAT while a larger one is UNSAT. Their own runs carry no certificate.

### 3. Local search
- **Objective.** local-v2.cpp:14–15 builds triples `x=1..n/2, y=x..n−x`, with the x = y triple as the 2-element {x, 2x}. Line 47 rechecks the incremental count against a full enumeration every 10,000 steps.
- **The saved best colouring.** `author-local-best.json` is a copy of scratch `local-best.json`. My `count.py` reports `N 1697 violations 5`: (537, 537, 1074), (537, 663, 1200), (537, 668, 1205), (537, 794, 1331), (663, 668, 1331), all in colour 6. `bun frontier diagnose` rejects it: `valid: no, violations (5)`, listing the same five triples.
- **Positive control.** I copied local-v2.cpp with exactly two edits (shown by `diff`): `n=1697` became `1696`, and the `restart==0` self-test block, which requires a valid prefix, is disabled. I seeded it with Rowley's 1696 colouring after random changes:

| Changed integers | Starting conflicts | Time to zero conflicts |
|---|---|---|
| 5 (seed 1) | 538 | 0.41 s |
| 5 (seed 2) | 444 | 0.02 s |
| 5 (seed 3) | 60 | 0.01 s |
| 50 | 1,751 | 48 moves |
| 200 | 6,878 | 202 moves |
| 600 | 13,180 | 1,256 moves, 0.23 s |

  The tool can repair a broken valid colouring, so "best 5 at N=1697" is a genuine score of a working search.
- **Context for that score.** The monitor shows `current` at 77, 49 and 39 in the last minutes. The 5 was reached once, at 1373 s of local3. local3 started by `RESUME best 6` from `local-best.txt`, which was written during the mixed two-process interval. The writeup says the 5 came from the clean run. That is true, but its starting point came from the mixed one.

### 4. Templates and the reflected completion
- **Formula.** templates.py:8–18 implements Rowley's product construction, S(k+q) ≥ m·S(k) + φ (rowley.txt lines 136–158). The φ values match the ancillary sheet `TFT-4,5,6` (6, 39 and 160 for m = 33, 109 and 376).
- **Reproduction test.** The author's `product376.json` equals Rowley's published sheet `S(7) >= 1664` entry for entry, up to a bijective relabelling of colours ({4→5, 1→2, 0→1, 2→3, 3→4, 5→0, 6→6}). So the template code reproduces Rowley's product partition.
- **The template code cannot reproduce 1696, and is not meant to.** The 1696 partition is not a product construction. The paper (lines 107–113) builds it by fixing a 6-colour partition of 1..536, setting 537 to colour 7, mirroring x ↦ 1697−x, and tree-searching the middle 538..1159.
- **Testing that method.** I fixed Rowley's 1..537 and its mirror at N=1696 (`enc2.py`, `fix_orig_1696.json`). The result was SAT with 0 conflicts in 0.68 s, so the method works for the original base.
- **Excluded variants.** I independently checked the five `basevariant*.json`. Each has length 536, colours 0..5 and 0 violations, and differs from Rowley's base in 23 or 24 positions (`UNIQUE_BASE_VARIANTS 2 of 5` in variant-controls.log). Their mirrored 1696 completions are UNSAT at the root in the author's logs (1 conflict, 0 decisions). Variants 0 and 2 also gave UNSAT with 1 conflict on my encoder. Excluding them is correct: they cannot reproduce 1696.
- **Reflected placements.** experiments.py:24–30 tried reflected placements of the original base at orders 1697 to 1712. All five are UNSAT at the root in stage2.log (0–1 conflicts, 0 decisions). I reproduced reflect1697 and reflect1712 (`s UNSATISFIABLE`, 1 conflict, 0 decisions).
- **Their "controls" are not matched.** experiments.py:28 runs the 1696 control with the baseline fixed outside the middle, not the shifted mirror, so it is trivially SAT. See C2.
- **Arithmetic bound.** With the exact values S(2)=4, S(3)=13 and S(4)=44, the three templates give at most 376·4+160 = 1664, 109·13+39 = 1456 and 33·44+6 = 1458. None can reach 1697 with any base. templates.py:19 used a 39-length 4-colour base, which gives 1293. See C1.

### 5. Did the search really run? Yes.
- **Times.** search.out shows `START 2026-11-17T16:09:00Z`. windows3.log shows `END 2026-11-17T18:08:50.095` and monitor.log shows `END seconds 5549.01 moves 112873492 restarts 113 best 5` at 18:08:51. That is 119 min 50 s ✓.
- **Stage switches.** stage-transition.log records each switch with its PIDs: 16:14:49, 16:21:37, 16:25:34, 16:29:40, 16:35:46 (the resource deviation), 16:36:20 and 17:11:40.
- **The overrun.** ps lines show two `local-v2` processes started 16:21:46 and 16:21:56 UTC with about 14:00 elapsed, so the 14-minute overrun is substantiated ✓.
- **Exit statuses.** search.out has `EXIT local=143 sat=143` ✓. sat.log has 61 child EXIT lines: 60 with code 0, plus `top1160_n1697 124`. The last EXIT is `base536_N1697_n1696 0`, and its N=1697 partner was killed at the stage switch without an EXIT line. That job's N=1698 and N=1700 cases never ran; the writeup does not claim them.
- **Move totals.** local3.log has 112,873,492 moves and 113 restarts ✓.
- **Candidate audit.** My recount of candidate-audit.jsonl: 688 rows, 688 unique files, 395 `valid: true`, 293 `valid: false`, maximum accepted value 1696, 0 `beats_best_known`. The current files' SHA256 values match all 688 recorded hashes. My own checker run on all 688 files agrees with the repo verifier on every one (395 valid in both, 293 invalid in both). The 292 files at N=1697 have at least 5 violations each.
- **Repair jobs.** repair-five.log has 10 RESULT pairs and repair-three.log has 15, so 25 target jobs, all `RESULT False` ✓. stage2.log also has 287 `PAIRED_REPAIR … control True target False` lines that the writeup does not mention. Leaving them out understates the work, not the result.

### 6. Text against evidence
- **Supported by the logs:** the title; claim (a); claim (b), now certified; claim (c), including its numbers; claim (e); the timing; the overrun; the 124/143 statuses; the clause and conflict numbers; the tabu tenure 7..23 (local-v2.cpp:46, `7+rng()%17`); local.cpp's seed 7301698, 100,000-step restarts and 2% noise; local-v2's 0.1, 0.5 and 1% noise (line 45); and the 1300 window and larger ones ending unknown (windows3.log PAIRED_WINDOW lines).
- **Five conflicts** is not presented as closeness. The writeup says "No lower bound on the minimum possible conflict count is claimed."
- **The UNSAT statement names the fixed colours exactly:** "integers 1 through 446 fixed to Rowley's colours".
- **Wording rules:** no "solved". The writeup says "not machine-checked" twice and the claim says it once. It does not call the tie an improvement.
- **Inference presented as measured.** writeup.md says "The final SAT controller and final local-search process both exited 0". The logs only contain the programs' own printed strings: local-v2.cpp:50 prints a hard-coded `exit 0`, and windows3.py:40 prints `'exit 0'`. No shell exit status was captured for local3 or windows3. The inference is sound, because both programs ran to the end of main, but the status was never measured.
- **Disclosure.** attempt.yaml lists the models gpt-6.1-sol (author) and claude-fable-5-2 (planner), and the tools CaDiCaL195, python-sat, the custom C++ tabu search, Python, xlrd, clang++, Frontier CLI, curl, pdftotext, Bun and uv. That is complete. numpy was installed (commands.txt) but no attempt script imports it. Declarations are `rights: false` and `disclosure_complete: false` ✓.
- **Licence.** None of the 17 attempt files contains a third-party copyright or licence header. The scripts are original code. No baseline data or paper text is copied in: the colouring is re-extracted by extract.py at replay, and Rowley's paper is CC BY 4.0 per `bun frontier show`.
- **Checks.** `bun frontier check` on the attempt printed `unchecked: Writeups are not machine-checked.` `bun run check` ran tsc (clean) and 427 tests (426 pass, 1 skip, 0 fail). Validate then exited 1, solely for `declarations: not confirmed` on all six swarm attempts, which the design expects.
- **Statements to correct:** C1, C2 and C3 below.

### 7. What was not tried (for a stronger attempt)
- **Rowley's own method at a larger order.** Rowley reports "a profusion" of non-symmetric 1696 partitions and a "highly non-critical" base (rowley.txt lines 114–119). The natural route to 1697 is to generate many 6-colour partitions of 1..536 (or of 1..m for m near 536), each first shown to reproduce a mirrored 1696 completion, and then attempt N=1697 with the mirror x ↦ 1698−x or with no mirror. The attempt generated only 2 unique bases, both root-infeasible even at 1696.
- **Non-symmetric completions at 1697 with the middle free.** The certificate rules out all of Rowley's 1..446. A stronger attempt would fix different prefixes, for example a SAT-generated 1696 partition's 1..446, or shorter prefixes with a cube-and-conquer split (march_cu + CaDiCaL), rather than single 300–900 s solver calls.
- **Weighted, clause-weighting local search.** No breakout, PAWS or SAPS variants and no probSAT/yalsat on the CNF. Also: start points other than Rowley's colouring, since every local3 restart descended from it or from local-best.
- **New product templates** with larger m·S(k)+φ, since the three supplied ones are capped at 1664 (C1). Also symmetric-partition searches at N=1697 using Fredricksen and Sweet's symmetric structure.

## Deviations
- My local-search control is a modified copy of local-v2.cpp, with n=1696 and its prefix self-test disabled, because the original hard-codes n=1697 (line 12). I did not run the author's binary unmodified at 1696, because it cannot be.
- I did not run a second SAT solver on the 1..446 instance. A verified LRAT certificate replaces that cross-check. My only second solver was a second encoder on the same CaDiCaL family, which was 3.1.0 (`6b3d70b9`) for my runs against CaDiCaL 1.9.5 for the author's.
- Boundary probes F = 400, 300, 200 and 100 ran at 300–600 s limits. All were unknown. Longer runs would not fit the 60-minute and 2-core budget.
- Wall clock was about 35 minutes of runs plus writing (18:21 to 18:55 UTC) on at most 2 cores. Peak RSS was 935 MB for CaDiCaL with proof output.
- I used no attempt code except a copy of sat.py in `author/`, run on known-answer controls only. Nothing under attempts/, problems/ or the author's worktree was changed.

## Concerns
Wording corrections for the author. These are the reason for OVERSTATED.

- **C1. Templates** (writeup.md, "Construction and repair variations", last paragraph, and "Replay and what to change next").
  - Writeup: "These trials used the supplied templates; they did not optimize their lengths or parameters." and "Weighted conflict search and other product-template parameters remain untried."
  - Corrected: "With the exact values S(2)=4, S(3)=13 and S(4)=44, Rowley's bound S(k+q) ≥ m·S(k)+φ gives at most 1664, 1456 and 1458 for the three supplied templates. None of them can reach 1697 with any base partition. These runs were reproductions: the 376 template reproduces Rowley's published 1664 partition up to colour relabelling. Only a new template could help." Change the follow-up to "new triangle-free templates with larger m·S(k)+φ remain untried".
- **C2. Reflected placements** (writeup.md, same section, first paragraph).
  - Writeup: "I tried reflected placements of the original prefix at orders 1697, 1698, 1700, 1704 and 1712. No accepted extension emerged."
  - Corrected: "Reflected placements of the original 1..537 at orders 1697, 1698, 1700, 1704 and 1712 were each UNSAT by unit propagation alone (0–1 conflicts, no decisions). The 1696 jobs run beside them fixed the unshifted baseline, so they are not matched controls."
- **C3. SAT controls** (writeup.md, "Baseline and checker tests", and the bullet "The length-1696 control …").
  - Writeup: "Each reported top-window UNSAT result had a SAT control at 1696 with the same free baseline positions."
  - Add: "The solver's phases were set to Rowley's colouring, so each control returned that colouring unchanged. The controls show only that the encoding does not exclude the known solution." Optionally the author may add: "An independent audit re-encoded the 1..446 instance, CaDiCaL 3.1.0 returned UNSAT, and lrat-check verified its LRAT proof." That sentence is true, but it reports the auditor's run, not the author's.

Minor, optional:
- Say the "exited 0" statuses are the programs' printed end lines.
- Mention the 287 stage-2 neighbourhood repair pairs.
- Say the local3 run resumed from the best-6 colouring saved during the mixed interval.

Residual doubts:
- The certificate proves my CNF UNSAT. The tie to the intended statement rests on reading `enc.py`. It is 40 lines and passes S(3)/S(4) known answers and a SAT control at 1696 accepted by the repo verifier.
- The proof file (2.1 GB) is in my scratch on a disk that is 96% full. The lead may delete it. Regenerate it with `cadical --lrat --binary=false cnf/n1697_f446.cnf proof.lrat` (about 6 minutes).

## Follow-ups
- If the author keeps the 1250-window claim, attach or describe the certificate route: `enc.py` plus CaDiCaL `--lrat` plus `lrat-check` (30 s). A replay is about 7 minutes.
- A stronger re-run should:
  - generate many 6-colour bases of 1..536 that each first reproduce a mirrored 1696 completion, then attempt 1697 with and without the mirror;
  - use cube-and-conquer for the F < 446 prefix instances that timed out here (F = 100, 200, 300 and 400 were unknown at 300–600 s);
  - use clause-weighting local search from start points other than Rowley's colouring.
- Product templates need a new template; parameter changes cannot help (C1).
