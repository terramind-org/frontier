Outcome: done
## Done
- Inspected the existing branch and continued it on `swarm/bsd-general-rank-argument--test-coprime-splitting-of-coveri-zku6g-c2`.
- Expanded `coprime-splitting.md` with a concrete ring-class Heegner test: for (y_c\in E(H_c)), first take (P_c=\operatorname{Tr}_{H_c/K}y_c\in E(K)); the candidate rational coset is (2^{-1}[\operatorname{Tr}_{K/\mathbf Q}P_c]\in E(\mathbf Q)/p^nE(\mathbf Q)). The normalized rational trace coset yields a rational point on the given covering exactly when its Kummer class is (x_n); an actual K-point supplied by (P_c) requires (\delta_K(P_c)=\operatorname{res}(x_n)). The latter implies the former, while the converse can fail because corestriction can have a kernel.
- Made explicit that norm compatibility, a nonzero Heegner point, or a twist (L)-value does not give that finite-level equality. A strict zero localization requires the resulting rational coset to be locally (p^n)-divisible at the strict place. A point on a quadratic twist must be transported and projected with the twist descent character before it can be compared on the fixed curve (E).
- Retained the torsor restriction-corestriction proof and the distinction between (H^1(\mathbf Q,E)[p^n]) and its finite (E[p^n])-lift. The exact obstruction remains construction of a matching Kummer coset (the K-point test is stronger than matching its trace, since corestriction may have a kernel); no general impossibility for special constructions is claimed.
- Verification: reviewed the algebra and existing primary-source discussion; `git diff --check` passed. No repository tests were run because this is a docs-only mathematical audit.
- Commit: see current branch history after this handoff is committed.

## Deviations
None.

## Concerns
The equality (\delta_K(P_c)=\operatorname{res}(x_n)) and the required strict local condition are not consequences of the cited Heegner/Kolyvagin norm relations or twist nonvanishing hypotheses. This is the precise unproved realization lemma.

## Follow-ups
For any proposed specific Heegner setup, verify the exact modular parametrization and twist descent conventions, then prove or refute that a traced Heegner point occupies the displayed finite Kummer coset at the chosen level.
