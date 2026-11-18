Outcome: done

## Done

Recovered PR 124 commit `dd60e0f5` and verified the Perminov seed SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`, fixed screen SHA-256 `d869c72bd610fcc70d7d5fdcbb353afebc8c6630d1d03af1e75e6044c58bedcb`, four retained trace hashes, rewrite order 1--6, c15's corrected order-1920 cursor, and the exact rational positive control. Rewrite 0 remains excluded because no per-support trace was retained. The positive control still exactly proves that the old integral gate returns no factorization while exact-Q recovery replaces four non-projectively-related terms by one.

Added a synthetic 12-row checkpoint control that does not access production rows. Its interrupted checkpoint after five rows named row 5 as the exact first unvisited row; resuming from that row produced the same completed sequence as the uninterrupted control.

Pinned to CPU 0, resumed only at order 1920, rewrite 1/support index 128548, `[1,12,14,15,16,18,21]`. The continuation processed orders 1920--13919 as 12,000 disjoint stored low-flattening rows, exactly 2,000 from each rewrite 1--6, in 474.504 seconds. Each record was appended and fsynced before an atomic cursor update. The old integral gate and exact-Q recovery each found zero reductions, so no rank-22 witness arose for Frontier diagnose/check. With c15, coverage is 2,320 rows per recorded rewrite (13,920 total); no production row was retested. The next exact cursor is order 13920, rewrite 1/support index 62141, `[0,5,14,15,18,21,22]`.

`bun run check` passed: 434 pass, 1 skip, 0 fail. Scripts, interruption control, raw log, append-only 12,000-row record, atomic result/checkpoint, hashes and audit are in `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c16/`.

## Deviations

The first attempt to prefix the production command with `/usr/bin/time` did not start because that executable is absent in this cloud image. It performed zero work; the subsequent CPU-0 command completed the authoritative batch and records the measured Python elapsed time. No production range was replayed.

## Concerns

This is a bounded exact-rational trace sample, not exhaustive rational recovery or a tensor-rank lower bound. It does not exclude untested retained rows, excluded rewrite 0, other rank-23 seeds, or other rewrite methods.

## Follow-ups

Resume only at deterministic order 13920, rewrite 1/support index 62141. Do not rerun the completed Sun or Perminov integral subset screens, prior 3--6 term scans, the 15,000-state walk, pencil scans, c15 orders 0--1919, or c16 orders 1920--13919.
