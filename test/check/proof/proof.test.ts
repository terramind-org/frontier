// Lean checker tests. Each one runs Lean (compile, Mathlib import, kernel replay), so they run one at a
// time (`bun run check:lean`, 15 minutes per test) and are left out of the fast `bun run check`.
// The source pre-check alone is tested without Lean in test/check/lean-runner.test.ts.
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
const ATTEMPT_REL = join('attempts', 'erdos1.erdos-1.variants.weaker', '20261018-agrim-a00001');
const GOOD_ATTEMPT = join(FIXTURE_REPO, ATTEMPT_REL);
const DECL = 'Erdos1.erdos_1.variants.weaker';
const FC_COMMIT = '9097e2f90e66d2f6244209cb1c07f7120d17ec53';
const PROGRESS = ['[1/3] building attempt…', '[2/3] kernel replay and statement check…', '[3/3] integrity check…'];

const lakeDir = findLakeDir();
const leanReady = lakeDir !== null && existsSync(join(LEAN_DIR, '.lake', 'packages', 'formal_conjectures'));
if (!leanReady) {
  console.warn(
    lakeDir
      ? 'SKIPPING Lean checker tests: lean/ is not set up (symlink an existing lean/.lake, or run `lake exe cache get` in lean/).'
      : 'SKIPPING Lean checker tests: `lake` is not installed (CI runs them in lean-check.yml).',
  );
}
// Serial on purpose: concurrent Lean runs on a loaded machine starve each other and time out.
const leanTest = leanReady ? test : test.skip;
const MIN = 60_000;
const LEAN_TIMEOUT = 15 * MIN;

const run = (file: string, kind: 'proof' | 'disproof' = 'proof', onProgress?: (line: string) => void) =>
  runLeanCheck(join(SOLUTIONS, file), DECL, kind, { onProgress });

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
    '(a) a correct proof is verified, through `bun frontier check --json` (no progress lines)',
    async () => {
      const res = await sh(FIXTURE_REPO, [process.execPath, join(ROOT, 'src', 'cli.ts'), 'check', GOOD_ATTEMPT, '--json']);
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
      expect(res.err).not.toContain('[1/3]');
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(b) sorry is rejected: "uses sorry", with the three progress lines in order',
    async () => {
      const lines: string[] = [];
      const v = await run('sorry.lean', 'proof', (l) => lines.push(l));
      expectRejected(v, /^uses sorry$/);
      expect(v.lean?.axioms).toContain('sorryAx');
      expect(lines).toEqual(PROGRESS);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(c) a changed (weakened) statement is rejected as a type mismatch showing both types',
    async () => {
      const v = await run('changed.lean');
      expectRejected(v, /^type mismatch: OpenProblemsAttempt\.solution must have type\n {2}\S.*\nbut has type\n {2}\S/);
      // Both types appear, pretty-printed with notation rather than as raw terms (`Exists fun C => …`).
      const reason = v.lean?.reason ?? '';
      expect(reason).toMatch(/must have type\n {2}∃ C/);
      expect(reason).toMatch(/but has type\n {2}∃ C.*≥/);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(d) an extra axiom is rejected by the source pre-check',
    async () => {
      expectRejected(await run('axiom.lean'), /^source uses an axiom declaration: `axiom` on line \d+ \(comments are ignored\)/);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(d) an extra axiom built past the pre-check is rejected by the axiom check',
    async () => {
      expectRejected(await phase2OnUncheckedBuild('axiom.lean'), /^uses axiom OpenProblemsAttempt\.cheat$/);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(e) native_decide in a helper lemma is rejected: "uses native_decide"',
    async () => {
      const v = await run('native-decide.lean');
      expectRejected(v, /^uses native_decide$/);
      // Lean 4.33 records native_decide as a per-use axiom named <decl>._native.native_decide.ax_<n>.
      expect(v.lean?.axioms.some((a) => a.includes('native_decide'))).toBe(true);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(f) run_cmd forging the environment is rejected by the source pre-check',
    async () => {
      expectRejected(await run('forge.lean'), /^source uses (set_option debug\.skipKernelTC|run_cmd): `(skipKernelTC|run_cmd)` on line \d+/);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(f) a declaration added without the kernel (skipKernelTC) is rejected by kernel replay',
    async () => {
      const v = await phase2OnUncheckedBuild('forge.lean');
      expectRejected(v, /^kernel replay failed: .*OpenProblemsAttempt\.solution/s);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(g) disproof direction: proving the statement instead of its negation is rejected',
    async () => {
      const v = await run('disproof-of-true.lean', 'disproof');
      expectRejected(v, /^type mismatch: OpenProblemsAttempt\.solution must have type\s+(¬|Not)/, 'negation');
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    '(g) verified disproof of a false upstream statement: skipped',
    () => {
      console.warn(
        'SKIPPED (g) positive disproof: formal-conjectures at 197f7f8 has no short false statement to refute; ' +
          'the direction is covered by the negation-target rejection test.',
      );
    },
    MIN,
  );

  leanTest(
    '(h) local notation, and comments that mention banned words, are verified',
    async () => {
      const v = await run('notation.lean');
      expect(v.result).toBe('verified');
      expect(v.lean?.axioms).toEqual(['Classical.choice', 'Quot.sound', 'propext']);
    },
    LEAN_TIMEOUT,
  );

  leanTest(
    'a compiler error is rejected through `bun frontier check`, citing the attempt’s own path, with progress on stderr',
    async () => {
      const repo = mkdtempSync(join(tmpdir(), 'frontier-broken-'));
      cpSync(FIXTURE_REPO, repo, { recursive: true });
      writeFileSync(
        join(repo, ATTEMPT_REL, 'solution.lean'),
        'import FormalConjectures.ErdosProblems.«1»\n\nnamespace OpenProblemsAttempt\n\ntheorem solution : 1 = 2 := by\n  exact rfl\n\nend OpenProblemsAttempt\n',
      );
      const res = await sh(repo, [process.execPath, join(ROOT, 'src', 'cli.ts'), 'check', ATTEMPT_REL]);
      expect(res.code).toBe(0);
      expect(res.out).toMatch(/^REJECTED: does not compile: .*error/s);
      expect(res.out).toContain(`${join(ATTEMPT_REL, 'solution.lean')}:6:`);
      expect(res.out).not.toContain('Attempt/Solution.lean');
      expect(res.err).toContain('[1/3] building attempt…');
      expect(res.err).toContain('[3/3] integrity check…');
      expect(res.err).not.toContain('[2/3]'); // nothing to replay when the build failed
    },
    LEAN_TIMEOUT,
  );
});
