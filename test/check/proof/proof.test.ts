import { describe, expect, test } from 'bun:test';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { findLakeDir, LEAN_DIR, RUNNER, runLeanCheck } from '../../../src/check/proof.ts';
import type { VerdictResult } from '../../../src/schema.ts';

const ROOT = join(import.meta.dir, '..', '..', '..');
const FIXTURES = join(ROOT, 'test', 'fixtures', 'proof');
const SOLUTIONS = join(FIXTURES, 'solutions');
const FIXTURE_REPO = join(FIXTURES, 'repo');
const GOOD_ATTEMPT = join(FIXTURE_REPO, 'attempts', 'erdos1.erdos-1.variants.weaker', '20261018-agrim-a00001');
const DECL = 'Erdos1.erdos_1.variants.weaker';
const FC_COMMIT = '197f7f8dcc457f556754f826389d2ec7a0d85b92';

const lakeDir = findLakeDir();
const leanReady = lakeDir !== null && existsSync(join(LEAN_DIR, '.lake', 'packages', 'formal_conjectures'));
if (!leanReady) {
  console.warn(
    lakeDir
      ? 'SKIPPING Lean checker tests: lean/ is not set up (run `lake exe cache get` in lean/).'
      : 'SKIPPING Lean checker tests: `lake` is not installed (CI runs them in lean-check.yml).',
  );
}
const leanTest = leanReady ? test.concurrent : test.skip;
const MIN = 60_000;

// Each Lean run imports Mathlib and hashes the package store; run at most three at once.
let running = 0;
const queue: (() => void)[] = [];
async function limited<T>(fn: () => Promise<T>): Promise<T> {
  if (running >= 3) await new Promise<void>((r) => queue.push(r));
  running++;
  try {
    return await fn();
  } finally {
    running--;
    queue.shift()?.();
  }
}

const run = (file: string, kind: 'proof' | 'disproof' = 'proof') =>
  limited(() => runLeanCheck(join(SOLUTIONS, file), DECL, kind));

async function sh(cwd: string, cmd: string[]): Promise<{ code: number; out: string; err: string }> {
  const env = { ...process.env, PATH: `${lakeDir}:${process.env.PATH ?? ''}` };
  const p = Bun.spawn(cmd, { cwd, env, stdout: 'pipe', stderr: 'pipe' });
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  return { code, out, err };
}

/**
 * Build a source with plain `lake build`, bypassing check-attempt.sh's pre-check (as an attacker building
 * their own .olean would), then judge only the resulting build files with phase 2.
 */
async function phase2OnUncheckedBuild(file: string): Promise<VerdictResult> {
  return limited(async () => {
    const work = mkdtempSync(join(tmpdir(), 'frontier-unchecked-'));
    for (const f of ['lakefile.toml', 'lake-manifest.json', 'lean-toolchain']) cpSync(join(LEAN_DIR, f), join(work, f));
    mkdirSync(join(work, 'Attempt'));
    mkdirSync(join(work, '.lake'));
    symlinkSync(join(LEAN_DIR, '.lake', 'packages'), join(work, '.lake', 'packages'));
    cpSync(join(SOLUTIONS, file), join(work, 'Attempt', 'Solution.lean'));
    const built = await sh(work, ['lake', 'build', 'Attempt']);
    if (built.code !== 0) throw new Error(`unchecked build of ${file} failed:\n${built.out}\n${built.err}`);
    const out = join(work, 'out');
    mkdirSync(join(out, 'build'), { recursive: true });
    writeFileSync(join(out, 'status'), 'ok\n');
    const lib = join(work, '.lake', 'build', 'lib', 'lean', 'Attempt');
    for (const f of readdirSync(lib)) if (/^Solution\.(olean|ilean)/.test(f)) cpSync(join(lib, f), join(out, 'build', f));
    const res = await sh(ROOT, ['bash', RUNNER, '--phase', 'check', out, DECL, 'proof']);
    if (res.code !== 0) throw new Error(`phase 2 failed: ${res.err}`);
    return JSON.parse(res.out.trim().split('\n').at(-1)!) as VerdictResult;
  });
}

function expectRejected(v: VerdictResult, reason: RegExp, target: 'statement' | 'negation' = 'statement') {
  expect(v.checker).toBe('lean');
  expect(v.result).toBe('rejected');
  expect(v.lean?.target).toBe(target);
  expect(v.lean?.fc_commit).toBe(FC_COMMIT);
  expect(v.lean?.reason ?? '').toMatch(reason);
}

describe('proof checker without Lean', () => {
  test('reports error, not a verdict, when lake is missing', async () => {
    const env = { PATH: '/usr/bin:/bin', HOME: mkdtempSync(join(tmpdir(), 'frontier-nohome-')) };
    expect(findLakeDir(env)).toBeNull();
    const v = await runLeanCheck(join(SOLUTIONS, 'good.lean'), DECL, 'proof', { env });
    expect(v).toEqual({ checker: 'lean', result: 'error', summary: 'Lean is not installed here; CI will check this attempt' });
  });
});

