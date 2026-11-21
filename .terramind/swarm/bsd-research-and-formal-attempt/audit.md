# Independent audit: 389a1 rank-two analytic certificate

Audit date: 21 November 2026. Scope: the Mellin normalization and Decimal interval implementation in `scripts/389a1_mellin_interval.py`, the exact central-zero/sign inputs, the curve identity, and the cited descent evidence. This is a curve-specific analytic-order certificate, not a proof of BSD.

## Finding and correction

The original saved run had an invalid `t >= T` tail bound. It replaced `exp(-c*n*t)` by `exp(-c*T*t)` for `1 <= n <= N` and `t >= T`. Since the least coefficient index is `n=1`, the justified uniform bound is only `exp(-c*t)`. The old rate `c*T` understated the tail by many orders of magnitude. This was an actual soundness defect in the reported interval.

I changed the implementation to integrate `t^2 exp(-c*t)` from `T=80` to infinity, using the exact antiderivative

`exp(-c*T) * (T^2/c + 2*T/c^2 + 2/c^3)`

and the safe coefficient sum `sum_(n=1)^80 2n = 80*81 = 6480`. The corrected upper tail bound is `0.00120320082963199065235169216373544008`. The coefficient truncation tail for `n>=81` is unchanged and remains `1.59602060051683750609671384883159438e-10`. The corrected output encloses

`4.33260943049475451282027568640961753 < Λ''(1) < 5.19755742831913992224203383539767095`.

The lower endpoint remains positive by a wide margin, so the conclusion that the completed second derivative is nonzero survives this defect. The saved stdout now corresponds to the corrected implementation.

## Interval arithmetic review

- The grid is exactly `[1,80]` with width `1/16`; all terms use `a_n` for `n<=80`. For `t>=1`, `log(t)^2` is increasing and `exp(-c*n*t)` is decreasing, so the independent endpoint product bounds on each cell are valid. Negative coefficients reverse which product endpoint enters the lower/upper sum, and the implementation handles that explicitly.
- Integer coefficients are generated from exact point counts at good primes `p<=80`, prime-power recurrences, and multiplicativity. Since the only bad prime is 389, these are all good primes. The point count includes the one point at infinity. The coefficient list agrees with the first coefficients shown on the L-function record.
- The bound `|a_n| <= d(n)*sqrt(n) <= 2n` follows from Deligne's bound and `d(n)<=2sqrt(n)`. The geometric-series bound for `n>=81`, with `q=exp(-c)` and `c` replaced by its lower endpoint, is a valid majorant; its remaining integral is over `[1,infinity)` and uses `log(t)^2<=t^2`.
- The elementary Decimal calls are made in local contexts of precision 36 and half-even rounding. Python documents Decimal arithmetic as correctly rounded, and `exp`, `ln`, and `sqrt` as correctly rounded operations. The `next_minus`/`next_plus` calls run under the process default precision 28 rather than the local 36-digit context. This is conservative (it steps farther than a 36-digit ulp), not an inward rounding defect, but it contradicts the earlier note's wording that widening is by one 36-digit representable value. All interval operands are Decimal values, and constants `pi` are enclosed by the stated decimal bracket; square root, `c`, arithmetic and transcendental values are widened. The exact Python platform implementation remains part of the computational trust base.

## Mellin normalization and sign

For the normalized weight-2 newform `f(z)=sum a_n exp(2*pi*i*n*z)` at level `N=389`, the completed function used by the script is

`Λ(s)=N^(s/2) (2π)^(-s) Γ(s) L(E,s)`.

Its Mellin integral is `N^(s/2) integral_0^infinity f(iy)y^(s-1)dy`. With Fricke eigenvalue `-1` (equivalently root number `+1` for weight 2), the weight-2 Fricke relation gives `f(i/(N*y))=N*y^2*f(iy)`. Substitution `t=sqrt(N)*y` and splitting at the fixed point gives the script's symmetric expression

