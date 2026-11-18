Outcome: done

## Done

- Recovered `fb34cb59` directly from a locally reachable branch ref, not transcript-only evidence, then cherry-picked it as `c2b43c2e`. The restored c6 files are `c6-resume-2969.json`, `c6-resume-2969.log`, and c6 baseline witness/metadata; they cover 2969–5394 with UNSAT=2,426, SAT=0, UNKNOWN=0 and establish cursor 5395. The c6 JSON hash is `733f93d0c1a9beb4fdb38a57f04524ae3cad37c2cf868691d37cb16342c17a49`.
- Matched the Exoo fixture hash `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`, encoder hash `61c728297681b0dfead93ab1d253588b9b20633d0c8d84aa91c73bd0a35fa2c4`, and lexicographic deletion-tuple order. Current Frontier diagnose accepted the baseline at value 35, tied to the best known value; prior recovered Frontier-check metadata remains available and all declarations stay false.
- Re-ran the asymmetric encoder controls before resuming: colour-0 K4 clauses have positive literals and colour-1 K6 clauses negative literals. The planted reconstruction exactly reproduces the 35-vertex fixture with forbidden counts `[0, 0]`. The exhaustive direct-scanner control has 14 variables and exactly 16,384 assignments.
- Ran one CPU for 1,740.041 seconds from `--start 5395`. `c7-resume-5395.json` (SHA-256 `b1eb857775ba3e4ab171747afb3f358df8de6a1c565166959af5b580c363c2ef`) and `c7-resume-5395.log` (SHA-256 `02681885961cdf5fd6467c04471276bfec37bd7026d5851b982ed3b5f0c245da`) preserve every tuple: indices 5395–7895, UNSAT=2,501, SAT=0, UNKNOWN/timeouts=0. There are no unresolved indices; exact first unvisited cursor is 7896.
- No candidate arose, so candidate check/diagnose was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

- The fresh checkout began at c5, but the requested c6 commit was reachable locally and restored directly. No transcript-only result was promoted to evidence.

## Concerns

- c4/c5/c6/c7 only exclude labelled tuples 0–7895 in this 52,360-case replacement neighbourhood of one Exoo 35-vertex colouring. Other tuples and base colourings remain.

## Follow-ups

1. Resume exactly at `--start 7896`, retaining the fixture/encoder hashes, lexicographic order, one-second per-case timeout, and per-tuple checkpointing.
2. If a SAT model appears, immediately write it to a disposable witness scaffold and run Frontier diagnose and check while declarations remain false.
3. Inspect PR 36's hosted discussion if `gh` becomes available before changing neighbourhoods.
