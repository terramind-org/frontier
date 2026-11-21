# Formal BSD attempt: rational weak target

Research cutoff: 21 November 2026. Target: `weierstrasscurve.affine.rat.weakbsd`, declaration `WeierstrassCurve.Affine.Rat.weakBSD`, as audited in `target.md`.

## Result

No proof of the target, nor any checker-accepted Lean lemma, was produced. The target is the general weak BSD conjecture for every elliptic curve over `ℚ`; the source material reviewed here does not contain a general proof. I did not replace its statement with a restricted theorem or a formal surrogate.

The strongest applicable verified arithmetic route in the handoffs is Gross–Zagier plus Kolyvagin for analytic order 0 or 1. In its applicable modular/Heegner settings, Gross–Zagier turns a nonzero first derivative into a nontorsion Heegner point, while Kolyvagin's Euler system bounds the Selmer group and proves finiteness of Sha. The rank-zero Euler-system result likewise gives rank zero and finite Sha when the central value is nonzero. Modularity supplies the modular parametrization for curves over `ℚ`. This route establishes an analytic-to-arithmetic result only in orders 0 and 1. It neither proves the arbitrary-order weak BSD equality nor the strong leading-coefficient formula. The cited converse results go in the other direction only with additional arithmetic and local hypotheses; they do not close the general implication.

A conditional proof strategy can therefore be stated, but not discharged: for a fixed `E/ℚ`, first obtain a meromorphic continuation of its Hasse–Weil L-series, then show that if its order at 1 is 0 or 1, the Mordell–Weil rank equals that order using the Gross–Zagier/Kolyvagin theorem with its hypotheses. The remaining order-`≥2` cases are exactly where the general rank equality remains open. This conditional result is not the catalog theorem, whose quantifier ranges over every elliptic curve and whose conclusion requires equality without a rank bound.

## Hypotheses and formal dependency audit

The chosen target's displayed Lean statement is `NumberField.WeakBSD E`, i.e. existence of `L : ℂ → ℂ` with `HasMeromorphicContinuation E L` and `meromorphicOrderAt L 1 = Module.finrank ℤ E.Point`. Its context is `E : Affine ℚ` and `[E.IsElliptic]`. The continuation predicate agrees with `E.LSeries` in `Re(s) > 3/2` and asserts global meromorphicity. The target does not assume analytic order 0/1, a Heegner hypothesis, a chosen prime, residual irreducibility, or finiteness of Sha.

The imported `EllipticCurveRank.mordell_weil` instance is marked solved upstream but its checked-in proof body at the pinned source commit is `by sorry`. The BSD theorem itself is also a `sorry` placeholder upstream. Therefore the target's rank expression uses the admitted Mordell–Weil finiteness instance, and any proof importing that instance will have a `sorryAx` dependency unless the relevant instance is replaced or otherwise avoided. I could not inspect the compiled theorem's actual axiom list: this checkout has no `lean`/`lake` executable and no `lean/.lake` dependency cache, so `#print axioms` and the authoritative checker are unavailable. This is an evidence limitation; the source audit establishes the admitted body, not a locally generated axiom report.

The weak target is the right one for rank arguments. Strong BSD additionally demands finite Sha and exact equality with the `bsdQuotient` leading coefficient. None of the reviewed rank-zero/one results supplies a general proof of that full normalized equality. No strong formula normalization is used in this attempt.

## Formal work and status

- Full proof: none.
- Checker-accepted lemmas: none.
- Honest partial argument: the literature-supported rank-0/1 conditional implication described above; it does not establish the target.
- Attempt scaffold: not created. `bun frontier new` requires a real GitHub login, but `gh` is absent, so the login could not be resolved without inventing identity. No attempt metadata or declarations were created or changed; consequently no declaration was set true.
- Checker: not run. `bun frontier check` cannot check a nonexistent attempt, and the Lean toolchain/dependency build is absent.

## First unresolved implication

After modularity/continuation, the first unresolved implication for the target is the unrestricted analytic-to-arithmetic equality

`meromorphicOrderAt L 1 = Module.finrank ℤ E.Point`

for arbitrary `E/ℚ`, particularly analytic order at least 2. The verified Gross–Zagier/Kolyvagin route only handles orders 0 and 1 under its theorem hypotheses. Separately, any claim of a fully trusted compiled proof must resolve or explicitly account for the admitted Mordell–Weil finiteness dependency (`sorryAx`).

## Concrete rank-two case study: 389a1

This section records a reproducible, literature-backed *computational* rank certificate target; no computation was executed in this checkout. LMFDB identifies Cremona label `389a1` (`389.a1`) with the requested minimal model

`y^2 + y = x^3 + x^2 - 2*x`

