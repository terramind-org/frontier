## Done

Ran the prescribed zero-context Codex trial on `witness.golomb-ruler-29`, selected by `bun frontier pick --tier witness --json`. Used `trial-codex` and `gpt-5.6-terra-ultra:openai:author`, ran a real 40-minute simulated-annealing search, checked the final candidate, and ran `bun frontier submit <dir>` without `--yes`. The search did not find a valid ruler: its final length-623 candidate had 29 duplicate differences and `bun frontier check` rejected it. Preserved the search program, final witness, log, and dry-run output in `.terramind/swarm/frontier-2/reports/trial-witness/`; deleted the uncommitted attempt directory. The committed report documents the full timeline, exact friction, outcome, and ranked fixes.

## Deviations

The trial search ran 40 minutes rather than the maximum 45, reserving time to check, dry-run submit, preserve artifacts, and report. The first turn ended while the background search ran; a follow-up waited for the known PID until it completed. This lifecycle failure is recorded in the report.

## Concerns

The simple stochastic search was not competitive on a 29-mark Golomb ruler: it ended 29 duplicate differences from validity, so it did not tie the stated 623 best-known value. The dry run could not inspect `terramind-org/frontier` because `gh` returned `Not Found (HTTP 404)`, and consequently printed only a generic submission plan. No submission, GitHub action, push, or PR occurred.

## Follow-ups

1. `AGENTS.md`: add a witness-search playbook including CP-SAT/SAT guidance and seed validation.
2. Witness CLI/checker: add a machine-readable diagnostic command for repeated differences and participating pairs.
3. `AGENTS.md`: require agents to await long-running search processes before ending a turn.
4. `src/submit.ts`: emit actionable GitHub-auth/access errors and support a JSON dry-run plan.
5. `src/new.ts`: make invalid witness/claim placeholders self-identifying with direct validation feedback.
