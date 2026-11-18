Outcome: done

## Done

- Recovered PR 101 / c11 evidence and independently rebuilt the affine aggregate pool: SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, 713 points, and 20,907 pool-contained collinear triples.
- CF-236 passed Frontier diagnose as valid, with value 236 tied to the stored best known value. Its canonical source hash remains `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- Added `cap7_seeded_pool_exchange.py`: it excludes the exact 10/11-blocker anchor classes addressed by earlier sweeps, selects pairs of novel nonidentity-affine pool points sharing CF-236 blocker endpoints, frees their joint endpoint neighborhood, freezes the other incumbent points, and uses exact incremental F_3 line checks for every selected set.
- The script has an independent 12-point cubic-versus-pair line-enumeration control, a 236-point planted control, and a direct seven-point positive-gain toy (four incumbent points plus three compatible pool points). All controls passed.
- One-core deterministic run: 349 eligible novel affine anchors, 148 excluded prior-class anchors, 53,429 anchor pairs with shared blockers. It completed 507 seeded restarts across three full unique neighborhoods; each had 54 free endpoints, a 182-point frozen core, a 56-point compatible local pool, and best valid size 216. The next fourth domain is resumable at `{"domain_index":3,"restart":123,"state":"greedy"}`. No candidate exceeded CF-236.
- Preserved source, command, stdout, control, result, baseline diagnosis, and SHA-256s: source `258cbec2145167106a0fbf3ae9085efe10132386a27c94bd23ab85e121f05136`; result `a19a5f2411e427cf7c8848775ae05b15b27263bfc6fe810c896182974e95bece`; control `8e4a3610db645b4eba496afe8792a75e28434b0d962f8a8967a83c98b7b9e10a`; stdout `256b3faa44e3e63adf8bd97017f97b38264d9019b1e7c7e8e0466bdfb586db75`; diagnosis `ab7a909e05f3f9a8fd26a4e16113cd5cf435b97ba9ff1d4fb5bb32332f9f0da5`.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed. No 237+ candidate existed, so no candidate Frontier check/diagnose was applicable. Declarations remain unchanged.

## Deviations

- The terminal-pane launcher failed. The available foreground command runner terminated jobs at roughly 30 seconds, so the intended bounded run was explicitly set to and completed at 25.027 seconds on one pinned core, rather than silently treating a killed process as a 30-minute result.

## Concerns

- This is a restricted, heuristic local-family search—not a full-pool SAT/PB proof. The unrestricted pool target >=237 remains unresolved: PR 101’s proof-producing full-pool result was `UNKNOWN`, with neither a witness nor an independently checked certificate.
- Only three full neighborhoods and 507 restarts completed; the result records a precise resume cursor and does not claim coverage of the other 53,425 shared-blocker pairs.

## Follow-ups

1. Resume exactly at domain 3/restart 123, retaining the anchor-level 10/11-blocker exclusion and neighborhood-hash deduplication.
2. If broader evidence is needed, run the preserved unrestricted CNF with a proof-producing solver long enough to emit either a model or a complete independently checked certificate.
