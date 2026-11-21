# Independent review: auxiliary-prime argument

**Scope.** I checked the Kummer exact sequences, the abstract countermodel, the asserted cross-prime compatibility, and the conclusion for arbitrary elliptic curves (E/mathbb Q). This review does not claim that the abstract model is realized by an elliptic curve.

## Findings

### 1. The fixed-prime exact sequences are correct, with one comparison caveat

For every (ngeq 1), the Kummer sequence for multiplication by (p^n) gives

\[
0\longrightarrow E(\mathbb Q)/p^nE(\mathbb Q)
\longrightarrow \operatorname{Sel}_{p^n}(E/\mathbb Q)
\longrightarrow \Sha(E/\mathbb Q)[p^n]\longrightarrow 0.
\]

Taking the direct limit in (n), with the usual transition maps, gives

\[
0\longrightarrow E(\mathbb Q)\otimes\mathbb Q_p/\mathbb Z_p
\longrightarrow \operatorname{Sel}_{p^\infty}(E/\mathbb Q)
\longrightarrow \Sha(E/\mathbb Q)[p^\infty]\longrightarrow 0.
\]

These are fixed-(p) statements. A useful correction in presentation: (H_f^1(\mathbb Q,V_p(E))) is not obtained by simply tensoring the torsion group \(\operatorname{Sel}_{p^\infty}\) with \(\mathbb Q_p\). It is defined from the rational representation and its local Bloch–Kato conditions; the comparison with Kummer classes uses the Tate module/rational representation and the corresponding Selmer structures. The standard Kummer map gives
\[
E(\mathbb Q)\otimes\mathbb Q_p\hookrightarrow H_f^1(\mathbb Q,V_p(E)),
\]
and the cited Bloch–Kato discussion states that this is an isomorphism exactly when the (p)-primary part of \(\Sha\) is finite. Thus the point needed for a Selmer-to-rank inference remains a substantive Sha/comparison input, not a consequence of having multiple coefficient primes. See [Conrad, *An Introduction to the Bloch–Kato Conjecture*, § on elliptic curves](https://virtualmath1.stanford.edu/~conrad/BSDseminar/refs/BKintro.pdf) and [Mazur–Rubin, *Kolyvagin Systems*, §1.6](https://www.wstein.org/people/rubin/book/hEulerSystems.pdf).

### 2. The abstract countermodel is valid and has the right limited scope

For (r>0), take (A=0), (S_p=(\mathbb Q_p/\mathbb Z_p)^r), and (X_p=(\mathbb Q_p/\mathbb Z_p)^r). The zero map (A\otimes\mathbb Q_p/\mathbb Z_p\to S_p), followed by the identity (S_p\to X_p), is exact. Each (S_p) has corank (r), while \(\operatorname{rank}A=0\). This proves that exactness of this abstract sequence and equality of its coranks as (p) varies do not logically force positive rank in the left-hand group.

It is not an elliptic-curve counterexample: no claim is made that these (S_p,X_p) arise as arithmetic Selmer and Tate–Shafarevich groups. Nor does a shared label on abstract generators create a map or arithmetic compatibility. The countermodel establishes insufficiency of the stated formal data, not impossibility of some stronger arithmetic theorem.

### 3. Cross-prime comparison claim is correct when stated as “no canonical natural comparison”

For distinct primes (p,q), there is no canonical coefficient inclusion (E[p^n]\to E[q^m]) supplied by the multiplication Kummer sequences. Consequently, those sequences themselves give no induced map identifying the two global cohomology groups or their Selmer subgroups. This should not be read as the claim that no maps of any kind can ever be constructed: maps can arise from additional structure, choices, correspondences, or a theorem. The point is that compatible ℓ-adic realizations (such as common Frobenius polynomials) do not by themselves supply a cross-prime map on global Selmer classes or certify that a class belongs to the rational Kummer image. The comparison therefore needs an explicit additional theorem and its hypotheses.

### 4. Motivic conjectures do not close the unconditional gap

Bloch–Kato predicts a relationship between the analytic order and a Selmer space for the relevant motive. It is conjectural in general. Even assuming a Selmer-dimension prediction, identifying that space with the rational Kummer image requires the Selmer/Sha comparison just described. Thus invoking Bloch–Kato here would introduce conjectural input and would not turn prime variation alone into an unconditional proof of weak BSD.

## Valid implication and remaining lemma

The direct unconditional implication is the usual one-prime Selmer upper bound: if for some prime (p) one has \(\operatorname{corank}_{\mathbb Z_p}\operatorname{Sel}_{p^\infty}(E/\mathbb Q)\leq r\), then
\[
\operatorname{rank}E(\mathbb Q)\leq r,
\]
because (E(\mathbb Q)\otimes\mathbb Q_p/\mathbb Z_p\) injects into that Selmer group and has corank equal to the Mordell–Weil rank. A bound holding at many primes is consistent with this conclusion but, by itself, gives no lower bound and no new point construction. For the weak BSD equality with analytic rank (r_{\rm an}), the missing direction remains a proof that \(\operatorname{rank}E(\mathbb Q)\geq r_{\rm an}\) for every (E/\mathbb Q), for example by constructing (r_{\rm an}) independent rational points. Alternatively one would need an unconditional theorem connecting the relevant analytic order to a Selmer space *and* a justified Selmer-to-Mordell–Weil comparison. Neither follows from auxiliary-prime variation as stated.

The basic finite-level exact sequence is also recorded in [Silverman, *The Arithmetic of Elliptic Curves*, 2nd ed., Chapter X, §4](https://doi.org/10.1007/978-0-387-09494-6). These references support the standard fixed-prime facts above; they do not provide the missing cross-prime or all-rank theorem.
