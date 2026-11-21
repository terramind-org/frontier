Outcome: done
## Done
- Independently audited the descent-height inference in `descent-height-review.md`, including bounded denominator cocycles in `H^1(Q,T_pE)`, coefficient reduction to `H^1(Q,E[p^n])`, transition compatibility, rational torsion terms, and the extra integral local-condition comparison needed before claiming classical Selmer membership.
- Established that, under the strict condition in the localization notes (kernel of local elliptic logarithm on the finite local condition), no nonzero strict class can be the `V_pE`-Kummer image of an individual rational point: non-torsion points have nonzero local logarithm and torsion maps to zero after rationalization. Distinguished possible `Z_p`-linear Mordell–Weil combinations, which are not generally individual rational points.
- Checked Northcott extraction: it is valid only after rational representatives exist at unbounded compatible levels and their image heights are uniformly bounded; it yields one fixed rational point. Replaced the generic scalar in `descent-height.md` with the explicit primitive unit `1 + sum_{j>=2} p^(j!)`, and stated that this is a height example, not a strict-class example.
- Ran `bun install` and `bun run check`: passed typecheck, 434 tests passed, 1 skipped, 0 failed, and validation reported 18,618 problems, 0 attempts. No submission was made.

## Deviations
None.

## Concerns
The bridge from a rational strict Selmer class to an integral classical Selmer tower is conditional on an integral lattice/local-condition comparison (including the finite-index/torsion discrepancy at the distinguished and bad primes). Denominator clearing alone proves only an integral global cocycle. Even granting the tower, Selmer classes give local solubility, not rational points on the coverings or a uniform image-height bound.

## Follow-ups
No theorem is supplied that produces rational points on the compatible coverings with the prescribed Kummer cosets and uniformly bounded image heights. The claimed second-point inference therefore remains unproved; the strict/logarithm condition further prevents the extracted individual non-torsion point from representing a nonzero strict class.
