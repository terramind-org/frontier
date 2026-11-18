Outcome: done

## Done

- Recovered PR 104 / `cd49037b` and verified its affine aggregate pool SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, 713 points, 20,907 triples, controls, 507-restart ledger, and cursor `{domain_index:3,restart:123,state:"greedy"}`.
- CF-236 passed Frontier diagnose as valid, with value 236 tied to the stored best known value. Its canonical source hash remains `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- Added `cap7_seeded_pool_exchange.py`: it excludes the exact 10/11-blocker anchor classes addressed by earlier sweeps, selects pairs of novel nonidentity-affine pool points sharing CF-236 blocker endpoints, frees their joint endpoint neighborhood, freezes the other incumbent points, and uses exact incremental F_3 line checks for every selected set.
- The script has an independent 12-point cubic-versus-pair line-enumeration control, a 236-point planted control, and a direct seven-point positive-gain toy (four incumbent points plus three compatible pool points). All controls passed.
- Added atomic resume support and advanced deterministic one-core managed-shell slices without replaying the 507 prior restarts. The terminal launcher failed, so the preserved cursor was consumed slice-by-slice. The measured continuation completed 18,932 total restarts over 147 completed neighborhoods; no candidate exceeded CF-236. First unvisited cursor: `{"domain_index":147,"restart":116,"state":"greedy"}`.
- Preserved source, prior checkpoint, 19 new slice logs, control, result, and baseline diagnosis. Current source SHA-256: `cca023ee85fce88f857dbb1c4c53fb0cc89ec67bd6e6a4ec878c8846b14f0e5d`; current result: `6dca42eadd63ce107a4d79bea66a91118116f1d5abde0e98efe130d0bd896c83`; prior c12 result: `a19a5f2411e427cf7c8848775ae05b15b27263bfc6fe810c896182974e95bece`.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed. No 237+ candidate existed, so no candidate Frontier check/diagnose was applicable. Declarations remain unchanged.

## Deviations

- The terminal-pane launcher failed. Managed 25-second foreground slices were used; the controller was interrupted after 825 seconds of new solver time, before the requested 30-minute allocation. The exact checkpoint makes this an honest resumable partial run.

## Concerns

- This is a restricted, heuristic local-family search—not a full-pool SAT/PB proof. The unrestricted pool target >=237 remains unresolved: PR 101’s proof-producing full-pool result was `UNKNOWN`, with neither a witness nor an independently checked certificate.
- This partial continuation covers 147 completed neighborhoods and 18,932 restarts, not the remaining selected domains or all 53,429 shared-blocker pairs.

## Follow-ups

1. Resume exactly at domain 147/restart 116, retaining the anchor-level 10/11-blocker exclusion and neighborhood-hash deduplication.
2. If broader evidence is needed, run the preserved unrestricted CNF with a proof-producing solver long enough to emit either a model or a complete independently checked certificate.
