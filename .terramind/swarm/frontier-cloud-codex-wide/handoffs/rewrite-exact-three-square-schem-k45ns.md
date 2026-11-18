Outcome: done

## Done

Recovered PR 141 commit `bb8f8b48` and verified its c18 manifest, Perminov seed SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`, four retained trace hashes, stable rewrite order 1--6, exact-Q positive control, interruption/restart controls, 24,000-row append-only record, and joined coverage through order 61919. The c18 manifest validates byte-for-byte; rewrite 0 remains excluded.

Pinned to CPU 0, c19 resumed only at order 61920, rewrite 1/support index 90389, `[1,3,4,5,8,13,15]`. It ran two restart-safe disjoint batches: orders 61920--73919 in 472.450 seconds and 73920--85919 in 472.523 seconds. Batch two reconciled all 12,000 durable c19 records before continuing. Each row was fsynced before the atomic cursor advanced. Both the unchanged integral test and exact rational recovery found zero reductions. No rank-22 witness arose, so Frontier candidate diagnosis/checking was not applicable.

Coverage is now contiguous through order 85919: 85,920 total stored rows, 14,320 per recorded rewrite. The exact first unvisited row is order 85920, rewrite 1/support index 73365, `[0,10,12,14,19,21,22]`. c19's 24,000-row append-only SHA-256 is `da22c4cf79fa9a81f1c556ac8155e427c39d4793257f84f33af13957e46479da`. `bun run check` passed: 434 pass, 1 skip, 0 fail. Evidence, hashes, controls, raw logs, results, and audit are in `matmul3-c19/`.

## Deviations

None.

## Concerns

This is a bounded exact-rational screen of retained Perminov trace rows, not exhaustive rational recovery or a tensor-rank lower bound. It does not exclude untested rows, excluded rewrite 0, other rank-23 seeds, or different rewrite methods.

## Follow-ups

Resume only at deterministic order 85920. Do not repeat orders 0--85919, generate missing rewrite 0, or reopen completed Perminov/Sun subset screens, prior 3--6-term scans, the 15,000-state walk, or pencil scans.
