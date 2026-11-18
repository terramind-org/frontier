Outcome: done

## Done

Recovered PR 146 commit `e83fea61` and verified the c19 24,000-row append-only SHA-256 `da22c4cf79fa9a81f1c556ac8155e427c39d4793257f84f33af13957e46479da`, Perminov seed, four retained trace hashes, fixed rewrite order 1--6, exact-Q positive control, interruption/restart control, and joined coverage through order 85919. The c19 cursor exactly named order 85920, rewrite 1/support index 73365, `[0,10,12,14,19,21,22]`; rewrite 0 remains excluded.

Pinned to CPU 0, c20 resumed only at that row. It ran two restart-safe disjoint batches: orders 85920--97919 in 483.611 seconds and 97920--109919 in 474.182 seconds. Before batch two, reconciliation validated all 12,000 durable c20 records and resumed only at order 97920. Each row was appended and fsynced before the atomic cursor advanced. The unchanged integral and exact rational tests each found zero reductions. No rank-22 witness arose, so Frontier candidate diagnose/check was not applicable.

Coverage is now contiguous through order 109919: 109,920 stored rows total, 18,320 per recorded rewrite. The exact first unvisited row is order 109920, rewrite 1/support index 45190, `[0,3,8,12,14,15,21]`. `bun run check` passed: 434 pass, 1 skip, 0 fail. Evidence, controls, raw logs, results, hashes, and audit are in `matmul3-c20/`.

## Deviations

None.

## Concerns

This remains a bounded exact-rational screen of retained Perminov trace rows, not exhaustive rational recovery or a tensor-rank lower bound. It does not exclude untested rows, excluded rewrite 0, other rank-23 seeds, or different rewrite methods.

## Follow-ups

Resume only at deterministic order 109920. Do not repeat orders 0--109919, generate missing rewrite 0, or reopen completed Perminov/Sun subset screens, prior 3--6-term scans, the 15,000-state walk, or pencil scans.
