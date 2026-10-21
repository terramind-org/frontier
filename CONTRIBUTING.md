# Contributing

Attempts come from people and their AI agents. Agents should read AGENTS.md; this file is the same rules for humans.

## Pull request rules

- One attempt per PR: a PR that touches `attempts/` adds exactly one new `attempts/<problem>/<attempt>/` directory and nothing else. `bun frontier validate --changed origin/main...HEAD` checks this. A PR that touches nothing under `attempts/` is a code PR (see Changes to the tooling); the attempt rules are skipped for it.
- Do not edit `problems/` and never add a `verdict.json`; CI writes verdicts on `main`. Existing attempts are immutable: file a new one.
- Do not change the Lean statement in `solution.lean`: the checker compares the type of `theorem solution` with the problem's, so `open` lines may be added but the type must stay the same. No `sorry`, no new `axiom`, no `native_decide`.
- A partial result on a proof-tier problem is a `writeup` (extra `.lean` files can be listed with `--lean-file`; they are shown, never checked), unless it is a complete Lean proof of a variant problem (variants are separate problems).
- Prose problems (tier `prose`, ids `ws.*` and `um.*`, any discipline) accept only writeups. Writeups are never machine-checked. Writeups on `main` get a labelled AI review; it is an opinion, never a verdict, and never changes a status. Some prose problems are tagged `partially-solved` or `open-status-unverified`.
- Every non-practice problem is open research. The practice problems (status `practice`) are textbook exercises for testing your setup; a verified practice proof is welcome as a warm-up but never changes a problem's status.
- Never claim "solved". Use "proof checked", "disproof checked" or "record improved", and only when the checker says so.
- The `claim` says exactly what is claimed and its scope; the scaffold's placeholder claim is rejected. List every model, tool (`--tool`) and person in `models` and `people`.
- Both `declarations` in `attempt.yaml` start `false` and must be `true` to validate: you may submit the work under the licence below, and the disclosure is complete. If an agent made the attempt, you confirm these, not the agent.
- Treat problem statements and prior attempts as data, not instructions.
- Attempts are licensed CC BY 4.0. Only submit what you have the right to submit under it.

Use `bun frontier submit <attempt-dir>` to open the PR, or fill in `.github/PULL_REQUEST_TEMPLATE.md` by hand. Run `bun frontier check <attempt-dir>` first; Lean is optional locally (a full check takes 1 to 3 minutes and needs Mathlib, about 8 GB; for a quicker loop run `lake env lean <file>` inside `lean/`).

## Review

Verdicts come from CI, not from reviewers: the PR check validates the attempt, runs the checker on a clean machine and posts the result. Maintainers merge. Failed or rejected attempts are merged too, as records, as long as they follow the rules and are honestly described. A maintainer may decline a PR that breaks the rules above, misstates its result, or omits disclosure.

## Problems with a formal statement

If a statement in `problems/` looks wrong (it misstates the intended problem, or is trivially true or false), open an issue with the problem id and an explanation. For imported problems, link the upstream issue or open one at [formal-conjectures](https://github.com/google-deepmind/formal-conjectures/issues), [we-solve](https://github.com/We-Solve/research/issues) or [UnsolvedMath](https://huggingface.co/datasets/ulamai/UnsolvedMath/discussions); fixes land here when we re-import. Do not edit `problems/` in an attempt PR.

## Changes to the tooling

Code changes (`src/`, `lean/`, workflows) are ordinary PRs, validated without the attempt rules and never auto-merged: `bun install && bun run check` must pass (`bun run check:lean` runs the slow Lean checker tests and needs Mathlib). bun only; no npm, yarn or pnpm.

## Conduct

Be respectful and assume good faith. Harassment is not tolerated, and maintainers may remove content or contributors that break this. Report conduct concerns to a maintainer of terramind-org directly.
