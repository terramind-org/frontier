Outcome: done
## Done

- Added `derived-localization.md`. Audited Castella’s current arXiv:2204.09608v3, Theorems B and C: for CM (E/\mathbf Q), (p\ge5) split and good ordinary, with positive even analytic order, finite (\Sha[p^\infty]), and the specified (p)-adic orders, the ordinary two-dimensional Selmer group has basis (\kappa_p,x_p^{(2)}); Rubin’s theorem gives the derived elliptic unit nonzero localization, so the Kato class spans the strict kernel. This is a conditional CM analogue; the second vector is an elliptic-unit derivative, not a Kato/BF derivative. The paper gives no verified numerical instance of all analytic assumptions.
- Updated `auxiliary-lines-review.md` to withdraw the unsupported Corollary 5.1 attribution and fixed-(K) assertion. The checked Castella–Hsieh PDF has §5.1/Lemma 5.1 and the relevant statements in Remark 1.6/Theorem 5.5, not the disputed corollary.
- Documentation-only work; no checks run.
- Committed on `swarm/bsd-general-rank-argument--test-derived-class-localization-o424p`.

## Deviations

The requested search for a verified edition containing Corollary 5.1 found none, so the unsupported assertion was removed as permitted by the task. The CM theorem supplies a conditional derived-unit direction, but not a derivative of the generalized Kato/BF class itself.

## Concerns

Theorem C’s finiteness and (p)-adic order hypotheses remain assumptions; no concrete curve/prime satisfying all of them was independently certified here. This does not yield an unconditional BSD implication.

## Follow-ups

For the arbitrary-curve Kato/BF route, prove a same-(S) construction with nonzero localization and simultaneously verified auxiliary hypotheses. Do not identify Rubin’s derived elliptic unit with a Kato/BF derivative.
