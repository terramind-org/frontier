Outcome: done

## Done

Recovered the final amended c16 commit `8c645ace` from a reachable git object, so its evidence is reconstructed artifact evidence rather than transcript-only evidence. Its manifest verifies, including the 12,000-line append-only record (SHA-256 `ce605b5da2d13fe513c57e9c7d3b4c62872d8ca8e5bc4891bfa424a3da4cd7d5`), atomic cursor, exact-Q positive control, and synthetic interruption control. The c15 split results (orders 0--1535 and 1536--1919) and c16 record join exactly to 0--13919.

Preserved the fixed hash/round-robin order over recorded rewrites 1--6 and kept rewrite 0 excluded. Pinned to CPU 0, c17 began only at the required first unvisited row: order 13920, rewrite 1/support index 62141, `[0,5,14,15,18,21,22]`. Its single append-only writer fsyncs each row before atomically advancing the cursor. Before the second batch it reconciled all 12,000 existing c17 rows against the deterministic order, then resumed at order 25920; no production row was replayed.

Two disjoint c17 batches completed: orders 13920--25919 in 477.979 seconds and 25920--37919 in 472.179 seconds, each with 2,000 rows per rewrite. Both the old integral gate and exact-Q recovery returned zero reductions for all 24,000 c17 rows. Combined c15--c17 coverage is 37,920 contiguous stored rows, exactly 6,320 per recorded rewrite, with zero reductions. Therefore no rank-22 witness existed to reconstruct or send to Frontier diagnose/check. The exact next cursor is order 37920: rewrite 1, support index 174139, `[3,4,8,15,16,18,20]`.

`bun run check` passed: 434 pass, 1 skip, 0 fail. c17 source, interruption/restart reconciliation control, append-only records, atomic result/checkpoint, raw logs, hashes, audit, and gate log are in `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c17/`.

## Deviations

None.

## Concerns

This is a bounded exact-rational trace sample, not exhaustive rational recovery and not a tensor-rank lower bound. It does not exclude the remaining retained rows, excluded rewrite 0, other rank-23 seeds, or different rewrite methods.

## Follow-ups

Resume only the deterministic retained-trace order at 37920, rewrite 1/support index 174139. Do not rerun c15--c17 orders 0--37919, the completed Sun or Perminov integral subset screens, prior 3--6 term scans, the 15,000-state walk, or either pencil scan.
