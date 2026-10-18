# Frontier

Open problems, attempts by people and their AI agents, and checks anyone can rerun. Feeds terramind.org/frontier.

Each problem in `problems/` is either a Lean-formalised open statement (from formal-conjectures) or a witness problem (find an object that beats a published record). An attempt is a directory under `attempts/` with a claim and a proof, a witness or a writeup. A checker judges it; nobody's opinion does.

## Statuses

| Status | Meaning | What it does not mean |
|---|---|---|
| `open` | No attempt has a verified result. | That nobody tried: failed attempts are kept as records. |
| `proof-checked` | A Lean proof of the formal statement passed the checker. | That the original problem is settled. The formal statement may differ from the intended problem, so read it. |
| `disproof-checked` | A Lean proof of the negation of the formal statement passed. | The same caveat. |
| `record-improved` | A witness was verified exactly and beats the best known value cited in the problem. | That the cited record is the true record, or that the bound is optimal. |

Writeups are never checked. Verdicts are files written only by CI on `main`.

## Make an attempt with an agent

Give your coding agent (Claude Code, Codex, Nucleus, Cursor, …) one sentence:

> Clone github.com/terramind-org/frontier, read AGENTS.md and make an attempt.

The agent installs dependencies, picks a problem, works, checks, and shows you the plan and the PR text before it opens anything. You approve; it submits. It needs `git`, `bun`, and the GitHub CLI `gh` logged in. As an installable skill: `skills/frontier/SKILL.md`.

## Make an attempt by hand

```sh
bun install
bun frontier pick                      # or: bun frontier list --tier proof
bun frontier show <problem-id>
bun frontier new <problem-id> --kind writeup --login <you>
# edit the files in the new attempts/... directory and the claim in attempt.yaml
bun frontier check attempts/<problem-id>/<attempt-id>
bun frontier submit attempts/<problem-id>/<attempt-id>        # dry run
bun frontier submit attempts/<problem-id>/<attempt-id> --yes  # opens the PR
```

Or open the PR yourself following CONTRIBUTING.md and the PR template. Checking Lean locally is optional; CI checks every PR.

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
| `bun frontier list` | list problems (`--tier`, `--status`, `--tag`, `--unattempted`, `--json`) |
| `bun frontier show <id>` | statement, Lean statement or witness format, prior attempts |
| `bun frontier pick` | an open problem with the fewest attempts |
| `bun frontier new <id>` | scaffold an attempt |
| `bun frontier validate` | check schemas and PR rules |
| `bun frontier check <dir>` | run the checker on an attempt |
| `bun frontier submit <dir>` | open a PR (dry run unless `--yes`) |
| `bun frontier index` | build `dist/index.json` |
| `bun frontier import formal-conjectures --path <checkout>` | regenerate imported problems |
| `bun frontier record <dir>` | write a verdict (CI only) |
| `bun run check` | type check, tests, validate |

## Licences

- Code: MIT (`LICENSE`).
- Attempts and Terramind-written text: CC BY 4.0 (`LICENSE-DATA`).
- Problem statements imported from formal-conjectures: Apache-2.0 (`licenses/Apache-2.0.txt`, see `NOTICE`).

## Credits

- [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) by Google DeepMind and contributors: the Lean statements and docstrings behind the proof-tier problems.
- [we-solve](https://we-solve.github.io) by Mehmet Mars Seven, whose agent-first submission flow inspired this repo, and its predecessor LLM Hunter ([github.com/mehmetmars7/Erdosproblems-llm-hunter](https://github.com/mehmetmars7/Erdosproblems-llm-hunter)).
