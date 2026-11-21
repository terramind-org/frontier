Outcome: done
## Done
Wrote `.terramind/swarm/bsd-general-rank-argument/abel.md`. It proves the Abelian implication from a cumulative logarithmic asymptotic to a Laplace coefficient only under explicit transform convergence assumptions, and notes that Hasse alone gives absolute convergence of this proposed transform only for `t > 1/2`. It distinguishes the transform of `log(N_p/p)` from `log L(E,1+t)`, accounts for the good-prime local factors, the non-absolutely-summable-at-zero prime-square majorant, the finite bad-prime contribution, the absolute Euler-product boundary at `Re(s)=3/2`, and the local logarithm/continuation issue. It identifies the further needed arithmetic estimate from reductions of a Mordell–Weil basis and checks Goldfeld, Conrad and Sheth against primary/publisher sources. Documentation-only task; no tests run.
## Deviations
None.
## Concerns
The requested Abel argument does not yield a sufficient criterion from (1) alone: the raw proposed Laplace transform need not converge near zero, and even where defined it is not the continued L-function logarithm. It would be unsafe to claim a weaker Goldfeld theorem without proving extra regularization and boundary terms.
## Follow-ups
Prove or disprove an appropriately regularized identity connecting the smoothed local logarithms to `log L(E,1+t)`, including the symmetric-square/prime-square contribution, branch control and any zero-free hypothesis; separately establish the coefficient-only product estimate from point reductions. Neither result was found or proved here.
