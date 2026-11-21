Outcome: done
## Done
- Read `AGENTS.md`; audited both rational targets and their number-field generalizations, including exact quantifiers, imported definitions, dependency assumptions, and prior-attempt availability.
- Compared the formulations with Andrew Wiles's official Clay description and identified the weak-target alignment, the strong-target's additional obligations, and the normalization checks required for the refined formula.
- Wrote the full audit with repository paths and pinned-source/Clay citations to `.terramind/swarm/bsd-research-and-formal-attempt/target.md`.
- Verified the pinned upstream BSD, Hasse–Weil and EllipticCurveRank source text directly. `bun frontier show` was unavailable because `bun` is not installed; tracked attempt history is absent from this fresh checkout.
## Deviations
- Could not use the required Frontier CLI `show` path because `bun` is unavailable. Used the catalog's embedded declarations and definitions and compared them against the pinned upstream source instead.
## Concerns
- The upstream Mordell–Weil finiteness instance is marked solved but its checked-in body is `sorry`, so its intended theorem is not a machine-verified dependency in this source snapshot.
- Prior BSD attempts could not be inspected because no `attempts/` tree is present in this checkout.
## Follow-ups
- Before a checker-tested proof is described as fully verified, inspect the checker’s axiom report and resolve whether the admitted Mordell–Weil dependency enters the final theorem.
- For strong BSD, independently confirm the normalization of the formal trailing coefficient and quotient against the completed L-series/local-factor conventions in the chosen source.
