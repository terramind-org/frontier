# Auxiliary-prime descent does not turn Selmer classes into rational points

Research cutoff: 21 November 2026. This note tests one proposed repair to the lower-bound gap: perhaps analytic methods produce (r) Selmer classes for many auxiliary primes (p), and compatibility as (p) varies forces (r) points in (E(\mathbb Q)). The Kummer sequences and available comparison theorems do not support that inference.

## The exact sequences, including the maps that do exist

For a number field (K), elliptic curve (E/K), rational prime (p), and integer (n\ge1), the Kummer sequence of Galois modules
\[
0\to E[p^n]\to E(\bar K)\xrightarrow{p^n}E(\bar K)\to0
\]
gives a global connecting map and local connecting maps. The classical Selmer group is the subgroup of (H^1(K,E[p^n])) whose localization at each place lies in the image of the local Kummer map. The resulting exact sequence is
\[
0\longrightarrow E(K)/p^nE(K)\longrightarrow \operatorname{Sel}_{p^n}(E/K)
\longrightarrow \Sha(E/K)[p^n]\longrightarrow0.
\]
Under the standard transition maps as (n) increases, direct limit gives
\[
0\longrightarrow E(K)\otimes\mathbb Q_p/\mathbb Z_p\longrightarrow
\operatorname{Sel}_{p^\infty}(E/K)\longrightarrow\Sha(E/K)[p^\infty]\longrightarrow0.
\]
These are exact sequences at a **fixed** (p). For (p\mid q), there is no natural map (E[p^n]\to E[q^m]), no induced cross-prime map between the corresponding (H^1)'s or Selmer groups, and no canonical “same class” operation between their torsion coefficients. The natural maps above are in the exponent (n) for a fixed prime (and restriction/corestriction when changing fields), not in the prime.

Tensoring at a fixed prime with (\mathbb Q_p) gives the Bloch–Kato Selmer space (H_f^1(\mathbb Q,V_p(E))), with the Kummer image
\[
E(\mathbb Q)\otimes\mathbb Q_p\hookrightarrow H_f^1(\mathbb Q,V_p(E)).
\]
The quotient measures the divisible (p)-primary Sha contribution; equality of dimensions with Mordell–Weil rank requires its vanishing (equivalently, finiteness of the relevant (\Sha[p^\infty])). Thus “dimension (r) for many (p)” still gives only an upper bound on rank unless one controls this quotient. Merely knowing those dimensions agree across primes does not identify the Kummer subspaces.

## Abstract group countermodel (not an elliptic-curve counterexample)

Fix (r>0). Take an abstract finitely generated group (A=0), and for every prime (p) define abstract groups
\[
S_p=(\mathbb Q_p/\mathbb Z_p)^r,\qquad X_p=(\mathbb Q_p/\mathbb Z_p)^r.
\]
Use the zero injection (A\otimes\mathbb Q_p/\mathbb Z_p=0\to S_p), and the identity surjection (S_p\to X_p). Then
\[
0\to A\otimes\mathbb Q_p/\mathbb Z_p\to S_p\to X_p\to0
\]
is exact for every (p); every (S_p) has corank (r), the coranks are uniform over arbitrarily many primes, but (operatorname{rank} A=0). This is an abstract model of the formal shape of the Kummer sequences, **not** a construction of an elliptic curve or a claim that an elliptic curve has such a Sha group. It proves that exactness and cross-prime agreement of coranks alone cannot imply the desired rational-point lower bound. Additional arithmetic input must rule out the (X_p) contribution or put the classes in the Kummer image.

One can add a purely numerical “compatibility datum” by labeling the (r) abstract generators at every prime with the same (r) labels; that still supplies no maps and changes no exactness. A genuine map with image known to lie in the Kummer subgroup, or a theorem proving the quotient (X_p) has corank zero, would be substantive extra input, not a consequence of auxiliary-prime variation.

## Does a motivic compatibility theorem supply that extra input?

The closest standard framework is the Bloch–Kato conjecture for the motive (h^1(E)) (with the appropriate Tate twist). Its rank prediction identifies the dimension of the Bloch–Kato Selmer space with the analytic order, and the elliptic-curve Kummer sequence explains why translating that prediction into Mordell–Weil rank also involves the Tate–Shafarevich contribution. In the elliptic-curve case the statement that the Kummer map is an isomorphism on (p)-adic vector spaces is equivalent to finiteness of the (p)-primary Sha; it is not a known consequence of having compatible realizations at many primes.

