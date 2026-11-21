# Formal target audit: weak and strong BSD

## Scope and source snapshot

The catalog contains four relevant proof targets, all imported from `google-deepmind/formal-conjectures` commit `6751c0f043985ac6647db28a45a63afdf21acffe`, module `FormalConjectures.Millennium.BSD`:

- Rational weak BSD: [`problems/weierstrasscurve.affine.rat.weakbsd.yaml`](../../../../problems/weierstrasscurve.affine.rat.weakbsd.yaml), Lean declaration `WeierstrassCurve.Affine.Rat.weakBSD` (catalog lines 37–46, 59–61).
- Rational strong BSD: [`problems/weierstrasscurve.affine.rat.strongbsd.yaml`](../../../../problems/weierstrasscurve.affine.rat.strongbsd.yaml), Lean declaration `WeierstrassCurve.Affine.Rat.strongBSD` (lines 37–46, 59).
- Number-field weak and strong variants: [`problems/weierstrasscurve.affine.numberfield.weakbsd.yaml`](../../../../problems/weierstrasscurve.affine.numberfield.weakbsd.yaml) and [`problems/weierstrasscurve.affine.numberfield.strongbsd.yaml`](../../../../problems/weierstrasscurve.affine.numberfield.strongbsd.yaml).

The task's “weakbsd” and “strongbsd” correspond to the rational declarations: both take an arbitrary affine Weierstrass curve `E : Affine ℚ` with `[E.IsElliptic]`. The number-field declarations generalize those statements over arbitrary `K` with `[Field K] [NumberField K] [DecidableEq K]` and `[E.IsElliptic]`.

## Formal propositions and quantifiers

At the pinned upstream source, `WeakBSD E` is

`∃ L : ℂ → ℂ, HasMeromorphicContinuation E L ∧ meromorphicOrderAt L 1 = Module.finrank ℤ E.Point`.

`StrongBSD E` is

`∃ L : ℂ → ℂ, HasMeromorphicContinuation E L ∧ meromorphicOrderAt L 1 = Module.finrank ℤ E.Point ∧ Finite E.tateShafarevich ∧ meromorphicTrailingCoeffAt L 1 = bsdQuotient E`.