describe('proof checker with Lean', () => {
  leanTest(
    '(a) a correct proof is verified, through `bun frontier check`',
    async () => {
      const res = await limited(() => sh(FIXTURE_REPO, [process.execPath, join(ROOT, 'src', 'cli.ts'), 'check', GOOD_ATTEMPT, '--json']));
      expect(res.code).toBe(0);
      const v = JSON.parse(res.out) as VerdictResult;
      expect(v.result).toBe('verified');
      expect(v.summary).toContain('proof checked');
      expect(v.lean).toEqual({
        toolchain: 'leanprover/lean4:v4.33.1',
        fc_commit: FC_COMMIT,
        target: 'statement',
        axioms: ['Classical.choice', 'Quot.sound', 'propext'],
      });
    },
    30 * MIN,
  );

  leanTest('(b) sorry is rejected: "uses sorry"', async () => {
    const v = await run('sorry.lean');
    expectRejected(v, /^uses sorry$/);
    expect(v.lean?.axioms).toContain('sorryAx');
  }, 30 * MIN);

  leanTest('(c) a changed (weakened) statement is rejected as a type mismatch', async () => {
    expectRejected(await run('changed.lean'), /^type mismatch: OpenProblemsAttempt\.solution must have type/);
  }, 30 * MIN);

  leanTest('(d) an extra axiom is rejected by the source pre-check', async () => {
    expectRejected(await run('axiom.lean'), /source uses an axiom declaration \(line \d+\)/);
  }, 30 * MIN);

  leanTest('(d) an extra axiom built past the pre-check is rejected by the axiom check', async () => {
    expectRejected(await phase2OnUncheckedBuild('axiom.lean'), /^uses axiom OpenProblemsAttempt\.cheat$/);
  }, 30 * MIN);

  leanTest('(e) native_decide in a helper lemma is rejected: "uses native_decide"', async () => {
    const v = await run('native-decide.lean');
    expectRejected(v, /^uses native_decide$/);
    // Lean 4.33 records native_decide as a per-use axiom named <decl>._native.native_decide.ax_<n>.
    expect(v.lean?.axioms.some((a) => a.includes('native_decide'))).toBe(true);
  }, 30 * MIN);

  leanTest('(f) run_cmd forging the environment is rejected by the source pre-check', async () => {
    expectRejected(await run('forge.lean'), /source uses .*attempts may not run code while compiling/);
  }, 30 * MIN);

  leanTest('(f) a declaration added without the kernel (skipKernelTC) is rejected by kernel replay', async () => {
    const v = await phase2OnUncheckedBuild('forge.lean');
    expectRejected(v, /^kernel replay failed: .*OpenProblemsAttempt\.solution/s);
  }, 30 * MIN);

  leanTest('(g) disproof direction: proving the statement instead of its negation is rejected', async () => {
    const v = await run('disproof-of-true.lean', 'disproof');
    // Check.lean loads no environment extensions (on purpose), so `¬` prints as `Not`.
    expectRejected(v, /^type mismatch: OpenProblemsAttempt\.solution must have type (¬|Not)\b/, 'negation');
  }, 30 * MIN);

  leanTest('(g) verified disproof of a false upstream statement: skipped', () => {
    console.warn(
      'SKIPPED (g) positive disproof: formal-conjectures at 197f7f8 has no short false statement to refute; ' +
        'the direction is covered by the negation-target rejection test.',
    );
  }, MIN);

  leanTest('a compiler error is rejected with the first errors', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'frontier-broken-'));
    const file = join(dir, 'solution.lean');
    writeFileSync(
      file,
      'import FormalConjectures.ErdosProblems.«1»\n\nnamespace OpenProblemsAttempt\n\ntheorem solution : 1 = 2 := by\n  exact rfl\n\nend OpenProblemsAttempt\n',
    );
    const v = await limited(() => runLeanCheck(file, DECL, 'proof'));
    expectRejected(v, /^does not compile: .*error/s);
    expect((v.lean?.reason ?? '').length).toBeLessThanOrEqual(2001 + 'does not compile: '.length);
  }, 30 * MIN);

  const precheckCases: [string, string, RegExp][] = [
    ['a Lean meta import', 'import Lean\nimport Mathlib.Tactic\n', /imports Lean, which is not on the allow-list/],
    ['#eval', 'import Mathlib.Tactic\n#eval 1\n', /source uses #eval/],
    ['skipKernelTC', 'import Mathlib.Tactic\nset_option debug.skipKernelTC true\n', /source uses set_option debug\.skipKernelTC/],
    ['implemented_by', 'import Mathlib.Tactic\n@[implemented_by id] def f (n : Nat) : Nat := n\n', /source uses @\[implemented_by\]/],
    ['an elaborator attribute', 'import Mathlib.Tactic\n@[tactic Lean.Parser.Tactic.done] def t : Nat := 0\n', /attribute that registers compile-time code/],
    ['an import outside the allow-list', 'import Evil.Module\n', /imports Evil\.Module, which is not on the allow-list/],
  ];
  for (const [name, src, reason] of precheckCases) {
    leanTest(`pre-check rejects ${name}`, async () => {
      const dir = mkdtempSync(join(tmpdir(), 'frontier-precheck-'));
      writeFileSync(join(dir, 'solution.lean'), src);
      expectRejected(await runLeanCheck(join(dir, 'solution.lean'), DECL, 'proof'), reason);
    }, 5 * MIN);
  }
});
