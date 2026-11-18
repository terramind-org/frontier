# r1 recorded-group single substitutions

This deterministic branch leaves the original 12-anchor generator cursor
parked at **197**. It reconstructs the same 264 fixed / 813 optional mixed
pool from the vendored 512-point cap and cached screen, collects recorded
12-anchor groups, sorts them by decreasing recomputed eligible/deletion ratio
and fingerprint, then enumerates dropped-ID/added-ID substitutions.

Each added point preserves the dropped point's leading F3 slice, and mutated
anchors must remain mutually cap-compatible. The full deletion cover and
eligibility are recomputed, then the strict gate `125 * eligible > 60 *
deletions` and frozen-assignment deduplication are applied before a restricted
solve.

The CPU-0 batch screened 48 substitutions from 47 recorded groups: 17 novel
restricted UNSAT results and 31 within-run duplicates; no prior duplicate,
prune, SAT, or timeout. Resume at base fingerprint
`ed3a9b5bb4c2505f47b06aa9023d61354c0eb6499402b250efec039ef60931de`,
dropped point `2187`, added point `2919`. The fixture hash is
`eb991105b685d77e13acc0d8ae467b9f04db22ca30fb0b3d7a4d656f68a72bf5`.

All new cases passed planted/direct and 256-assignment encoding controls with
zero mismatches; the positive-gain control passed. These frozen-neighborhood
results do not address the full 813-variable pool. No candidate was emitted;
the directly verified cap size remains 512.
