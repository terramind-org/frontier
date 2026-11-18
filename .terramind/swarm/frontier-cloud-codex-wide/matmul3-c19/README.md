# c19 Perminov retained-trace exact-Q continuation

c19 recovered and SHA-256 verified PR 141 commit `bb8f8b48`'s c18 evidence, including its Perminov seed, four stored traces, fixed rewrite order, exact-Q positive control, interruption/restart controls, 24,000-row append-only stream, and order-61920 atomic cursor. The c18 package's own manifest validates byte-for-byte.

The continuation runs the unchanged program `matmul3-c17/rational_sample_perminov_resume.py` (SHA-256 `ec531a3e413f1944d92efc50ae8f8e4540260f3ab2d816a6ab42166008631f53`). It reads stored low-flattening trace rows only: no integral subset screen was regenerated. Each rewrite is sorted by `SHA-256(perminov-q-c15-v1:neighbour:support_index)` and rows are consumed round-robin across recorded rewrites 1--6. Rewrite 0 remains excluded because it has no retained per-support trace.

The synthetic interruption control confirms that a cursor names the actual first unvisited row and that resumed order is identical to uninterrupted order. Every production row is appended and fsynced before the atomic cursor is replaced. Batch two reconciled all 12,000 durable c19 records before starting at order 73920.

CPU 0 processed orders 61920--73919 and 73920--85919. Both the historical integral criterion and exact rational complementary-flattening recovery returned no reduction. Consequently no rank-22 witness arose for reconstruction or Frontier diagnosis/checking. This remains a bounded stored-trace screen, not a tensor-rank lower bound or exhaustive rational search.
