## Done

Judge verdict: **PASS on all seven conditions.** One cosmetic fix; no breakage where tasks meet.

1. `bun install --frozen-lockfile; bun run check` — PASS. Run 1 (no Lean set up): tsc clean, 180 tests (Lean ones skipped), `validate` ok: 1479 problems. Run 2 with Lean set up (`lake exe cache get` in `lean/`, 7.5 GB `.lake`): 178 pass, 1 skip, 1 fail, 604 s. The failure was `(b) sorry is rejected` — "could not build the imported modules", i.e. the first concurrent tests racing to build the shared formal-conjectures modules on a cold cache (167 s). Rerun of `bun test test/check/proof` on the warm cache: **18 pass, 0 fail** (567 s); the one skip is the by-design "(g) verified disproof" skip documented in design.md.
2. Conditions:
   - (1) check passes: PASS (above).
   - (2) problem count: PASS. 1479 files = 1471 proof + 8 witness; 167 tagged `answer-required`. `bun frontier index`: `1479 problems, 0 attempts, 0 verified; open 1479`, `by_tier {proof:1471, witness:8}`.
   - (3) `index` writes `dist/index.json`/`--out`: PASS (`wrote /tmp/idx.json`, counts above).
   - (4) Lean checker: PASS. Good fixture verified, plus rejections for sorry ("uses sorry"), changed statement (type mismatch), extra axiom (pre-check and axiom check), native_decide, run_cmd forgery, skipKernelTC (kernel replay), wrong disproof direction, compiler error, and every pre-check pattern; all in `test/check/proof/proof.test.ts`, 18 pass on the warm cache.
   - (5) witness verifiers: PASS. `bun frontier check` on the 512-point cap set: `verified: Valid witness … value 512; ties the best known`. Collinear 3-point set: `REJECTED: Invalid: points 0, 1, 2 are collinear`. Witness tests (capset, ramsey, golomb, schur, kissing, covering, tier) all in the 180-test run.
   - (6) agent loop: PASS. `pick --tier witness` → `new witness.cap-set-f3-8 --kind witness` → fixture → `check` verified → `submit <dir>` dry run printed plan and PR body (gh cannot read terramind-org/frontier, so the generic-plan NOTE appeared, as designed). Attempt dir deleted. Writeup on `erdos604.erdos-604.variants.average`: `unchecked: Writeups are not machine-checked.` (deleted). `new --kind proof` and `--kind disproof` on `arxiv.0805.3777.ismaxrank-cube` (answer-required): refused, exit 2, nothing created.
   - (7) workflows + forged verdict: PASS. `validate --changed BASE...HEAD` on a temp branch: clean attempt → `ok`, exit 0; attempt + forged `verdict.json` → `verdict.json is written by CI on main, never by a submitter`, exit 1. Temp branch deleted. `test/record` + `test/submit`: 21 pass, 1 skip. actionlint is not installed; all five workflows parse as YAML.
3. Docs vs CLI: every command and flag in README.md, AGENTS.md, CONTRIBUTING.md (`list/show/pick/new/validate [--changed]/check/submit [--yes]/index/import formal-conjectures --path/record`, `pick --tag`, `--model`, `--mode`) exists in `--help` and behaves as described. No doc changes needed.
4. grep for solved/TODO/FIXME/stub/placeholder: all hits justified — "never say solved" rules (AGENTS, CONTRIBUTING, SKILL.md) and a test asserting no "solved"; `solved` as the upstream `category research solved` skipped in import fixtures/tests; `placeholder` for the scaffold claim in AGENTS.md and the documented `lean/Attempt/Solution.lean` slot module; `todo` is a variable name in record.yml; `-- TODO` is upstream comment text in an import fixture. No stubs.

Files touched: `src/commands/submit.ts` (PR body printed `…(2024))..` — doubled full stop after a verdict summary ending in "."; strip one trailing "." before the sentence's own). `bun test test/submit` 9 pass. This handoff file.

## Deviations
Set up Lean locally (`cd lean && lake exe cache get`) to run the Lean tests; `lean/.lake` is gitignored and left in the worktree. Did not run `lake update` (killed it; manifest unchanged).

## Concerns
- Cold-cache flake: on a first run with an unbuilt `lean/.lake`, the concurrent Lean tests all build the same formal-conjectures modules and one failed with "could not build the imported modules". CI is unaffected only if its build step warms the cache first (lean-check.yml's cache step does for attempts, but the `bun test` job for the proof tests should build `FormalConjectures` first or run those tests with a warm cache).
- Full Lean suite took ~9.5 min here (design says ~12).
- No actionlint on this machine; workflows are only YAML-parse and unit-tested, never run on GitHub.

## Follow-ups
- Consider a `lake build` warm-up step (or a beforeAll in `proof.test.ts`) so the Lean tests are not racy on a cold cache.
