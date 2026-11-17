## Done

**The S(7) record is beaten: the repo verifier accepts a 7-colour sum-free partition of 1..1698. The published record is 1696.**

**Attempt.** `attempts/witness.schur-7/20261117-terramind-com-f3ecc4/`, kind `witness`.
- Title: "Many 6-colour bases + Rowley mirror one order up (SAT, 2 h): 7-colour Schur partition of 1..1698".
- Declarations are left `false`. Nothing was submitted, and no PR to main was opened.
- `bun frontier check attempts/witness.schur-7/20261117-terramind-com-f3ecc4`, verbatim:
  ```
  note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
  verified: Valid witness for witness.schur-7 with value 1698; beats the best known (1696, Rowley, arXiv:2107.03560).
  ```
- `bun frontier validate` on the attempt complains only that the declarations are not confirmed.
- `bun run check`: tsc clean, 434 pass, 0 fail. Validate fails only on the unconfirmed declarations of the 7 swarm attempts (design decision 6).

**Result.** Record 1696; best reached 1698. The verifier says it beats the best known value.
- `witness.json` is byte-identical to scratch `best/N1698_b1_0014_sym.json`. SHA-256: `a3bd293ccede7f6c09530333b54e84f3c2feca3104cf323fdcaca479e7d34da5`.
- `bun frontier diagnose` prints `value: 1698`, `valid: yes`, `beats the best known value`.
- Two independent checkers of my own (`indep_check.py`, pairwise; `indep_check2.py`, class sets, with x = 2x reported separately) both report 0 monochromatic triples and colours in 0..6.
- Two more distinct 1698 colourings are also accepted by `diagnose`: `sols/b1_0134_sym1698soft400.json` (36b53ef4…) and `sols/b1_0182_sym1698soft400.json` (e8e370c7…). So is a non-symmetric 1697 one, `best/N1697_b1_0014_free.json` (3dcfb545…).
- No 1699 partition was found. The best 1699 colourings, from breakout local search, have 5 and 6 violations.

**How it was found.** This is Rowley's own construction one order up.
- Base `b1_0014` is a 6-colour partition of 1..536 that differs from Rowley's in 28 positions. It came from an "alone" base `b1_0008` (a SAT re-solve of Rowley's base with 282 positions freed, which passed the mirrored 1696 check), followed by a joint 1696 re-solve.
- 537 gets colour 6. The colouring is fully symmetric under x -> 1699 - x; 1699 is not divisible by 3, so the full mirror is allowed.
- CaDiCaL 3.1.0 returned SAT at the root (0 conflicts, 0.35 s, seed 781351734) at 19:34:16 UTC, 8.7 minutes into the budget.
- `reproduce.py` replays that call and returns an identical colouring (`logs/reproduce.log`).

**Objective numbers.**
- Bases: 60 distinct bases generated, 20 to 60 positions from Rowley's. 55 reproduce a mirrored 1696: all 51 joint bases and 4 of 9 alone bases.
- Modes over the 55 passing bases:

  | Mode | Results |
  |---|---|
  | shift1697 (x -> 1698 - x, middle free) | UNSAT 55/55 at the root |
  | sym1698 | SAT 1 (`b1_0014`), UNSAT 54 |
  | free1697 | SAT 1, time limit 18 |
  | partial1697 | UNSAT 19 |
  | sym1698soft400 | SAT 3, UNSAT 16 |
  | sym1699soft400 | UNSAT 19 |

- Push at 1699 to 1701: every symmetric or near-symmetric call that fixed 1..200 or more of a base was UNSAT within 9 s. Top windows of the 1698 colouring were root-UNSAT. Calls fixing 1..150 timed out.
- Long calls of 600 s: sym1699 with F = 150 and F = 100, base-fixed free1699, and near1700 with F = 150 all hit the time limit. sym1701 with F = 150 was UNSAT in 532 s.
- Cube-and-conquer: calibration only (see Deviations).

**Timing.** UTC start 19:25:35, last search end 21:23:18, about 118 minutes. Exit statuses, all written by the wrapper:
- bases: 0
- longq: 0
- local search: 0
- three push runs: stopped by SIGTERM to restart with changed modes (`logs/notes.txt`)

The searches ran unattended for about 10 minutes (20:31 to 20:42 UTC) while I was paused at a usage limit. That was inside the budget, and nothing ran past it. All processes I started have ended.