and gives conductor 389. The points `(0,0)` and `(1,0)` lie on the model: both sides are 0 at each point. The LMFDB record lists these as Mordell–Weil generators and rank bounds `[2,2]`, but that row is catalog data, not the proof artifact used below. Sources: [LMFDB 389.a1](https://www.lmfdb.org/EllipticCurve/Q/389a1/) and [its data record](https://www.lmfdb.org/EllipticCurve/Q/data/389.a1).

The Magma handbook publishes this exact descent command and transcript for the same curve:

```magma
E := EllipticCurve("389a1");
time rank, gens, sha := MordellWeilShaInformation(E);
```

The documented output says the torsion subgroup is trivial, the 2-Selmer group has rank 2, two independent points were found, and after 2-descent `2 <= Rank(E) <= 2`; the point search on 2-coverings is explicitly bounded by height 100. The handbook describes the returned rank interval and independent points, and the 2-Selmer group gives the upper bound. This is the relevant unconditional rank certificate route: a Selmer upper bound of 2 plus two independent rational points gives rank exactly 2, without invoking BSD or an analytic-rank computation. The published transcript is reproducible evidence, but it is not an independently serialized descent certificate, and this environment lacks Magma, so I did not rerun it or validate its exact version-specific output. The handbook notes descent can require class-group computations; no GRH assumption is stated in the published 389 transcript. Sources: [Magma handbook example for 389a1](https://www.math.uzh.ch/sepp/magma-2.18.5-cr/HandbookVolume10.pdf) and [current Mordell–Weil and descent documentation](https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html).

Published output, copied as evidence from the cited handbook (not a local run):

```text
Torsion Subgroup is trivial
Analytic rank = 2
The 2-Selmer group has rank 2
Found a point of infinite order.
Found 2 independent points.
After 2-descent:
    2 <= Rank(E) <= 2
    Sha(E)[2] is trivial
(Searched up to height 100 on the 2-coverings.)
Time: 0.280
```

The `Analytic rank = 2` line is a heuristic within the routine and is not needed for the exact rank interval printed after descent.

The analytic evidence must be kept separate. The Magma modular-symbol example reports `LRatio(M,1) = 0`, then computes a floating-point leading coefficient and reports analytic rank 2; its handbook defines `AnalyticRank` as a heuristic derivative search. Taken as the exact modular-symbol central-value computation, `L(E,1)=0`; the LMFDB L-function record gives functional-equation sign `+1`. With the known continuation and this sign, the functional equation forces the order to be even, so these exact inputs give the rigorous lower bound `ord_{s=1} L(E,s) >= 2`. They do **not** bound the order above by 2: exact order 2 requires rigorous nonvanishing of the second derivative (or an equivalent certificate), which the printed floating-point value does not supply. The 2-descent certificate proves algebraic rank 2, but using that to conclude analytic order 2 would assume the weak BSD equality under investigation. Sources: [Magma modular-symbol BSD example](https://docs.magma-maths.org/ModularArithmeticGeometry/ModularSymbols/elliptic-curves.html), [LMFDB L-function record, sign and central value](https://www.lmfdb.org/L/2/389/1.1/c1/0/29), and [Magma analytic-rank documentation](https://docs.magma-maths.org/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/intro-2.html).

The first generalization failure is exact: this certificate is attached to one explicit curve and depends on a computed 2-Selmer group and explicit point independence. It proves no uniform upper bound on algebraic rank for arbitrary curves, and it says nothing that converts arbitrary analytic vanishing order into algebraic rank. The analytic order upper bound (order exactly 2) remains unproved by the cited output. No strong BSD formula or normalization is used.

Reproduction command recorded from the published handbook (not executed here): the two-line Magma block above. Environment probes in this checkout: `command -v magma` and `command -v sage` produced no path; `command -v bun` returned `/usr/local/bin/bun`. This is an assessment of published evidence, not a locally reproduced certificate and not a formal or Frontier-checked result.

## Analytic-order upper-bound follow-up (2026-11-21)

The requested independent upper bound `ord_{s=1} L(E,s) <= 2` was not established. The leading candidate, Bober's explicit-formula method, needs careful separation of its two conclusions:

- The zero-sum argument bounds the *analytic* order under GRH for this curve's Hasse–Weil L-function. Bober uses a nonnegative test function with value 1 at zero, so under GRH the sum over critical-line zeros majorizes the central multiplicity. It is not an unconditional result.
- Bober's theorem converting that bound into a Mordell–Weil rank bound assumes both BSD and GRH. It therefore cannot answer this request without assuming BSD. The paper's own abstract and introduction say so explicitly. Sources: [Bober, published paper, abstract and §§1–2](https://msp.org/obs/2013/1-1/obs-v1-n1-p07-s.pdf); [Passagemath/Sage API, analytic_rank_upper_bound](https://passagemath.org/docs/10.6/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_rational_field.html), which labels the returned analytic-rank upper bound conditional on GRH.

Thus no applicability-safe published *unconditional* upper-bound theorem was identified. The even functional-equation sign and exact central vanishing discussed above still prove only order at least 2. The 2-descent rank 2 does not imply analytic order at most 2 without BSD.

I did not complete the proposed independent Mellin-integral interval. The relevant split would express the completed second derivative using the Fricke functional equation and an integral over `[1,∞)` of the transformed cusp form weighted by `log(y)^2`. To certify a nonzero value, a finite computation must enclose the integral and separately bound both the Fourier-series truncation and the remaining `y`-tail. This run did not produce those interval bounds or an executed certificate; ordinary high-precision floating point would not suffice. Local probes: `command -v sage` and `command -v magma` found no executable; Python 3.13.5 is present, `mpmath.iv` and SciPy are importable, but no interval quadrature and truncation proof was implemented. No interval is claimed.

The requested `design.md` is not present in this worktree: `find . -maxdepth 5 -type f \( -name 'design.md' -o -name 'design*.md' \)` returned no paths. The task's supplied design-document copy remains explicitly read-only, so I did not recreate or edit it. The previous environment notes remain in the handoff.

This follow-up changes no result status: the rigorous analytic information recorded for 389a1 remains the lower bound `ord_{s=1} L(E,s) >= 2`, conditional on the stated exact modular-symbol central vanishing, known continuation, and sign. Exact order 2 remains unproved here.
