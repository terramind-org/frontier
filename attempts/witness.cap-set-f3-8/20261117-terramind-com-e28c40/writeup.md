# Exclusion-guided cap plateaus, stabilizer models and full-line SAT in F_3^8

No cap larger than 512 was found. This writeup records the failed search. Frontier reports `unchecked` for writeups.
The largest retained valid cap has 512 points and ties the recorded 512 lower bound.
One saved 448 start stayed at 448. The other grew through exchanges to the original 512-cap.
A separately constructed 448-point literature product grew to 449.

## Measured

The search-process envelope is **2026-11-17T19:07:18+00:00 to 2026-11-17T20:51:40+00:00**, about
104.37 minutes of a 120-minute budget, including calibration and overlapping streams.
The first time is the shell timestamp immediately before the first Python process, so it includes its import time.
UTC phase timestamps below are the first and last JSON log records and may exclude imports.

Research walks retained 3 distinct labelled 512-caps. Including the full stabilizer model,
there were 4 distinct retained labelled 512-caps, in
1 signed-coordinate class under coordinate permutations and independent coordinate negations.
The smallest outside-point blocking count among these 512-caps was 4.
These counts cover saved walk states and returned incumbents. Internal solver assignments were unobserved.
Calibration objects are excluded from the research count. General affine equivalence was not computed.

`bun frontier diagnose` accepted the baseline, recovered 512, constructed products, 449 gain, 494 intermediate
and regrown 512. The regrown 512 matches the original labelled baseline exactly and ties the record.
All retained cap objects also passed the exact inner checker. No research candidate above the record was produced; the broken 513 was a negative control.

### Exchange runs

`OPTIMAL` means CP-SAT reports optimality for that conditional model. `FEASIBLE` is only an incumbent;
`UNKNOWN` gives no result. Neither status is a Frontier verdict. The neighborhood count uses the pair
(start-cap hash, removed-set hash), so repeated removals are not counted as distinct.
Canonical counts include starts and accepted or inspected equal-size alternatives at every size in that run.

| Run | Seed | Start | Best | Canonical states | Completed calls | Distinct neighborhoods | Call statuses | Logged seconds | Process exit |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| plateau | 211 | 512 | 512 | 1 | 223 | 186 | {'FEASIBLE': 54, 'OPTIMAL': 159, 'INFEASIBLE': 9, 'UNKNOWN': 1} | 2100.1 | 0 |
| smaller-early | 217 | 448 | 448 | 34 | 35 | 35 | {'FEASIBLE': 29, 'OPTIMAL': 6} | 1000.0 | 0 |
| product448 | 403 | 448 | 449 | 35 | 50 | 50 | {'FEASIBLE': 40, 'OPTIMAL': 10} | 1400.1 | 0 |
| product405 | 404 | 405 | 405 | 12 | 42 | 42 | {'FEASIBLE': 28, 'OPTIMAL': 13, 'UNKNOWN': 1} | 1000.1 | 0 |
| other448 | 405 | 448 | 512 | 9 | 65 | 61 | {'FEASIBLE': 14, 'OPTIMAL': 48, 'UNKNOWN': 3} | 692.0 | 143 |
| smaller | 216 | 449 | 449 | 37 | 60 | 60 | {'FEASIBLE': 49, 'OPTIMAL': 10, 'UNKNOWN': 1} | 1800.2 | 0 |

The first 512-cap walk sampled 244 neighborhoods: 223 solver calls and 21 memory-cap skips. Its 223 calls included
9 empty removals, whose tabu clauses made the model infeasible. Later walks skip empty removals directly.
It recorded three labelled 512-caps, all in the starting signed-coordinate class, with minimum blocking count four.
The signed-coordinate class count stayed at one.

The `other448` run began at a complete 448-cap (minimum outside blocking count one). Its first recovered 512 was
logged at 2026-11-17T20:14:09.129404+00:00.
It was deliberately stopped with SIGTERM after recovery of the known baseline, releasing a core for full-space SAT.
Its exit is 143; 65 solver returns are complete, and call 79 was interrupted. The controller's stop reason, UTC time,
last neighborhood and exit status are retained. Its log ends with a controller-generated termination record.
The later `smaller` run starts at the saved 449 literature-product cap.

### Symmetry models

A colored point-coordinate incidence graph gives signed-coordinate stabilizer generators of the baseline.
The discovered full stabilizer has order 512. The full model uses those eight generators plus global negation;
`few` uses global negation plus the first two generators, and `half` uses it plus the first four.
Every affine line is enumerated and its point orbits become a Boolean clause. Repeated orbit variables are
collapsed: three points in one orbit forbid that orbit; two orbits give a pair clause. Orbit cardinalities are the weights.
These models include every affine line within the selected invariant families.

