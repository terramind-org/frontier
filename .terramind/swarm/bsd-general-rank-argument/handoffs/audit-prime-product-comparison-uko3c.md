Outcome: done
## Done
- Independently checked the prime-product note against Conrad, Sheth's final version/preprint, and Freiberg–Kurlberg.
- Wrote `.terramind/swarm/bsd-general-rank-argument/prime-product-review.md` with a correction to the direct-product leading constant: it is `r! sqrt(2) exp(r gamma) / L^(r)(E,1)`, the reciprocal of the constant Conrad states for the reciprocal product.
- Clarified the all-cutoff quantifier in Goldfeld, Sheth's finite-logarithmic-measure exception and RH hypothesis, and the need to control higher terms of the logarithmic Euler-factor expansion as well as any subgroup/index information.
- Repository check: initial run could not find `tsc` because dependencies were absent. After `bun install --frozen-lockfile`, `bun run check` passed: typecheck succeeded, 434 tests passed, 1 skipped, 0 failed, and validate reported 18,618 problems, 0 attempts.

## Deviations
None. Only the task-owned review and handoff files were changed.

## Concerns
The source `prime-product.md` still contains the inverted constant. This task owns the independent review file; the corrected formula and evidence are recorded there for the lead to apply to the source note.

## Follow-ups
Update `prime-product.md`'s direct-product constant to `r! sqrt(2) exp(r gamma) / L^(r)(E,1)` if its owner accepts the audit. The uniform all-cutoff estimate from reductions of a fixed Mordell–Weil basis remains unproved; this audit does not establish weak BSD.
