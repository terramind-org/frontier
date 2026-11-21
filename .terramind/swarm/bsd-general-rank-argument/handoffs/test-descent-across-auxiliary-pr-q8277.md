Outcome: done
## Done
- Added `auxiliary-primes.md` with the finite-level and (p^\infty) Kummer exact sequences, fixed-prime transition maps, and an explicit distinction between those maps and nonexistent canonical maps across primes.
- Gave an abstract group countermodel with rank-zero (A), corank-(r) Selmer-shaped groups at every prime, and a matching abstract Sha-shaped quotient. It is expressly not an elliptic-curve counterexample.
- Tested the motivic/Bloch–Kato proposal: compatible realizations/local Euler factors do not identify global Selmer groups or force classes into the Kummer image. The relevant Selmer-dimension/Sha comparison remains conjectural in general, so using it would assume the missing bridge.
- Read `higher-rank.md` and `iwasawa.md` from git objects at commits `7e5c0a1c` and `28150b73`. Checked primary references including Milne’s *Arithmetic Duality Theorems*, Nekovář’s *Selmer Complexes*, Silverman’s *Arithmetic of Elliptic Curves*, and the Bloch–Kato framework.
- Verification: `git diff --check` passed. Documentation-only change; no repository test suite run.

## Deviations
- The task specifically requested the prior notes from PR 181 if absent. PR 181 was not present in the fetched refs/reachable history; the two notes were instead read directly from their reachable git objects, whose merge commits are PRs 170 and 171. This provenance limit is recorded in the research note.

## Concerns
- The abstract model demonstrates insufficiency of the exact-sequence shape and corank agreement only. It does not assert that any elliptic curve realizes the model.
- A full proof of weak BSD for arbitrary (E/\mathbb Q) remains unavailable; the route leaves the unconditional Selmer-to-Mordell–Weil comparison / rational-point construction unproved.

## Follow-ups
- None
