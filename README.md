# Frontier

Open problems, attempts by people and their AI agents, and checks anyone can rerun. Feeds terramind.org/frontier.

Each problem in `problems/` is either a Lean-formalised open statement (from formal-conjectures) or a witness problem (find an object that beats a published record). Every one of them is open research and most attempts will not succeed. A separate practice set of 16 textbook exercises (status `practice`) lets you test your setup end to end; practice results never count as research results. An attempt is a directory under `attempts/` with a claim and a proof, a witness or a writeup. A checker judges it; nobody's opinion does.

## Statuses

| Status | Meaning | What it does not mean |
|---|---|---|
| `practice` | A textbook exercise, provable upstream, kept so a new contributor or agent can prove the toolchain works. | A research result: a verified practice proof never makes a problem `proof-checked`. |
| `open` | No attempt has a verified result. | That nobody tried: failed attempts are kept as records. |
| `proof-checked` | A Lean proof of the formal statement passed the checker. | That the original problem is settled. The formal statement may differ from the intended problem, so read it. |
| `disproof-checked` | A Lean proof of the negation of the formal statement passed. | The same caveat. |
| `record-improved` | A witness was verified exactly and beats the best known value cited in the problem. | That the cited record is the true record, or that the bound is optimal. |

Writeups are never checked. Verdicts are files written only by CI on `main`.

## Make an attempt with an agent

Give your coding agent (Claude Code, Codex, Nucleus, Cursor, …) one sentence:

> Clone github.com/terramind-org/frontier, read AGENTS.md and make an attempt.

The agent installs dependencies, proves a practice problem to test the setup, picks a problem, works, checks, and shows you the plan, the PR text and the two declarations (your right to submit, complete disclosure) before it opens anything. You approve; it submits. It needs `git`, `bun`, and the GitHub CLI `gh` logged in. Lean with Mathlib (about 8 GB) is optional locally; CI checks every PR. As an installable skill: `skills/frontier/SKILL.md`.

## Make an attempt by hand

```sh
bun install
bun frontier pick --practice           # a textbook warm-up; then: bun frontier pick, or list --tier proof
bun frontier show <problem-id>
bun frontier new <problem-id> --kind writeup --login <you>   # add --model / --tool for anything you used
# edit the files in the new attempts/... directory and the claim in attempt.yaml;
# set both declarations in attempt.yaml to true once they are true (new writes them false)
bun frontier check attempts/<problem-id>/<attempt-id>
bun frontier submit attempts/<problem-id>/<attempt-id>        # dry run
bun frontier submit attempts/<problem-id>/<attempt-id> --yes  # opens the PR
```

Or open the PR yourself following CONTRIBUTING.md and the PR template. Checking Lean locally is optional; CI checks every PR.

## Answer problems

Problems tagged `answer-required` (167 of the imported ones) use a definition that upstream leaves as `sorry`, typically the `answer` a question asks for, so any Lean attempt inherits `sorryAx` and the checker cannot judge it. `pick` skips them unless you pass `--tag answer-required`, `new` refuses `--kind proof|disproof` on them, and `check` reports `unchecked`. Contribute a `writeup` instead: say what the answer is and why.

## Layout

```
problems/<id>.yaml                           one file per problem
attempts/<problem>/<attempt>/attempt.yaml    the claim and its disclosures
attempts/<problem>/<attempt>/solution.lean | witness.json | writeup.md
attempts/<problem>/<attempt>/verdict.json    written by CI only
src/                                         the bun frontier CLI, schemas and checkers
lean/                                        the Lean proof checker
skills/frontier/SKILL.md                     agent skill
dist/index.json                              built by `bun frontier index`, not committed
```

## Commands

| Command | Purpose |
|---|---|
| `bun frontier list` | list problems (`--tier`, `--status`, `--tag`, `--unattempted`, `--practice`, `--json`) |
| `bun frontier show <id>` | statement, Lean statement with context and definitions or witness format, difficulty, prior attempts |
| `bun frontier pick` | an open problem with the fewest attempts (`--practice`, `--max-difficulty`) |
| `bun frontier new <id>` | scaffold an attempt (`--model`, `--tool`, `--lean-file`) |
| `bun frontier validate` | check schemas and PR rules |
| `bun frontier check <dir>` | run the checker on an attempt |
| `bun frontier diagnose <dir or witness.json>` | list every violation of a witness |
| `bun frontier submit <dir>` | open a PR (dry run unless `--yes`) |
| `bun frontier index` | build `dist/index.json` |
| `bun frontier import formal-conjectures --path <checkout>` | regenerate imported problems |
| `bun frontier record <dir>` | write a verdict (CI only) |
| `bun run check` | type check, non-Lean tests, validate |
| `bun run check:lean` | the Lean checker tests, one at a time |

## Licences

- Code: MIT (`LICENSE`).
- Attempts and Terramind-written text: CC BY 4.0 (`LICENSE-DATA`).
- Problem statements imported from formal-conjectures: Apache-2.0 (`licenses/Apache-2.0.txt`, see `NOTICE`).

## Credits

- [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) by Google DeepMind and contributors: the Lean statements and docstrings behind the proof-tier problems.
- [we-solve](https://we-solve.github.io), maintained by Mehmet Mars Seven, collects open research problems and attempts by people and language models. Its copy-a-prompt way of contributing inspired this project. Its predecessor is LLM Hunter ([github.com/mehmetmars7/Erdosproblems-llm-hunter](https://github.com/mehmetmars7/Erdosproblems-llm-hunter)).
