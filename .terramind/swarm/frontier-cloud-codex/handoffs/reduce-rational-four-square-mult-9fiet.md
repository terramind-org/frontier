Outcome: done

## Done

Created a rank-48 rational witness at
`attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9` from Lille's
`4x4x4_tensor.mpl.bz2` catalogue download.  The initial direct conversion
failed the exact matrix-unit orientation check: Frontier reported that the
coefficient of `A[0][0] * B[0][1]` landed in `C[1][0]`, rather than
`C[0][1]`.  Transposing each `c` factor fixed that orientation.

The resulting commands and verdicts were:

```text
bun frontier check attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9
verified: Valid witness ... with value 48; ties the best known ...

bun frontier diagnose attempts/witness.matmul-rank-4x4x4/20261118-agrim26-ceced9
valid: yes
result: ties the best known value
```

The retained witness has 48 terms, not 47.  Exact proportional-pair scans
found zero collisions for every pair of factor modes: `ab`, `ac`, and
`bc`; hence no two terms can be combined by the requested shared-two-factor
reduction.  I exhaustively tested the 48 combinations of the six tensor-mode
permutations and eight independent matrix transposes.  Exactly the six
matrix-multiplication symmetries stayed valid:
`012/0`, `021/1`, `102/7`, `120/5`, `201/6`, and `210/2`.  Each
remained rank 48; none supplied a rank-47 reduction.

After that search wall, I pivoted to the Golomb task.  Baseline commands on
the PR-56 attempt were:

```text
bun frontier check attempts/witness.golomb-ruler-29/20261118-agrim26-830b60
verified: Valid witness ... with value 623; ties the best known ...

bun frontier diagnose attempts/witness.golomb-ruler-29/20261118-agrim26-830b60
valid: yes
result: ties the best known value
```

I extended the prior exact deletion/recompletion program in disposable
`/tmp` storage from deletion counts `[3,4,5]` to `[3,4,5,6]`, at cap
622 and pinned it to CPU 0.  It exhaustively completed all eligible cores:

* delete 3: 729/729 (left 351, right 351, both endpoints 27), 27 leaves;
* delete 4: 6,201/6,201 (left 2,925, right 2,925, both 351), 351 leaves;
* delete 5: 38,025/38,025 (left 17,550, right 17,550, both 2,925), 2,926 leaves;
* delete 6: 179,010/179,010 (left 80,730, right 80,730, both 17,550), 17,579 leaves.

All corresponding retained-both-endpoint cores were safely frozen because
their span is 623 (>622); their counts were respectively 2,925, 17,550,
80,730, and 296,010.  The run started at
`2026-11-18T11:11:46.222Z`, exited 0, and took 105,267 ms of active
one-core time, below the requested 30-minute ceiling.  There was no
length-622 candidate.  Existing controls also passed, including recovering
both 623-seed endpoints from the 27-mark interior.

The mandated practice warm-up was scaffolded and checked separately, then
removed so this branch preserves the one-attempt-per-PR rule.  Its check
command ran and returned: `error: Lean is not installed here; CI will check
this attempt`.  No attempt declarations were changed from false.

## Deviations

The requested user-visible terminal launch failed before starting the search:
`ipcMain.removeListener is not a function`.  I used the available shell
session instead, explicitly pinned with `taskset -c 0`; it exited 0.

The initial untransposed Lille conversion was rejected, with 96 orientation
violations.  The corrected output-factor transpose is the only repository
scheme retained.

## Concerns

The rank-48 import is a known-value tie, not a rank-47 result.  The
proportional-pair and tensor-symmetry checks are exact but cover only those
reduction mechanisms.

The Golomb result exhausts only the specified six-deletion/recompletion
neighborhood of the 623 seed at cap 622.  It does not prove that a shorter
29-mark ruler does not exist.

## Follow-ups

None.  No PR or submission was opened, pushed, or requested, and both
declarations remain false.
