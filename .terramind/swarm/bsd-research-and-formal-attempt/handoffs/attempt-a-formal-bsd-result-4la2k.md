Outcome: cannot finish — no independent certified upper bound for the analytic order was obtained

## Done

- Continued on `swarm/bsd-research-and-formal-attempt--attempt-a-formal-bsd-result-4la2k-c3` and updated `formal-attempt.md` with the analytic-upper-bound audit.
- Checked Bober's primary paper. It states the rank theorem under BSD and GRH. Its explicit-formula zero-sum argument bounds analytic multiplicity only under GRH; this is conditional, not an unconditional certificate for 389a1. Sage/Passagemath also documents its Bober analytic-rank upper bound as conditional on GRH.
- The previously recorded rigorous information remains the sign-plus-central-vanishing lower bound `ord_{s=1} L(E,s) >= 2`, under the stated continuation and exact modular-symbol value. No analytic upper bound `<=2`, exact interval for `L''(1)`, or order-excluding-zero computation was produced. No new script or interval result is claimed.
- Probes: `python3 --version` → `Python 3.13.5`; Sage and Magma were absent; Python `mpmath.iv` and SciPy were importable. `bun run check` failed immediately with exit 127 because `tsc` is not installed (`$ tsc --noEmit ...`, `tsc: command not found`).
- `find . -maxdepth 5 -type f \( -name 'design.md' -o -name 'design*.md' \)` found no design document. The supplied design copy is read-only, so it was not recreated or edited.
- No Frontier attempt, submission, or declarations were created or changed.

## Deviations

- The requested reproducible unconditional analytic interval and truncation proof were not completed. Bober's method requires GRH even to bound analytic order; the published rank conclusion further assumes BSD. A certified Mellin computation would need explicit validated quadrature and Fourier/tail bounds, which this run did not implement.
- Could not update `design.md`: it is absent from the worktree and the provided copy was explicitly read-only.
- Repository check was attempted as requested but could not start because TypeScript compiler `tsc` is unavailable.

## Concerns

- The exact analytic order of 389a1 remains unproved by this work. Algebraic rank 2 cannot be used to infer it without BSD.
- `mpmath.iv` being present is not itself a rigorous certificate for the whole improper Mellin integral; any follow-up must document validated quadrature, coefficient computation, and both truncation tails.

## Follow-ups

- On a Sage-capable environment, compute the Bober analytic upper bound and label it conditional on GRH; do not present it as unconditional or convert it into algebraic rank without BSD.
- Alternatively produce an independently checkable interval for the Mellin-split completed second derivative, with exact coefficients, validated quadrature, and explicit Fourier and integral tail bounds.
- Run `bun run check` after providing the repository's expected TypeScript compiler and dependencies.
- Provide a writable design-document path if the lead still needs that record updated.
