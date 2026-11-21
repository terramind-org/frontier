# Independent review: central-zero isolation by averaging

## Verdict

The central-zero isolation note's main obstruction is sound. Its all-cutoff premise is strong enough, through the Abel transform and the grouped Euler-log comparison in [`abel.md`](abel.md), to imply that (L(E,s)) has no zeros for $\Re(s)>1$. The functional equation about (s=1), together with conjugation, then excludes every noncentral zero in the critical strip. Thus that premise already implies RH for this (L)-function; it is not an RH-avoiding route to weak BSD.

The explicit-formula discussion also correctly identifies why Bober's nonnegative-kernel inequality is conditional on RH. Real-axis nonnegativity of a test function says nothing about its values at off-line zeros. Symmetry pairs these terms but does not force their sum to be nonnegative. Compact Fourier support does not fix this: the Paley–Wiener bound grows exponentially in the imaginary direction, and scaling a fixed off-line zero toward the center increases, rather than suppresses, the available bound.

I found no defect that changes the conclusion. The qualifications below sharpen the scope of the zero-side and arithmetic claims.

## Checks

### Zero-free implication

Write (u=\log x) and (A(u)=\sum_{\log p\le u}b_p), where (b_p=\log(N_p/p)). The premise is (A(u)=R\log u+o(\log u)). Stieltjes partial summation gives, for \(\Re(t)>0\),

\[
F(t)=\sum_p b_pp^{-t}=t\int_0^\infty A(u)e^{-tu}\,du.
\]

The growth (A(u)=O(\log(2+u))) makes the integral locally uniformly convergent there. On the positive real axis, the substitution (v=tu) gives (F(t)=R\log(1/t)+o(\log(1/t))). The local comparison in `abel.md` constructs a holomorphic grouped correction (C(t)) on this half-plane, bounded as real (t\downarrow0), and continues the identity

\[
L(E,1+t)=\exp(C(t)-F(t))
\]

from its absolute Euler-product region by the identity theorem. Since the right side is nonzero, this proves zero-freeness for \(\Re(s)>1\). This use of the identity theorem does not select a logarithm branch for the continued (L)-function: it continues an equality of holomorphic functions.

The completed functional equation sends a zero at (s\) to one at (2-s). A zero with \(\Re(s)<1\) would therefore yield one with real part greater than 1. Conjugation handles the usual symmetry as well. This establishes the asserted location of nontrivial zeros. Strictly, “RH” here is a statement about nontrivial zeros; trivial zeros outside the critical strip are not ruled out or meant to be ruled out.

### Off-line terms and limiting argument

For an even real-type entire test function (h), a generic quartet (z,-z,\bar z,-\bar z) contributes (4\Re h(z)). This is not sign-controlled by (h(t)\ge0) for real (t). Zeros on the real or imaginary symmetry axes have smaller orbits, but symmetry still supplies no general positivity for their off-line contributions. Bober's inference that the explicit-formula zero sum is at least the central multiplicity therefore needs all zeros on the critical line (or a separate estimate proving the same inequality).

If \(\operatorname{supp}\widehat h\subset[-\Delta,\Delta]\), Fourier inversion gives at most an exponential-type bound of the form \(|h(x+iy)|\le C_h e^{2\pi\Delta|y|}\) (with harmless polynomial factors depending on the test-function convention). For the scaled test (h(Tz)), this bound is (C_h e^{2\pi\Delta T|\Im z|}). It provides no dominated-convergence argument over off-line zeros as (T\to\infty). To pass a limiting operation through the full zero sum, one must independently control the aggregate noncentral contribution for that family; pointwise concentration on the real axis is insufficient.

RH is sufficient for Bober's sign argument, but not logically necessary for every possible averaging theorem. A proved zero-density or weighted aggregate bound could substitute if it controls the entire noncentral contribution with the required limiting error or sign. The review does not establish such a bound, nor an impossibility theorem for different kernels or averages.

### Arithmetic comparison

At good primes (N_p/p=1-a_p/p+1/p), so Hasse gives the pointwise bound (b_p=-a_p/p+O(1/p)). This does not provide the cancellation needed after summation: the absolute Hasse bound on the linear term is of order \(\sum_{p\le x}p^{-1/2}\), much larger than \(\log\log x\). The local Taylor expansion also contains a quadratic term at the relevant boundary scale; treating it as an absolutely summable error at (t=0) would be invalid. `abel.md` correctly groups the square contribution as a difference of prime-zeta sums before taking (t\downarrow0\), and treats the finitely many bad primes separately.

The exact missing arithmetic statement is a uniform estimate proving

\[
\sum_{p\le x}\log(N_p/p)=r_{MW}\log\log x+o(\log\log x)
\]

for every (E/\mathbb Q), or a genuinely weaker smoothed estimate accompanied by an independent zero-side theorem identifying its coefficient with the central multiplicity. Reduction of a fixed Mordell–Weil subgroup only bounds its image order by (N_p); it supplies no lower bound uniform in (p), and fixed-modulus Kummer/Chebotarev information does not give the growing-modulus uniformity required here. No such arithmetic estimate is proved by the averaging argument.

Smoothing improves neither obligation by itself. If a family of cutoffs is sufficiently uniform to recover the sharp premise (or the Abel growth used above), it inherits the RH consequence. If it is weaker, the central multiplicity is not identified until the noncentral zero contribution has separately been controlled. In either case, an arithmetic comparison with (r_{MW}) remains unproved.

## Source cross-check

Bober's primary paper states its method under GRH and its Lemma 2.1 is the explicit formula behind the compact-support argument: [*Conditionally Bounding Analytic Ranks of Elliptic Curves*](https://mathweb.ucsd.edu/~kedlaya/ants10/bober/paper.pdf). Sheth's paper states the RH-conditional partial-product asymptotic away from a set of finite logarithmic measure, not the universal coefficient-only point-reduction estimate needed here: [*Euler Product Asymptotics for L-functions of Elliptic Curves*](https://doi.org/10.1093/imrn/rnaf214). These support the stated boundary of the cited methods; neither supplies the missing arithmetic lemma.

## Disposition

No mathematical correction to `explicit-average.md` was needed. This review sharpens two readings: zero-sum convergence under a scaling limit requires aggregate control, not just a pointwise Paley–Wiener estimate; and a substitute to RH could in principle be a sufficiently strong zero-density/weighted estimate, so the obstruction is to the stated positivity argument, not to all possible averaging methods. The route still does not derive unconditional weak BSD.
