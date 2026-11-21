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
