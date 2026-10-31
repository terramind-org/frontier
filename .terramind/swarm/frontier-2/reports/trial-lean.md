# Trial: a Claude agent on Lean problems, AGENTS.md only

Agent: claude-opus-5-5 (Claude Code in Nucleus), `--login trial-claude`. Date: 2026-10-19; attempts 08:27–09:19 (52 min), after-the-fact investigation 09:20–09:25.
Context used before the attempts finished: AGENTS.md, README.md, CONTRIBUTING.md, `bun frontier` output, and
the upstream FormalConjectures sources under `lean/.lake/packages/formal_conjectures/` (see "Context" below).
No `src/`, `lean/Check.lean`, tests or swarm docs were read until both attempts had reached `submit` (dry run).

No check returned `verified`. Nothing was pushed, and `submit --yes` was never run.

## Outcome in one paragraph

The pipeline works end to end. A capable agent can scaffold, iterate, get a clear Lean error back, and produce an
honest PR body. But four things would stop or mislead a zero-context agent:

1. Every proof scaffold is rejected as generated, because the scaffold's own comment contains the word `axiom`.
2. The catalogue contains no tractable problems. All 274 imported variants are upstream `research open`, so
   "realistic progress is in variants" is false, and the human's warm-up (`erdos1…weaker`, a textbook result)
   doesn't exist.
3. `check` is very slow: 1–10 minutes per run, with no progress output. Most of that time is sha256 over 7.8 GB,
   not Lean.
4. `show`/`new` print a broken statement for 10 problems (truncated at `letI`), and scaffolds can't parse statements
   that use upstream `local notation`.

Neither attempt proved its problem; both are partial writeups with Lean lemmas attached.

## Timeline

