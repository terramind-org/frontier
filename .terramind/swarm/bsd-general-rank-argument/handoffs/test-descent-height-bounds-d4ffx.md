Outcome: done
## Done

- Added `descent-height.md` with the finite (p^n)-Kummer and Selmer sequences, both coefficient transition directions, and the inverse-limit sequence.
- Proved the scoped Northcott extraction lemma: uniformly bounded heights of rational Kummer representatives on unbounded compatible levels force the inverse-limit class to come from one rational point.
- Tested the claim against compatible p-adic multiples of a known non-torsion point. Bounded coefficients do not bound rational representative heights; a nonintegral (p)-adic scalar cannot be represented by a bounded-height sequence of rational points.
- Reviewed Fisher–Sills, arXiv:1103.4944, especially the definition of coverings and Theorem 4.1(iv). It supplies model-dependent height comparisons conditional on rational points and explicit degree 2, 3, 4 scope, not solubility or a uniform unbounded-level (p^n) bound.
- Explained why finite descent does not exclude divisible Sha and stated the additional rationality, uniform-height and independence lemma needed by the proposed repair.
- `git diff --check` passed. This is a documentation-only research task; no repository tests were run.

## Deviations

- None.

## Concerns

- The strict Selmer structure in the originating argument may differ from the classical Selmer structure used to write the standard Kummer sequences. The note flags that its exact Kummer kernel and transitions must be supplied before transferring the deduction.
- The source search found no primary theorem giving the needed unconditional solubility and depth-uniform height control for general (p^n)-coverings.

## Follow-ups

- Independently audit whether the strict Selmer classes in the prior Kato/localization argument map into the classical inverse system in the manner required by the extraction lemma.
