Outcome: done

## Done

- Recovered PR 85's locally reachable `b0bc5af2` state directly, rather than relying on its transcript. The existing c4–c7 files jointly cover the contiguous index range 0–7895. The checked fixture SHA-256 is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`.
- Audited tuple enumeration before resuming: `itertools.combinations(range(35), 4)` has exactly C(35,4) = 52,360 tuples, indexed 0–52,359 in lexicographic order. Index 7895 is `[1,6,11,19]`; 7896 is `[1,6,11,20]`; the final tuple is `[31,32,33,34]`. The prior 52,860 end bound is incorrect by 500 and was not used for coverage credit. The concatenated c4–c8 audit has no duplicate, missing, or tuple-mismatch entry for its credited 0–10,330 range.
- Verified the baseline with Frontier diagnose: valid value 35, tying the best known value. All declarations remain false. Re-ran the asymmetric controls: colour-0 K4 clauses use positive literals and colour-1 K6 clauses use negative literals; planted reconstruction reproduced the fixture with forbidden counts `[0,0]`; the exhaustive scanner control has 14 variables and exactly 16,384 assignments. Corrected the stale source comment which previously claimed 15 variables / 32,768 assignments.
- Ran one CPU for 1,740.318 seconds from `--start 7896`. `c8-resume-7896.json` (SHA-256 `771e51e87d7d762f701d49b649da2b7971cb0642885033ecd66bf1b5ca2b8f2c`) and `c8-resume-7896.log` (SHA-256 `9d1bacd3d2f2d72f9fc5f6c937d823db07fd09f3cd9b797e73fd5760bf2c52bf`) preserve every tuple: indices 7896–10330, UNSAT=2,435, SAT=0, UNKNOWN/timeouts=0. The exact first unvisited cursor is 10331.
- The c8 controls JSON hash is `11c3173633561579b64e584adbb8b51a78885bee602f1ea727d7d0cc1d31f407`; encoder hash after comment correction is `1d4fb41f0839c4a76089a60141a6f42c7325e76e8bd12329cb28d58fc8661463`. No candidate arose, so candidate validation was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

- `gh` is unavailable, so PR 85's hosted metadata/discussion could not be read; the locally reachable commit was the recovery source.
- The terminal-pane service failed to create a pane, so the single bounded process was waited on directly; no concurrent solver was started.

## Concerns

- Only labelled tuples 0–10,330 of the correct 52,360-case replacement neighbourhood of one Exoo 35-vertex colouring have been exhaustively searched. Other tuples and base colourings remain.

## Follow-ups

1. Resume exactly at `--start 10331`, retaining the fixture hash, lexicographic order, one-second per-case timeout, and per-tuple checkpointing. Never use an end cursor beyond 52,360.
2. If a SAT model appears, immediately write it to a disposable witness scaffold and run Frontier diagnose and check while declarations remain false.
3. Inspect PR 36's hosted discussion if `gh` becomes available before changing neighbourhoods.
