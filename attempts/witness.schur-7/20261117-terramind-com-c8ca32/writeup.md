# Rowley-seeded SAT windows and tabu search: no extension found

This is a failed search for a seven-colour Schur partition of `1..1697`. The largest accepted object was Rowley's existing partition of `1..1696`. The best observed colouring at 1697 had five monochromatic triples. CaDiCaL reported UNSAT when the first 446 colours of Rowley's partition were fixed and every later colour was free. This writeup is not machine-checked.

The UNSAT result concerns that fixed prefix. The unrestricted 1697 instance timed out. The search supplies no upper bound on the Schur number S(7).

## Baseline and checker tests

The baseline came from the ancillary spreadsheet to [Rowley, arXiv:2107.03560](https://arxiv.org/abs/2107.03560), specifically the sheet `S(7) >= 1696`. `extract.py` reads the integer and subset columns, checks the sequence is exactly 1 through 1696, and subtracts one from the subset labels. Spreadsheet SHA256:

```
c50cf981c1c437557b261cb8a66e193ee2cf77a8a50b0ae70c986b1c1cbb6fbb
```

`bun frontier diagnose` accepted the resulting baseline at 1696 and reported a tie. A deliberately broken copy assigns integer 2 the colour of integer 1. The repository verifier rejected it with 19 violations, including `1 + 1 = 2`. The independent Python enumeration also returned zero for the baseline and 19 for that broken copy.

The SAT encoder passed four small regression cases: one colour at length 1 was SAT, one colour at length 2 was UNSAT, two colours at length 4 were SAT, and two colours at length 5 were UNSAT. Each reported top-window UNSAT result had a SAT control at 1696 with the same free baseline positions. The solver's phases were set to Rowley's colouring, so each control returned that colouring unchanged. The controls show only that the encoding does not exclude the known solution. The final local-search implementation checked 50 randomly chosen move-cost predictions against full triple enumeration and passed them all.

After the search stopped, the repository verifier diagnosed every saved colouring file. The audit covered 688 files: 395 accepted, 293 invalid, zero command or parsing errors, and zero accepted improvements. These are file counts, including repeated controls and intermediate snapshots. The maximum accepted length was 1696.

## SAT search

The solver was PySAT's `Cadical195`, through python-sat 1.9.dev22. There is one Boolean variable per free integer and colour. Each free integer has an exactly-one constraint. For every `x <= y` with `x + y <= N`, each colour gets the clause forbidding all three positions from having that colour. Equal summands are included. Fixed colours simplify the clauses; they do not remove a constraint unless it is already satisfied. SAT assignments were decoded and independently enumerated before repository diagnosis.

The first stage freed top windows of 32, 64, 128, 256, 400, 600, 800, 848, 1000 and 1160 baseline positions. It also tried seeded random subsets, entire colour classes, and residue classes modulo 2, 3 and 4. Later stages enlarged the contiguous windows, increased the per-job limits, and retried timed-out jobs. Initial limits ranged from 90 to 300 seconds; longer retries allowed up to 900 seconds, bounded by the common deadline. Random-subset seeds were 7301697 and 7301699.

The largest completed contiguous-window result was:

- Target length 1697; integers 1 through 446 fixed to Rowley's colours.
- Integers 447 through 1697 free, including the new endpoint. Thus 1250 baseline positions were freed, with 1251 free integers in the target instance.
- 1,628,827 simplified clauses; CaDiCaL returned UNSAT after 405.48 seconds, reporting 4,870,267 conflicts.
- The length-1696 control with the same 1250 free baseline positions returned SAT, and its decoded colouring passed repository diagnosis. Its phases were set to Rowley's colouring and it returned that colouring unchanged; it shows only that the encoding does not exclude the known solution.

The 1300-position window remained unknown when the final deadline interrupted its longer retry. Larger windows also timed out. A fully freed 1697 instance was tried with the five-conflict colouring as a phase preference. That phase seed added no fixed-colour constraints, and the job timed out. The author retained no DRAT certificate for these UNSAT cases; they were solver-reported results with the baseline controls described above and replayable encodings. The independent auditor subsequently checked an LRAT certificate from a separate encoding of the 1..446 fixed-prefix instance, as described below.

## Construction and repair variations

Rowley's paper describes a constrained completion from a six-colour prefix of length 536. Reflected placements of the original 1..537 at orders 1697, 1698, 1700, 1704 and 1712 were each UNSAT by unit propagation alone (0–1 conflicts, no decisions). The 1696 jobs run beside them fixed the unshifted baseline, so they are not matched controls.

Five SAT requests generated six-colour partitions of length 536 distinct from the original prefix, while fixing its first 100 entries. Those requests produced only two unique variants. Their reflected length-1696 completion controls were UNSAT too. They therefore failed as replacement seeds even at the known length; their failed extension jobs add no evidence about the attainable global bound.

`templates.py` also rebuilt seven-colour constructions from all three supplied product templates. The length-33 template combined with a derived four-colour partition of length 39 gave 1293; the length-109 template with a three-colour partition of length 13 gave 1456; the length-376 template with a two-colour partition of length 4 gave 1664. Repository diagnosis accepted all three. The composition follows [Rowley's linear graph construction](https://arxiv.org/abs/1912.01164). With the exact values S(2)=4, S(3)=13 and S(4)=44, Rowley's bound S(k+q) ≥ m·S(k)+φ gives at most 1664, 1456 and 1458 for the 376, 109 and 33 templates respectively. None of them can reach 1697 with any base partition. These runs were reproductions: the 376 template reproduces Rowley's published 1664 partition up to colour relabelling. Only a new template could help.

After local search reached five conflicts, exact repair jobs freed its entire colour-6 class together with individual other classes, every pair of other classes, low positions, or random extra positions. All 25 restricted target jobs returned UNSAT; every corresponding original-baseline control was SAT. Free sets and seed snapshots remain in scratch. Stage 2 also ran 287 neighbourhood repair pairs, each with a SAT control and an UNSAT target. These results apply to the stated frozen colours; baseline-phase controls show only that the encoding does not exclude the known solution.

## Local search and observed objective

`local.cpp` enumerates the 719,952 triples at length 1697, counting each unordered pair once and allowing equal summands. It maintains move costs and a list of violated triples. Moves use a tabu tenure from 7 through 23, with aspiration for a new best score.

The first configuration used seed 7301698, 100,000-step restarts and 2 percent random moves. The second used seed 7301700, one-million-step restarts and random-move rates of 0.1, 0.5 or 1 percent. It usually restarted near the saved best colouring. The final local-search run resumed from the best-6 colouring saved during the mixed two-process interval described below. That single-process run made 112,873,492 moves over 113 restarts and ended at best objective five. The verifier confirmed these five remaining triples, all in colour 6:

```
537 + 537 = 1074
537 + 663 = 1200
537 + 668 = 1205
537 + 794 = 1331
663 + 668 = 1331
```

Five is the best observed score. No lower bound on the minimum possible conflict count is claimed.

## Timing, resource deviation and exit status

Search ran from 2026-11-17 16:09:00 UTC to approximately 18:08:50 UTC, about 119 minutes 50 seconds. The final SAT controller and final local-search process both printed their own `exit 0` end lines; these were not captured shell exit statuses. Timed-out SAT children were killed and recorded with normalized timeout status 124. Earlier controller/configuration switches used SIGTERM; the first wrapper records status 143 for both interrupted children.

I exceeded the two-core allowance for roughly 14 minutes. A delayed terminal launch led me to repeat the local-search command, leaving two identical local searches alongside SAT. On discovery I stopped both local instances and restarted one clean instance with a separate log. The mixed `local2.log` is retained and excluded from clean-run move counts. The five-conflict candidate came from the later single-process run. Subsequent process snapshots showed one local search and one SAT child. The virtual environment and search data are in scratch; uv also used its normal shared package cache during setup.

## Replay and what to change next

The retained scratch directory is `.terramind/scratch/schur7/` in this worktree. It contains source downloads, baseline and broken files, candidate and phase snapshots, per-job requests, logs, `commands.txt`, `environment.log`, and `candidate-audit.jsonl`. Source-only copies of the search and audit scripts accompany this writeup. Python was 3.12.1 and xlrd was 2.0.2; compilation used `c++ -O3 -std=c++17`.

For a clean replay, copy the scripts into a new scratch directory, put the ancillary spreadsheet at `ancillary/specimens.xls`, and run `extract.py` with the scratch Python under `-I`. The extractor also emits `baseline.txt`, matching the inline conversion used by the original C++ setup. Run `selftest.py`, then invoke `sat.py child REQUEST.json` on a retained request. For example, the completed 1250-window request fixes the first 446 baseline positions; its companion control uses length 1696. Controllers have this run's absolute deadline. The two pause wrappers have historical PIDs and now refuse unsafe PID reuse; replay their individual requests directly. Those identity guards were added after execution and leave the SAT encoding and parameters unchanged.

The first follow-up is to generate many six-colour partitions of 1..536 (or of 1..m near 536), each first shown to reproduce a mirrored 1696 completion, then attempt 1697 with the mirror x → 1698 − x and with no mirror. Cube-and-conquer for prefixes shorter than 446 and clause-weighting local search from start points other than Rowley's colouring remain untried. New templates with larger m·S(k)+φ remain untried. The checked certificate already rules out the specific 1..446 prefix; the timeouts leave shorter fixed prefixes undecided.

## Independent audit

An independent audit by claude-opus-5-5 re-ran the baseline and known-answer controls, examined the search logs and code, and re-encoded the instance with Rowley's colours fixed on integers 1 through 446 and all of 447..1697 free; three passages were corrected concerning the product templates, reflected placements and baseline-phase SAT controls. In the auditor's run, not the author's, the separate encoding used at-least-one colour per integer, every triple clause and unit clauses for the fixed colours (11,879 variables, 5,044,483 clauses); CaDiCaL 3.1.0 returned UNSAT in about six minutes (373.7 seconds), and lrat-check verified its LRAT proof. The same encoder passed the S(3)=13 and S(4)=44 known-answer controls and found a different valid 1696 colouring with 1..446 fixed, while fixing only the first 400, 300, 200 or 100 colours remained undecided at limits of 300–600 seconds. This audit is an opinion backed by reruns, not a check by the repository verifier: the certificate rules out only extensions of Rowley's colours on 1..446 to 1697, nothing more, and neither the encoder nor the proof checker is itself formally verified.
