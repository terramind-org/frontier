Outcome: done
## Done
- Updated `auxiliary-lines.md` with pairwise common coefficient extensions, explicit embeddings into a common finite extension, scalar-extended localization and preservation of its kernel line, and the correctly situated exterior-product vanishing.
- Clarified that descent of a class to the base coefficient space requires coefficient/Galois invariance; line membership after extension alone does not provide descent.
- Corrected the projection description to the natural constituent projection of (1.7), retained the verified Lemma 5.1 Selmer-membership citation, and aligned the independent review. The cited authors’ PDF has §5.1 rather than the claimed “Corollary 5.1”; the review now flags that numbering mismatch and does not attribute a cross-K theorem to it.
- Checked primary source: Castella–Hsieh authors’ PDF, Theorem A and Remark 1.6 (pp. 4–5), Lemma 5.1 and Proposition 5.2 (p. 23), Theorem 5.3 (pp. 23–24). Verified Theorem A’s hypotheses per auxiliary choice, the fixed local map, projection/Selmer membership, and mixed-root vanishing.
- `bun run check` passed: 434 tests passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts.
- Committed changes on `swarm/bsd-general-rank-argument--audit-exterior-product-compariso-uxe5e-c2`.

## Deviations
- The requested fixed-K “Corollary 5.1” could not be verified in the cited authors’ PDF, which labels this material §5.1 and includes Lemma 5.1. Rather than preserve an unsupported attribution, the notes identify the edition/numbering mismatch and make the varying-K comparison solely through the pairwise common-kernel argument.

## Concerns
- The general pairwise wedge conclusion is conditional on each selected datum meeting Theorem A and the shared Selmer/localization hypotheses. It proves no descent of individual classes to the base field and no rational-rank lower bound.

## Follow-ups
- Confirm the exact intended edition/reference for the fixed-K character-variation result before restoring any Corollary 5.1 attribution.
