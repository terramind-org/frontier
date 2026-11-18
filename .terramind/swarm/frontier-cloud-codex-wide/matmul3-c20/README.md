# c20 Perminov retained-trace exact-Q continuation

c20 recovered PR 146 commit `e83fea61` as primary repository evidence. Its c19 record stream has SHA-256 `da22c4cf79fa9a81f1c556ac8155e427c39d4793257f84f33af13957e46479da`; the cursor names order 85920, rewrite 1, support index 73365, `[0,10,12,14,19,21,22]`.

The unchanged c17 recovery program read the four retained trace files only. It sorts each rewrite by `SHA-256(perminov-q-c15-v1:neighbour:support_index)` then consumes rows round-robin over rewrites 1--6. Rewrite 0 remains excluded because it has no retained per-support trace. No integral screen, pencil scan, or bounded walk was regenerated.

The synthetic interruption control records order 5 as the first unvisited row after five writes and resumes to the same sequence as an uninterrupted run. Each production result is appended and fsynced before the atomic cursor is replaced. Before batch two, the program reconciled all 12,000 durable records before starting at order 97920.

On CPU 0, c20 processed orders 85920--97919 in 483.611 seconds and 97920--109919 in 474.182 seconds. Both historical integral recovery and exact rational complementary-flattening recovery reported zero reductions. No rank-22 witness arose for Frontier diagnose/check. This is a bounded retained-trace sample, not an exhaustive rational screen or tensor-rank lower bound.
