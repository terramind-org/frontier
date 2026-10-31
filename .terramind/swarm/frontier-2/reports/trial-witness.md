# Codex witness trial — 19 October 2026

## Outcome

I selected `witness.golomb-ruler-29` using the required `bun frontier pick --tier witness --json`. Its published best known value is **623**. The 40-minute simulated-annealing search produced no valid ruler: its best candidate had **29 duplicate pairwise differences**, so no valid value was reached and it did not tie 623. The final check rejected the candidate.

`beats_best_known: true` never occurred.

## Timeline

| Elapsed | Command / action | Result |
| --- | --- | --- |
| 00:00 | `bun install` | Installed 9 packages in 147 ms. |
| 00:01 | `bun frontier pick --tier witness --json` | Picked `witness.golomb-ruler-29`, with zero recorded attempts. |
| 00:01 | `bun frontier show witness.golomb-ruler-29` | Learned the exact JSON format, 623 best known, and the difference-uniqueness constraint. |
| 00:02 | `bun frontier new witness.golomb-ruler-29 --kind witness --login trial-codex --model "gpt-5.6-terra-ultra:openai:author"` | Created `attempts/witness.golomb-ruler-29/20261019-trial-codex-31bffa/`. |
| 00:03 | Wrote `search.ts` | Implemented random-restart simulated annealing over 27 interior marks at fixed length 623; objective was duplicate differences. |
| 00:04–40:04 | `bun .../search.ts` | Used the full 40-minute compute budget. The log improved from 59 duplicates to 29, but never reached zero. |
| 40:04 | `bun frontier check <attempt-dir>` | Rejected: `Invalid: difference 1 occurs twice: 1 - 0 and 2 - 1`. |
| 40:04 | `bun frontier submit <attempt-dir>` | Dry run only; printed a generic PR plan and correctly made no changes. |
| 40:05 | Copied artifacts then deleted the attempt directory | Trial artifacts retained under `reports/trial-witness/`; no attempt is committed. |

## Friction and failures

1. **The documented witness workflow does not give a search baseline or construction hint.** `AGENTS.md` says: “**Witness problems reward search compute: write a program that searches, then put its best output in `witness.json`**.” That is directionally correct but insufficient for a difficult 29-mark Golomb ruler: it omits the fact that naive local search at the current best-known length is extremely unlikely to find a valid object. The selected problem has zero prior attempts, so `show` supplied no strategy either.

2. **The command output gives only the scalar objective, not diagnostic structure.** The search could report only duplicate count. To improve a partial candidate, an agent needs the repeated difference frequencies and the marks participating in them; neither the witness format nor CLI surfaces a helper for that.

3. **The time budget was easy to violate operationally.** The requested 40-minute process was started in the background; the first agent turn ended while it ran, so no completion event reached the worker. A follow-up had to inspect `ps` and wait twice in the foreground because the shell wrapper itself outlived the initial wait. Agents need an explicit “do not finish while compute runs” instruction or a CLI search runner whose result is awaited.

4. **`submit` has no machine-readable dry-run output.** It printed the generic plan correctly, but the reported error was: “**NOTE: could not read terramind-org/frontier: gh: Not Found (HTTP 404)**”. That is a poor diagnosis in an offline/unauthenticated trial: it does not say whether `gh` is absent, unauthenticated, or the repository is intentionally inaccessible. The generic plan still includes a fictional GitHub URL and instructions that cannot run in this environment.

5. **The scaffold permits an unchecked placeholder as the default `witness.json`.** `new` created `{}` and an `attempt.yaml` claim reading “**Describe exactly what this attempt claims.**” The check caught the invalid final witness, but a valid scaffold could include the constraint summary and a typed empty array or explicitly make `check` flag the placeholder claim first.

## What would be needed to do better

- A constraint-programming/SAT/ILP formulation with all-different difference constraints, symmetry breaking, and incremental feasibility search over ruler length. OR-Tools CP-SAT, a SAT solver, or a specialised Golomb-ruler package is materially more appropriate than the implemented stochastic objective.
- A known 29-mark ruler seed, preferably from the cited `rulers-all-00.zip`, to verify the local checker and derive neighbourhood moves. The trial followed the CLI-only constraint and did not download or inspect source data.
- More than 40 CPU minutes, preferably parallel restarts or solver cores. At 40 minutes the simple annealer reached only 29 duplicate differences, not a near-valid candidate.
- A CLI helper such as `bun frontier witness diagnose <problem-id> <witness.json>` returning repeated-difference histograms and a precise scorer, so search programs can optimise the same objective the verifier uses.

## Ranked concrete fixes

1. **`AGENTS.md` — add a witness-search playbook.** State that record-level Golomb rulers generally need CP-SAT/SAT or a seeded construction; include a compact all-different-differences formulation and tell agents to validate an archival seed before spending compute.
2. **`src/cli.ts` / witness checker command surface — add `frontier witness diagnose`.** Print the value, every repeated difference, and involved pairs in JSON, enabling deterministic scorer integration and faster debugging.
3. **`AGENTS.md` — add a long-compute lifecycle rule.** After “write a program that searches,” say to run it synchronously or await its PID and never end an agent turn with a search process running; recommend recording wall-clock budget and exit status.
4. **`src/submit.ts` — distinguish GitHub failures.** Replace “`gh: Not Found (HTTP 404)`” with actionable states for no `gh`, no authentication, no repository access, and no network; offer a `--json` dry-run plan for agents.
5. **`src/new.ts` — identify scaffolding as intentionally invalid.** Emit a claim placeholder rejected by `check` with a direct message, and include a `witness.json` schema example in command output without pretending `{}` is usable.

## Preserved artifacts

- `reports/trial-witness/search.ts` — complete 40-minute search program.
- `reports/trial-witness/witness.json` — final rejected candidate.
- `reports/trial-witness/search.log` — objective improvements and terminal result.
- `reports/trial-witness/dry-run.txt` — required check and submission dry-run output.