The proven compatibility of the (\ell)-adic realizations of (h^1(E)) (for example, the common Frobenius polynomials supplied by the theory of elliptic curves and Faltings) concerns the Galois representations / local Euler factors. It does **not** identify global Selmer groups for different coefficient primes, identify their local Selmer conditions under a cross-prime map, or prove that the quotient by the rational Kummer image vanishes. The required “motivic compatibility theorem” would have to do one of those latter jobs. No unconditional theorem with that content for arbitrary (E/\mathbb Q) was located.

In particular, Bloch–Kato is not such an unconditional exclusion theorem: its Selmer-dimension prediction is conjectural in general and, even if assumed, a Selmer-space dimension is not automatically a point count without the Sha/realization comparison. Applying the conjecture here would assume essentially the rank assertion being sought, not repair the inference from prime variation.

## Verdict on the proposed repair

Auxiliary-prime variation does not presently force rational points. At each (p), one has a Kummer injection and a quotient; across distinct primes, one has compatible realizations of the motive in a broad sense, but no canonical cross-prime Selmer map that sends a class at one prime to a point or identifies its Kummer origin. A sufficient additional lemma would be any of:

1. for each relevant (p), the map (E(\mathbb Q)\otimes\mathbb Q_p\to H_f^1(\mathbb Q,V_p(E))) is surjective (the pertinent Sha finiteness statement);
2. a proved common motivic object whose realizations identify the relevant global Selmer classes and prove that their common classes lie in the rational Kummer image; or
3. a direct construction of (r) rational points with nonsingular canonical-height matrix.

For arbitrary (E/\mathbb Q), none is supplied by the proposed compatibility argument without assuming the missing BSD/Sha input. This route therefore leaves the same unproved lemma as the earlier lower-bound audit: analytic-rank-many rational points (or an equivalent unconditional Selmer-to-Mordell–Weil comparison).

## Primary references checked

- J. S. Milne, *Arithmetic Duality Theorems*, 2nd ed., 2006, Chapter I, §6 (Selmer groups and the exact sequence with (A(K)/nA(K)) and (\Sha(A/K)[n])); author-hosted text: https://www.jmilne.org/math/Books/ADTnot.pdf .
- J. H. Silverman, *The Arithmetic of Elliptic Curves*, 2nd ed., GTM 106, Springer, 2009, Chapter X, §4 (Kummer maps, Selmer groups, and Sha exact sequence); DOI: https://doi.org/10.1007/978-0-387-09494-6 .
- J. Nekovář, *Selmer Complexes*, Astérisque 310 (2006), especially the introduction and §6.1 for Selmer complexes and Bloch–Kato local conditions; publisher/Numdam record: https://www.numdam.org/item/AST_2006__310__R1_0/ . It supplies a derived formalism for a fixed coefficient representation, not the missing cross-prime Kummer-image theorem.
- S. Bloch and K. Kato, “L-functions and Tamagawa numbers of motives,” in *The Grothendieck Festschrift*, vol. I, Progress in Math. 86 (1990), 333–400. This is the conjectural motivic Selmer/L-value framework, not an unconditional all-rank BSD theorem.
- J.-P. Serre and J. Tate, “Good reduction of abelian varieties,” *Annals of Mathematics* 88 (1968), 492–517, and G. Faltings, “Endlichkeitssätze für abelsche Varietäten über Zahlkörpern,” *Invent. Math.* 73 (1983), 349–366. These foundational results support the common arithmetic/geometric representation framework; neither asserts cross-prime equality of global Selmer groups or vanishing of their Sha quotients.
- J. S. Milne, “The Tate–Shafarevich group of an abelian variety,” in *Arithmetic Geometry*, Springer (1986), 167–194, for the role and finiteness conjecture of Sha; author page: https://www.jmilne.org/math/articles/1986b.pdf .

### Prior-note provenance

The two prior notes were read directly from git objects, not copied from another worker's checkout: `higher-rank.md` at commit `7e5c0a1c` (PR 171 merge) and `iwasawa.md` at commit `28150b73` (PR 170 merge). PR 181 itself and its objects were not present in this worktree's fetched refs/reachable history (`git log --all` has no #181 merge), so their provenance could not be verified as originating in PR 181. They inform the boundary above: derived classes and p-adic Selmer conclusions are not rational points, and the Bloch–Kato/Kato frameworks retain theorem hypotheses and the Sha comparison.
