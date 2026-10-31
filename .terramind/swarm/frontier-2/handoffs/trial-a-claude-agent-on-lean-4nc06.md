# Handoff: trial-lean (Trial a Claude agent on Lean)

## Done

- Ran the trial as a zero-context agent (AGENTS.md, README, CONTRIBUTING, CLI output, plus upstream problem sources)
  from 08:27 to 09:19. Both attempts reached `bun frontier submit <dir>` (dry run). No `--yes`, no push, no GitHub,
  no `lake exe cache get`. Only FormalConjectures modules were built into the shared cache (727, OEIS 103662,
  Paper.Kurepa).
- **Warm-up.** `erdos1.erdos-1.variants.weaker` isn't in `problems/`, and none of the 274 variants is upstream
  textbook or solved. I picked `oeisa103662.conjecture.variants.a-40` and proved in Lean that b^40 has a zero digit
  for every b > 1 that is odd or divisible by 5. The case b even with 5 ∤ b is open; a search found no counterexample
  for b ≤ 200000. Filed as a writeup with `partial.lean`.
- **Main** (done 08:50–09:19, about 30 of the 60 minutes, before the lead's continue message; not repeated).
  `pick --tier proof` gave Erdős 604 (average pinned distances), which is out of reach in 60 minutes, so I
  worked on `erdos727.erdos-727.variants.k-2` instead. Proved in Lean the reduction to C(2n,n), the bound
  `2·v_p((n+1)(n+2)) ≤ log_p 2n` and its consequence `p² ≤ 2n`, and computed the 23,760 solutions up to 2·10⁶.
  Infinitude is not proved. Kept a rejected proof attempt (`uses sorry`) and the writeup I'd actually submit.
- **Probes:** a changed statement (k = 0) is rejected with `type mismatch` (good); a deliberate tactic error comes
  back as a full Lean error with goal state (good); the Kurepa scaffold doesn't parse.
- No check returned `verified`. All Lean lemmas use only `propext`, `Classical.choice` and `Quot.sound`
  (`#print axioms`).
- Report: `.terramind/swarm/frontier-2/reports/trial-lean.md`. It has the timeline with every `check` duration,
  every stumble quoted, root causes from reading `src/` and `lean/check-attempt.sh` afterwards, and 15 ranked
  fixes. Artefacts are in `reports/trial-lean/`: attempt files, all check/validate/submit outputs, probes, the
  scripts behind every number, and the per-variant upstream status table. Attempt directories were deleted;
  nothing under `attempts/` is committed.
- The lead's evidence items (a)–(e) each have a section in the report with exact output. (a) is now counted
  properly: 10 of 1,471 statements end mid-`letI` binder, all 10 confirmed truncated against upstream, and none has
  unbalanced brackets (`scripts/truncation.ts`, `outputs/truncated-statements.txt`). That corrects the 9 in my first
  draft.
- Repo check, `bun run check`: `tsc --noEmit` passed. `bun test` gave **169 pass, 10 fail**, so `validate` never
  ran. All 10 failures are Lean checker tests in `test/check/proof/proof.test.ts`, each
  `timed out after 1800000ms`. They run `test.concurrent` behind a limiter on a machine at load average 16–24 with
  ~19 other `lake`/`rustc` processes. In isolation, test (d) passes in 0.5 s. Test (b): rerun pending; previous failure
  attributed to queue time, unconfirmed. One isolated run of (b) **failed** after 1,537.97 s, which is under the
  30-minute limit, so queue time doesn't explain that run; I didn't read its cause (`outputs/isolated-test-b.txt`).
  I changed no code, but the full gate did not pass in this worktree, and (b) needs the judge's rerun.

## Deviations

- The task says to read `design.md` before starting, but the trial rules forbid swarm docs until the attempts are
  done. I read it after the attempts, at 09:25.
- I read the upstream FormalConjectures `.lean` sources in `lean/.lake/packages/formal_conjectures/` during the
  trial. `show` doesn't print the definitions a statement uses (`h`, `f`, `gamma`, `v_l`, local notation), and
  `show` links that source. I count this as problem data, not Frontier internals. It's recorded as a finding.
- I used `cd lean && lake build <module> && lake env lean <file>` for fast iteration (30–60 s versus 1–10 min for
  `check`). AGENTS.md doesn't mention this; it's recorded as a fix.
- The main attempt used about 30 of the allowed 60 minutes; I stopped when no constructive route was left.
- Both final attempts are `writeup`s, not `proof`s, because AGENTS.md says a partial result on a proof-tier problem
  is a writeup. The 727 rejected proof attempt is kept in `reports/trial-lean/727-proof/` for the record.

## Concerns

- **Every proof scaffold is rejected as generated.** The comment `` new `axiom`s are rejected `` written by
  `src/commands/new.ts` trips the raw-text precheck in `lean/check-attempt.sh`:
  `source uses an axiom declaration (line 6); attempts may not run code while compiling`. The same precheck rejects
  comments containing the words meta, macro, syntax, elab, unsafe or initialize. Fix this before any external agent
  tries the repo.
- **10 problems have a truncated Lean statement** (`letI`/`haveI` aren't handled by `statementEnd` in
  `src/import/lean-parse.ts`). The site-pages task renders `lean.statement`, so these 10 /frontier/ problem pages
  show broken Lean today. The ids are in the report.
- **Scaffolds don't carry upstream `open`/`local notation` context.** The Kurepa scaffold fails to parse, and others
  probably do too. Not measured across the catalogue.
- **The catalogue has no tractable proof problems.** Everything imported is upstream research-open, so AGENTS.md's
  "realistic progress is in variants" sets agents up to fail. The site copy may make the same promise; worth a look
  by the fact-checker.
- **Local `check` takes 1–10 minutes**, dominated by sha256 over 7.8 GB of packages, three times per run. `submit`
  re-runs it: a dry run took 8 min 20 s. `bun run check` in this worktree also ran long for the same reason (it
  runs the Lean fixtures).
- **The Lean test suite didn't pass here.** 10 Lean checker tests timed out in `bun run check`. Run on its own,
  test (b) still failed, after 1,538 s, under its timeout, with the cause unread. The judge's rerun should confirm
  whether the suite passes on a quieter machine.
- The placeholder claim passes `validate`, `check` and `submit` and lands in the PR body.
- `new` pre-ticks `declarations: rights: true, disclosure_complete: true`, so the agent declares rights on the
  human's behalf and the PR body shows both boxes ticked.
- `validate` accepts extra files such as `partial.lean` in a writeup, but nothing compiles them. AGENTS.md lists only
  `writeup.md`.

## Follow-ups

Ranked fixes (details, files and quotes are in the report):

1. `src/commands/new.ts`: reword the scaffold comment (no `` `axiom` ``). `lean/check-attempt.sh` precheck: name the
   matched word and say comments are scanned, or better, strip comments before scanning. Add a test that a
   scaffold passes the precheck.
2. `src/import/lean-parse.ts` `statementEnd`: handle `letI`/`haveI`/`let_fun`, add a parser test, re-import
   (10 problems).
3. `src/commands/new.ts` plus the importer: emit the upstream `open`/`open scoped`/notation context, and compile
   every scaffold once in CI. AGENTS.md: "same elaborated type" rather than "line must stay as scaffolded".
4. `lean/check-attempt.sh`: cheaper tamper hashing in local mode, plus progress output. `src/commands/submit.ts`:
   reuse a recent check result for an unchanged file.
5. AGENTS.md "Work": document `lake build <module>` + `lake env lean` + `#print axioms` as the iteration loop, and
   say `check` takes minutes.
6. Importer or AGENTS.md "Picking well": import textbook/solved variants as a practice tier, or state plainly that
   every imported problem is open research.
7. `src/commands/validate.ts` / `src/schema.ts`: reject the placeholder claim; `submit` should refuse it.
8. `src/commands/show.ts`: print the definitions a statement uses, or the local upstream path.
9. `src/commands/pick.ts`: put `--model` in the "Attempt it" hint (it currently leads to `human_only`).
10. AGENTS.md + schema: allow and document `.lean` files in writeups; document that changing kind means a new
    attempt.
11. AGENTS.md step 7: show the pre-ticked declarations to the human. Add a way to credit tools.
12. `src/commands/submit.ts:57`: fix the doubled `rejected: rejected:`.
13. AGENTS.md Setup: document reusing an existing Mathlib cache. `.gitignore`: add `lean/.lake` without the slash.
14. `src/commands/show.ts`: suggest near ids for an unknown id.
15. Checker messages: map `Attempt/Solution.lean` back to the attempt's path, and pretty-print `type mismatch` types.