`Λ(s)=integral_1^infinity f(i*t/sqrt(N))*(t^(s-1)+t^(1-s))dt`.

Twice differentiating at `s=1` gives the factor `2` and `log(t)^2` in the computation. The alternate common convention using `Γ_C(s)=2(2π)^(-s)Γ(s)` differs by a positive constant factor 2; it does not affect zero/nonzero or order. The script and its printed number consistently use the no-extra-2 convention. With `Λ(1)=Λ'(1)=0`, multiplication by the nonvanishing gamma/conductor factor does not change the second derivative's zero/nonzero status at 1.

The modular-symbol input is not a floating-point guess: the Magma handbook declares `LRatio(A,1)` to return an exact rational (`FldRatElt`), and its elliptic-curves modular-symbol example for this curve reports `LRatio(M,1)=0`. The corresponding central value is therefore exactly zero, subject to the handbook computation and correct association of the modular-symbol factor with 389a1. The LMFDB L-function record identifies conductor 389, sign `+1`, and the functional equation `Λ(s)=Λ(2-s)`. Together these give even order and order at least two; the corrected positive `Λ''(1)` proves exact order two. The LMFDB analytic-rank field alone is not used as proof.

## Curve identity and descent evidence

LMFDB's 389.a1 data gives minimal Weierstrass coefficients `[0,1,1,-2,0]`, conductor 389, discriminant 389, and the model `y^2+y=x^3+x^2-2x`. This matches the script's point-count equation. The points `(0,0)` and `(1,0)` satisfy it by direct substitution.

The Magma handbook's 389 conductor example runs `MordellWeilShaInformation(E)` on `EllipticCurve("389a1")` and prints trivial torsion, 2-Selmer rank 2, two independent points found, and after 2-descent `2 <= Rank(E) <= 2`; it notes a height-100 search on 2-coverings. That supports rank exactly two as the output of the documented Magma computation, with the rank upper bound coming from descent and the lower bound from independent rational points. Its separate `Analytic rank = 2` line is a heuristic of the routine and is unnecessary to this algebraic rank conclusion. This is not a serialized certificate independently checked here: Magma was unavailable, so the published transcript was audited but not rerun. LMFDB's rank and generator rows are corroborating database data, not the proof artifact.

## Generalization boundary

The interval code establishes an analytic order for the specific level-389 eigenform, using its conductor, Fricke sign, coefficients, and exact modular-symbol central vanishing. It does not establish rank equality for arbitrary elliptic curves, nor derive analytic order from algebraic rank. Combined with the distinct published descent computation, it gives matching analytic and algebraic rank evidence for this one curve. It proves neither weak BSD in general nor the strong BSD leading-coefficient formula.

## Verification

- Ran `python3 .terramind/swarm/bsd-research-and-formal-attempt/scripts/389a1_mellin_interval.py`; output saved in `389a1_mellin_interval.stdout`.
- `bun install` completed under Bun 1.4.5.
- `bun run check` was started and its result is recorded in the handoff.

## Primary references

- [Magma handbook: modular-symbol elliptic curves](https://docs.magma-maths.org/ModularArithmeticGeometry/ModularSymbols/elliptic-curves.html) (389a1 `LRatio` example).
- [Magma handbook: exact type and semantics of `LRatio`](https://magma.maths.usyd.edu.au/magma/handbook/text/1776) (`FldRatElt`; the value is an exact rational).
- [Magma handbook: Mordell–Weil groups and descent](https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html) (389 rank-two example and interpretation of rank bounds).
- [LMFDB 389.a1 curve record](https://www.lmfdb.org/EllipticCurve/Q/data/389.a1) (model, conductor, discriminant, generators).
- [LMFDB 389 L-function record](https://www.lmfdb.org/L/2/389/1.1/c1/0/29) (sign, functional equation, central value and coefficients).
- [Python Decimal documentation](https://docs.python.org/3/library/decimal.html) (rounding and elementary operations).
