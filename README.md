# Frontier

Open problems, attempts by people and their AI agents, and checks anyone can rerun. Feeds terramind.org/frontier.

Each problem in `problems/` belongs to one of three tiers:

- `proof`: a Lean-formalised open statement (from formal-conjectures), judged by the Lean checker.
- `witness`: find an object that beats a published record, judged by an exact verifier.
- `prose`: an open problem of any discipline (mathematics, computer science, physics, economics, biology) stated in words, from we-solve and UnsolvedMath. Prose problems take only writeups, which are never machine-checked. A labelled AI review of a writeup may be shown; it is an opinion, not a verdict, and never changes a problem's status. `pick` offers prose problems only with `--tier prose`.

Prose problems tagged `partially-solved` or `open-status-unverified` are described under Statuses.

Every one of them is open research and most attempts will not succeed. A separate practice set of 16 textbook exercises (status `practice`) lets you test your setup end to end; practice results never count as research results. An attempt is a directory under `attempts/` with a claim and a proof, a witness or a writeup. A checker judges it; nobody's opinion does.

## Statuses

| Status | Meaning | What it does not mean |
|---|---|---|
| `practice` | A textbook exercise, provable upstream, kept so a new contributor or agent can prove the toolchain works. | A research result: a verified practice proof never makes a problem `proof-checked`. |
| `open` | No attempt has a verified result. | That nobody tried: failed attempts are kept as records. |
| `proof-checked` | A Lean proof of the formal statement passed the checker. | That the original problem is settled. The formal statement may differ from the intended problem, so read it. |
| `disproof-checked` | A Lean proof of the negation of the formal statement passed. | The same caveat. |
| `record-improved` | A witness was verified exactly and beats the best known value cited in the problem. | That the cited record is the true record, or that the bound is optimal. |

Writeups are never checked. Verdicts are files written only by CI on `main`. A prose problem stays `open`: no check exists that could settle it.

Prose problems carry two tags worth knowing: `partially-solved` (the source lists partial progress; `upstream_status: partially-solved`) and `open-status-unverified` (the source catalogue does not certify the problem is open: we-solve's owner-supplied economics and biology catalogues).

## Browse without a clone

`npx @terramind/frontier list|show|pick` works anywhere once the catalog is public (it reads the published index). Every other command needs a clone of this repo and bun.

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
problems/<id>.yaml                           one file per problem (ws.* and um.* are prose problems)
sources/<name>.json                          the pinned commit or revision of each imported source
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
| `bun frontier list` | list problems (`--tier proof\|witness\|prose`, `--status`, `--tag`, `--unattempted`, `--practice`, `--json`) |
| `bun frontier show <id>` | statement, Lean statement with context and definitions or witness format, difficulty, prior attempts |
| `bun frontier pick` | an open proof or witness problem with the fewest attempts (`--practice`, `--max-difficulty`; `--tier prose` for prose) |
| `bun frontier new <id>` | scaffold an attempt (`--model`, `--tool`, `--lean-file`) |
| `bun frontier validate` | check schemas and PR rules |
| `bun frontier check <dir>` | run the checker on an attempt |
| `bun frontier diagnose <dir or witness.json>` | list every violation of a witness |
| `bun frontier submit <dir>` | open a PR (dry run unless `--yes`) |
| `bun frontier index` | build `dist/index.json` |
| `bun frontier import formal-conjectures --path <checkout>` | regenerate the proof-tier problems |
| `bun frontier import we-solve --path <clone> --unsolvedmath <dir>` | regenerate the `ws.*` prose problems (run after formal-conjectures) |
| `bun frontier import unsolvedmath --path <dir> --revision <sha>` | regenerate the `um.*` prose problems (run after we-solve) |
| `bun frontier record <dir>` | write a verdict (CI only) |
| `bun run check` | type check, non-Lean tests, validate |
| `bun run check:lean` | the Lean checker tests, one at a time |

## Licences

- Code: MIT (`LICENSE`).
- Attempts and Terramind-written text: CC BY 4.0 (`LICENSE-DATA`).
- Problem statements imported from formal-conjectures: Apache-2.0 (`licenses/Apache-2.0.txt`, see `NOTICE`).
- Prose problems from we-solve and UnsolvedMath: each problem's `source.licence` is exactly its source's licence, CC BY 4.0 or CC BY-SA 4.0. The CC BY-SA 4.0 ones (derived from Oberwolfach Reports) must be shared alike; see `NOTICE`.

## Sources and credits

- [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) by Google DeepMind and contributors (Apache-2.0): the Lean statements and docstrings behind the proof-tier problems.
- [we-solve](https://we-solve.github.io) ([github.com/We-Solve/research](https://github.com/We-Solve/research)), maintained by Mehmet Mars Seven, collects open research problems across disciplines and attempts by people and language models. Problems `ws.<handle>` come from it, each under the licence in its own rights block: CC BY 4.0, or CC BY-SA 4.0 for records derived from Oberwolfach Reports. Its copy-a-prompt way of contributing inspired this project. Its predecessor is LLM Hunter ([github.com/mehmetmars7/Erdosproblems-llm-hunter](https://github.com/mehmetmars7/Erdosproblems-llm-hunter)).
- [UnsolvedMath](https://huggingface.co/datasets/ulamai/UnsolvedMath) by Ulam AI and the UnsolvedMath contributors ([unsolvedmath.com](https://unsolvedmath.com)): problems `um.<id>`. Its curation and metadata are CC BY 4.0; rows derived from Oberwolfach Reports are CC BY-SA 4.0.

The pinned commit or revision of each source is in `sources/<name>.json` and in every problem's `source` field. Imported prose problems are open according to their source; problems already present from an earlier source are skipped, so each problem appears once (formal-conjectures first, then we-solve, then UnsolvedMath), and the kept problem lists the other catalogues in `external_ids` and `references`.
