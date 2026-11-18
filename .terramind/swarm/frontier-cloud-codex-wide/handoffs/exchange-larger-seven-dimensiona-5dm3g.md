Outcome: done

## Done

- Recovered PR 113 / `67dc4898` and verified the original affine pool SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, 713 points, 20,907 exact triples, CF-236 control, and terminal old greedy ledger/cursor `{domain_index:256,restart:0,state:"done"}`. The inherited count is exactly 32,768 greedy restarts over 256 neighborhoods; none was replayed.
- Built a new disjoint frozen-core catalog. It excludes every inherited neighborhood fingerprint and collapses identical frozen assignments, leaving 53,173 fresh assignments. Ranking is deterministic: eligible alternatives per removable incumbent descending, then eligible count descending, frozen-core fingerprint ascending, then anchor IDs ascending.
- Ran a complete DPLL SAT feasibility check for local target 237 on ranks 0–1,035 (1,036 new frozen-core domains) on one CPU. Each freezes CF-236 outside its new two-anchor blocker-endpoint set, includes all compatible pool points, and uses every contained collinear triple as an at-most-two clause. All 1,036 were exhaustive restricted UNSAT; 0 cardinality prunes, 0 UNKNOWN, 0 SAT. Compatible pools were 43–45 points with 41–43 removable incumbent endpoints, and DPLL explored 37–406 nodes/domain. Actual solver wall time was 33.197 seconds (14.415 + 18.782).
- Controls passed: independent small brute-force line enumeration, a non-vacuous collinear triple fixture, and planted valid CF-236 assignment. CF-236 Frontier diagnose passed (valid 236, tied best, no violations). No 237+ candidate existed for Frontier witness checking.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed. Preserved the source, controls, rank 0–11 probe, rank 12–1,035 result, stdout, baseline diagnosis, and hashes. Final source SHA-256: `131decf6f0f0bf35b1c4dc31584f7aa7629678d8f73132d5751e5ecf47679cbf`; final result SHA-256: `c51e76ca02301f34730f33d3757093905c14291fc037504a6264c3bf22de1f52`. First unvisited fresh rank is 1,036, fingerprint `1d8b984c8a74b4a18baea0a08e52b77b635822bb2afb5f5baefa516524dea291`.

## Deviations

- No installed external proof-producing SAT backend was available. The retained bounded solver output records complete DPLL status and node counts for each restricted domain, but no independently checkable external UNSAT certificate is claimed.

## Concerns

- These 1,036 results are only frozen-core restricted domains; they do not close the unrestricted 713-point >=237 query.
- The old restart ledger is terminal at 32,768. The 1,036 exact SAT solves are new domain checks, not restarts, and must not be added to that greedy restart count.

## Follow-ups

1. Continue the disjoint exact catalog at rank 1,036 using the recorded fingerprint; do not replay ranks 0–1,035 or the old 256 greedy neighborhoods.
2. For a global result, use a proof-producing SAT/PB backend on the preserved unrestricted instance and independently verify any certificate.
