## Done

Data repo (branch `swarm/frontier-2--judge-cycle-2-jwvzt`, from `swarm/frontier-2` e2f6d1e):

- **`bun install --frozen-lockfile`**: PASS (9 packages).
- **`bun run check`**: **FAIL** — `tsc --noEmit` passed, `bun test` ran 223 tests: 214 pass, **8 fail**, 1816 s; `validate` never ran because `&&` stopped. All 8 failures are in `test/check/proof/proof.test.ts` ("proof checker with Lean", (a)(b)(c)(d)(e)(f)(g) and "a compiler error is rejected"). (a)(b)(c) returned `result: "error"` at ~1563 s; (d)–(g) and the compiler-error test hit the 1,800,000 ms test timeout. The machine was at load average 15–31 (parallel swarm workers running `lake`/`rustc`) and each check sha256-hashes 7.8 GB. Lean was available through the symlinked `lean/.lake` (not committed).
  - Isolated rerun of `bun test test/check/proof/proof.test.ts -t "sorry is rejected"`: **PASS** (1 pass, 730 s, load ~15). So (b) is not broken by the merge; the failures are consistent with load and queue time, but I did not rerun the other seven individually (each ~12 min), so that attribution is unconfirmed for them.
  - Pieces run separately: `tsc --noEmit` PASS; `bun src/cli.ts validate` PASS (`ok: 1485 problems, 0 attempts`); `bun test --path-ignore-patterns 'test/check/proof/*'` PASS (204 pass, 1 skip, 0 fail, 205 tests, 20 files).
- **`bun frontier index`**: 1,485 problems, 0 attempts. By tier: proof 1,471, witness 14. By field: mathematics 1,479 (1,471 proof + 8 witness), computer-science 6 (all witness). By status: open 1,485; proof-checked 0, disproof-checked 0, record-improved 0. Commit `e2f6d1e`.
- **CS witness check via the CLI** (`new witness.sorting-network-size-13`, Batcher network from `test/check/witness/cs-constructions.ts`, scratch attempt deleted afterwards): valid → `verified: Valid witness … with value 48; does not reach the best known 45`; same network with 3 comparators dropped → `REJECTED: Invalid: the network does not sort the 0-1 input 1111100000000 …`.
- **Site** (`~/.terramind/worktrees/terramind-org-frontier`, `feat/frontier`): `bun run sync:frontier <this repo>/dist/index.json` → 1,485 problems, frontier e2f6d1e; `bun run ts:check` PASS; `bun run build` PASS, **1,510 static pages**, no warnings (0 matches for "warn"). Rendered `/frontier/` HTML shows 1,485 open problems, 1,471 with a Lean statement, 14 record problems, commit e2f6d1e; the CS problem page for `witness.matmul-rank-5x5x5` is present. Commits on `feat/frontier`: `f476034` (snapshot; its message also says it names computer science on the home row, but that edit only landed in the next commit, because my first `sed` failed) and `b082a14` (home row label). Not pushed.
- **Cycle 3 fix list**: `.terramind/swarm/frontier-2/reports/cycle3-fixes.md` — 25 items, de-duplicated across the Codex trial, the Claude trial and the fact-check, ranked, each with evidence, files, change, and data/site.

Files touched — data repo: `.terramind/swarm/frontier-2/reports/cycle3-fixes.md`, `.terramind/swarm/frontier-2/handoffs/judge-cycle-2-jwvzt.md` (plus an uncommitted symlink `lean/.lake`, which shows as untracked). Site repo: `data/frontier/index.json`, `app/(site)/page.tsx`.

## Deviations

- Fixed one thing where tasks meet, in the site repo: the home row label "3 · Mathematics" → "3 · Mathematics and computer science" (fact-check row #4 predicted it would go false once the CS problems landed).
- Did not apply any trial or fact-check fixes, as instructed.
- Did not run the 390px browser pass; I checked rendered HTML from the build instead.

## Concerns

- **The merged data repo does not pass `bun run check` as run here**; the Lean tests are the issue. Only (b) was shown to pass in isolation. The lead should rerun the proof tests on an idle machine (or one at a time) before calling the gate green. This also confirms trial-lean's fix #4 (checks are too slow: 12 min for one test) and the missing test-concurrency guard.
- The site snapshot names commit `e2f6d1e`, which has no remote; the "commit" links on the pages are dead until the repo exists (fact-check #6, #17).
- Orphaned `check-attempt.sh` / `lake build Attempt` processes from the aborted full run may still be running; they belong to this worktree and are harmless but slow the machine.

## Follow-ups

Everything in `cycle3-fixes.md`. Top five: scaffold rejects itself (`new.ts` comment contains "axiom"), 10 statements truncated at `letI`, scaffolds lack `open`/notation context, `check` speed and silence, witness-search playbook and wait-for-your-own-jobs rule in AGENTS.md. Site: the "checked by the Lean proof checker" headline counts answer-required problems, the lede ignores writeups, and the we-solve credit wording.