| Run | Orbit variables | Constraints | Returned incumbent | Upper bound | CP-SAT status | Seconds |
|---|---:|---:|---:|---:|---|---:|
| exact-all | 124 | 23678 | 512 | 512 | OPTIMAL | 1.90 |
| exact-few | 1220 | 1011238 | 508 | 3872 | FEASIBLE | 1004.13 |
| exact-half | 300 | 146527 | 512 | 1392 | FEASIBLE | 1002.72 |
| exact-few-warm | 1220 | 1011239 | 512 | 3872 | FEASIBLE | 906.35 |

The all-generator bound of 512 applies only to that symmetry restriction. No independently checkable proof
certificate was retained. The weaker models' loose bounds leave the target unresolved.
The first `few` run used the baseline with one orbit removed as its hint and failed to recover 512 within its limit,
although the baseline is feasible in the model. This measures failure to recover the known feasible baseline with that weakened hint.
The `half` and `few-warm` runs use the complete known 512 as a hint and require cardinality at least 512.
The warm retry recovered 512 from the complete hint.

### Region plus boundary

For each sampled codimension-two or -three affine region, the removal contains all cap points in the region and
both endpoints of every cap pair whose third point is inside it. The projected-frequency implementation was
checked against direct enumeration on 24 small tests, including dense and coordinate-aligned forms.
All 24 eight-dimensional samples removed all 512 points and freed all 6,561 candidates. Their forms and offsets
are logged. They exceeded the 2,200-candidate CP-SAT cap, so **none of those 24 CP-SAT models was run**.
The 24 regions are a finite logged sample.

The lower-memory replacement is a full-space SAT decision model for cardinality at least 513, allowing all points
to change. It contains 7,173,360 affine-line clauses and 983,039 cardinality-network clauses,
with 655,359 auxiliary variables. All 6,561 point variables remain free. The baseline supplies branching phases only;
other solver randomization settings retain their library defaults.
Glucose4 returned **UNKNOWN** after 600.32 seconds including construction, with no witness and no upper bound.
Its recorded statistics are 646,854 conflicts, 8,521,386 decisions and
1,939,892,794 propagations. The decision problem remains undetermined.

## Method and calibration