**Evidence.** Worktree `watery-shoal`, scratch `.terramind/scratch/schur7-r2/`.
- Logs: `logs/calib.jsonl` (PySAT run), `logs/calib-bin.jsonl`, `logs/calib-diagnose.log`, `logs/cnc-calib1696*.jsonl`, `logs/bases.jsonl` (444 lines), `logs/push-run{1,2,3}.jsonl`, `logs/longq.jsonl`, `logs/ls_A.log`, `logs/ls_B.log`, `logs/breakout-calib.log`, `logs/final-diagnose.log`, `logs/final-indep-check.log`, `logs/all-candidates-diagnose.log`, `logs/reproduce.log`, `logs/summary.json`, `logs/*.status`, `logs/bun-run-check.log`.
- Colourings: in `best/`, `sols/`, `push/` and `bases/`.
- Calibration:
  - Checker: baseline 0 violations, broken copy 19.
  - K = 3: 13 SAT / 14 UNSAT. K = 4: 44 SAT / 45 UNSAT.
  - Rowley's base mirrored at 1696: SAT, accepted by `diagnose`.
  - Planted refill of 300 positions: SAT, accepted.
  - Full mirror at 1697: UNSAT, as predicted.
  - Cube conquer at 1696: SAT only at F >= 400.
  - Breakout repairs 60- and 400-position perturbations.
- The baseline came from the arXiv ancillary spreadsheet (SHA-256 c50cf981…6fbb). `diagnose` accepts it at 1696.

## Deviations

- **Cube-and-conquer was not run at N >= 1697** (brief step 3).
  - Calibration showed the conquer step finds a known 1696 solution in 90 s only for prefixes F >= 400. F = 350 and F = 300 timed out on the cube agreeing with Rowley's colouring.
  - Then the 1698 colouring appeared 9 minutes in, so core 2 went to pushing N past 1698 (push line, long calls) instead of 1697 cubes.
  - The brief's prefix-cube study is therefore only its calibration.
- **Shifted mirror at N = 1697 replaced in practice.** The brief's "mirror x -> 1698 - x" at N = 1697 cannot work as a full mirror: 566 + 566 = 1132 = 1698 - 566. I kept it as `shift1697` (base mirrored only, all UNSAT at the root) and added the full mirror at 1698 (x -> 1699 - x), which is where the result came from.
- **Solver.** The brief named CaDiCaL via python-sat. PySAT's timed interrupt of Cadical195 hung on this machine, so every search call uses the CaDiCaL 3.1.0 binary (wall-clock `-t`, return codes, stats). python-sat is used only for cardinality encodings and the first calibration run.
- **Local search** ran 26 minutes at N = 1699 rather than 1697, from non-Rowley start points (the 1698 and 1697 colourings).
- **Short overlaps of a third process.** The breakout calibration took about 2 s as a third process while two searches ran. Diagnose and reproduce ran after the budget.
- **Scripts.** `push.py` in the attempt is the last of three versions. Runs 1 and 2 used earlier mode lists, described in `notes.md`.
- **Extra attempt files.** The attempt ships `notes.md` beside `witness.json` for the method description; a witness attempt has no writeup file. The schema allows extra files.

## Concerns

- **Novelty.** "Beats the best known" is relative to the catalog value 1696 (Rowley 2021). I did not search the literature after 2021 beyond the problem's references. If S(7) >= 1698 or more was published elsewhere, this is not new. The verifier's verdict on validity stands either way.
- **The result is at the root of an easy instance.** The SAT came with 0 conflicts (lucky phases). The construction is close to Rowley's, so a reviewer may want to confirm independently that nobody has shown this colouring before. The colouring itself is checked three ways.
- **UNSAT claims** (shift1697, sym1698 for 54 bases, sym1699/1700/1701 with prefixes of 200 or more, sym1701 F = 150) carry solver statistics only, with no DRAT/LRAT proofs. Root-level ones could be certified in seconds if needed.
- **Disclosure lists python-sat** (cardinality encoding, first calibration) and the custom breakout. NumPy was installed but not used, so it is not listed.

## Follow-ups

- **Audit:** re-verify `witness.json` from scratch, rebuild it with `reproduce.py` and CaDiCaL at commit 6b3d70b, and check the claim wording.
- **Next round on Schur 7: N = 1699 (x -> 1700 - x, symmetric allowed).** Use cube-and-conquer with long cubes on the structured instance with a short or empty fixed prefix. The 600 s single calls at F = 100 and 150 were undecided. Also bases whose low part (1..200) differs from Rowley's, since every fixed prefix of 200 or more failed fast.
- **Same method on S(6) or other Schur records:** Rowley-style base plus mirror with many generated bases. One order up worked here after 55 bases, with SAT at the root.
- **Lead decision:** whether and how to present a record improvement to the owner before any submission. Declarations are false and nothing is submitted.
