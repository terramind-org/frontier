Outcome: done

## Done

Created c8 from recovered commit `e8a76d02`. Verified the required c7 inputs before the run: the Perminov source certificate is SHA-256 `80bb4187ddf0cfc04654ca3e524f4d311c5a62245ee231a1101280b43fd2ae3a`; the corrected checkpoint script is SHA-256 `f5e0f615b98328989d26ba77fe7f08f3bcb424b225a2fab5e012d7452538238d`; and c7's accepted byte-identical restart-control trace is SHA-256 `3f848349132bdcc042c056f0b86fe625537afdcf0b9474f6405865bf0d118eef`.

The decoded baseline was diagnosed again with Frontier as valid at value 23, tying the known value. On CPU 0, the unchanged corrected screen resumed exactly at neighbour 2, support index 7,843, first unvisited support `[0,1,3,9,12,13,16]`. Its planted seven-to-one exact reduction passed. The process stayed active across ordinary checkpoints and gracefully finished a 475,000-support bounded segment in 1,269.2146425247192 seconds.

Neighbour 2 (move `[0,15,16]`) is now complete for its previously unvisited range: 237,314 supports, 28,062 low-flattening supports, minimum maximum factor rank 5, and zero constructive integer reductions. Neighbour 3 (move `[1,3,21]`) has a new prefix of 237,686 supports, 29,162 low-flattening supports, minimum maximum factor rank 5, and zero reductions. No candidate was emitted, so no candidate Frontier diagnose/check was applicable. The exact resume cursor is neighbour 3, support index 237,686, first unvisited support `[7,10,14,15,16,21,22]`.

All c8 seed/baseline copies, script, result, 475,000-line deterministic trace, checkpoint, planted control, raw terminal log, baseline diagnosis, repository check, README, and checksum manifest are under `.terramind/swarm/frontier-cloud-codex-wide/matmul3-c8/`. `bun run check` passed: 434 pass, 1 skip, 0 fail.

## Deviations

The bounded run used `--stop-after 475000` rather than consuming the entire nominal 30-minute cap. This gave the script a graceful final write and left time to rerun the baseline diagnosis and repository gate; it did not stop at a routine checkpoint.

## Concerns

This excludes only the implemented integral constructive factorization criterion for the covered supports. It is not a tensor-rank lower bound and does not rule out the remaining neighbour-3 supports, neighbours 4–6, rational/non-integral replacements, other rank-23 schemes, or different reduction methods.

## Follow-ups

Resume only the seven-term range at `--start-neighbour 3 --start-support-index 237686`, then neighbours 4–6 in order. Do not revisit neighbour 0 (c6), neighbour 1 (c7), c8's completed neighbour-2 range, supports 3–6, the 15,000-state walk, or exhausted pencil scans.
