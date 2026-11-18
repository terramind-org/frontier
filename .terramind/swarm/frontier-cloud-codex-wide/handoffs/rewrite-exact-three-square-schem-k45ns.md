Outcome: done

## Done

Recovered PR 120/c14's exact-Q positive control, then recovered the distinct Perminov rank-23 certificate (SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`), fixed rewrite order, and four retained trace hashes. The c4 Frontier diagnosis retained with the seed accepts it at rank 23, tying the known value. The calibrated identity is exactly verified: `4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1 = 4e0⊗(e0+e1/2)⊗(e0+e1/2)`. The old integer gate returns none; exact-Q recovery returns one term, and the inputs differ across both complementary factors.

Pinned to CPU 0, c15 consumed stored low-flattening rows only; no integral subset enumeration was replayed. It sorted each retained rewrite by `SHA-256(perminov-q-c15-v1:neighbour:support_index)` and consumed that order round-robin. The two non-overlapping batches tested 1,920 supports: 320 from each recorded rewrite 1--6. The old and rational methods both found zero reductions. The first batch ran 68.441 seconds; the second ran 19.780 seconds. No rank-22 witness arose, so Frontier candidate diagnose/check was not applicable. The exact next cursor is order 1920: rewrite 1, support index 128548, `[1,12,14,15,16,18,21]`. `bun run check` passed: 434 pass, 1 skip, 0 fail. Scripts, controls, raw batch logs, atomic checkpoints, result records, hashes, and audit are in `matmul3-c15/`.

## Deviations

The first batch's intermediate checkpoint mistakenly named its batch-end cursor before all batch rows had completed. It never caused retesting: its terminal result is correct, was preserved, and c15 corrected the per-support cursor before the separate second batch. The final authoritative cursor is the corrected second-batch checkpoint.

Rewrite 0 has no retained JSONL trace because it completed before trace capture; c15 explicitly excludes it rather than regenerating an integral screen. The deterministic stratified sample therefore covers stored rewrites 1--6 only.

## Concerns

This is a bounded exact-rational sample, not exhaustive rational recovery and not a tensor-rank lower bound. It does not exclude untested trace rows, rewrite 0, rational replacements beyond the sample, other rank-23 seeds, or different rewrite methods.

## Follow-ups

Resume only the rational trace order at index 1920 if more Perminov sampling is wanted. Do not rerun any exhausted Perminov/Sun integral subset screens, prior 3--6-term screens, the 15,000-state walk, or either pencil scan.
