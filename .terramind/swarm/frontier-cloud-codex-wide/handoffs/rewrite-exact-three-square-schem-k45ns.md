Outcome: done

## Done

Created c7 from c6 and added support-level deterministic checkpointing in `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c7/seven_term_checkpointed.py`. The accepted interruption control ran 50 supports of neighbour 1 uninterrupted, then 20 supports plus a resume from cursor index 20 for 30 supports. The concatenated interrupted/resumed trace is byte-identical to the uninterrupted trace (both SHA-256 `3f848349132bdcc042c056f0b86fe625537afdcf0b9474f6405865bf0d118eef`). The planted seven-to-one exact reduction passed in every control and in the real run.

The pinned Perminov seed remains SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`. Its decoded baseline was diagnosed with Frontier as valid at rank 23 and tying the known value; the c5 check evidence is retained in the preceding commit. The new baseline diagnosis and repository check are recorded under `matmul3-c7/`. `bun run check` passed: 434 pass, 1 skip, 0 fail.

On CPU 0, resumed seven-term screening at c6's cursor: neighbour 1, support `[0,1,2,3,4,5,6]` (index 0). Neighbour 1 completed all 245,157 supports: 33,982 low-flattening supports, minimum maximum factor rank 5, and zero constructive reductions. The same process then screened 7,843 supports of neighbour 2 (move `[0,15,16]`): 837 low-flattening supports, minimum maximum factor rank 6, zero reductions. It was intentionally interrupted after a durable 1,000-support checkpoint, exit 130, after 751 seconds. The exact resume cursor is neighbour 2, support index 7,843, first unvisited support `[0,1,3,9,12,13,16]`. No candidate was emitted, so none required Frontier candidate verification.

All scripts, seed/baseline, raw logs, traces, controls, checkpoints, and a reproduction note are under `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c7/`.

## Deviations

The first local version of the checkpoint control revealed an implementation error: its stop limit was tested only after a low-flattening support. Those `control-*` raw artifacts are retained as audit evidence. The counter/cursor logic was corrected before the accepted byte-identical control and the real run. The requested 30-minute ceiling was not reached: after neighbour 1 completed and neighbour 2 had a durable cursor, the run was intentionally stopped at 751 seconds to preserve a measured handoff.

## Concerns

The result excludes only the implemented integral constructive criterion for the covered supports. It is not a tensor-rank lower bound and does not rule out later supports, other rank-23 schemes, rational/non-integral replacements, or another reduction technique.

## Follow-ups

Resume only the unvisited seven-term range with `--start-neighbour 2 --start-support-index 7843`, then neighbours 3–6 in order. Do not rerun the complete neighbour 0 (c6), neighbour 1 (c7), supports 3–6, the 15,000-state walk, or the exhausted pencil scans.
