# Hole/exchange and all-point Lp search from 604 points, 2 h, no 605 found

This failed two-hour local search around the published 604-point configuration
found no valid 605-point configuration. The best numerical 605-point
configuration (the 604 with one point inserted, all points relaxed) had maximum
pairwise cosine 0.5072124712612411 (required <= 0.5). One 34-second relaxation
from the baseline plus a random point reaches the same value (0.5072137), so
this figure is not evidence that 605 is close to reachable. The same optimiser
from random starts reaches only about 0.543 to 0.544 at N = 603 to 605.
The repository verifier rejected the integer export at scale 10^12 with 12,485
violations. Exact configurations validated only at 604, tying the repository
record. This writeup is not machine-checked and establishes no upper bound.

## Baseline and exact acceptance path

The baseline is the published EinsteinArena file
[solution_n=604_d=11.json](https://github.com/togethercomputer/EinsteinArena-new-SOTA/blob/c388c6f7408c886311940896713339a1a70c2394/kissing-number/solutions/solution_n%3D604_d%3D11.json).
Its SHA-256 is
`0bde9ca2c434d7beb5af63a64a291498e8c264d9a5718b738e92dd70b9ba7761`.
The raw download was parsed as JSON with Python isolation enabled; no downloaded
code was executed. The source data remains in the retained scratch directory.

`bun frontier diagnose .terramind/scratch/kissing11/baseline.json --problem witness.kissing-number-11`
reported value 604, valid yes, and a tie. A Python integer checker independently
implemented arithmetic in Z[sqrt(2)] and the verifier's common-radius distance
rule. Both that checker and a numerical checker accepted the baseline and
rejected a copy whose last vector duplicated the first. The repository verifier
also rejected that broken copy, reporting the duplicate and its zero distance.
The audit found that `bun frontier diagnose` exits 0 even for an invalid witness;
a success gate must read its output, not its exit code. The existing search gate
therefore relies on its independent `exact_valid` check.

All baseline vectors have squared norm 36. The split is 496 integer vectors and
108 vectors with a sqrt(2) part. The integer portion contains 480 vectors with
four coordinates of magnitude 3 and 16 coordinate-axis vectors of magnitude 6.
The baseline has exactly 19,704 tight pairs, with inner product exactly 18,
at the 60-degree bound, and zero slack. These counts were computed from the
downloaded coordinates. Scale-and-round cannot be relied on to make a numerical
neighbour of this tight configuration exact: even the unperturbed baseline
exported from floats was rejected in the audit. A numerical 605 near it would
need exact reconstruction, such as snapping to the configuration's Z[sqrt(2)]
alphabet, unless strict slack were first obtained.

The search used unit vectors for numerical optimization. The repository requires
every squared distance to be at least the largest squared norm. Numerical angles
alone were never accepted as a witness.

## Search and parameters

The shared wall-clock window began at 2026-11-17 16:09:52 UTC. The budget guard
sent SIGTERM to the main process at 18:09:51.995739 UTC, 7199.995739 seconds after
that origin. The guard includes startup and pauses in the budget. No search job
remained running when the attempt was scaffolded.

`search.py` used seed 17112026. Its first phase sampled random directions,
perturbed record points, and polar vertices of the 496-point backbone obtained
by linear programming. It minimized a smooth maximum cosine with L-BFGS and
polished single directions with SLSQP. This sampled deep holes; it did not
enumerate all of them. The log records 161,415 hole trials, including 53,805 LP
calls. The 256 retained directions contained 64 distinct directions after
rounding to eight decimal places. Every retained direction overlapped 51 of the
604 fixed points. The best insertion cosine was 1/sqrt(3), approximately
0.5773502691896273. The hole phase found that best value at 0.06 s;
the remaining trials never improved it.

The next phase tried k-for-k+1 exchanges for k = 1 through 6. It removed nearby
blockers or a nearby contact neighborhood, then optimized the replacement points
with a squared positive-overlap loss. Perturbation magnitudes cycled through
0, 0.015, 0.05 and 0.15. Each L-BFGS run allowed 1,000 iterations. The log records
1,322,820 exchange trials. None improved the best maximum cosine.
Every exchange started from one of 64 holes of a single type, each with 51
points at cosine 1/sqrt(3). Removing at most six of them could not clear the
rest, so this phase was structurally unable to succeed; the trial count
measures repetition, not breadth. The final
phase moved all 605 points with the same squared-overlap loss, allowing 2,500
iterations per restart. Its last progress record shows 723 completed restarts
and a best saved maximum cosine of 0.5574815076231908.

A second core ran all-point Lp continuation to weight the worst overlaps more
heavily. Each p stage allowed 1,500 L-BFGS iterations. Seed 17112027 used
p = 2, 4, 8, 16; seed 17112029 continued through 32 and 64. Those profiles were
stopped at plateaus, with their checkpoints retained. Seed 17112030 continued
through 128 and 256 and tripled perturbations to 0, 0.009, 0.045 and 0.15.
The final profile completed 61 restart cycles and 713,909 objective evaluations,
and produced the best saved numerical result reported above. It reached its
best value at 220 s of 3,575 s; the remaining time did not improve it. The
earlier profiles plateaued at 733 s of 1,840 s and 151 s of 1,400 s.
Central finite
differences checked its gradients. The p=2 error was below 10^-6; the higher-p
errors were below 10^-9.

NumPy emitted floating-point warnings on some matrix products. An independent
einsum recomputation of the final Gram matrix found finite entries throughout
and a largest difference of 4.44e-16 from matrix multiplication. This check
supports the reported numerical objective; it does not certify a configuration.

## Coordinate-pool experiments

Selected coordinate patterns from the record gave 3,876 backbone-compatible
directions. Expanded pure-q and disjoint two-p coordinate shells gave 4,284.
Conflict-graph MILPs reported an optimum of 108 extension points for each pool,
and only with the 496-vector backbone held fixed.
A guarded 5,000-direction subset of a larger integer pool also returned 108.
The resulting 604-point files all passed the repository verifier as ties.
These are numerical optimization results on specified finite pools. They do
not bound configurations outside those pools or with the backbone free.

An enlarged pool had 19,034 directions: the 4,284 earlier ones plus the integer
vectors of eight selected norm-36 patterns. It omits the 1,536
backbone-compatible integer vectors of pattern (3,3,3,2,2,1). Its conflict graph
had 34,171,904 edges. Its log shows it had already formed the dense
19,034-square float64 Gram matrix (2.90 GB) with its Boolean comparison
(0.36 GB), so it very likely exceeded the 3 GB memory cap before it was stopped.
The sampled RSS of 1,882,752 KiB is not a peak.
`integer_pool_initial.py` preserves that source for audit; do not rerun
it under this memory budget. `integer_pool.py` adds the 5,000-direction guard.
A later Boolean-block and bitset dominance pass tested 2,269,643 possible
dominators, deleted zero vertices, and declined to build the full MILP.

The main process spent about 284 s paused during the two integer-pool runs so that only
two research jobs ran concurrently. BLAS thread limits and HiGHS threads were
set to one. The environment was Python 3.11.8, NumPy 2.2.6, SciPy 1.16.3 and
HiGHS 1.8.0. No Lean, cloud compute or paid API was used.

## Exit status, evidence and reproduction

The main launcher's recorded wait status is 145 = 128 + 17. Signal 17 is
SIGSTOP on this macOS, so this reflects a stopped job; the main process's final
termination status was not captured. The budget guard independently records
sending SIGTERM at the deadline. The final Lp profile reached the shared deadline and exited
0. The two earlier Lp profiles and the aborted full integer model have status
143 after intentional SIGTERM. The finite-pool, guarded-subset and dominance
jobs exited 0. The main counts above come from its final progress record rather
than a normal completion summary.

Scratch is retained at `.terramind/scratch/kissing11/` in the worker checkout.
It contains the raw data, `commands.log`, `run-index.json`, `resource-notes.log`,
`budget-stop.json`, all stdout logs, checker self-tests, verifier diagnostics and
best numerical checkpoints. The run index records log creation times, command
parameters, seeds, source hashes and exit statuses. `best-objective.json` and
`evidence-summary.json` record the final metrics. Only source scripts are copied
into this attempt; the data and logs remain in scratch.

For an acceptance-path replay, run the copied `search.py --scratch <scratch>
--self-test` with `python3 -I`, then run the repository diagnostics on
`baseline.json`, `broken.json`, `integer-pool-best.json` and
`rounded-best605.json` with `--problem witness.kissing-number-11`. Expected
results are valid 604, invalid duplicate, valid 604 and invalid 605. To rerun a
search, copy its source into a fresh scratch directory alongside the pinned
baseline and follow `commands.log`. The wall-clock phase boundaries make exact
trial counts hardware-dependent.

## What to change next

Calibrate every stage on a punctured 604 before a long run, requiring restoration
of the known configuration. Lower or replace the exchange success gate, or
polish with epigraph SLSQP or an LP before gating: it would have missed most
real solutions in the audit's known-answer tests (only 4 of 144 passed).

Rank candidate directions by blocker count and remove a whole blocker set
(about 51 points), or a cap, re-optimising m + 1 points instead of k <= 6.
Free the backbone in the MILP by solving an independent set over the 496
backbone vectors plus the pool, using clique constraints or a dedicated solver.
Complete the pools with the 1,536 missing integer directions and systematic
mixed p + q*sqrt(2) coordinates. Use the configuration's symmetry group to
orbit-reduce holes and MILPs.

Start from other structures, such as other published 11-dimensional,
laminated or code-based configurations, instead of baseline plus one point.
Add exact reconstruction inside the relaxation loop, snapping to the
Z[sqrt(2)]/6 alphabet or using a PSLQ/LLL fit before rounding.
Record peak memory and the true exit status per process.

## Independent audit

A second model re-derived the baseline's exact structure, confirmed that each
stage restores a punctured 604, reran relaxation at several sizes for
calibration, checked the export path and the MILP model, and recounted the
logs. It found seven statements overstated or incomplete; the text was
corrected accordingly. The audit is an opinion backed by reruns, not a check
by the repository verifier.
