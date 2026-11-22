Outcome: done

## Done

- Added `transverse-coset.md`, deriving the eventual finite-level exclusion criterion for a compatible class outside the completed saturation of the known primitive point plus torsion. The proof uses compatibility and compactness of the finite cyclic-line quotients.
- Specified that a rational point on any excluded covering yields a Kummer representative outside the saturated rational line, hence rank at least two.
- Proved the `O_{E,B}(p^{2n})` canonical-height bound for centered representatives of every Mordell–Weil completion vector in a fixed full basis, and explicitly separated this estimate from arbitrary Selmer classes with a possible `T_p Sha` component.
- Audited Cassels–Tate and higher-descent routes: nonzero obstruction values can rule out solubility; vanishing or a lift through finite descent is not a sufficient rational-point certificate without extra hypotheses. Identified the first missing noncircular input as proving a transverse class has zero image in `Sha[p^n]` at some finite level.
- Verified the documentation edit with `git diff --check` (clean). No repository tests were run because this is a research-note-only task.

## Deviations

None.

## Concerns

The finite-level criterion is conditional on `x` being an integral compatible class in the classical inverse-limit Selmer group and on the asserted independence after tensoring with `Q_p`. It detects transversality but does not supply a class or force solubility. In the height estimate the constant depends on the fixed Mordell–Weil basis as well as `E`.

## Follow-ups

An independent review should check the finite-level saturation/torsion conventions against the lead's exact strict Selmer structure. The open mathematical gap is the stated unconditional rationality/solubility lemma for at least one transverse covering; no argument here proves it.
