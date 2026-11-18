Outcome: done

## Done

- Recovered PR 109 / `e9cb36ab` and verified its 713-point affine pool SHA-256 `4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6`, 20,907 exact line constraints, controls, 18,932-restart ledger, and checkpoint `{domain_index:147,restart:116,state:"greedy"}`.
- Preserved the recovered atomic continuation (1,118 restarts) to `{domain_index:156,restart:82,state:"greedy"}`; it is continuous from the c13 cursor: `18,932 + 1,118 = 20,050` restarts, with no replay.
- Ran 23 new single-CPU c14 foreground slices using the same single-writer atomic checkpoint. They performed 12,718 further restarts in 504.94 measured solver seconds and exhausted the specified 256 distinct restricted neighborhoods at `{domain_index:256,restart:0,state:"done"}`.
- The cumulative ledger is 32,768 restarts (13,836 since the c13 checkpoint); every selected neighborhood is summarized exactly once, and no domain was cardinality-pruned. Best directly line-checked size remained the valid 236-point CF-236 control. No 237+ candidate existed, so candidate Frontier check/diagnose was not applicable.
- CF-236 independently passed `bun frontier diagnose ... --problem witness.cap-set-f3-7 --json`: valid, value 236, tied best known, no violations. `bun run check` passed: 434 passed, 1 skipped, 0 failed.
- Preserved c14 slice logs, checkpoint, source, controls, result, and baseline. Final result SHA-256: `ba8063ae42e74c4b9f096628d201bc34eeeb322199a5243591128666f793eedb`; source SHA-256: `cca023ee85fce88f857dbb1c4c53fb0cc89ec67bd6e6a4ec878c8846b14f0e5d`.

## Deviations

- The terminal-pane launcher was unavailable, so the experiment used 23 bounded foreground slices. Each slice consumed and atomically replaced the sole checkpoint; the total was below the 30-minute ceiling because the selected domain exhausted.

## Concerns

- This exhausts only the documented 256 seeded restricted neighborhoods, not all 53,429 shared-blocker anchor pairs.
- The unrestricted 713-point target >=237 remains unresolved: this restricted heuristic search produced neither a 237-point witness nor a full certificate.

## Follow-ups

1. Select a new, disjoint restricted-neighborhood family or extend beyond the first 256 pair specifications; do not replay this completed domain.
2. For a global result, run the preserved unrestricted CNF with a model- or certificate-producing solver and independently verify any certificate.
