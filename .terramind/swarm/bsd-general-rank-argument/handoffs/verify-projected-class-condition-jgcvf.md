Outcome: done
## Done
- Wrote the independent projection audit to `.terramind/swarm/bsd-general-rank-argument/noncm-projection-review.md`.
- Checked the Castella projection, coefficient target, weight-two regulator specialization, Selmer/strict local conditions, residual and auxiliary hypotheses, rank-two criterion, and the distinct BDV Beilinson–Flach/Eisenstein comparison against the cited primary papers.
- Identified the source note's two material hypothesis transcription errors: (h2) requires `q || N_f`, not `q ∤ N_f`; (h3) requires the residual image contain a conjugate of `SL₂(F_p)`, not `GL₂(F_p)`. Recorded corrected formulations in the review for the lead to apply to the source note.
- `bun run check` passed: TypeScript check, 434 tests passed, 1 skipped, 0 failed, and validation reported 18,618 problems and 0 attempts.
- Committed all work on `swarm/bsd-general-rank-argument--verify-projected-class-condition-jgcvf`.

## Deviations
None.

## Concerns
The described non-CM rank-two result remains conditional on the stated residual and auxiliary hypotheses. Even under those hypotheses, it equates nonvanishing of the generalized Kato class (in dimension two) with nonzero Selmer localization; it does not prove that localization nonzero.

## Follow-ups
Correct the corresponding residual hypothesis statements in `noncm-projection.md` when its owner or lead next edits that file.
