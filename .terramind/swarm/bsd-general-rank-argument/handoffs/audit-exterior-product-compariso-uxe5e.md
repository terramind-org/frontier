Outcome: done
## Done
- Wrote the independent primary-source review in `auxiliary-lines-review.md`.
- Corrected the coefficient-field issue: varying-data classes require comparison after scalar extension to a common finite field for each pair, and the exterior product vanishes there; descent to \(\mathbf Q_p\) and a single finite field for an infinite family are not established.
- Checked the published theorem's per-choice hypotheses, natural representation projection, Selmer/local condition, fixed-(K) scope of Corollary 5.1, mixed-root result, and the limitation on extracting rational points.
- Ran `bun install` and `bun run check`: 434 passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts.
- Committed as `41cd9d29` on `swarm/bsd-general-rank-argument--audit-exterior-product-compariso-uxe5e`.

## Deviations
None.

## Concerns
- The pairwise exterior-product conclusion is conditional on each datum satisfying the theorem's conditions, producing a Selmer class, and the common fixed-((E,p)) rank-two/rank-one-localization assumptions.
- The argument does not produce rational points or prove a rational-rank lower bound.

## Follow-ups
- If the lead retains `auxiliary-lines.md` as the canonical note, propagate its coefficient-field and reference corrections from the independent review before relying on the note's unconditional \(\mathbf Q_p\)-exterior-product wording.
