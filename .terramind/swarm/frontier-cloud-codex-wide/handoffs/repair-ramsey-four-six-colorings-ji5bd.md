Outcome: done

## Done

- Recovered `eaf16a5a` and all c5 experiment material. Fixture hash is `37606d8d04af6eb290b9cafcf6b3927edcef1fbe2ee64bdfffbbb5e93d27d321`; c5 output hash is `3cd910cce9f7ba303a7ae6f7ab6e632991c6c4853921252fc18d4ce9d0a5b2a6`; encoder hash is `61c728297681b0dfead93ab1d253588b9b20633d0c8d84aa91c73bd0a35fa2c4`.
- Revalidated Exoo's baseline using `bun frontier diagnose` (valid, value 35, ties best known) and `bun frontier check` on a disposable witness scaffold. Its declarations remained false and the scaffold was moved out of the checkout afterward.
- Re-ran both controls before resuming: the asymmetric clauses forbid colour-0 K4s with a positive literal and colour-1 K6s with a negative literal; planted reconstruction returns the exact 35-vertex fixture with no forbidden clique. The exhaustive direct-scanner control has 14 variables and exactly 16,384 assignments (not 32,768).
- Used one core for 1,740.178 seconds from `--start 2969`. `c6-resume-2969.json` (SHA-256 `733f93d0c1a9beb4fdb38a57f04524ae3cad37c2cf868691d37cb16342c17a49`) and raw `c6-resume-2969.log` (SHA-256 `30139a887eb52b1effde8e17f05c780a1298834e995dc0f92c1635e7dd1d3b13`) preserve every result: indices 2969–5394, UNSAT=2,426, SAT=0, UNKNOWN/timeouts=0. The first unvisited cursor is 5395; unresolved indices are empty.
- No candidate arose, so candidate verification was inapplicable. `bun run check` passed: 434 pass, 1 skip, 0 fail; 18,618 problems and 0 attempts.

## Deviations

- None.

## Concerns

- The tested labelled neighbourhood is still narrow: c4/c5/c6 exclude only tuples 0–5394 of the 52,360 delete-four/five-reinsert cases based on this one Exoo colouring. Other tuples and bases remain.

## Follow-ups

1. Resume exactly at `--start 5395` with the preserved fixture and encoder hashes; retain lexicographic tuple order and per-case timeout accounting.
2. If any SAT model appears, immediately write it to a disposable witness scaffold and run both Frontier diagnose and check while declarations remain false.
3. Inspect PR 36's hosted discussion if `gh` becomes available before changing neighbourhoods.
