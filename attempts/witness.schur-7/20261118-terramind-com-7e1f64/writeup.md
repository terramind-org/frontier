# Six-colour bases and prefix SAT, eight hours, no partition of 1..1699 found

This run searched for a seven-colour Schur partition of length at least 1699. Frontier accepted length 1698 as the largest result of this run. Its reference value at the start was 1696. The negative results below concern specific restrictions and give no upper bound on S(7). The repository treats this attempt as a writeup.

## Calibration

The Frontier verifier accepted Rowley's seven-colour partition of 1..1696 from the paper's supplementary data. Assigning 2 the colour of 1 made the verifier reject the copy. An independent Python enumeration counts all x + y = z with x <= y, including 1 + 1 = 2. It agreed with both outcomes. [Rowley, 2021](https://arxiv.org/abs/2107.03560)

The SAT encoder returned SAT at 13 and UNSAT at 14 with three colours, and SAT at 44 and UNSAT at 45 with four. The last test first timed out in 20 s with every label free, then returned UNSAT after normalizing the labels of 1 and 2. These integers must have different colours. The full-size positive control fixed a supplied six-colour base of length 536, assigned 537 colour 6 using labels 0 through 6, and reproduced a valid reflected 1698 partition. Frontier accepted the control and rejected its broken copy. It also accepted the unmirrored 1698 controls from the three seeds.

The cube procedure recovered a planted length-44 colouring in one branch. The other two branches for that control returned UNSAT. Weighted local search repaired another broken length-44 colouring in one move. The exact repair stage recovered a valid 1698 colouring when freed at the integers participating in a deliberately introduced violation. On randomized small fixed-colour and masked instances, every definite answer from the implication propagator agreed with a separate CaDiCaL call.

## Measured

The generators produced 146,739 distinct six-colour bases at length 536. The count was the same after renaming colours by first occurrence. A base counts once regardless of how often a generator returned it. Of these bases, 135,498 reproduced 1696 and 59,372 reached 1698 in the fixed-base reflected route. Every counted 1698 outcome passed both Frontier diagnosis and the independent enumeration. The final yield was 40.5% per distinct base, with 43.8% of the 1696 completions also reaching 1698.

| Elapsed hour | Bases | Completed at 1696 | Completed at 1698 | 1698 per base |
| --- | ---: | ---: | ---: | ---: |
| 1 | 17,851 | 16,353 | 6,449 | 36.1% |
| 2 | 36,712 | 33,871 | 13,921 | 37.9% |
| 3 | 52,280 | 48,302 | 20,274 | 38.8% |
| 4 | 70,526 | 65,036 | 27,808 | 39.4% |
| 5 | 89,963 | 83,012 | 35,663 | 39.6% |
| 6 | 108,639 | 100,242 | 43,577 | 40.1% |
| 7 | 127,298 | 117,469 | 51,418 | 40.4% |
| end | 146,739 | 135,498 | 59,372 | 40.5% |

The generators mixed fixed random windows, fixed prefixes, sparse release, randomized phases, direct legal recolourings and joint base/completion SAT. Source selection drew mainly from a successful seed and later 1698 completions, along with the published baseline and other candidate bases. The main numbered generator seeds were `857200000 + 10000000 * worker + iteration`. Base completion used seed 846005. The target-guided generator used `851780000 + iteration`. The checkpoint keeps the selected source, fixed positions, phases and outcome for each call. SQLite sampling and incremental solver state can change the order after a restart.

The successful starting base differed from Rowley's in 28 positions. In a comparison set of 26 bases, the distances from Rowley's ranged from 20 to 51 with median 36. No position among the first 32 carried a colour unique to the successful start. Its last class had size 82, below the comparison range of 83 through 113, and its class 2 had maximum gap 7, the bottom of the observed range. In this run, median distance from the successful start was 19 for bases completing at 1698 and 27 for bases whose 1698 test returned UNSAT. Class sizes and within-class gaps are retained with each base. These are observations about the sampled bases and their recorded labels.

### Restricted tests at 1699 and beyond

The exact encoder creates one Boolean per integer representative and permitted colour, requires exactly one colour, and forbids every monochromatic sum. It simplifies clauses against fixed colours and combines equivalent representatives for reflection. The incremental generator and failed-assumption oracle used CaDiCaL 1.9.5 via python-sat 1.9.dev22. Exact wall-clock-limited jobs used the CaDiCaL 3.1.0 executable. The incremental calls used conflict budgets under the common wall-clock cutoff. In the target-guided phase, the oracle recorded 391 UNSAT base assignments at 1699. Returned failed-assumption sets restricted subsequent generator calls to bases outside those particular contradictory patterns.

The reflected sweep tested 59,367 bases that reached 1698. For each it tried pivot m + 1 for m from 530 through 545 and lengths 1699 through 1702. Five additional 1698 completions arrived too close to the deadline to run both sweeps. Integers 1..min(m,536) kept the base colours. Values 537..m, when present, could use colours 0 through 5. The propagator processes forced colours. Two fixed equal-colour positions exclude that colour at their sum and positive difference, and a fixed even position excludes that colour at its half. In the reflected model it applies the exclusions modulo N + 1, folding a residue onto its smaller representative. A domain emptied by these deductions is a conditional contradiction. At 1700 full reflection itself makes 567 and 1134 share a colour, so 567 + 567 = 1134 makes every fully reflected instance impossible.

The recorded 1699 sweep had 949,872 reflected propagation contradictions and 0 open propagation cases. Unmirrored centre and top windows leave the endpoint free and release four pairs of widths, (32, 32), (64, 48), (160, 144) and (288, 192). These produced 237,468 propagation contradictions and 0 open propagation cases at 1699. Separate native solver jobs at 1699 recorded 79,944 UNSAT and 31 timeouts. The totals count requests, including overlapping restrictions and alternative encodings of the same case. The exact index is `logs/unsat-1699.jsonl.gz` in scratch. Native job keys resolve to the full formula request and seed in `checkpoints.sqlite`. Propagation entries identify the base or completion, and their listed pivot or windows determine the restriction.

The cube search removed the mirror and pivot and fixed only prefixes of length 500 down to 150. To pick a split, it compared the minimum domain reduction across the available colours at several constrained free positions. It then ran the even and odd branches on separate workers. All branches returned UNSAT on seed 0 for prefix lengths 460 and 500 at 1699. The shorter-prefix roots had a timeout or an unfinished branch. These prefixes describe one seed family, even where different seed files agree on much of a prefix.

- `push-broad-0-prefix-1699-350` returned `TIMEOUT` after 1800.4 s and 16,236,885 conflicts.
- `push-broad-0-prefix-1700-250` returned `TIMEOUT` after 1800.5 s and 17,695,504 conflicts.
- `push-broad-1-prefix-1699-250` returned `TIMEOUT` after 3600.6 s and 30,876,512 conflicts.
- `push-broad-2-prefix-1699-200` returned `TIMEOUT` after 1800.6 s and 17,276,605 conflicts.
- `push-broad-2-prefix-1700-350` returned `TIMEOUT` after 1800.4 s and 15,529,528 conflicts.

For three restricted 1699 instances, CaDiCaL emitted LRAT and lrat-check confirmed it. The solver input and proof were regenerable and deleted after checking. Scratch retains the certificate digest, checker output and complete job request.

- `push-seed-0-pivot-1699-536`, 429,773 bytes. SHA-256 `8740110c29f0598150dcf055401a93893cdd9c09836b43ac0cb7cd054d0d1d88`. The checker printed `c VERIFIED`.
- `push-seed-0-window-1699-288-192`, 1,441,061 bytes. SHA-256 `d80b27958d5326204c91051153886df612d150459811a9a884cf5169e63acbfa`. The checker printed `c VERIFIED`.
- `push-seed-2-window-1699-288-192`, 1,368,204 bytes. SHA-256 `6fc2f29cdd4dab749a5ad83c826dcca82777fd297977069c38194796867dd51d`. The checker printed `c VERIFIED`.

Clause-weighted repair at 1699 ran 121 trials with 815,416,941 recolour moves. The per-trial estimates of distinct states ranged from 4,392,330 to 7,177,240 using a 1,024-register HyperLogLog count. These estimates do not give a distinct count across trials. The best candidate had 2 violations under full enumeration. Exact repair then freed the conflicting integers, growing windows and sets of entire classes. None of the completed repairs returned a checked solution at 1699.

## Inferred

A successful 1698 seed made it possible to generate many distinct 1698 bases. The wider sample still gave conditional contradictions throughout the fully fixed template tests. The smaller window tests and the exact runs with long fixed prefixes rule out many modifications of these starts. The timeouts with shorter prefixes leave a much larger search space open. The unrestricted exact case was outside the scope of the run. The two-violation result is a score from the local objective.

## Run record and replay

The budget window ran from 2026-11-17T21:13:02Z to 2026-11-18T05:13:01Z. The workers stopped within their deadline margins and all exited with status 0. The supervisor logged `all search workers exited early` because the last worker exited about five seconds before the cutoff. Earlier segment exits include intentional termination for configuration changes and one cube dispatch error. The corrected dispatch resumed from the existing checkpoints under the original deadline. The supervisor logged hourly progress and filesystem space. It ran three base workers in the first hour, then two base workers alongside the two workers sharing cube branches, exact repair and weighted local search. The largest sampled worker-group RSS in the persisted monitoring segments was 4.22 GiB. The largest sampled checkpoint footprint was 1,051 MiB. The disk guard used an 8 GiB free-space floor and deleted per-call CNFs and proof files.

Scratch remains under `.terramind/scratch/schur7-r3/` in the working tree. It contains `progress.md`, the run and calibration logs, `checkpoints.sqlite` and the compressed 1699 index. The supplied inputs and databases remain in scratch. Replay from that directory with Python 3.12 and the binaries under `bin/`. Build `encode.cpp`, `propagate.cpp` and `breakout.cpp` separately using `c++ -O3 -std=c++17`, and provide CaDiCaL 3.1.0 and lrat-check. The lrat-check build used drat-trim revision `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`. The repository verifier runs through Bun.

To replay one native job, load its checkpoint with `archive.get("job", key)` and pass its `job`, `seed` and `timeout_seconds` to `searchlib.solve` under a fresh name. The companion `calibrate.py`, `cubes.py`, `variants.py` and `repair.py` entry points reproduce their controls when invoked in scratch. Use `side.py calibrate` for the weighted search control.
