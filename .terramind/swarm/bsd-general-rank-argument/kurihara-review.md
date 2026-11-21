# Independent review of the Kurihara comparison

## Verdict

The central conclusion in `kurihara.md` is correct: Kim's paper gives an exact formula for the Selmer corank in terms of the first nonzero Kurihara index, and gives only a parity relation with the complex analytic order. It supplies no unconditional inequality comparing those two orders. In particular, neither an equality nor either direction of an order inequality follows from the cited comparison.

This is a comparison of two different invariants, not two normalizations of the same order. The Kurihara index is the minimum number of prime factors of a square-free Kolyvagin index at which a class in a finite quotient is nonzero. The analytic order is the Taylor order at (s=1). Kim relates the former to Selmer corank and proves a parity statement for that corank; he does not identify it with the Taylor order.

## Primary theorem and hypotheses

Kim's primary paper is Chan-Ho Kim, [*The Structure of Selmer Groups and the Iwasawa Main Conjecture for Elliptic Curves*](https://preprint.press.jhu.edu/ajm/sites/default/files/AJM-kim.pdf), dated May 12, 2025. The relevant definitions are §§1.2.2 and 1.4.1–1.4.4; Theorem 1.8 is §1.5.2; the consequences are Corollaries 1.11–1.13 in §1.7.

The normalization and definitions in `kurihara.md` agree in substance with the paper: (p\ge5), the Kolyvagin primes satisfy \(\ell\nmid Np\), \(\ell\equiv1\pmod p\), and \(a_\ell(E)\equiv\ell+1\pmod p\); \(I_n=\sum_{\ell\mid n}(\ell-1,a_\ell-\ell-1)\mathbb Z_p\); and \(\tilde\delta_n\) is the modular-symbol/logarithm sum reduced modulo \(I_n\). For \(n=1\), \(I_1=0\) and \(\tilde\delta_1=[0]^+=L(E,1)/\Omega_E^+\). The source says the class is well-defined up to a unit; thus zero versus nonzero is independent of primitive-root choices.

One precision point: §1.4.1 first assumes residual irreducibility and (p\nmid\) the Manin constant to define integral modular symbols, but Theorem 1.8 itself assumes the stronger condition that \(\bar\rho_{E,p}\) is **surjective**, along with (p\ge5) and (p\nmid\) the Manin constant. The theorem imposes no good-ordinary or semistability hypothesis. The reviewed document reports this distinction correctly.

Under those Theorem 1.8 hypotheses and \(\operatorname{ord}(\tilde\delta)<\infty\), the paper proves
\[
\operatorname{corank}_{\mathbb Z_p}\operatorname{Sel}(\mathbb Q,E[p^\infty])
=\operatorname{ord}(\tilde\delta).
\]
If additionally \(\Sha(E/\mathbb Q)[p^\infty]\) is finite, Theorem 1.8(4) gives \(\operatorname{rank}E(\mathbb Q)=\operatorname{ord}(\tilde\delta)\). The finiteness of this primary part is a genuine extra hypothesis for converting Selmer corank into Mordell–Weil rank; it is not included in Corollary 1.12.

## What the corollaries establish

Corollary 1.12 assumes the Theorem 1.8 hypotheses and finite Kurihara order, and states
\[
\operatorname{corank}_{\mathbb Z_p}\operatorname{Sel}(\mathbb Q,E[p^\infty])
\equiv \operatorname{ord}_{s=1}L(E,s)\pmod 2.
\]
Combined with Theorem 1.8, this is parity of \(\operatorname{ord}(\tilde\delta)\) and analytic order. It does not imply an order inequality: integers of the same parity can be ordered either way, and can differ by any even amount. No exceptional-zero correction or p-adic interpolation hypothesis occurs in this corollary; it is proved from the functional equation for the Kurihara classes (Kim §3.5) and Theorem 1.8. Hence importing exceptional-zero corrections from a p-adic (L)-function argument would not strengthen or modify this particular parity statement.

