Outcome: done
## Done
- Added `coprime-splitting.md` with the restriction-corestriction criterion for the underlying (E)-torsor class, distinguished from the finite (E[p^n])-Selmer lift.
- Derived the exact point condition: for a (K)-point mapping to (P\in E(K)), the rational Kummer coset is (d^{-1}[\operatorname{Tr}_{K/\mathbf Q}P]\in E(\mathbf Q)/p^nE(\mathbf Q)), and it must equal the coset represented by (x_n).
- Audited Heegner/ring-class fields and reciprocity: standard norm/Euler-system relations do not supply the needed equality to an arbitrary transverse class or its strict localization. Concluded coprime splitting is equivalent to rational solubility of the same covering.
- Added `coprime-splitting-review.md` as the independent check, including the convention/sign caveat.
- Verification: docs-only mathematical/source review; no repository checks run, as the task is a research note and the repository instructions limit this task accordingly.

## Deviations
None.

## Concerns
No cited source matches the required Kummer coset for a given transverse (x_n); the realization lemma in the note remains unproved. The conclusion is that no general such statement was found, not that special constructions are impossible.

## Follow-ups
If pursued, prove or refute the exact realization lemma under a specified Heegner setup, including its strict local condition and finite-level equality in (H^1(K,E[p^n])).
