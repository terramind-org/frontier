Outcome: done
## Done
- Audited finite-level detection, primitive saturation, torsion handling, classical-versus-strict compatibility, rational-solubility implication, and Mordell–Weil height scaling.
- Confirmed that finite-level exclusion gives transversality only. A rank-at-least-two conclusion follows conditionally from rational solubility at one excluded level; no arithmetic argument here establishes such solubility.
- Corrected `transverse-coset.md`: the centered-height estimate is a worst-case `O(p^(2n))` upper bound, not sharp for every nonzero vector. An ordinary integer coordinate such as 1 has constant centered representatives at sufficiently large levels.
- Added independent review at `.terramind/swarm/bsd-general-rank-argument/transverse-coset-review.md`.
- `bun run check` passed after `bun install` supplied the declared dependencies. `git diff --check` passed.
- Committed the work on `swarm/bsd-general-rank-argument--audit-finite-descent-certificate-iez4z`.
## Deviations
None.
## Concerns
The missing arithmetic input remains: prove that a transverse compatible class has zero Sha image at some finite level. Without this, no rational-solubility certificate or unconditional weak BSD lower bound follows.
## Follow-ups
None.
