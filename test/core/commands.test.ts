import { describe, expect, test } from 'bun:test';
import { mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { main } from '../../src/cli.ts';
import { check as leanCheck } from '../../src/check/proof.ts';
import { checkAttempt } from '../../src/commands/check.ts';
import { buildIndex } from '../../src/commands/index.ts';
import { leanTemplate, scaffoldAttempt, solutionDeclaration } from '../../src/commands/new.ts';
import { pickProblem } from '../../src/commands/pick.ts';
import { changedIssues, validateRepo } from '../../src/commands/validate.ts';
import { loadAll, loadProblem } from '../../src/repo.ts';
import { Attempt, Index } from '../../src/schema.ts';
import { BAD, GOOD, confirmDeclarations, copyFixture, fillClaim, ready, sh } from './helpers.ts';

const lines = (issues: { path: string; message: string }[]) => issues.map((i) => `${i.path}: ${i.message}`);

/** Run the CLI in `cwd`, capturing console output. */
async function cli(cwd: string, ...argv: string[]): Promise<{ code: number; out: string }> {
  const out: string[] = [];
  const [log, err, prev] = [console.log, console.error, process.cwd()];
  console.log = (...a) => void out.push(a.join(' '));
  console.error = (...a) => void out.push(a.join(' '));
  process.chdir(cwd);
  try {
    return { code: await main(argv), out: out.join('\n') };
  } finally {
    process.chdir(prev);
    console.log = log;
    console.error = err;
  }
}

describe('validate', () => {
  test('the good fixture is valid', async () => {
    const r = await validateRepo(GOOD);
    expect(lines(r.issues)).toEqual([]);
    expect([r.problems, r.attempts]).toEqual([6, 5]);
  });
  test('an empty repo is valid', async () => {
    const root = copyFixture('good');
    rmSync(join(root, 'problems'), { recursive: true });
    rmSync(join(root, 'attempts'), { recursive: true });
    mkdirSync(join(root, 'problems')); // an empty problems/ is still what marks a clone
    expect((await validateRepo(root)).issues).toEqual([]);
    expect((await cli(root, 'validate')).code).toBe(0);
  });
  test('the bad fixture reports each broken rule at the right path', async () => {
    const out = lines((await validateRepo(BAD)).issues).join('\n');
    const a = 'attempts/toy.add-comm/20260110-bad-';
    expect(out).toContain(`${a}000001/attempt.yaml: id "20260110-bad-0000ff" must equal the directory name`);
    expect(out).toContain(`${a}000002/attempt.yaml: kind "witness" is not allowed on a "proof" problem`);
    expect(out).toContain(`${a}000003/solution.lean: listed in files but does not exist`);
    expect(out).toContain(`${a}000004/attempt.yaml: file "../escape.lean" must be a relative path`);
    expect(out).toContain(`${a}000005/attempt.yaml: mode "ai_only" requires at least one entry in models`);
    expect(out).toContain(`${a}000006/verdict.json: not a valid Verdict`);
    expect(out).toContain('attempts/toy.missing: problem "toy.missing" does not exist');
    expect(out).not.toContain(`${a}000007`);
  });
  test('schema errors and file name mismatches in problems', async () => {
    const root = copyFixture('good');
    const f = join(root, 'problems', 'toy.add-comm.yaml');
    writeFileSync(f, readFileSync(f, 'utf8').replace('tier: proof', 'tier: essay'));
    writeFileSync(join(root, 'problems', 'wrong-name.yaml'), readFileSync(join(root, 'problems', 'toy.open-two.yaml'), 'utf8'));
    const out = lines((await validateRepo(root)).issues);
    expect(out.some((l) => l.startsWith('problems/toy.add-comm.yaml: tier:'))).toBe(true);
    expect(out).toContain('problems/wrong-name.yaml: file name must be toy.open-two.yaml');
  });
  test('oversized files and symlinks are flagged', async () => {
    const root = copyFixture('good');
    const dir = join(root, 'attempts/toy.add-comm/20260102-alice-aaaaaa');
    writeFileSync(join(dir, 'solution.lean'), 'x'.repeat(1024 * 1024 + 1));
    symlinkSync('/etc/hosts', join(dir, 'link.txt'));
    const out = lines((await validateRepo(root)).issues);
    expect(out.some((l) => l.includes('solution.lean: file is larger than 1 MB'))).toBe(true);
    expect(out.some((l) => l.includes('link.txt: symbolic links are not allowed'))).toBe(true);
  });
  test('cli: exit 1 with "path: message" lines; path filter', async () => {
    const r = await cli(BAD, 'validate');
    expect(r.code).toBe(1);
    const rows = r.out.split('\n');
    expect(rows.length).toBeGreaterThan(5);
    expect(rows.every((l) => /^[^:]+: .+/.test(l))).toBe(true);
    const only = await cli(BAD, 'validate', 'attempts/toy.add-comm/20260110-bad-000003');
    expect(only.code).toBe(1);
    expect(only.out.split('\n').every((l) => l.includes('000003'))).toBe(true);
    expect((await cli(BAD, 'validate', 'attempts/toy.add-comm/20260110-bad-000007')).code).toBe(0);
  });
});

describe('validate --changed', () => {
  async function gitRepo() {
    const root = copyFixture('good');
    await sh(root, 'git', 'init', '-q', '-b', 'main');
    await sh(root, 'git', 'config', 'user.email', 't@example.org');
    await sh(root, 'git', 'config', 'user.name', 't');
    await sh(root, 'git', 'add', '-A');
    await sh(root, 'git', 'commit', '-q', '-m', 'base');
    await sh(root, 'git', 'checkout', '-q', '-b', 'pr');
    return root;
  }
  async function addAttempt(root: string) {
    const problem = (await loadProblem('toy.open-two', root))!;
    const { dir } = await scaffoldAttempt({
      root, problem, kind: 'proof', login: 'zed',
      models: [{ name: 'm', provider: 'p', role: 'r' }], date: new Date('2026-02-01T00:00:00Z'),
    });
    ready(dir);
    return dir;
  }
  async function commit(root: string) {
    await sh(root, 'git', 'add', '-A');
    await sh(root, 'git', 'commit', '-q', '-m', 'pr');
  }

  test('one new attempt directory passes', async () => {
    const root = await gitRepo();
    const dir = await addAttempt(root);
    await commit(root);
    const r = await changedIssues(root, 'main...HEAD');
    expect(lines(r.issues)).toEqual([]);
    expect(r.attemptDir).toBe(dir.slice(root.length + 1));
    const viaCli = await cli(root, 'validate', '--changed', 'main...HEAD');
    expect(viaCli.code).toBe(0);
  });
  test('a PR that touches nothing under attempts/ is a code PR and skips the attempt rules', async () => {
    const root = await gitRepo();
    writeFileSync(join(root, 'README.md'), 'hi\n');
    writeFileSync(join(root, 'problems/toy.open-two.yaml'), 'changed: true\n');
    await commit(root);
    const r = await changedIssues(root, 'main...HEAD');
    expect(r.issues).toEqual([]);
    expect(r.attemptDir).toBeNull();
    expect((await cli(root, 'validate', '--changed', 'main...HEAD')).code).toBe(0);
  });
  test('code changes cannot ride along in an attempt PR', async () => {
    const root = await gitRepo();
    await addAttempt(root);
    writeFileSync(join(root, 'README.md'), 'hi\n');
    await commit(root);
    const out = lines((await changedIssues(root, 'main...HEAD')).issues).join('\n');
    expect(out).toContain('README.md: a submission may only add files under attempts/');
    expect((await cli(root, 'validate', '--changed', 'main...HEAD')).code).toBe(1);
  });
  test('editing problems/, adding verdict.json, editing old attempts and stray files all fail', async () => {
    const root = await gitRepo();
    const dir = await addAttempt(root);
    writeFileSync(join(dir, 'verdict.json'), '{}\n');
    writeFileSync(join(root, 'problems/toy.open-two.yaml'), 'changed: true\n');
    writeFileSync(join(root, 'attempts/toy.add-comm/20260102-alice-aaaaaa/solution.lean'), 'tampered\n');
    writeFileSync(join(root, 'README.md'), 'hi\n');
    await commit(root);
    const out = lines((await changedIssues(root, 'main..HEAD')).issues).join('\n');
    expect(out).toContain('verdict.json: verdict.json is written by CI on main');
    expect(out).toContain('problems/toy.open-two.yaml: a submission must not touch problems/');
    expect(out).toContain('20260102-alice-aaaaaa/solution.lean: a submission may only add files (git status M)');
    expect(out).toContain('README.md: a submission may only add files under attempts/');
    expect(out).toContain('must add exactly one attempt directory');
    expect((await cli(root, 'validate', '--changed', 'main..HEAD')).code).toBe(1);
  });
  test('adding a file to an existing attempt directory fails', async () => {
    const root = await gitRepo();
    writeFileSync(join(root, 'attempts/toy.add-comm/20260102-alice-aaaaaa/extra.md'), 'x\n');
    await commit(root);
    expect(lines((await changedIssues(root, 'main...HEAD')).issues).join('\n')).toContain('attempt directory already exists');
  });
  test('an invalid new attempt reports its validation issues', async () => {
    const root = await gitRepo();
    const dir = await addAttempt(root);
    rmSync(join(dir, 'solution.lean'));
    await commit(root);
    expect(lines((await changedIssues(root, 'main...HEAD')).issues).join('\n')).toContain('solution.lean: listed in files but does not exist');
  });
  test('an empty diff has no issues', async () => {
    const root = await gitRepo();
    expect((await changedIssues(root, 'main...HEAD')).issues).toEqual([]);
  });
});

describe('new', () => {
  const proofStatement = 'theorem add_comm_toy (a b : ℕ) : a + b = b + a';
  test('solutionDeclaration: proof keeps binders and type; disproof negates the whole statement', () => {
    expect(solutionDeclaration(proofStatement, false)).toBe('theorem solution (a b : ℕ) : a + b = b + a');
    expect(solutionDeclaration(proofStatement, true)).toBe('theorem solution : ¬ (∀ (a b : ℕ), a + b = b + a)');
    expect(solutionDeclaration('theorem erdos_1 : ∀ n : ℕ, n = n', true)).toBe('theorem solution : ¬ (∀ n : ℕ, n = n)');
    expect(solutionDeclaration('lemma foo {α : Type} [Inhabited α] (x : α) : x = x := by sorry', false)).toBe(
      'theorem solution {α : Type} [Inhabited α] (x : α) : x = x',
    );
    expect(solutionDeclaration('@[category research open, AMS 11]\ntheorem foo (h : a ∣ b)\n    : P a b', false)).toBe(
      'theorem solution (h : a ∣ b) : P a b',
    );
    expect(() => solutionDeclaration('def x := 1', false)).toThrow();
  });
  test('scaffold: proof', async () => {
    const root = copyFixture('good');
    const problem = (await loadProblem('toy.add-comm', root))!;
    const r = await scaffoldAttempt({
      root, problem, kind: 'proof', login: 'Alice',
      models: [{ name: 'm', provider: 'p', role: 'author' }], date: new Date('2026-03-04T10:00:00Z'),
    });
    expect(r.attempt.id).toMatch(/^20260304-alice-[0-9a-f]{6}$/);
    expect(r.dir).toBe(join(root, 'attempts', 'toy.add-comm', r.attempt.id));
    expect(r.files).toEqual(['attempt.yaml', 'solution.lean']);
    const lean = readFileSync(join(r.dir, 'solution.lean'), 'utf8');
    expect(lean.startsWith('import Toy.Problems\n')).toBe(true);
    expect(lean).toContain('namespace OpenProblemsAttempt');
    expect(lean).toContain('theorem solution (a b : ℕ) : a + b = b + a := by\n  sorry');
    expect(lean).toContain('-- Replace the placeholder below with your proof.');
    expect(lean.trimEnd().endsWith('end OpenProblemsAttempt')).toBe(true);
    const written = parseYaml(readFileSync(join(r.dir, 'attempt.yaml'), 'utf8'));
    expect(written).toMatchObject({
      title: 'Proof attempt on Toy: addition commutes',
      claim: 'Describe exactly what this attempt claims.',
      created: '2026-03-04',
      mode: 'ai_only',
      licence: 'CC-BY-4.0',
      declarations: { rights: false, disclosure_complete: false },
      files: ['solution.lean'],
    });
    // The false declarations fail validation, with the instruction to show them to the human.
    const unconfirmed = (await validateRepo(root)).issues.map((i) => i.message);
    expect(unconfirmed).toHaveLength(1);
    expect(unconfirmed.join('\n')).toContain('Show the declarations');
    expect(unconfirmed.join('\n')).toContain('only after they agree');
    // Then the placeholder claim fails until the submitter replaces it.
    confirmDeclarations(r.dir);
    expect((await validateRepo(root)).issues.map((i) => i.message)).toEqual([
      'claim is still the scaffold placeholder; replace it with exactly what this attempt claims',
    ]);
    fillClaim(r.dir);
    expect((await validateRepo(root)).issues).toEqual([]);
  });
  test('scaffold: disproof wraps the type; witness and writeup files; default mode', async () => {
    const root = copyFixture('good');
    const proof = (await loadProblem('toy.add-comm', root))!;
    const d = await scaffoldAttempt({ root, problem: proof, kind: 'disproof', login: 'bob' });
    expect(readFileSync(join(d.dir, 'solution.lean'), 'utf8')).toContain('theorem solution : ¬ (∀ (a b : ℕ), a + b = b + a) := by\n  sorry');
    expect(d.attempt.mode).toBe('human_only');
    expect(leanTemplate(proof, 'disproof')).toContain('proof of the negation');
    const w = await scaffoldAttempt({ root, problem: (await loadProblem('witness.toy-cap', root))!, kind: 'witness', login: 'bob' });
    expect(readFileSync(join(w.dir, 'witness.json'), 'utf8')).toBe('{}\n');
    const t = await scaffoldAttempt({ root, problem: proof, kind: 'writeup', login: 'bob' });
    expect(readFileSync(join(t.dir, 'writeup.md'), 'utf8').startsWith('# Writeup attempt on Toy: addition commutes')).toBe(true);
    for (const a of [d, w, t]) ready(a.dir);
    expect((await validateRepo(root)).issues).toEqual([]);
  });
  test('scaffold refuses a kind the tier does not allow, ai_only without models, bad logins', async () => {
    const root = copyFixture('good');
    const proof = (await loadProblem('toy.add-comm', root))!;
    await expect(scaffoldAttempt({ root, problem: proof, kind: 'witness', login: 'bob' })).rejects.toThrow('not allowed');
    await expect(scaffoldAttempt({ root, problem: proof, kind: 'proof', login: 'bob', mode: 'ai_only' })).rejects.toThrow('requires at least one entry in models');
    await expect(scaffoldAttempt({ root, problem: proof, kind: 'proof', login: 'bad login' })).rejects.toThrow();
  });
  test('Attempt schema accepts what new writes', async () => {
    const root = copyFixture('good');
    const r = await scaffoldAttempt({ root, problem: (await loadProblem('toy.add-comm', root))!, kind: 'proof', login: 'x' });
    expect(Attempt.safeParse(r.attempt).success).toBe(false); // declarations are false until confirmed
    expect(Attempt.safeParse({ ...r.attempt, declarations: { rights: true, disclosure_complete: true } }).success).toBe(true);
  });
  test('cli: --login required (exit 2); creates the directory; --json prints {dir, files}', async () => {
    const root = copyFixture('good');
    expect((await cli(root, 'new', 'toy.add-comm', '--kind', 'proof')).code).toBe(2);
    expect((await cli(root, 'new', 'toy.add-comm', '--kind', 'proof', '--login', 'x', '--model', 'only-two:parts')).code).toBe(2);
    const r = await cli(root, 'new', 'toy.add-comm', '--kind', 'proof', '--login', 'x', '--model', 'm:p:author', '--model', 'n:q:reviewer', '--json');
    expect(r.code).toBe(0);
    const parsed = JSON.parse(r.out) as { dir: string; files: string[] };
    expect(parsed.files).toEqual(['attempt.yaml', 'solution.lean']);
    expect(readFileSync(join(parsed.dir, 'attempt.yaml'), 'utf8')).toContain('role: reviewer');
    ready(parsed.dir);
    expect((await validateRepo(root)).issues).toEqual([]);
  });
});

describe('pick', () => {
  test('only open problems with the fewest attempts; deterministic per seed; seeds vary', async () => {
    const rows = await loadAll(GOOD);
    const zero = new Set(['toy.open-two', 'toy.open-three', 'witness.toy-cap']);
    const picks = new Set<string>();
    for (let s = 0; s < 40; s++) {
      const a = pickProblem(rows, String(s))!;
      expect(pickProblem(rows, String(s))!.problem.id).toBe(a.problem.id);
      expect(zero.has(a.problem.id)).toBe(true);
      picks.add(a.problem.id);
    }
    expect(picks.size).toBe(3);
  });
  test('tier filter, fewest-attempts rule, and none left', async () => {
    const rows = await loadAll(GOOD);
    expect(pickProblem(rows, '1', 'witness')!.problem.id).toBe('witness.toy-cap');
    expect(pickProblem(rows.filter((r) => r.status !== 'open'), '1')).toBeNull();
    expect(pickProblem(rows.filter((r) => r.attempts.length > 0), '1')!.problem.id).toBe('toy.open-one');
  });
  test('cli output is stable for a seed', async () => {
    const a = await cli(GOOD, 'pick', '--seed', '7', '--json');
    const b = await cli(GOOD, 'pick', '--seed', '7', '--json');
    expect(a.code).toBe(0);
    expect(a.out).toBe(b.out);
  });
});

describe('check', () => {
  test('writeups are unchecked', async () => {
    const o = await checkAttempt(GOOD, join(GOOD, 'attempts/toy.open-one/20260104-carol-cccccc'));
    expect('result' in o && o.result).toMatchObject({ checker: 'none', result: 'unchecked' });
  });
  test('dispatches to the tier checker and returns its verdict', async () => {
    const seen: string[] = [];
    const o = await checkAttempt(GOOD, join(GOOD, 'attempts/toy.add-comm/20260102-alice-aaaaaa'), async (tier) => {
      seen.push(tier);
      return async (input) => {
        expect(input.attempt.kind).toBe('proof');
        expect(input.repoRoot).toBe(GOOD);
        return { checker: 'lean', result: 'rejected', summary: 'nope' };
      };
    });
    expect(seen).toEqual(['proof']);
    expect('result' in o && o.result.result).toBe('rejected');
  });
  test('missing checker module is an error verdict; a throwing checker too', async () => {
    const dir = join(GOOD, 'attempts/witness.toy-best/20260105-dave-dddddd');
    const o = await checkAttempt(GOOD, dir, async () => null);
    expect('result' in o && o.result).toEqual({ checker: 'none', result: 'error', summary: 'no checker for tier witness' });
    const t = await checkAttempt(GOOD, dir, async () => async () => {
      throw new Error('boom');
    });
    expect('result' in t && t.result.summary).toContain('boom');
  });
  test('an invalid attempt is reported, not checked', async () => {
    const o = await checkAttempt(BAD, join(BAD, 'attempts/toy.add-comm/20260110-bad-000003'), async () => {
      throw new Error('must not run');
    });
    expect('invalid' in o && o.invalid.join()).toContain('solution.lean: listed in files but does not exist');
    expect('invalid' in (await checkAttempt(GOOD, join(GOOD, 'problems')))).toBe(true);
  });
  test('cli: invalid exits 1; a writeup exits 0 and --json prints the VerdictResult', async () => {
    expect((await cli(BAD, 'check', 'attempts/toy.add-comm/20260110-bad-000003')).code).toBe(1);
    const r = await cli(GOOD, 'check', 'attempts/toy.open-one/20260104-carol-cccccc', '--json');
    expect(r.code).toBe(0);
    expect(JSON.parse(r.out)).toMatchObject({ checker: 'none', result: 'unchecked' });
  });
});

describe('index', () => {
  test('status rule and counts on the fixture', async () => {
    const idx = await buildIndex(GOOD, new Date('2026-05-05T00:00:00Z'));
    expect(Index.safeParse(idx).success).toBe(true);
    expect(Object.fromEntries(idx.problems.map((p) => [p.id, p.status]))).toEqual({
      'toy.add-comm': 'proof-checked',
      'toy.open-one': 'open',
      'toy.open-three': 'open',
      'toy.open-two': 'open',
      'witness.toy-best': 'record-improved',
      'witness.toy-cap': 'open',
    });
    expect(idx.counts).toEqual({
      problems: 6, practice: 0, attempts: 5, verified: 3,
      by_tier: { proof: 4, witness: 2, prose: 0 },
      by_status: { open: 4, 'proof-checked': 1, 'disproof-checked': 0, 'record-improved': 1, practice: 0 },
    });
    expect(idx.generated_at).toBe('2026-05-05T00:00:00.000Z');
    expect(idx.sources).toEqual([]);
    expect(idx.problems.find((p) => p.id === 'toy.add-comm')!.attempts.map((a) => [a.id, a.verdict?.result])).toEqual([
      ['20260102-alice-aaaaaa', 'verified'],
      ['20260103-bob-bbbbbb', 'rejected'],
    ]);
    expect(idx.problems.find((p) => p.id === 'toy.open-one')!.attempts[0]!.verdict).toBeNull();
    expect(idx.problems.map((p) => p.id)).toEqual(idx.problems.map((p) => p.id).sort());
  });
  test('a rejected disproof does not change status; verified disproof does', async () => {
    const root = copyFixture('good');
    const f = join(root, 'attempts/toy.add-comm/20260103-bob-bbbbbb/verdict.json');
    writeFileSync(join(root, 'attempts/toy.add-comm/20260102-alice-aaaaaa/verdict.json'), readFileSync(f, 'utf8').replace('"attempt": "20260103-bob-bbbbbb"', '"attempt": "20260102-alice-aaaaaa"'));
    writeFileSync(f, readFileSync(f, 'utf8').replace('"rejected"', '"verified"'));
    const idx = await buildIndex(root);
    expect(idx.problems.find((p) => p.id === 'toy.add-comm')!.status).toBe('disproof-checked');
  });
  test('reads sources/*.json and refuses an invalid repo', async () => {
    const root = copyFixture('good');
    mkdirSync(join(root, 'sources'));
    writeFileSync(
      join(root, 'sources/formal-conjectures.json'),
      JSON.stringify({ repo: 'https://github.com/google-deepmind/formal-conjectures', commit: 'a'.repeat(40), lean_toolchain: 'x', licence: 'Apache-2.0', imported_at: '2026-01-01' }),
    );
    expect((await buildIndex(root)).sources).toEqual([
      { name: 'formal-conjectures', repo: 'https://github.com/google-deepmind/formal-conjectures', commit: 'a'.repeat(40), licence: 'Apache-2.0' },
    ]);
    await expect(buildIndex(BAD)).rejects.toThrow('repo is invalid');
  });
  test('cli writes --out and prints counts', async () => {
    const root = copyFixture('good');
    const out = join(root, 'out', 'idx.json');
    const r = await cli(root, 'index', '--out', out);
    expect(r.code).toBe(0);
    expect(r.out).toContain('6 problems, 5 attempts, 3 verified');
    const text = readFileSync(out, 'utf8');
    expect(text.endsWith('\n')).toBe(true);
    expect(Index.parse(JSON.parse(text)).counts.problems).toBe(6);
  });
});

describe('cli', () => {
  test('unknown command exits 2 with help; help exits 0 and lists commands', async () => {
    const bogus = await cli(GOOD, 'bogus');
    expect(bogus.code).toBe(2);
    expect(bogus.out).toContain('Commands:');
    const help = await cli(GOOD, '--help');
    expect(help.code).toBe(0);
    for (const c of ['list', 'show', 'pick', 'new', 'validate', 'check', 'index']) expect(help.out).toContain(`  ${c} `);
    const sub = await cli(GOOD, 'new', '--help');
    expect(sub.code).toBe(0);
    expect(sub.out).toContain('Usage: bun frontier new');
  });
  test('list, show and usage errors', async () => {
    const ids = async (...a: string[]) => (JSON.parse((await cli(GOOD, 'list', '--json', ...a)).out) as { id: string }[]).map((r) => r.id);
    expect(await ids('--tier', 'witness')).toEqual(['witness.toy-best', 'witness.toy-cap']);
    expect(await ids('--unattempted')).toEqual(['toy.open-three', 'toy.open-two', 'witness.toy-cap']);
    expect(await ids('--status', 'proof-checked')).toEqual(['toy.add-comm']);
    expect(await ids('--tag', 'witness')).toEqual(['witness.toy-best', 'witness.toy-cap']);
    const show = await cli(GOOD, 'show', 'toy.add-comm', '--json');
    expect(JSON.parse(show.out).status).toBe('proof-checked');
    const text = await cli(GOOD, 'show', 'witness.toy-best');
    expect(text.out).toContain('Best known: 10');
    expect(text.out).toContain('verified (witness)');
    expect((await cli(GOOD, 'show', 'nope')).code).toBe(1);
    expect((await cli(GOOD, 'list', '--bogus-flag')).code).toBe(2);
  });
});

describe('answer-required problems', () => {
  const tagged = (rows: Awaited<ReturnType<typeof loadAll>>, id: string) =>
    rows.map((r) => (r.problem.id === id ? { ...r, problem: { ...r.problem, tags: [...r.problem.tags, 'answer-required'] } } : r));

  test('proof checker returns unchecked without running Lean', async () => {
    const rows = tagged(await loadAll(GOOD), 'toy.add-comm');
    const row = rows.find((r) => r.problem.id === 'toy.add-comm')!;
    const result = await leanCheck({
      repoRoot: GOOD,
      problem: row.problem,
      attempt: row.attempts[0]!.attempt,
      attemptDir: join(GOOD, 'attempts/toy.add-comm/20260102-alice-aaaaaa'),
    });
    expect(result).toEqual({
      checker: 'lean',
      result: 'unchecked',
      summary:
        'This problem asks for an answer that upstream leaves as sorry; automatic checking of answer problems is not supported yet. Submit a writeup.',
    });
  });

  test('pick skips answer-required problems unless --tag answer-required is given', async () => {
    const rows = tagged(await loadAll(GOOD), 'toy.open-two');
    for (let s = 0; s < 40; s++) expect(pickProblem(rows, String(s))!.problem.id).not.toBe('toy.open-two');
    for (let s = 0; s < 5; s++) expect(pickProblem(rows, String(s), undefined, 'answer-required')!.problem.id).toBe('toy.open-two');
    expect(pickProblem(rows, '1', 'witness', 'answer-required')).toBeNull();
  });

  test('new refuses proof and disproof, points to writeup, and still allows a writeup', async () => {
    const root = copyFixture('good');
    const file = join(root, 'problems', 'toy.add-comm.yaml');
    writeFileSync(file, readFileSync(file, 'utf8').replace('  - toy\n', '  - toy\n  - answer-required\n'));
    for (const kind of ['proof', 'disproof']) {
      const r = await cli(root, 'new', 'toy.add-comm', '--kind', kind, '--login', 'alice');
      expect(r.code).toBe(2);
      expect(r.out).toContain('--kind writeup');
    }
    const ok = await cli(root, 'new', 'toy.add-comm', '--kind', 'writeup', '--login', 'alice');
    expect(ok.code).toBe(0);
  });
});
