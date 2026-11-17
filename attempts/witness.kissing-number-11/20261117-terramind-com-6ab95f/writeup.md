# Hole/exchange and all-point Lp search from 604 points, 2 h, no 605 found

The search found no valid configuration with 605 points. The best saved numerical
configuration had maximum pairwise cosine 0.5072124712612411, or positive overlap
0.007212471261241138 above the required 0.5. Its minimum angle was
59.52166841688265 degrees. The repository verifier rejected an integer export
at scale 10^12 with 12,485 violations. Accepted configurations contained
604 points and tied the repository's record.

This is a failed-search writeup. It is not machine-checked and establishes no
upper bound on the kissing number.

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

All baseline vectors have squared norm 36. The split is 496 integer vectors and
108 vectors with a sqrt(2) part. The integer portion contains 480 vectors with
four coordinates of magnitude 3 and 16 coordinate-axis vectors of magnitude 6.
The baseline has 19,704 contacting pairs. These counts were computed from the
downloaded coordinates.

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
0.5773502691896273.

The next phase tried k-for-k+1 exchanges for k = 1 through 6. It removed nearby
blockers or a nearby contact neighborhood, then optimized the replacement points
with a squared positive-overlap loss. Perturbation magnitudes cycled through
0, 0.015, 0.05 and 0.15. Each L-BFGS run allowed 1,000 iterations. The log records
1,322,820 exchange trials. None improved the best maximum cosine. The final
phase moved all 605 points with the same squared-overlap loss, allowing 2,500
iterations per restart. Its last progress record shows 723 completed restarts
and a best saved maximum cosine of 0.5574815076231908.

A second core ran all-point Lp continuation to weight the worst overlaps more
heavily. Each p stage allowed 1,500 L-BFGS iterations. Seed 17112027 used
p = 2, 4, 8, 16; seed 17112029 continued through 32 and 64. Those profiles were
stopped at plateaus, with their checkpoints retained. Seed 17112030 continued
through 128 and 256 and tripled perturbations to 0, 0.009, 0.045 and 0.15.
The final profile completed 61 restart cycles and 713,909 objective evaluations,
and produced the best saved numerical result reported above. Central finite
differences checked its gradients. The p=2 error was below 10^-6; the higher-p
errors were below 10^-9.

NumPy emitted floating-point warnings on some matrix products. An independent
einsum recomputation of the final Gram matrix found finite entries throughout
and a largest difference of 4.44e-16 from matrix multiplication. This check
supports the reported numerical objective; it does not certify a configuration.

## Coordinate-pool experiments

Selected coordinate patterns from the record gave 3,876 backbone-compatible
directions. Expanded pure-q and disjoint two-p coordinate shells gave 4,284.
Conflict-graph MILPs reported an optimum of 108 extension points for each pool.
A guarded 5,000-direction subset of a larger integer pool also returned 108.
The resulting 604-point files all passed the repository verifier as ties.
These are numerical optimization results on specified finite pools. They do
not bound configurations outside those pools.

The full integer pool had 19,034 directions and 34,171,904 conflict edges. Its
initial dense model was stopped without a result because its allocation pattern
could exceed the 3 GB memory cap. The observed RSS was 1,882,752 KiB, but peak
memory was not captured. Resource compliance for that aborted run cannot be
asserted. `integer_pool_initial.py` preserves that source for audit; do not rerun
it under this memory budget. `integer_pool.py` adds the 5,000-direction guard.
A later Boolean-block and bitset dominance pass tested 2,269,643 possible
dominators, deleted zero vertices, and declined to build the full MILP.

The main process was paused during those supplemental experiments so that only
two research jobs ran concurrently. BLAS thread limits and HiGHS threads were
set to one. The environment was Python 3.11.8, NumPy 2.2.6, SciPy 1.16.3 and
HiGHS 1.8.0. No Lean, cloud compute or paid API was used.

## Exit status, evidence and reproduction

The main launcher's recorded wait status is 145. It had previously been stopped
and resumed; the budget guard independently records its final SIGTERM. It did
not finish normally. The final Lp profile reached the shared deadline and exited
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

I would not repeat the same k<=6 exchanges around the retained holes. Their 51
initial blockers make them poor neighborhoods for a small exchange. Rank
backbone-compatible candidates by blocker count, or move a larger part of the
backbone. The full 19,034-direction pool still needs a memory-bounded optimizer
with stronger clique constraints. Mixed p+q*sqrt(2) coordinates with cancellation
within a coordinate were not explored systematically. A numerical configuration
that reaches the angle threshold would still need exact reconstruction or
strict slack before integer rounding.

