Outcome: done

## Done

- Created `swarm/frontier-cloud-codex-wide--extend-a-39-vertex-ramsey-core-zstgo-c10` from recovered `9c42339f`; made no attempt, submission, declaration change, push, PR, or merge.
- Rechecked fourth fixture `57e68639f884e6ccf769367b37f9ac103f9df5c41b55f455f9ad63845e00299a`, encoder `7d34b69ceeae8c93b32a9f38fac410bbac8291fde184c858e00a534ef615bc4f`, source/provenance `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb` / `7b2f4011e64a21a3f433e69d3a68cae38a784f56398d49b6c3a0c1331104e7c8`, tuple order, and the color-swap-aware inequivalence certificate against the prior three seeds.
- Added atomic per-tuple checkpoint runner `ramsey_c10_checkpoint_sweep.py` (`64cf7651404ed995e3d888f8336de4db90c85ed3e2977c29520a87c8a75329cd`). Its exhaustive encoder/scanner and planted-reconstruction controls passed; control hash: `aeecbd825b1f8082fd7b90b58cdca8e5fd4e3d47b0a62f8aacabfcbe0bcedc52`.
- Retried only index 1,583 (`[1,35,40]`) with a separate 120-second cap: UNSAT in 0.3816975590016227 seconds with 1,803 decisions. The original eight-second timeout remains historical evidence; retry hash: `2d32712d0bf9e639d2dc1cf21e423f8674567d334fcd46245853585a14058e26`.
- Ran only indices 1,584–5,924 on `taskset -c 0` for 1,580.0143323009997 seconds: 4,341 UNSAT, 0 timeout, 0 SAT, and 8,615,214 decisions. Result hash: `b89e9fbd59a01e532916e747fe28d64bb2c5a8c77952e033ef62b1edce28c228`.
- Audit: indices 0–5,924 are final UNSAT exactly once after the isolated retry, with no gaps, duplicates, or unresolved tuple. First unvisited cursor: 5,925; indices 5,925–11,479 are unvisited.
- `bun run check` passed: 434 tests passed, 1 skipped; validation reported 18,618 problems and 0 attempts. No SAT graph arose, so Frontier `diagnose` and `check` were inapplicable.

## Deviations

- None.

## Concerns

- This excludes only the labelled frozen-39-core/four-insertion family for the tested fourth seed; it does not determine `R(5,5)`.
- The fourth-seed suffix from 5,925 onward is unvisited, not UNSAT. Declarations remain false and publication remains pending human approval.

## Follow-ups

1. Resume the identical fourth fixture, encoder, and tuple order with `--start 5925`.
2. Validate any SAT candidate immediately with disposable Frontier `diagnose` and `check` before any claim.
3. Pivot only after this seed is exhausted, with recorded color-swap-aware inequivalence and fixture/order hashes.