Points use most-significant-first base-three integer IDs. The inner checker enumerates unordered pairs and their
coordinatewise third points. The published 512-cap was downloaded from
[the public data file](https://github.com/google-deepmind/funsearch/blob/main/cap_set/n8_size512.txt), compared with
the retained baseline, and accepted by the repo verifier at 512. Both checkers rejected a broken 513-point copy.

Before the main exchange run, deleting five baseline points was repaired to 512 (OPTIMAL). Forbidding the original
128-point refill found a different valid 512-cap (FEASIBLE); its signed-coordinate hash equals the baseline's.
A nonmaximal 12-point cap in dimension four grew to 20 (FEASIBLE), and the region/refill control grew 19 to 20.
Independent checks reproduced the complete baseline blocking distribution, tested 12 random signed-coordinate
transformations, and exhaustively compared orbit clauses with direct cap checks on all 32 centrally symmetric
subsets of F_3^2 (largest valid size four).

The first incremental symmetry encoder failed its 90-second known-20 control in dimension four.
It was dropped from the main schedule. Its failed control, source and exit 1 are retained for audit. Only calibration used this encoder.
The replacement full-line orbit encoder found 20 in the small controls. The SAT encoder separately found 20 from a
12-point phase hint in 1.59 seconds before its large run.

For an exchange, keep K, compute every addable candidate F, and maximize the refill over F with all pair/triple
constraints. For nonempty R, forbid restoration of R; previous compatible labelled states also get no-good clauses.
Accept gains and equal-size caps with new signed-coordinate certificates; retain each returned equal-size labelled
alternative even when its certificate is already known. Candidate sets above 2,200 are skipped explicitly.
Removals mix sizes 128, 192, 256, 320, 384 and 416, coordinate-reflection controls, and low-blocker targeting with
8, 32, 96 or 160 extra removals. Each CP-SAT call has one worker and normally at most 35 seconds.
Seeds, R/F/start hashes, sizes, statuses, bounds, restoration flags and timings are logged per completed call.
Every retained state has its full outside blocking histogram, distance from the start and raw/canonical hashes.
Unvisited neighborhoods and models interrupted before optimality remain uncharacterized.

## Literature starts

The 45- and 112-caps were constructed from the projective 56-cap. The starting point is
the weights-three/six description in [Large caps in projective Galois spaces, section 3](https://www.yvesedel.de/Papers/CapSurvey.pdf).
An explicitly derived 2-(6,3,2) support design selects 40 projective weight-three points; a product condition selects
16 weight-six points. All projective pair combinations were checked, giving a 56-cap. Its positive and negative
representatives give a checked 112-cap in F_3^6. Deleting an 11-hyperplane, normalizing its complement, and taking
an affine chart gives a checked 45-cap in F_3^5. The construction and direct checks are original code here.

Products with explicit four- and nine-caps give 448 and 405 in dimension eight, both accepted by the repo verifier.
A five-point deletion from the 448 product was restored to 448 before its run. That product then reached a
valid 449. The 405 product remained at 405. Their values remain below the record of 512.
The two priority-generated 448 inputs came from the prior attempt's retained data, named `variant2_448.json` and
`variant3_448.json`. They are distinct starts. Their coordinates and all new caps remain in scratch for audit;
the attempt contains the writeup and original source code.

## Evidence, runtime and reproduction

Retained evidence is in the `tame-aurora` worktree under `.terramind/scratch/capset8-r2/`.
`*.jsonl` holds progress, `*.stderr` diagnostics, and `*.start`, `*.end`, `*.exit` process metadata.
`visited/` holds accepted and inspected equal-size caps; the exact/SAT files hold returned solver incumbents.
`interruptions.jsonl` explains the deliberate termination. `summary-final.json` and `final-metrics.json` summarize
observations. Phase-specific `*.search-source.py` files preserve earlier source versions.

Two single-worker search streams ran concurrently, with OMP and BLAS thread counts set to one. There was no
OS-level CPU or memory sandbox; a brief independent checker overlapped both streams. Some later checks paused one
stream first. The largest logged single-process peak RSS was 1.324 GiB on this machine;
this is not an aggregate resource certificate. Disk usage remained below the 2 GiB limit.
Dependencies used were Python 3.12.1, NumPy 2.5.5, OR-Tools 9.15.6755, pynauty 2.8.8.1 and python-sat 1.9.dev22
with Glucose4. No paid APIs, cloud compute or Lean were used.

| Phase | First JSON UTC | Last JSON UTC | Exit |
|---|---|---|---:|
| calibration | 2026-11-17T19:07:37.649630+00:00 | 2026-11-17T19:12:20.381796+00:00 | 1 |
| exact-all | 2026-11-17T19:12:27.824532+00:00 | 2026-11-17T19:12:29.727343+00:00 | 0 |
| control-few | 2026-11-17T19:12:53.871414+00:00 | 2026-11-17T19:12:53.909742+00:00 | 0 |
| control-half | 2026-11-17T19:12:54.325289+00:00 | 2026-11-17T19:12:54.339833+00:00 | 0 |
| plateau | 2026-11-17T19:12:54.728287+00:00 | 2026-11-17T19:47:54.780283+00:00 | 0 |
| smaller-early | 2026-11-17T19:14:42.605677+00:00 | 2026-11-17T19:31:22.628949+00:00 | 0 |
| region | 2026-11-17T19:47:56.836018+00:00 | 2026-11-17T19:48:01.215680+00:00 | 0 |
| product-build | 2026-11-17T19:31:41.213164+00:00 | 2026-11-17T19:31:41.241890+00:00 | 0 |
| product448 | 2026-11-17T19:31:42.790653+00:00 | 2026-11-17T19:55:02.921254+00:00 | 0 |
| product405 | 2026-11-17T19:55:04.505712+00:00 | 2026-11-17T20:11:44.568574+00:00 | 0 |
| other448 | 2026-11-17T20:11:46.976151+00:00 | 2026-11-17T20:23:19Z | 143 |
| exact-few | 2026-11-17T19:48:03.081239+00:00 | 2026-11-17T20:04:47.257884+00:00 | 0 |
| exact-half | 2026-11-17T20:04:49.567533+00:00 | 2026-11-17T20:21:32.320583+00:00 | 0 |
| sat-control | 2026-11-17T20:26:19.301613+00:00 | 2026-11-17T20:26:20.900837+00:00 | 0 |
| sat-region | 2026-11-17T20:26:26.161778+00:00 | 2026-11-17T20:36:26.553053+00:00 | 0 |
| smaller | 2026-11-17T20:21:39.676941+00:00 | 2026-11-17T20:51:39.886555+00:00 | 0 |
| exact-few-warm | 2026-11-17T20:36:29.060530+00:00 | 2026-11-17T20:51:35.440281+00:00 | 0 |

Copy the source files and inputs to fresh scratch before running them.
Prepare `baseline.json` from the linked text file as `{"points": [...]}`, create the Python environment with the
versions above, and run `search.py calibrate`. `hill_products.py` builds the literature starts; `exact_sym.py` runs
the orbit models; `full_region_sat.py control` and then `full_region_sat.py 600` run the SAT tests. The shell schedules
record phase parameters. The archived `calibration_initial.py` reproduces the dropped control.
The two historical priority-generated inputs and the saved 449 continuation input are required for exact replay of
those particular starts; they are retained for audit rather than embedded in source. Time-limited solver outputs
and state counts can vary with machine load.

## Inferred

These runs found no cap above 512. The saved second 448-cap can reach the known 512 construction through exchanges;
that successful recovery does not demonstrate a route past it. The canonical quotient shows exactly how much of
the apparent labelled 512 diversity survives signed-coordinate equivalence. It does not settle affine equivalence
of the smaller caps. The loose subgroup bounds and unrestricted SAT UNKNOWN leave larger caps open.

A later search should test substantially different 512 classes, global exclusion of known signed-coordinate images,
and stronger cuts or symmetry handling for the full-space SAT model. The retained smaller-cap trajectories are
usable starts. The outcome of other plateau walks, regions and symmetry groups remains undetermined.
