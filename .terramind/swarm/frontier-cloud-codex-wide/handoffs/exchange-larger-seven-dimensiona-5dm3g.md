Outcome: done

## c11 proof-producing SAT follow-up

- Recovered original c10 commit `1552edcb` directly from the reachable c10 branch; restored its PB source/instance/control/result exactly, excluding its five incidental `__pycache__` blobs. The c10 instance SHA-256 remains `0a10029f577565a730ac53f47020827efa629c3ceed2f4e08ccad901d10c4787`.
- Rebuilt the unrestricted c9 affine pool and confirmed 713 points, pool SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, and 20,907 triples. The new DIMACS contains no restriction beyond that pool: 339,625 variables and 698,967 clauses, SHA-256 `97925168d03bb7190a1ca501017765bbce6cebcf81ed5d5853410df8b6d60b5f`.
- Controls: a non-vacuous fixture with line `[0,12,371]` rejects all three selected but accepts two; brute-force/fast small enumeration agrees; and planted CF-236 satisfies every line clause. Frontier diagnose accepted CF-236 (236, ties record).
- One-core command was `taskset -c 0 cadical --no-binary -t 1560 cap7_affine_pool_sat_237.cnf cap7_affine_pool_sat_237.drat`. CaDiCaL 3.1.0 returned `UNKNOWN` after exactly 1560.00 real seconds (1532.42 solver CPU seconds, 11,674,096 conflicts); no candidate or UNSAT certificate exists. The query is unresolved. Its incomplete 6.8 GB trace was deliberately not retained.
- SAT source/CNF/meta/log SHA-256: `fc8b6be6273e9160f5475a1cba7b50135bde76a8c5e6d5151a254f6ad7496aa5`, `97925168d03bb7190a1ca501017765bbce6cebcf81ed5d5853410df8b6d60b5f`, `0de8e9d99ec6538634a227f8bc8f931a55f558917e3cf905cafd4e8bb0c10a13`, `bec6e36c9fb054feeeaaf209ee9bcd2c6981d2d7c509ced605b48e8a45e3810c`.

## Done

- Created c9 from recovered PR 79 / c8 commit `f2cc12cf`. The recovered CF-236 witness passed `bun frontier diagnose .terramind/swarm/frontier-cloud-codex-wide/raw/cap7_cf236.json --problem witness.cap-set-f3-7`: valid, value 236, tied best known. Its raw-file SHA-256 is `3b42f2f7a4d9dc372601179611dd6f185418eff7c40c0c67aa1af917c7ff3582`; its canonical sorted point-set SHA-256 is `6352c2d059a2cf61ec98459050cd460e20e6037a54a681036939054318c6f8df`.
- Added `cap7_affine_layer_recombine.py`, a distinct nonlocal search family. It splits CF-236 on coordinate `x0` into slices `12/112/112`, retains `x0=0`, and applies separate documented invertible affine maps of the six tail coordinates to the `x0=1` and `x0=2` slices. It never uses a shared layer map as a nonlocal construction. The aggregate pool contains 713 distinct points (a genuine upper bound above 236); each pair-domain has upper bound 236.
- Controls passed before the run: the identity/identity positive control returns the exact valid 236-cap; independent brute-force enumeration of all triples agrees with incremental compatibility on a 9-point fixture; and two transformed 112-point layers independently satisfy the exact cap test. Each selected point in every run is filtered with the exact equation `third(p,q) not in selected` for every already selected `q`.
- One-core command: `PYTHONDONTWRITEBYTECODE=1 taskset -c 0 python3 .terramind/swarm/frontier-cloud-codex-wide/cap7_affine_layer_recombine.py --seconds 1740 --restarts 4096 --out .terramind/swarm/frontier-cloud-codex-wide/raw/cap7_affine_layer_result.json`. It ran to the 1740-second bound on CPU 0. It completed 59,959 deterministic greedy restarts across the aggregate plus 13 complete nonlocal pair-domains. One pair-domain is unresolved at the explicit cursor `{"construction_index":14,"restart":2615,"state":"greedy"}`; no domain was silently dropped.
- Best valid size was the 236-point identity/identity positive control. The augmented 713-point pool peaked at 142 under the exact filter; completed nonlocal pair-domains peaked at 225. No candidate exceeded 236, so there was no improvement to send through Frontier check/diagnose.
- Preserved script/control/result/stdout SHA-256 respectively: `c34c198c1b0b287a575432ae4c9fced01dba91fce0d7dded9a1507e06d8ae615`; `f18a161a0bf7d97ae4d8f215c90b72880e07294779177c755cd5fe217adabbed`; `408fe404d0cc3e560b9e23b29fa175032fc5bacaccd1b952840061984319ad65`; `ec9f6d7e913c2441e28feb31e021274c606048ca0ef45e4c2e36344d6aebf19a`.
- `bun run check` passed: 434 passed, 1 skipped, 0 failed; validation reported 18,618 problems and 0 attempts. No attempt, submission, merge, local compute, or declaration change was made.

## Deviations

- This bounded randomized-greedy construction search reached its 29-minute internal deadline rather than completing all 16 domains; its deterministic seeds and exact resume cursor preserve the unfinished tail. It is an exact cap-condition filter, not an exact maximum-subset solver.
- PR 79 was recovered through its available pull ref (`f2cc12cf`) rather than `gh`.

## Concerns

- The 713-point figure is only a candidate-pool upper bound; cross-layer line constraints make it much smaller after selection. The experiment does not prove a global upper bound or rule out different affine maps/splits.
- The remaining tail begins at domain 14 / restart 2615. Resume with the same seed order, not a fresh sample, if this map family is continued.

## Follow-ups

1. Resume only the unfinished final affine pair-domain from `{"construction_index":14,"restart":2615,"state":"greedy"}`, or use a stronger exact/CP-SAT subset solver on the 713-point aggregate pool.
2. Explore a different hyperplane functional or transformations with a larger structured candidate pool; do not repeat the completed 59,959 restarts or the prior 491,520 deletion covers.
