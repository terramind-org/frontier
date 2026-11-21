Outcome: done
## Done
- Corrected the residual hypotheses in `.terramind/swarm/bsd-general-rank-argument/noncm-projection.md`: (h2) requires a prime `q || N_f` (dividing the conductor exactly once), ramified in the residual representation if `q ≡ ±1 (mod p)`; (h3) requires either `p > 5` or the residual image to contain a conjugate of `SL₂(F_p)`.
- Verified these against Castella, *Nonvanishing of Generalised Kato Classes and Iwasawa Main Conjectures*, revised author manuscript, §5.2 (hypotheses (h1)–(h3), Choice 5.2.1, Theorem 5.2.3): https://web.math.ucsb.edu/~castella/GKC-IMC.pdf. Checked the downstream reuse in Choice 5.2.1: the same `q || N_f` is inert in `K`, and each prime factor of `N_f/q` splits in `K`.
- Updated the independent review to record the exact reference, note that the publicly hosted arXiv v1 prints the errors (`q ∤ N_f`, `GL₂(F_p)`, and “of” for “or”), and distinguish that text from the corrected revised manuscript.
- Confirmed the localization gap remains: even with a two-dimensional Selmer group and the theorem's residual and auxiliary hypotheses, a separate proof that `loc_p` is nonzero is needed; equivalently under Theorem 5.2.3, the correctly specialized generalized Kato class must be nonzero in the strict finite Selmer group. Its own local restriction is zero in the strict group; central vanishing gives the local condition, not nonvanishing.
- `bun run check` passed: 434 tests passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts. `git diff --check` passed.
- Committed on `swarm/bsd-general-rank-argument--verify-projected-class-condition-jgcvf-c2`.

## Deviations
None.

## Concerns
The arXiv v1 text is not a reliable citation for the corrected wording in §5.2; cite the revised author manuscript directly. The general nonzero-localization input remains unproved.

## Follow-ups
None.
