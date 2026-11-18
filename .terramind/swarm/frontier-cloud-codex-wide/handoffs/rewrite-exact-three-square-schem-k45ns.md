Outcome: done

## Done

Created branch `swarm/frontier-cloud-codex-wide--rewrite-exact-three-square-schem-k45ns-c5`, read `AGENTS.md`, and first checked recovery of c4. Git object `e6455c1de592dc01f82384959053dcb63bda8b00` survived, but its artifacts were absent from the swarm branch. I restored the exact c4 tree from that object into `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c4/`, then copied it immutably into `matmul3-c5/recovered-c4/`. Its seed is the Perminov rank-23 certificate, SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`.

The recovered baseline was independently diagnosed and checked through a disposable, declarations-false scaffold before that scaffold was moved outside the checkout. Both outputs are retained under `matmul3-c5/`: diagnosis reports `valid: true`, value 23, ties best known; check reports `verified` and ties the catalogue value.

Ran the new exact six-term-only support screen, pinned to CPU 0:

```text
taskset -c 0 python3 six_term_neighbors.py matmul3-c4/perminov-cr58-cn122.json six-term-result.json --support-size 6 --control-output planted-control.json --candidate rank22-candidate.json
```

The screen used the recovered seven exact shared-factor Perminov neighbours and the corrected 9-by-9 complementary flattening. It visited all `C(23,6)=100,947` supports for each neighbour: 706,629 total. The exact per-neighbour low-flattening counts were `[3384,3613,3014,3143,3296,3113,3325]` (22,888 total), and every neighbour's minimum maximum factor rank was 5. There were zero constructive integer reductions, hence no rank-22 candidate to diagnose or check. The planted six-identical-summand control reduced exactly from six to one, recorded in `planted-control.json`.

The final command exited 0 after 523.1770594120026 seconds (the shell transcript records 523 whole seconds). Resume cursor is complete: no next neighbour or support. No support size 3, 4, or 5 was visited. `bun run check` passed: 434 tests passed, 1 skipped, 0 failed. `artifacts-sha256.txt` covers every retained c5 artifact, including recovered c4 evidence.

## Deviations

The initial c5 timing command used `/usr/bin/time`, which is unavailable in this cloud image. It did not start the screen. The retained transcript records this failed wrapper, followed by the successful CPU-0 rerun timed with shell `SECONDS` and the script's fractional timer.

The prior c4 artifacts were recoverable only from the dangling Git object, not the swarm branch. They are therefore explicitly retained as recovered provenance rather than represented as branch-native prior work. No evidence is missing from the prior transcript after recovery: commit object, seed, c4 script, raw run log, results, baseline witness, verifier outputs, malformed audit candidate, and manifests all survived in the object.

## Concerns

This exhausts only the corrected constructive criterion: a six-term support must factor in one mode and every complementary 9-by-9 vector must be decomposable with integer factors. It is not a tensor-rank lower bound and does not exclude seven-or-more-term substitutions, other rank-23 orbits, rational/non-integral replacements, or techniques outside this factorization criterion.

## Follow-ups

If further search is warranted, extend this exact fixed-neighbour criterion to seven-term supports with checkpointed per-neighbour cursor output. Do not rerun the completed five- or six-term passes, exhausted 3/4-term pencil scans, or the 15,000-state walk. A distinct verified rank-23 source would be a better diversification target than repeating the Perminov orbit.
