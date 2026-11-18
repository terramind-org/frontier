Outcome: done

## Done

Recovered PR 134 commit `cf999d4b` directly from this checkout and verified the Perminov seed SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`, four stored trace hashes, stable rewrite order 1--6, exact-Q positive control, synthetic interruption control, c17 append-only record SHA-256 `1956ccad9acadc02c3ec11fdf781a172a21c47745b6f61206be4292429f60169`, and contiguous joined coverage 0--37919. Rewrite 0 remains excluded because no retained per-support trace exists. The inherited positive control exactly shows the integral gate missing a non-projective four-to-one rational identity, while exact-Q recovery verifies it.

Pinned to CPU 0, c18 began only at order 37920, rewrite 1/support index 174139, `[3,4,8,15,16,18,20]`. Its synthetic interruption/restart control again checkpoints the actual first unvisited row (row 5 after five rows) and resumes to the same completed sequence. The production writer fsyncs every JSONL record before atomically replacing the cursor. Two disjoint batches completed: 37920--49919 in 474.923 seconds and, after reconciliation of those 12,000 durable rows, 49920--61919 in 471.689 seconds. Neither the unchanged integral method nor exact-Q recovery found a reduction; thus no rank-22 witness existed to reconstruct or send to Frontier diagnose/check.

c18 adds 24,000 rows, 4,000 per recorded rewrite. Cumulative deterministic coverage is now contiguous through 61919: 10,320 rows per rewrite and 61,920 total, with zero reductions. The c18 append-only record SHA-256 is `2b4e000f9b3fade149bca67ac6499b549633d17085f8fd55a1eb39b8cc8714b8`; its final cursor is order 61920, rewrite 1/support index 90389, `[1,3,4,5,8,13,15]`.

`bun run check` passed: 434 pass, 1 skip, 0 fail. c18 controls, append-only records, atomic results/checkpoint, raw logs, coverage audit, hashes, and gate log are in `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c18/`.

## Deviations

None.

## Concerns

This is a bounded exact-rational trace sample, not exhaustive rational recovery and not a tensor-rank lower bound. It does not exclude the remaining retained rows, excluded rewrite 0, other rank-23 seeds, or different rewrite methods.

## Follow-ups

Resume only the deterministic retained-trace order at 61920, rewrite 1/support index 90389. Do not rerun c15--c18 orders 0--61919, regenerate rewrite 0, the completed Sun or Perminov integral subset screens, prior 3--6 term scans, the 15,000-state walk, or either pencil scan.
