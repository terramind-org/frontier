Outcome: done
## Done
- Independently reviewed the zero-free implication, explicit-formula off-line terms, scaled-kernel limiting issue, and arithmetic comparison in `explicit-average.md` and `abel.md`.
- Added `explicit-average-review.md`. The central conclusion is sound: the all-cutoff coefficient premise implies nonvanishing for `Re(s)>1`; the functional equation and conjugation put all nontrivial zeros on the central line. Bober's kernel positivity does not extend to off-line zeros, and compact Fourier support does not provide transverse decay under scaling.
- Clarified that an aggregate zero-density/weighted estimate could in principle replace RH for a different averaging proof; the obstruction is to the stated positivity route, not a theorem that all averages fail. No defect changing the main conclusion was found.
- Confirmed the missing arithmetic lemma remains the universal estimate `sum_{p<=x} log(N_p/p) = rank E(Q) * log log x + o(log log x)`, or a weaker smoothed estimate plus independent zero-side control. No such estimate follows from reduction of fixed Mordell–Weil points.
- Verification: `bun run check` passed (TypeScript, 434 tests passed, 1 skipped, catalog validation: 18,618 problems, 0 attempts).

## Deviations
None.

## Concerns
The arithmetic comparison remains unproved, so this work does not derive unconditional weak BSD.

## Follow-ups
None.