| Time | Command / action | Result | `check` duration |
|---|---|---|---|
| 08:27 | read README, CONTRIBUTING, AGENTS; `bun install` | 9 packages, 85 ms | |
| 08:27 | `ln -s …/silent-crossing/lean/.lake lean/.lake` | ok; shows as **untracked** in `git status` (`.lake/` pattern does not match a symlink) | |
| 08:27 | `bun frontier show erdos1.erdos-1.variants.weaker` | `No problem "erdos1.erdos-1.variants.weaker". Try \`bun frontier list\`.` | |
| 08:28 | `list --tier proof --tag variant` | 274 variants, all `open`, 0 attempts | |
| 08:28–08:30 | `show --json` on all 274 (loop, 90 s) | every `upstream_status` is `open` | |
| 08:30–08:32 | read upstream `.lean` files for definitions (`show` doesn't print them) | upstream has `erdos_1.variants.weaker` as `@[category textbook]`; it wasn't imported | |
| 08:32 | `new erdos727.erdos-727.variants.k-2 --kind proof` | scaffold is `theorem solution : letI k := by sorry`: **truncated statement** | |
| 08:32 | `check` on the untouched scaffold | `REJECTED: rejected: source uses an axiom declaration (line 6); attempts may not run code while compiling` (line 6 is the scaffold's own comment) | 1 s |
| 08:32 | full statement + `sorry`, `check` | `REJECTED: rejected: uses sorry` | **9 min 38 s** (cold: built the FC module), no output while running |
| 08:42 | same, `check --json` | `rejected`, axioms `[propext, sorryAx]` | 3 min 15 s |
| 08:43–08:47 | computations for misformalisation/counterexample hunting (Erdős 49 to 2·10⁵, Erdős 340 greedy Sidon to 1.5·10⁶, Erdős 727 to 2·10⁶) | nothing | |
| 08:47 | `cd lean && lake env lean A40.lean` | `object file … OEIS/103662.olean … does not exist` | |
| 08:48 | `lake build 'FormalConjectures.OEIS.«103662»'` then `lake env lean` | built in 24 s; partial a-40 lemma **compiled first try** in 30 s | |
| 08:49 | `new oeisa103662.conjecture.variants.a-40 --kind writeup`; `check`; `validate` | `unchecked`; `ok`, **with the placeholder claim still in place** | 0.25 s |
| 08:49 | add `partial.lean` to `files:` | `validate` ok (extra files allowed in a writeup) | |
| 08:50 | `submit` (dry run), a-40 | `NOTE: could not read terramind-org/frontier: gh: Not Found (HTTP 404)`; generic plan + PR body | 1.4 s |
| 08:50 | `pick --tier proof` | `erdos604.erdos-604.variants.average` (sum of pinned distinct distances ≫ n²/√log n), a major open problem | |
| 08:51–08:52 | read Erdős 967 (finite case), searched 727 families | 727 chosen as the main attempt | |
| 08:52 | `lake env lean` E727 lemmas | `omega could not prove the goal` (missing `n ≠ 0`); fixed, compiled in 37 s | |
| 08:54 | lemmas + `sorry` in solution.lean, `check` | `REJECTED: rejected: uses sorry` | 4 min 43 s |
| 08:59 | deliberate `rw` error, `check --json` | full Lean error with goal state | 1 min 12 s |
| 09:00 | same, plain `check` | same error, multi-line | 1 min 50 s |
| 09:02–09:04 | proved a **changed** statement (k = 0), `check` | `REJECTED: rejected: type mismatch: … must have type … but has type …` | 2 min 00 s |
| 09:06 | `submit` (dry run) on the rejected proof with the placeholder claim | plan + PR body containing `Describe exactly what this attempt claims.`; verdict line `rejected: rejected: uses sorry` | **8 min 20 s** (re-runs check) |
| 09:15 | strengthened lemma compiled (45 s); `#print axioms` → `[propext, Classical.choice, Quot.sound]` | | |
| 09:16 | `new erdos727… --kind writeup` (second attempt dir; kind can't be changed) | | |
| 09:19 | `check`, `submit` (dry run), 727 writeup | `unchecked`; plan + PR body | 1.5 s |
| 09:20–09:25 | after-the-fact reading of `src/`, `lean/check-attempt.sh`; Kurepa scaffold probe (build + compile 3 min 44 s) | root causes below | |

`check` wall times for Lean attempts: 1 s (precheck reject), 9:38, 3:15, 4:43, 1:12, 1:50, 2:00, plus 8:20 inside
`submit`. Direct `lake env lean` on the same files: 30–60 s (1:41 once under load).

## What the attempts achieved

**Warm-up: `oeisa103662.conjecture.variants.a-40`** (no `b > 1` with `b^40` zeroless). Chosen because it was the
only short statement where an elementary argument gets real traction. Proved in Lean: every `b > 1` that is odd or
divisible by 5 has a 0 among the last four digits of `b^40`, via `b^40 ≡ 1 (mod 100)` or `≡ 625 (mod 10^4)`, or
`10 ∣ b`. The case `b` even with `5 ∤ b` is untouched: residues alone can't force a zero there (the last 3 digits are
one of 176, 376, 576, 776, 976). Searching every such `b ≤ 200000` found no zeroless `b^40`. Filed as a `writeup`
with `partial.lean`. Files: `trial-lean/a40-writeup/`.

**Main: `erdos727.erdos-727.variants.k-2`** (infinitely many `n` with `((n+2)!)^2 ∣ (2n)!`). `pick` gave Erdős 604
(average pinned distances), which nobody gets anywhere on in 60 minutes, so I took 727 under the "or a variant you
judge tractable" clause. Proved in Lean:

- `((n+2)!)^2 ∣ (2n)! ↔ ((n+1)(n+2))^2 ∣ C(2n,n)`;
- `2·v_p((n+1)(n+2)) ≤ log_p(2n)`, hence every prime factor `p` of `(n+1)(n+2)` has `p² ≤ 2n`.

Computed all 23,760 solutions up to 2·10⁶ (smallest 208). Their proportion rises from 0.55% to 1.19%. Six power
families give one hit, 4093. Infinitude is not proved: it needs `n+1` and `n+2` simultaneously smooth with the right
base-`p` carries for every prime factor, and I found no family. I spent about 30 of the allowed 60 minutes on
this attempt (08:50–09:19). I stopped once the only routes left were analytic-number-theory density arguments,
which can't be formalised in the remaining time. Files: `trial-lean/727-proof/` (the rejected proof
attempt) and `trial-lean/727-writeup/` (what I'd submit).

**Tamper probe:** a complete proof of the same theorem with `k := 0` was rejected (`type mismatch`). Good.

## Every stumble, quoted

### Blocking or misleading

1. **The scaffold rejects itself.** `new` writes this comment:
   `` `sorry`, `native_decide` and new `axiom`s are rejected. ``
   The untouched scaffold then gets:
   `REJECTED: rejected: source uses an axiom declaration (line 6); attempts may not run code while compiling`.
   Line 6 is that comment. The precheck in `lean/check-attempt.sh` greps raw text, comments included (by design,
   per its header), with `B="(^|[^A-Za-z0-9_'.])"` / `A="([^A-Za-z0-9_'!?]|$)"`; a backtick satisfies both
   boundaries. The same rule rejects any comment that uses the words `meta`, `macro`, `syntax`, `elab`, `unsafe`
   or `initialize` ("meta-argument", "the syntax of …"). The reason text ("attempts may not run code while
   compiling") points the agent at the wrong thing. An agent that runs `check` right after `new`, as The loop
   says, gets a false rejection on its very first check.
2. **Truncated statements.** `show erdos727.erdos-727.variants.k-2` prints
   `theorem erdos_727.variants.k_2 :\n    letI k`, and `new` scaffolds `theorem solution : letI k := by sorry`,
   which can't compile. Cause: `statementEnd` in `src/import/lean-parse.ts` skips the `:=` of `let`/`have` binders
   but not `letI`/`haveI` (`/^(let|have)(?![\w'.!?])/` fails on `letI`). **10 of 1,471** statements are
   affected (the full list and method are in "Evidence for the lead's items" below). The checker itself is fine: it compares elaborated types, so a hand-fixed
   statement passed the statement check. But `show`, `new`, `dist/index.json` and the new /frontier/ problem pages
   all carry the broken text.
3. **Scaffolds lack the upstream `open`/notation context.** `new kurepa.kurepa-conjecture.variants.gcd` scaffolds
   `theorem solution (n : ℕ) : 2 < n → (n !).gcd (! n) = 2 := by`, which fails with
   `error: unexpected token ')'; expected term`. `! n` is a `local notation` in the upstream file, and `n !` needs
   `open Nat`. Statements using `#A`, `ℝ²`, `π`, `σ`, `φ` or `Ω` probably need `open scoped …` lines that the
   scaffold doesn't emit. I didn't measure how many of the 1,471 fail to elaborate as scaffolded. AGENTS.md then says
   "the `theorem solution …` line … must stay as scaffolded", so an agent has no legal move, even though the
   checker would accept any spelling with the same elaborated type.
4. **No tractable problems exist in the catalogue.** All 274 variants have `upstream_status: open` (checked via
   `show --json` on each), so the importer brought in `research open` only. Upstream has 219 `textbook` and 2,443
   `research solved` declarations, none imported. AGENTS.md's "Realistic progress is in variants and special
   cases … where the statement is weaker or finite" reads as if variants are easier. They are open research
   problems, just narrower ones. The human's warm-up premise ("it's a textbook result, so it may not be imported")
   was right; their fallback ("pick any variant you judge most tractable") had nothing tractable to land on.
5. **`check` is slow and silent.** 9 min 38 s cold, 1–5 min warm, with no output until the verdict. The time goes
   to the tamper-resistance step in `lean/check-attempt.sh`: it sha256-hashes "all of lean/.lake/packages" (7.8 GB,
   146,537 files) three times per check. On macOS that uses `shasum -a 256`, which is Perl. The first run also
   builds the imported FormalConjectures module, silently. `submit` re-runs the whole check, which took 8 min 20 s
   for a dry run. Meanwhile `lake env lean file.lean` gives the same Lean errors in 30–60 s, but AGENTS.md doesn't
   mention it. Without that discovery, the 60-minute budget would have allowed about 12 iterations.

### Unclear or wrong

6. **The placeholder claim passes everything.** `claim: Describe exactly what this attempt claims.` passes
   `validate`, `check` and `submit`, and lands verbatim in the PR body under "### Claim". AGENTS.md says it "must
   be replaced", but nothing enforces it.
7. **`show` omits definitions.** You can't judge tractability from `∀ᶠ n in atTop, 2 ≤ h n` without knowing `h`.
   I read `lean/.lake/packages/formal_conjectures/FormalConjectures/<…>.lean` instead (the path follows from
   `show`'s `source:` URL). AGENTS.md doesn't say this is expected or allowed.
8. **`pick` suggests the wrong `new` command.** Its "Attempt it:" line is
   `bun frontier new <id> --kind proof --login <your-github-login>`, with no `--model`. An agent that copies it
   records an AI attempt as `mode: human_only`, which is a disclosure error. AGENTS.md says to pass `--model`, but
   the CLI's own hint contradicts it.
9. **A writeup with Lean is undocumented.** AGENTS.md says a writeup is `writeup.md`. `validate` accepted
   `partial.lean` listed in `files:`, but nothing compiles it. Partial Lean results are the most useful output of a
   failed proof attempt; the rules should say where they go and whether CI compiles them.
10. **The kind can't be changed.** After the proof attempt failed, the rule "a partial result … is a writeup"
    forced a second `new` with a new attempt id. Not documented.
11. **Declarations are pre-ticked.** `new` writes `declarations: rights: true, disclosure_complete: true`, and the
    PR body shows `[x] I have the right to submit this work`. The agent declares rights on the human's behalf
    without being asked. AGENTS.md step 7 should tell the agent to point these out at the dry run.
12. **There's no way to list tools.** "List every model, tool and person in `models` and `people`", but `--model`
    takes only `name:provider:role`. I used bun scripts and Lean/Mathlib and had nowhere to record them, so I
    recorded neither.
13. **The verdict prefix is doubled in `submit`.** `rejected: rejected: uses sorry` (`src/commands/submit.ts:57`
    prefixes a summary that already starts with `rejected:`).
14. **The repo 404s.** `NOTE: could not read terramind-org/frontier: gh: Not Found (HTTP 404)`. Expected, since the
    repo doesn't exist yet. The note handles it well.
15. **Lean errors cite a different path.** `Attempt/Solution.lean:14:14` is the checker's copy; the line numbers
    match the agent's `solution.lean`, but the path doesn't. Minor.
16. **The local Mathlib setup is undocumented**, as intended for this trial. The symlink to the existing cache, and
    "never run `lake exe cache get`", are what made Lean usable on a tight disk. AGENTS.md's install line ("Mathlib
    is large, so check free disk before building") doesn't tell an agent that `lean/.lake` can point at an
    existing cache. `check-attempt.sh`'s own error text says `run 'lake exe cache get'`, which would download about
    8 GB. A symlinked `lean/.lake` also shows as untracked in git.
17. **A missing id gets no suggestions.** `No problem "erdos1.erdos-1.variants.weaker". Try \`bun frontier list\`.`
    Fine, but it could suggest near ids or say "imported problems are upstream research-open only".

### What worked well

- **Lean error messages through `check` are good:** full message, line:col, and goal state with hypotheses. Example:
  `` rejected: does not compile: error: Attempt/Solution.lean:14:14: Tactic `rewrite` failed: Did not find an occurrence of the pattern Nat.factorial 0 in the target expression … ⊢ … ``.
  A `sorry` warning is shown alongside. `--json` adds the axiom list (`[propext, sorryAx]`), which helps.
- **The statement-mismatch message is clear in intent but noisy:** `type mismatch: OpenProblemsAttempt.solution must
  have type (Set.ofPred fun n => Nat.instDvd.dvd (instHPow.hPow …` prints raw instances. A pretty-printed form
  would read better.
- **`submit` dry run:** the warning on a rejected attempt is exactly right ("It can still be submitted …
  Do not describe it as a proof."), and the plan is explicit.
- **`answer-required`** matches the statements that use `.answer` (26 variants). The text in AGENTS.md and README is
  clear, and `pick` skipping them makes sense. I didn't hit it in practice.
- **The variant guidance ("prove those as `proof`")** is clear. The problem is only that the variants are open.

## Context I needed beyond AGENTS.md

Upstream definitions (stumble 7), `lake env lean` for fast iteration (5), `lake build <module>` before
`lake env lean` (otherwise `object file … does not exist`), and `#print axioms` to self-check. I'd call reading the
upstream source legitimate problem data. I didn't read Frontier's `src/` or `lean/` until afterwards.

## Evidence for the lead's items

**(a) Statements cut at the `:=` inside a `letI` binder.** For every `problems/*.yaml` with a `lean.statement`, I
flagged values ending mid-binder (`letI|haveI|let|have|let_fun <name>`, optionally `: <type>`) or with unbalanced
brackets, then compared each with the upstream source to confirm the stored text is a strict prefix
(`scripts/truncation.ts`, output in `outputs/truncated-statements.txt`). Of 1,471 statements, **10** end mid-binder,
all at `letI`, and all 10 are confirmed truncated against upstream. None has unbalanced brackets.

| Problem | Stored statement ends with | Upstream continues with |
|---|---|---|
| `brocard.brocard-conjecture` | `letI prev` | `:= n.nth Nat.Prime; letI next := …` |
| `erdos1002.erdos-1002` | `letI f` | `:= fun (α : ℝ) (n : ℕ) ↦ (1 / log n) * ∑ …` |
| `erdos1139.erdos-1139` | `letI u` | `:= Nat.nth (fun n ↦ 0 < n ∧ Ω n ≤ 2) …` |
| `erdos137.erdos-137.variants.multiple-powerful-factors` | `letI N` | `:= ∏ x ∈ Finset.Ioc m (m + n), x …` |
| `erdos317.erdos-317` | `letI lhs : ℝ` | `:= \|∑ k, (δ k) / (k + 1)\| …` |
| `erdos317.erdos-317.variants.claim2` | `letI lhs` | `:= \|∑ k, ((δ k : ℚ) / (k + 1))\| …` |
| `erdos477.erdos-477.variants.x-pow-three` | `letI f` | `:= X ^ 3 ∀ A : Set ℤ, …` |
| `erdos488.erdos-488` | `letI B` | `:= …` (after an inline comment) |
| `erdos727.erdos-727.variants.k-2` | `letI k` | `:= 2 Set.Infinite {n : ℕ \| …}` |
| `erdos835.erdos-835.variants.johnson` | `letI k` | `:= l + 3 J(2 * k, k).chromaticNumber = k + 1` |

Stored YAML for 727: `statement: |-\n    theorem erdos_727.variants.k_2 :\n        letI k`. The resulting scaffold is
`probes/727-scaffold-as-generated.lean` (`theorem solution : letI k := by`). My first count in this report said 9;
the regex missed `erdos317.erdos-317` because of its `: ℝ` ascription.

**(b) `show` omits upstream definitions.** `bun frontier show erdos770.erdos-770.variants.three` prints only
`theorem erdos_770.variants.three : {n | h n = 3}.Infinite`. The meaning of `h` lives in
`FormalConjectures/ErdosProblems/770.lean`:
`noncomputable def h (n : ℕ) : ℕ∞ := sInf {m | 2 < m ∧ ((Finset.Icc 2 m.toNat).image fun i => (i ^ n - 1)).gcd id = 1}`.
The same holds for `gamma` (Green 24), `v_l` (Erdős 889), `f` (Erdős 49), `IsValidZerolessPower` (A103662), and
Kurepa's `local notation "!" n => left_factorial n`. `show --json` has no field for them either (keys: `schema`,
`id`, `title`, `field`, `tier`, `statement`, `ams`, `tags`, `references`, `source`, `upstream_status`, `lean`,
`added`).

**(c) A `--kind proof` warm-up was impossible.** `bun frontier list --tier proof --tag variant` lists 274 variants,
and `show --json` on each gives `upstream_status: open` for all 274 (`outputs/variants-upstream-status.tsv`,
`cut -f2 | sort | uniq -c` → `274 open`). Upstream has the intended warm-up as
`@[category textbook, AMS 5 11] theorem erdos_1.variants.weaker` (`ErdosProblems/1.lean:60–61`), but
`show erdos1.erdos-1.variants.weaker` answers `No problem "erdos1.erdos-1.variants.weaker". Try \`bun frontier list\`.`
Attribute counts in the pinned upstream: `research open` 1,472, `research solved` 2,443, `textbook` 219, `test`
2,042. Only the open ones were imported. So both of my attempts on open variants ended as partial writeups.

**(d) The scaffold pre-ticks the declarations.** Every `new` writes this to `attempt.yaml` before the human has
seen anything:

```yaml
declarations:
  rights: true
  disclosure_complete: true
```

The `submit` dry run then renders it as
`- [x] I have the right to submit this work, and I submit it under CC BY 4.0.` and
`- [x] The models, tools and people listed above are the complete disclosure of how this was produced.`
(`outputs/submit-dryrun-a40.txt`, lines 38–39). Nothing in `new`, `validate` or `submit` asks for either.

**(e) Validation accepted an extra `partial.lean`.** The final a-40 writeup has
`files:\n  - writeup.md\n  - partial.lean`. `bun frontier validate` prints
`ok: attempts/oeisa103662.conjecture.variants.a-40/20261019-trial-claude-f88872`, and `check` prints
`unchecked: Writeups are not machine-checked.` (`outputs/validate-a40-with-partial-lean.txt`). So the `.lean` file
is accepted but nobody compiles it. AGENTS.md step 4 lists only `writeup.md` for a writeup.

## Repo check (`bun run check`)

Run once at the end on this branch (no code changes; only `.terramind/` files added): `tsc --noEmit` passed; then
`bun test` reported **169 pass, 10 fail**, so `validate` never ran. All 10 failures are in
`test/check/proof/proof.test.ts` under "proof checker with Lean", and every one is
`this test timed out after 1800000ms` (each logged at 1,800,379 ms). The tests are `test.concurrent` behind a
concurrency limiter, so a queued test's 30-minute clock runs while it waits. Meanwhile each check sha256-hashes 7.8 GB
three times, on a machine at load average 16–22 with 19 other `lake`/`rustc` processes from parallel workers. In
isolation, "(d) an extra axiom is rejected by the source pre-check" passes in 0.5 s
(`outputs/isolated-test-d.txt`). Status of "(b) sorry is rejected": **rerun pending; previous failure attributed
to queue time, unconfirmed.** One isolated run of (b) did finish at load average ~24, and it **failed** after
1,537.97 s (`(fail) … (b) sorry is rejected: "uses sorry" [1537712.75ms]`, `0 pass, 1 fail`,
`outputs/isolated-test-b.txt`). That is under the 30-minute test timeout, so queue time doesn't explain that run.
I did not read why it failed. The judge's rerun decides. The full gate did not pass here, and the full output is in
`outputs/bun-run-check.txt`.

## Ranked fixes

1. **`src/commands/new.ts`**: reword the scaffold comment so it can't match the precheck (for example
   "`sorry`, `native_decide` and new axioms are rejected", with no backticks around `axiom`). Add a test that the
   scaffold for a fixture problem passes `precheck`. **`lean/check-attempt.sh` `precheck`**: say what matched,
   e.g. `the word "axiom" appears on line 6 (comments are scanned too)`, rather than "attempts may not run code".
   Better: strip `--` and nested `/- -/` comments in the TS caller before the scan, so prose words in comments stop
   rejecting attempts.
2. **`src/import/lean-parse.ts` `statementEnd`**: treat `letI`, `haveI` (and `let_fun`) like `let`/`have`, add the
   727 case to the parser tests, and re-import. The 10 affected problems are listed below; the site pages render
   this text too.
3. **`src/commands/new.ts`** (with the importer storing the context): emit the upstream file's `open …`,
   `open scoped …` and `namespace` context (or the elaborated statement via `#check`-style pretty printing) so
   every scaffold elaborates. Add a one-off CI job that compiles every scaffold with `sorry` and lists the
   failures. **AGENTS.md**: replace "the `theorem solution …` line must stay as scaffolded" with "the statement
   must elaborate to the same type as the problem's; you may add `open` lines; the checker compares types".
4. **`lean/check-attempt.sh`**: make local checks fast. Hash once before phase 1 and once after phase 2 rather than
   three times, use `sha256sum`/`b3sum` when available, or in local mode compare a size+mtime manifest (CI's
   verdict is authoritative anyway). Print progress ("building FormalConjectures.ErdosProblems.«727» (first time,
   a few minutes)…", "replaying constants…").
   **`src/commands/submit.ts`**: reuse a check result recorded within the last N minutes for the same file hash
   rather than re-running.
5. **AGENTS.md "Work" step**: document the fast loop:
   `cd lean && lake build '<module from show>' && lake env lean ../attempts/<…>/solution.lean`, then `#print axioms`,
   then `bun frontier check` once at the end. Say `check` takes minutes.
6. **Importer, or AGENTS.md "Picking well"**: either import upstream `textbook`/`research solved` variants as a
   practice tier (marked, so they can't produce `proof-checked` headlines), or rewrite the paragraph to say plainly
   that every imported problem, variants included, is an open research problem, and that partial results go in
   writeups.
7. **`src/commands/validate.ts` / `src/schema.ts`**: reject a `claim` equal to the scaffold placeholder, and maybe a
   default title too. `submit` should refuse it.
8. **`src/commands/show.ts`**: print the definitions the statement uses (store them at import), or at least the
   local path of the upstream file. **AGENTS.md**: say that reading it is expected.
9. **`src/commands/pick.ts`**: put `--model "<model>:<provider>:<role>"` in the "Attempt it" hint.
10. **AGENTS.md + `src/schema.ts`**: say whether a writeup may carry `.lean` files (it should), and ideally have
    `check` compile them without judging them. Document that changing kind means a new attempt.
11. **AGENTS.md step 7**: tell the agent to show the pre-ticked declarations to the human. Add a `tools:` field
    (or `--tool name:role`) so bun scripts, SAT solvers and Lean can be credited.
12. **`src/commands/submit.ts:57`**: drop the doubled `rejected:` prefix.
13. **AGENTS.md "Setup"**: document reusing an existing Mathlib cache (`ln -s <cache>/lean/.lake lean/.lake`), and
    warn that the checker's `lake exe cache get` hint downloads about 8 GB. **`.gitignore`**: add `lean/.lake`
    without the trailing slash so a symlink is ignored.
14. **`src/commands/show.ts`**: on an unknown id, suggest close ids and mention that only upstream-open problems
    are imported.
15. **Checker messages**: map `Attempt/Solution.lean` back to the attempt's path, and pretty-print types in the
    `type mismatch` reason.

## Files

`.terramind/swarm/frontier-2/reports/trial-lean/`:

- `a40-writeup/`, `727-writeup/`: the two attempts as they'd be submitted (attempt.yaml, writeup.md, partial.lean).
- `727-proof/`: the rejected proof attempt (lemmas + `sorry`, placeholder claim left as it was).
- `probes/`: the generated 727 scaffold, the changed-statement proof (k = 0), and the uncompilable Kurepa scaffold.
- `outputs/`: every `check`, `validate` and `submit` output quoted above, plus `variants-upstream-status.tsv` (id,
  upstream status, tags and the first 200 characters of the statement for all 274 variants).
- `scripts/`: the bun scripts behind every number in this report.

The attempt directories were deleted after copying; nothing under `attempts/` is committed.
