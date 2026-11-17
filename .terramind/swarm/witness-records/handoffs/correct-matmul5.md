## Done

Corrected `attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/attempt.yaml` and `writeup.md` against `audit-matmul5.md`. No search was run and no search or lift source was changed.

1. Lift correction.
   Old: "Its Jacobian, consistent/inconsistent linear solves, and a complete positive lifting path on the rank-125 schoolbook tensor passed `lift_selftest.py`. The lift strategy remains untested on a new low-rank scheme."
   New: "`lift_selftest.py` checks the linear solver and the Jacobian. Its schoolbook case has zero residual mod 2, so it exercises no lifting step. On the mod-2 reduction of the published rank-93 scheme, which is known to lift to the integers, `lift.py` is consistent at level 1 but inconsistent at modulus 4. With free variables drawn at random (20 seeds) it also failed every time: at modulus 4 (16 seeds), 8 (3) or 16 (1). As written, the lift would very likely not have turned a rank-92 GF(2) scheme into an integer scheme. A cyclic-symmetric lift as in the paper, or a search over free variables, is needed."

2. Symmetry correction.
   Old: "It did not implement the additional row/column reversal symmetry from the paper."
   New: "The paper found its 5x5 rank-93 scheme with C3 alone, starting from the diagonal partition {{1,5},{2,4},{3}}. It used the extra row/column-reversal symmetry only for 6x6. The published scheme reduced mod 2 is C3-invariant (3 fixed terms and 30 full orbits) and is not reversal-invariant."

3. Cyclic walk scope correction.
   Old: "Fixed input orbits were excluded from these orbit moves."
   New: "Fixed terms are excluded from orbit moves, so the C3 walk kept the baseline's 3 fixed terms throughout. Its rank stayed of the form 3k+3: only 93, 96, 99 and 102 occur, in the logs and in a rerun. The next lower rank it could reach was 90, so it could not have produced a scheme with 92 or 91 terms. Only the ordinary walk could have reached 92."

4. Resource evidence correction.
   Old: "An early sample showed about 198% CPU and about 2 MB resident memory."
   New: "An early `ps` sample, not retained, showed about 198% CPU and about 2 MB resident memory."

5. Upstream listing correction.
   Old: "listed one 5x5 rank-93 scheme and its lift; no second starting construction was used."
   New: "listed `schemes/555m93.txt` and its lift; the files `code/r5-93-1.txt` and `code/r5-93-seeded.txt` were not inspected. No second starting construction was used."

Task item 2: Added the audit's separate 180-second rerun measurements: ordinary mode visited 4,193,637 distinct states in its first 4,194,304 steps and saw ranks 93–96; C3 visited 1,210,749 distinct states in about 28.3 million steps (4.3%) and returned to the start 7,525 times. C3 accounts for about 57% of the final segment's flips, so about 1.2 billion flips overstates exploration. Added the audit's structural observations: 78 of 93 baseline terms share no factor with another term, and 66 never changed across the saved states examined. Explicitly scoped the near-rigidity to walking at rank 93 from this scheme, rather than the paper's method of descending from high-rank diagonal-partition starts. Clarified that no cycle-frequency statistic was collected during the original run.

Task item 3: Ran the requested recursive scrub before and after editing. Its only initial match was the absolute scratch directory in `writeup.md`; replaced it with `<scratch>/matmul5/`. The final scrub returned no matches (exit 1). No other attempt file needed a path change. The old absolute path is deliberately not reproduced here.

Task item 4: Added a Follow-ups / untried section, led by the audit's concrete findings: a two-block diagonal partition for rank 92 = 3*30 + 2, a single block for rank 91, many descents from diagonal-partition starts, retaining the current run's best state in the restart pool, greedy orbit reductions, replacing and baseline-testing the lift, and logging distinct states and distance from the start. Other untried options follow these findings.

Task item 5: Kept `kind: writeup`, the existing title and claim statements, and both declarations exactly false. Added the two requested scope sentences to the claim, reproduced in full below.

Task item 6: Kept every existing disclosure entry and added `claude-opus-5-5`, provider `anthropic`, role `auditor`, using the existing YAML shape.

Task item 7: Added Independent audit: a second model re-verified the baseline and mod-2 reduction, reviewed the move code, reached ranks 7 and 23 from ordinary schoolbook 2x2 and 3x3 starts, instrumented distinct-state reruns, recounted the logs, and tested the lift on a known-answer case that failed. It records the four corrections and distinguishes the audit's opinion backed by reruns from the repo verifier. The writeup remains explicitly not machine-checked.

Title in full:

GF(2) ordinary and cyclic flip walks, 2 h, no rank below 93 found

Claim in full:

Records an unsuccessful two-hour bounded search from the published rank-93 5x5 matrix-multiplication scheme. The lowest rank reached over GF(2) was 93. Frontier accepted the published integer baseline at rank 93, tying the record; no new integer scheme with 92 or fewer terms was found. This writeup is not machine-checked and provides no lower bound or nonexistence result. Only the ordinary walk could have reached rank 92 (the cyclic walk's ranks are 3k + 3). The integer lift included here failed its known-answer test on the published scheme, so this pipeline had no working route to integer coefficients at 5x5.

Verification: `bun install` exited 0. `git diff --check` passed. `bun run check` exited 1: type-checking passed; 426 tests passed, 1 skipped, 0 failed (2,426 assertions, 34 files); final validation reported only unconfirmed declarations in the six swarm attempts. Those declarations are intentionally false. No Lean checks were needed for these prose-only edits.

Verbatim output of `bun frontier check attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b` (exit 0):

```text
$ bun src/cli.ts check "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b"
note: checked anyway; before submit: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
unchecked: Writeups are not machine-checked.
```

Verbatim output of `bun frontier validate attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b` (exit 1):

```text
$ bun src/cli.ts validate "attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b"
attempts/witness.matmul-rank-5x5x5/20261117-terramind-com-d0134b/attempt.yaml: declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree
error: script "frontier" exited with code 1
```

## Deviations

The brief names two handoff paths: `correct-matmul5.md` and `correct-the-matrix-multiplicatio-98zq1.md`. Identical copies are provided at both paths to satisfy both requirements. No departure from the auditor's replacement wording was needed; the scope correction replaces the existing fixed-orbit sentence rather than repeating it. The original absolute path is described rather than quoted in this handoff to preserve the required scrub.

## Concerns

None. No audit finding is disputed. Validation remains blocked only by intentionally unconfirmed declarations; the writeup itself has no machine-checked verdict.

## Follow-ups

None.