The exact definitions and declarations are in upstream [`BSD.lean`](https://github.com/google-deepmind/formal-conjectures/blob/6751c0f043985ac6647db28a45a63afdf21acffe/FormalConjectures/Millennium/BSD.lean#L62-L119): `WeakBSD` lines 62–71, `bsdQuotient` 73–78, `StrongBSD` 80–86, and the rational theorem declarations 111–119. The number-field theorem declarations are 88–103.

The continuation predicate in upstream [`HasseWeil.lean`](https://github.com/google-deepmind/formal-conjectures/blob/6751c0f043985ac6647db28a45a63afdf21acffe/FormalConjectures/Wikipedia/HasseWeil.lean#L56-L66) requires a globally meromorphic function agreeing with `E.LSeries` throughout `Re(s) > 3/2`. Thus the existential quantifier is over a specific global continuation, and the order is evaluated at `s = 1`. This is slightly stronger as a package than statements that assume continuation and assert only the order; the upstream comment explicitly discusses the distinction and uniqueness near the point in `BSD.lean` lines 62–69.

## Rank, assumptions, and admitted dependencies

The rank is the integer-module finrank of the elliptic curve's point group, not a separate user-supplied natural number. Upstream makes `EllipticCurveRank.mordell_weil` a local instance in `BSD.lean` line 56. The declaration says the point group is a finite `ℤ`-module and is marked `research solved` with a formal-proof reference, but its body in the pinned source is `by sorry`: [`EllipticCurveRank.lean`](https://github.com/google-deepmind/formal-conjectures/blob/6751c0f043985ac6647db28a45a63afdf21acffe/FormalConjectures/Wikipedia/EllipticCurveRank.lean#L59-L70). This matters for proof trust: `finrank` is intended to denote Mordell–Weil rank, but in this imported snapshot the finiteness instance itself is admitted.

The BSD conjecture declarations themselves are also `by sorry` in the research-catalog source (`BSD.lean` lines 88–97 and 111–119). These are conjecture placeholders, not proofs. The matching Hasse–Weil existence theorem over number fields and the rational analytic-continuation theorem are likewise `sorry` bodies in [`HasseWeil.lean`](https://github.com/google-deepmind/formal-conjectures/blob/6751c0f043985ac6647db28a45a63afdf21acffe/FormalConjectures/Wikipedia/HasseWeil.lean#L90-L115); only the latter is tagged solved. No explicit `axiom` command occurs in the inspected BSD/HasseWeil/EllipticCurveRank source excerpts, but Lean `sorry` introduces `sorryAx`. A checker-tested proof must therefore report its own axiom footprint and must not treat these source annotations as independently machine-checked evidence.

`StrongBSD` further requires finiteness of `E.tateShafarevich`; `bsdQuotient` uses its `Nat.card`, period, regulator, projective Tamagawa product, absolute field discriminant square root, and the square of the torsion cardinality. The target equality is between the meromorphic trailing coefficient and this real-valued quotient (upstream `BSD.lean` lines 73–86). The exact normalization—especially completion/bad Euler factors, period conventions, and the definition of trailing coefficient—needs careful alignment before using a literature formula as a proof target.

## Comparison with Clay's statement

Andrew Wiles's official Clay description says the Taylor expansion at `s=1` has first nonzero term `c(s−1)^r` with `r = rank(C(ℚ))`, and explicitly gives the consequence `L(C,1)=0` iff `C(ℚ)` is infinite. It first describes the incomplete Euler product and says its continuation is now proved. See the official [Clay PDF](https://www.claymath.org/wp-content/uploads/2022/05/birchswin.pdf), pp. 1–2 (PDF page 1 lines 42–60 in the extracted text). Its refined version uses a completed L-series and predicts the leading coefficient using Sha, regulator, real period, local factors and torsion (p. 2, lines 61–86).

**No evident scope mismatch in the rational weak target:** it asserts the same order-of-vanishing/rank equality for every elliptic curve over `ℚ`, using a global continuation. It omits Clay's equivalent rank-zero/nonzero-value corollary, which is not an additional conjecture. The meromorphic formulation is weaker in regularity than a holomorphic continuation but still gives the order statement; over `ℚ`, the analytic continuation is known independently by modularity. The formal definition's extra existential packaging does not appear to add a new open conjecture here, though in its generic number-field form it explicitly includes Hasse–Weil continuation.

**Strong BSD is a refinement, not just Clay's stated weak problem.** It includes weak BSD plus finiteness of Sha and a leading-coefficient formula. This matches the kind of refined formula Clay records, but a checker attempt must prove the precise formal normalization, not merely the weak order statement. Compare the imported `bsdQuotient` definition with Clay's completed-series expression and verify the local-factor/product conventions before claiming the formula matches term-for-term. The catalog labels the rational weak target as the Clay Millennium problem; it does not make the stronger formula a separate Clay prize target.

## Prior attempts and execution limits

`AGENTS.md` was read in full. This fresh checkout has no tracked `attempts/` directory (`git ls-tree -r --name-only HEAD | grep '^attempts/'` returned no entries), and `bun` is not installed (`bun frontier show ...` could not execute). Therefore there are no prior BSD attempts available to inspect in this checkout, and CLI-rendered `show` output could not be obtained. The target YAML embeds the relevant Lean declarations/definitions, and those were cross-checked against the exact pinned upstream source fetched directly. This audit does not edit catalog records or attempts and makes no declarations.

## Recommendation for the research attempt

If the intended deliverable is a result on the Clay weak conjecture, target the rational `weakbsd` declaration and state plainly that the rank side depends on the imported Mordell–Weil finiteness instance in the current upstream library. A proof of `strongbsd` has materially broader obligations: Sha finiteness and the normalized leading coefficient. Do not present a weak target proof as a proof of strong BSD, or as a proof of the full refined formula.
