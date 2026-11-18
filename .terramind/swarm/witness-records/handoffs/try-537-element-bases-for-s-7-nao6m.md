Best N accepted by the repo verifier for a partition this task produced: 1698 (calibration rebuilds from the repo and Zenodo prefixes). It ties the public bound of 1698 and does not pass it. No N ≥ 1699 was found. The best colouring in the pivot-538 family is N = 1612.

## Done

**Attempt.** `attempts/witness.schur-7/20261118-terramind-com-f211f6`, kind `writeup`. Title: "Pivot 538 over the 131 published 537-element six-colour bases, plus Zenodo-1698 seeds (SAT with mirror, 2 h budget): no partition of 1..1699, does not pass the public bound 1698". The directory holds `writeup.md` and 19 search scripts. All are the author's own except `schur.py`, which is copied unchanged from attempt `f3ecc4`. Declarations are left false and nothing was submitted.

`bun frontier check attempts/witness.schur-7/20261118-terramind-com-f211f6`:

```text
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

`bun frontier validate` on the attempt reports only "declarations: not confirmed". `bun run check`: type check passes, 434 tests pass, 1 is skipped and 0 fail. Validate then fails only with the 14 "declarations: not confirmed" lines of the swarm's attempts.

**Result**

- Catalog record: 1696. Public bound: 1698 (Zenodo DOI 10.5281/zenodo.23670665, 26 Oct 2026, re-downloaded, SHA-256 `33f2f6c3…809e7`, valid by my checker and `diagnose`).
- Best reached:
  - pivot 538: N = 1612. All 131 bases are SAT at 1612 with the full base fixed, and `diagnose` accepts one at value 1612.
  - overall: 1698. Calibration rebuilds tie the public bound.
- Search ran from 22:37:10 UTC on 17 Nov to 00:21:07 UTC on 18 Nov: 103 min 57 s of the 120 min budget, at most 2 solver processes, apart from a 4 s overlap at 22:41.
- Exit statuses: every process exited 0, except the ladder and sweep v1 to v4, which I stopped by SIGTERM to restart with a changed configuration (each logged in `budget.txt`).
- Search calls, calibration excluded: 3,548 UNSAT, 199 undecided (conflict limit), 3 binary time limits, and 794 SAT. All 794 SAT calls are at N ≤ 1612.

**Findings**

- **The S(6) ≥ 537 bases are published.** arXiv:2610.31362 (CC BY 4.0) has 131 machine-readable bases in its ancillary file `solutions537.txt`. All 131 verified, and they are cited, not copied.
- **Full 537-base fixed.** Pivot 538 is SAT up to N = 1612 = 3 · 537 + 1 for every base, under both mirror modes. It is UNSAT at every N tested from 1613 to 1619, and at the root at 1620 to 1690 and 1699 to 1704.
  - `propchain.py` traces the root failure. 538 and its mirror N − 537 are both colour 6, which bars (N − 537)/2. That forces a run of colour-6 integers until N − 1075 has no colour.
- **Line (a), core-guided descent, at 1699 to 1704.** Every base tried is UNSAT once its first 131 to 147 integers are fixed (63 for the asymmetric base F5.001). Shorter prefixes stay undecided at 100k conflicts.
  - Full mirror: 56 bases at 1699 and 1701.
  - Partial mirror: 8 bases at each N from 1699 to 1704.
- **Rowley-family prefixes under pivot 538.** UNSAT for F ≥ 66 to 70.
- **Line (b), Zenodo seed.**
  - The pivot-537 template with Zenodo 1..F is UNSAT for F ≥ 66 at 1699, 1700 and 1701.
  - At F = 56 (1699, full mirror), all 36 cubes are UNSAT.
  - All 54 freed windows of 200, 400 and 600 positions are UNSAT at the root.
  - Prefixes of 700 or more with no mirror: UNSAT. 1..537 with no mirror: time limit.
- **Line (c), cube-and-conquer.** 40 of 40 cubes UNSAT on five instances. All 16 cubes UNSAT for F1.026 at F = 137 (1699, full mirror).
- **Line (d), other bases.**
  - Suffix-fixed bases (S..537 only): UNSAT for S ≤ 300, undecided at S = 400 for 6 of 7 bases.
  - Joint runs with the whole base free: 7 runs, at 4 M or 15 M conflicts, all undecided.
- **LRAT.** Five UNSAT instances (P1 to P5) were proved with CaDiCaL `--lrat` and lrat-check reported VERIFIED, with a truncated-proof negative control. Proof files were deleted after recording SHA-256 and the verdict.

**Evidence.** Worktree `decisive-steppe`, scratch `.terramind/scratch/schur7-538/`.

- `prior-art.md`.
- `logs/budget.txt`: every process with PID, args, UTC start and stop.
- `logs/*.exit`.
- Search logs:
  - `logs/sweep*_w*.jsonl`: line (a) and (b1);
  - `logs/search.jsonl`: binary ladder;
  - `logs/zenwin.jsonl`, `logs/zenpre.jsonl`;
  - `logs/cnc.jsonl`, `logs/suffix.jsonl`, `logs/joint.jsonl`;
  - `logs/proofs.jsonl`: hashes and verdicts.
- `logs/report.md`: aggregate tables.
- `logs/bun_check.log`.
- Calibration: `logs/calib.jsonl`, `logs/calib_incr.jsonl` and `logs/calib_diagnose.log`.
- Inputs: `inputs/`, plus downloads in `dl/`.
- SAT outputs: `out/`.

Calibration results:

- Checker: 0 violations on both 1698 partitions, 21 on the broken copy, and `diagnose` agrees.
- Binary SAT: K = 3 is SAT at 13 and UNSAT at 14.
- Pivot-537 symmetric 1698 with the repo or Zenodo prefix fixed (F = 536 down to 100): SAT, 0 violations, accepted by `diagnose`. The repo prefix reproduces the repo witness exactly. Both prefixes time out at F = 50.
- Planted 300-position refill: restored.
- Full mirror at 1697: UNSAT, as predicted.
- Incremental path: SAT on the same controls.
- Cube-and-conquer: the known cube at F = 50 is SAT in 31.5 s.
- Pivot 538: SAT at 1612 for all bases.

## Deviations

- **Conflict budgets instead of wall-clock caps.** PySAT's interrupt timer did not fire (an 8 s cap ran for more than 3 minutes). From sweep v3 on, the incremental runs use conflict budgets, and "LIMIT" means undecided. Binary runs kept wall-clock limits.
- **F went below 300.** The brief's F sweep "537 down to about 300 in steps" was replaced by a core-guided descent. On UNSAT, the core's largest fixed position gives the next F. It went far below 300 at little cost.
- **Not every base in every mode.**
  - Full mirror at 1699 and 1701: 56 of 131 bases (all five families). The F1 results were uniform.
  - Partial mirror at 1699 to 1704: 8 sampled bases.
  - Full mirror at 1702: joint runs only.
  - N = 1703 full is impossible (3 divides 1704), so it was not run.
- **Line (d) changed.** Instead of generating new bases at a minimum Hamming distance and repeating (a), I ran:
  - suffix-fixed bases;
  - joint runs, where the solver builds a new base together with its extension.

  The reason: the cores showed that the low part of any published base already rules out the extension, so a base generated on its own would likely fail the same way.
- **Extra lines.** Added an N ladder, the exact top N for full bases, and Rowley-family prefixes under pivot 538, to locate where the family stops.
- **More proofs.** Five LRAT proofs instead of three. P1 and P3 are root refutations, P2, P4 and P5 are non-trivial.
- **Budget.** 104 of 120 minutes were used.
- **Two handoff files.** This handoff is written to both `schur7-538.md` (the brief's name) and `try-537-element-bases-for-s-7-nao6m.md` (the harness name), with identical content.

## Concerns

- Cores from PySAT are not minimal, but they are sound for the "every F ≥ p is UNSAT" inference. Apart from P1 to P5, all UNSAT claims rest on CaDiCaL without proofs.
- The encoder (`schur.py`, from f3ecc4) is not formally verified. It passed full-size positive controls, but LRAT certifies only the CNF.
- Complete cube coverage relies on PySAT's propagation to list the allowed colours.
- The template forbids colour 6 on all of 1..537 and on its mirror. Constructions that put the seventh colour inside the base are not covered.
- The machine load average was about 14 on 14 cores. Per-process CPU seconds were not measured. Summed per-call solver time is in `report.md`.
- The catalog still says 1696, so `check` and `diagnose` print "beats the best known" for any 1698. The 1698 rebuilds here only tie the public bound and are not filed.

## Follow-ups

- A long joint search (whole base free) with cube-and-conquer at 1699 and 1701 full. A pivot-538 extension needs a base whose first ~140 positions differ from all 131 published bases.
- Pivot 538 with the Rowley-family low prefix (1..50 to 56, where it is undecided) and the rest of the base free.
- Non-symmetric constructions at 1700, where the full mirror is impossible. Other pivots.
- A maintainer PR to update `problems/witness.schur-7.yaml` best_known to 1698 (Zenodo) is still a maintainer decision.
