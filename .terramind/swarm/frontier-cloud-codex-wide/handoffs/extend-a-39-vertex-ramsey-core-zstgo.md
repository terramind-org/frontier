Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c11` from recovered `6c82092d`; made no attempt, submission, declaration change, push, PR, or merge.
- Rechecked the fourth fixture `57e68639f884e6ccf769367b37f9ac103f9df5c41b55f455f9ad63845e00299a`, encoder `7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`, lexicographic tuple ordering, planted reconstruction, exhaustive encoder/scanner control, color-swap-aware inequivalence evidence, and the audited prefix through index 5,924.
- Ran only indices 5,925–10,447 with `taskset -c 0` and atomic per-tuple checkpoints for 1,650.1742624910003 seconds: 4,522 UNSAT, 1 timeout, 0 SAT, and 9,184,419 decisions. The timeout is index 10,447 (`[22,30,33]`), with 715 decisions; it is unresolved and not counted as UNSAT. Raw result hash: `072b49fb84188c1f8324b230e199d2d0d1359a500dfbcff4b1d8f68c404826d0`.
- Audit across the recovered prefix and this run finds 8,864 distinct classified indices and no duplicates or gaps through 10,447: indices 0–10,446 are final UNSAT exactly once; index 10,447 is unresolved. First unvisited cursor: 10,448; indices 10,448–11,479 are unvisited.
- Control result hash: `85b2364f402e9fcf655430d1ceee64cfe910785890fe341c9be64cedf2f743c5`; all planted and exhaustive controls passed. No SAT graph arose, so Frontier `diagnose` and `check` were inapplicable.
- `bun run check` passed: 434 tests passed, 1 skipped; validation reported 18,618 problems and 0 attempts.

## Deviations

- Restored `python-sat==1.9.dev23` in a temporary virtual environment because the fresh sandbox did not retain PySAT; the recorded fixture, encoder, commands, and outputs otherwise match the recovered experiment.

## Concerns

- This only tests the frozen-39-core/four-insertion family for the fourth seed; it does not determine `R(5,5)`.
- Index 10,447 remains unresolved and the suffix from 10,448 onward is unvisited; neither is counted as UNSAT. Declarations remain false and publication remains pending human approval.

## Follow-ups

1. Retry only index 10,447 (`[22,30,33]`) with a longer cap, retaining the original timeout separately, then resume at 10,448.
2. Validate any SAT candidate immediately with disposable Frontier `diagnose` and `check` before any claim.
3. Pivot only after this seed is exhausted, with recorded color-swap-aware inequivalence and fixture/order hashes.
