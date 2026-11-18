Outcome: done

## Done

- Recovered PR 117 / `ab0f80b0` and revalidated the inherited 713-point pool (SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`), 20,907 collinear triples, valid CF-236 baseline, deterministic catalog ranking, rank-1,036 fingerprint `1d8b984c8a74b4a18baea0a08e52b77b635822bb2afb5f5baefa516524dea291`, and the terminal 32,768-restart greedy ledger. No greedy restart was replayed.
- Resumed the disjoint frozen-core exact feasibility catalog at rank 1,036. It processed every remaining rank through 53,172 contiguously: 52,137 exhaustive restricted UNSAT results, 0 SAT, 0 UNKNOWN/cutoffs, and 0 cardinality prunes. The terminal cursor is `null` because all 53,173 ranked fresh frozen assignments (the inherited 0–1,035 plus this run's 1,036–53,172) are exhausted. Best directly checked size remains 236.
- Each restricted query freezes CF-236 outside a two-anchor blocker-endpoint set and includes every compatible affine-pool point with all local at-most-two collinearity clauses. These results are scoped to those frozen cores; they are not a proof about the unrestricted pool.
- Controls passed: a non-vacuous collinear triple fixture, independent small brute-force enumeration control, and planted valid CF-236 assignment. Frontier diagnose of CF-236 passed: valid, 236, tied best known, no violations. No 237+ witness was found, so no candidate Frontier check was applicable.
- The one-core command ran for 239.642 seconds including catalog reconstruction (the requested 80-second logical deadline was exceeded inside a single inherited DPLL call, whose old deadline check had 1,024-node granularity). The continuation fixes its cursor semantics: an UNKNOWN now remains the next rank rather than being skipped.
- No proof-producing solver or certificate checker is installed in this cloud image (`cadical`, `drat-trim`, `lrat-check`, `kissat`, `minisat`, and `picosat` absent), so no independently verified certificate is claimed. The losslessly compressed per-domain result is 10.0 MiB; its uncompressed SHA-256 is `03224c5c6b44591649698657c106ba489d00cc90ef8686301772dfa9752af0a6` and compressed SHA-256 is `23d86ad5dde9c36fac239067eefac681c5cb5893693dc5880fb651b5433692af`.
- `bun run check` exited 0: 434 passed, 1 skipped, 0 failed. The source SHA-256 is `614c2fa2ac2fd36f9dbe1322f32ac5f64d1e9c205a8199dafb9abec497ad7cac`.

## Deviations

- The terminal-pane launcher failed before execution. A foreground pinned command was used instead.
- The inherited DPLL deadline check did not preempt one difficult domain at the requested 80-second logical deadline; it completed all remaining domains in 239.642 seconds. There were no cutoff results, and the cursor fix protects future interrupted runs.

## Concerns

- Exhausting this catalog does not decide the unrestricted 713-point >=237 problem: every query retains a frozen CF-236 core outside one two-anchor neighborhood.
- The internal exhaustive DPLL outcomes have no externally checkable proof certificates. They must not be described as verified certificates.

## Follow-ups

1. Do not replay ranks 0–53,172 or the completed 256-neighborhood greedy schedule; this two-anchor frozen-core family is exhausted.
2. For a global claim, run the full 713-point >=237 CNF/PB model with a proof-producing solver and independently check any resulting certificate.