Corollary 1.13 states that if \(\tilde\delta_n\ne0\) for a particular \(n\in\mathcal N_1\), then \(\operatorname{rank}E(\mathbb Q)\le\nu(n)\). This is a rank bound from the selected auxiliary index, not from analytic order. Taking the minimum over nonzero classes gives the corresponding bound by \(\operatorname{ord}(\tilde\delta)\) when finite. By contrast, the finite-Sha hypothesis in Theorem 1.8 upgrades that to equality with rank, still without comparing rank to analytic order.

## Exceptional and already-controlled cases

The paper's analytic-rank-zero consequence is genuinely stronger in that special case: if \(L(E,1)\ne0\), then \(\tilde\delta_1\ne0\), so \(\operatorname{ord}(\tilde\delta)=0\) directly. This is equality with analytic order zero, not a general comparison argument. Kim's Corollary 1.11 also gives the rank-zero converse under finite Kurihara order and the same residual and Manin hypotheses.

For analytic rank one, if the Kurihara collection is finite-order and the Theorem 1.8 hypotheses hold, the parity formula makes its index odd. To conclude that it equals one, use additional known rank-one results (Gross–Zagier–Kolyvagin, which also give the relevant Sha finiteness), then Theorem 1.8. This is again restricted to an already-controlled analytic-rank case; it provides no induction step or comparison for analytic order at least two. Kim's Corollary 1.6 lists conditions that guarantee nonvanishing of the collection: localized Iwasawa main conjecture, or in particular good ordinary reduction, analytic rank zero, or analytic rank one with semistable reduction (with the paper's standing residual and Manin hypotheses). These are nonvanishing inputs, not order-comparison theorems.

There is no separate exceptional case in Corollary 1.12 for split or nonsplit multiplicative reduction, additive reduction, or a vanishing Euler factor: the corollary's stated conditions are surjectivity, the Manin-constant condition, and finite \(\operatorname{ord}(\tilde\delta)\), with \(p\ge5\). The more restrictive reduction assumptions enter some cited routes that guarantee nonvanishing, not the parity implication itself.

## Assessment of the augmentation discussion

The discussion in `kurihara.md` correctly distinguishes the complex Taylor variable, the cyclotomic Iwasawa augmentation variable, and the auxiliary-prime count. Kim's Conjecture 1.14 concerns an (X\)-adic order for a Kato zeta element and is explicitly conjectural; it is not a theorem identifying that order with \(\operatorname{ord}(\tilde\delta)\). Kim's proved bridge for the latter is Theorem 1.8 and Corollary 1.12. Therefore a specialization or interpolation argument cannot be inserted here without a new theorem with its hypotheses, local factors, and exceptional-zero terms stated and proved.

## Exact open implication

The proposed general-rank route still lacks a theorem that, for every relevant \(E/\mathbb Q\) and admissible (p), relates \(\operatorname{ord}(\tilde\delta)\) (or Selmer corank) to \(\operatorname{ord}_{s=1}L(E,s)\) beyond parity. The precise missing claims would be either
\[
\operatorname{ord}(\tilde\delta)\le \operatorname{ord}_{s=1}L(E,s)
\quad\text{or}\quad
\operatorname{ord}_{s=1}L(E,s)\le \operatorname{ord}(\tilde\delta),
\]
with appropriate unconditional hypotheses and any needed nonvanishing and Sha assumptions. Neither follows from Kim's theorem or the two corollaries reviewed here. Consequently, this source does not close either general weak-BSD inequality.

## Source references

- Kim, primary paper, [journal-hosted PDF](https://preprint.press.jhu.edu/ajm/sites/default/files/AJM-kim.pdf): §§1.2.2, 1.4.1–1.4.4, 1.5.2 (Theorem 1.8), 1.7.1–1.7.3 (Corollaries 1.11–1.13), and §3.5 (functional equation for Kurihara classes).
- [arXiv:2203.12159](https://arxiv.org/abs/2203.12159): version/bibliographic record.
