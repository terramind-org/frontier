# c18 Perminov exact-Q retained-trace continuation

c18 recovered c17 commit `cf999d4b` directly from this checkout. Its seed, four stored trace hashes, fixed rewrite order, exact-Q positive control, interruption control, append-only 24,000-row record, and atomic cursor were verified before continuing. Those artifacts establish contiguous coverage through order 37919.

The unchanged c17 program uses exact rational complementary-flattening recovery alongside the old integral method. Stored low-flattening rows are ordered by `SHA-256(perminov-q-c15-v1:neighbour:support_index)` within each recorded rewrite and consumed round-robin across rewrites 1--6. Rewrite 0 stays excluded because it has no retained per-support trace; no integral screen was regenerated.

The synthetic interruption/restart control checkpoints row 5 as the first unvisited row after five rows and resumes to the same sequence as an uninterrupted control. CPU 0 ran disjoint batches 37920--49919 and 49920--61919. The second reconciled all 12,000 durable c18 records before continuing. Both methods found zero reductions, so no rank-22 candidate existed to reconstruct or validate.

This is a bounded exact-Q screen of retained trace records, not a tensor-rank lower bound or an exhaustive rational search.
