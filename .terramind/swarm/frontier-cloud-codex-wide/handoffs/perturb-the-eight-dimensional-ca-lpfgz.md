Outcome: done

## Done

- Recovered PR 98 / `72ca478f` and reconstructed its mixed-pool scope from the original fixture and screen: fixture SHA-256 `eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`; screen SHA-256 `7ed2e8b2a4caec32f242a60d461f2d41df706df5ba8d23109997c88d17260bac`; 264 fixed points, 813 optional choices, 248 planted baseline optionals, and threshold 249 (total 513). Frontier diagnose again accepts the planted 512-point cap and reports that it ties the known value.
- Added `search/cap8_witness_neighborhood.py`, a one-core deterministic witness-directed neighborhood search.  It starts from the planted 248 optional points, selects outside anchors with deterministic seeds, greedily frees mutable blocker endpoints, freezes every other incumbent point, admits only anchors and outside alternatives made eligible by that release, then rebuilds every affine-line constraint exactly.  It fingerprints the frozen assignment and deduplicates repeated neighborhoods.
- The first seed selection collapsed to a duplicate frozen assignment; this was detected by the ledger rather than counted as independent evidence.  The final diversified run covered six distinct fingerprints (seeds `17,29,43,71,101,131`), all `UNSAT` in their restricted models.  Their deletion / eligible-alternative / variable / line-constraint counts were respectively `116/23/139/9582`, `99/16/115/6550`, `116/29/145/10383`, `104/40/144/9916`, `96/17/113/6309`, and `99/19/118/6877`.  The exact target in each was `deletions + 1`, preserving the total-size threshold of 513.
- Every case passed the planted baseline clause check and a 256-assignment direct scanner versus constraint-enumeration control.  A positive-gain scanner control also passed: replacing one point on a coordinate line with its other two points yields a valid `1 -> 2` toy exchange.  There were no SAT cases, no timeouts, and no candidate, so no candidate Frontier validation was applicable.  Best directly verified cap size remains 512.
- Saved the reproducible script, the duplicate-detection ledgers, the final ledger/hash manifest, the direct Frontier baseline diagnosis, and `bun run check` output.  Final ledger SHA-256 is `23143b2fcb1ef871782033ced0d25be5faa2177869c8430bd2c8de115e99d68f`; script SHA-256 is `61bfe0dd0b8a579b0b648c71ece34f4cacf3ae890fb489b34bf37f137783f78a`.  `bun run check` passed: 434 passed, 1 skipped, 0 failed.

## Deviations

- Pivoted away from another full proof-producing solve as requested.  No SAT proof backend was used because every restricted model was small and the primary exact MILP backend returned a conclusive local UNSAT quickly.
- The initially designed six seeds produced a duplicate frozen assignment.  I retained its compact ledger and changed the deterministic starting-anchor tie-breaker before the final run; only the six distinct final fingerprints are presented as cases.

## Concerns

- Each UNSAT result is limited to its exact frozen assignment, released endpoint cover, and eligible alternative set.  It is not evidence that the 813-variable mixed pool is UNSAT.
- These covers remove 96--116 incumbent points while yielding only 16--40 related alternatives, so this particular four-anchor family has insufficient local cardinality slack before line constraints are considered.

## Follow-ups

- Use the final ledger's resume point (`next_seed: 137`) to test larger or different anchor sets while preserving fingerprint deduplication and the direct scanner controls.
- Prefer anchor groups optimized for a lower delete-to-eligible-alternative ratio; send any SAT candidate of size at least 513 through Frontier diagnose and check before interpreting it.
