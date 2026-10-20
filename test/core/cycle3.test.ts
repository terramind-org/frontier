import { describe, expect, test } from 'bun:test';
import { existsSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { main } from '../../src/cli.ts';
import { checkAttempt } from '../../src/commands/check.ts';
import { buildIndex } from '../../src/commands/index.ts';
import { leanTemplate, scaffoldAttempt } from '../../src/commands/new.ts';
import { newCommand, pickProblem } from '../../src/commands/pick.ts';
import { loadAll, loadProblem, nearestIds, toYaml } from '../../src/repo.ts';
import { Index } from '../../src/schema.ts';
import type { Problem } from '../../src/schema.ts';
import { validateAttemptDir, validateRepo } from '../../src/commands/validate.ts';
import { copyFixture, ready } from './helpers.ts';

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

/** Write `problems/<id>.yaml` as a patched copy of another fixture problem. */
async function addProblem(root: string, from: string, id: string, patch: (p: any) => void): Promise<void> {
  const p = structuredClone((await loadProblem(from, root))!) as any;
  p.id = id;
  patch(p);
  writeFileSync(join(root, 'problems', `${id}.yaml`), toYaml(p));
}

const BANNED = /\b(axiom|meta|macro|syntax|elab|unsafe|initialize|sorry|native_decide)\b/;

/** A fixture repo with a context-bearing proof problem, a practice problem and rated witness problems. */
async function richRoot(): Promise<string> {
  const root = copyFixture('good');
  await addProblem(root, 'toy.add-comm', 'toy.with-context', (p) => {
    p.title = 'Toy: needs context';
    p.lean.statement = 'theorem with_context (n : ℕ) : n ! = n !';
    p.lean.context = ['open Nat', 'local notation "!" n => Nat.factorial n'];
    p.lean.definitions = [
      { name: 'Toy.helper', kind: 'def', text: 'def helper (n : ℕ) : ℕ := n + 1', url: 'https://example.org/f.lean#L3' },
    ];
  });
  await addProblem(root, 'toy.add-comm', 'toy.practice-one', (p) => {
    p.title = 'Practice: addition';
    p.tags = ['practice'];
    p.upstream_status = 'textbook';
    p.difficulty = { level: 'practice', note: 'One line: use Nat.add_comm.' };
  });
  await addProblem(root, 'witness.toy-cap', 'witness.toy-easy', (p) => {
    p.difficulty = { level: 'approachable', note: 'A direct construction reaches the record.' };
  });
  await addProblem(root, 'witness.toy-cap', 'witness.toy-hard', (p) => {
    p.difficulty = { level: 'very-hard', note: 'Beating the record needs new ideas.' };
  });
  return root;
}

describe('new: scaffold text', () => {
  test('context lines come before the namespace; the comment has no banned word', async () => {
    const root = await richRoot();
    const problem = (await loadProblem('toy.with-context', root))!;
    for (const kind of ['proof', 'disproof'] as const) {
      const text = leanTemplate(problem, kind);
      expect(text).toBe(
        [
          'import Toy.Problems',
          '',
          'open Nat',
          'local notation "!" n => Nat.factorial n',
          '',
          'namespace OpenProblemsAttempt',
          '',
          kind === 'proof' ? '-- Replace the placeholder below with your proof.' : '-- Replace the placeholder below with your proof of the negation.',
          kind === 'proof' ? 'theorem solution (n : ℕ) : n ! = n ! := by' : 'theorem solution : ¬ (∀ (n : ℕ), n ! = n !) := by',
          '  sorry',
          '',
          'end OpenProblemsAttempt',
          '',
        ].join('\n'),
      );
      const comments = text.split('\n').filter((l) => l.trimStart().startsWith('--'));
      expect(comments.length).toBeGreaterThan(0);
      for (const c of comments) expect(c).not.toMatch(BANNED);
    }
  });
  test('a problem without context scaffolds with no blank block before the namespace', async () => {
    const root = copyFixture('good');
    const text = leanTemplate((await loadProblem('toy.add-comm', root))!, 'proof');
    expect(text.startsWith('import Toy.Problems\n\nnamespace OpenProblemsAttempt\n')).toBe(true);
  });
});

describe('new: declarations, tools, writeup lean files', () => {
  test('declarations are false; validate and submit refuse until the human confirmed, check runs with a note', async () => {
    const root = copyFixture('good');
    const problem = (await loadProblem('toy.open-one', root))!;
    const { dir } = await scaffoldAttempt({ root, problem, kind: 'writeup', login: 'zed' });
    const rel = dir.slice(root.length + 1);
    const text = readFileSync(join(dir, 'attempt.yaml'), 'utf8');
    expect(text).toContain('rights: false');
    expect(text).toContain('disclosure_complete: false');

    const issues = (await validateAttemptDir(root, dir)).map((i) => i.message).join('\n');
    expect(issues).toContain('declarations: not confirmed');
    expect(issues).toContain('Show the declarations');
    expect(issues).toContain('your human');

    const v = await cli(root, 'validate');
    expect(v.code).toBe(1);
    expect(v.out).toContain(`${rel}/attempt.yaml: declarations: not confirmed`);

    // A local check judges the work, not the paperwork: it runs, and says what submit will still need.
    const c = await cli(root, 'check', rel);
    expect(c.code).toBe(0);
    expect(c.out).toContain('unchecked');
    expect(c.out).toContain('before submit');
    expect(c.out).toContain('Show the declarations');

    // submit refuses before it asks gh anything.
    const { submit } = await import('../../src/commands/submit.ts');
    const calls: string[] = [];
    const lines: string[] = [];
    const exec = async (cmd: string, args: string[]) => {
      calls.push(`${cmd} ${args.join(' ')}`);
      return { code: 0, stdout: '', stderr: '' };
    };
    expect(await submit({ root, dir, yes: true, repo: 'terramind-org/frontier', exec, log: (l) => lines.push(l) })).toBe(1);
    expect(calls).toEqual([]);
    expect(lines.join('\n')).toContain('not valid');
    expect(lines.join('\n')).toContain('Show the declarations');
  });

  test('a confirmed declaration but a placeholder claim still fails', async () => {
    const root = copyFixture('good');
    const problem = (await loadProblem('toy.open-one', root))!;
    const { dir } = await scaffoldAttempt({ root, problem, kind: 'writeup', login: 'zed' });
    const file = join(dir, 'attempt.yaml');
    writeFileSync(file, readFileSync(file, 'utf8').replace('rights: false', 'rights: true').replace('disclosure_complete: false', 'disclosure_complete: true'));
    expect((await validateAttemptDir(root, dir)).map((i) => i.message)).toEqual([
      'claim is still the scaffold placeholder; replace it with exactly what this attempt claims',
    ]);
  });

  test('--tool records name:role with provider "tool"; human_only unless an AI model is given', async () => {
    const root = copyFixture('good');
    const r = await cli(root, 'new', 'toy.add-comm', '--kind', 'proof', '--login', 'x', '--tool', 'cp-sat:search', '--tool', 'lake:checker', '--json');
    expect(r.code).toBe(0);
    const dir = (JSON.parse(r.out) as { dir: string }).dir;
    const a = parseYaml(readFileSync(join(dir, 'attempt.yaml'), 'utf8'));
    expect(a.models).toEqual([
      { name: 'cp-sat', provider: 'tool', role: 'search' },
      { name: 'lake', provider: 'tool', role: 'checker' },
    ]);
    expect(a.mode).toBe('human_only');
    const both = await cli(root, 'new', 'toy.add-comm', '--kind', 'proof', '--login', 'x', '--model', 'm:p:author', '--tool', 'lake:checker', '--json');
    const b = parseYaml(readFileSync(join((JSON.parse(both.out) as { dir: string }).dir, 'attempt.yaml'), 'utf8'));
    expect(b.mode).toBe('ai_only');
    expect(b.models).toHaveLength(2);
    ready(dir);
    ready((JSON.parse(both.out) as { dir: string }).dir);
    expect((await validateRepo(root)).issues).toEqual([]);
    expect((await cli(root, 'new', 'toy.add-comm', '--kind', 'proof', '--login', 'x', '--tool', 'noroles')).code).toBe(2);
  });

  test('a writeup may carry extra .lean files: created, listed, valid, unchecked, not compiled', async () => {
    const root = copyFixture('good');
    const r = await cli(root, 'new', 'toy.add-comm', '--kind', 'writeup', '--login', 'x', '--lean-file', 'partial.lean', '--json');
    expect(r.code).toBe(0);
    const parsed = JSON.parse(r.out) as { dir: string; files: string[] };
    expect(parsed.files).toEqual(['attempt.yaml', 'writeup.md', 'partial.lean']);
    expect(readFileSync(join(parsed.dir, 'partial.lean'), 'utf8')).toBe('import Toy.Problems\n\n');
    expect(parseYaml(readFileSync(join(parsed.dir, 'attempt.yaml'), 'utf8')).files).toEqual(['writeup.md', 'partial.lean']);
    ready(parsed.dir);
    expect((await validateRepo(root)).issues).toEqual([]);
    const out = await checkAttempt(realpathSync(root), parsed.dir);
    if ('invalid' in out) throw new Error(out.invalid.join('\n'));
    expect(out.result.result).toBe('unchecked');
    expect(out.result.summary).toContain('partial.lean is shown with the writeup but not compiled');
  });

  test('--lean-file is for writeups and must be a plain .lean name', async () => {
    const root = copyFixture('good');
    expect((await cli(root, 'new', 'toy.add-comm', '--kind', 'proof', '--login', 'x', '--lean-file', 'a.lean')).code).toBe(2);
    expect((await cli(root, 'new', 'toy.add-comm', '--kind', 'writeup', '--login', 'x', '--lean-file', '../a.lean')).code).toBe(2);
    expect((await cli(root, 'new', 'toy.add-comm', '--kind', 'writeup', '--login', 'x', '--lean-file', 'a.txt')).code).toBe(2);
  });

  test('an unknown id lists the nearest ids and says what is imported', async () => {
    const root = copyFixture('good');
    const r = await cli(root, 'new', 'toy.add-comn', '--kind', 'proof', '--login', 'x');
    expect(r.code).toBe(1);
    expect(r.out).toContain('Nearest ids:');
    expect(r.out).toContain('toy.add-comm');
    expect(r.out).toContain('Only upstream-open problems');
  });
});

describe('show', () => {
  test('prints context, definitions, difficulty and the practice marker', async () => {
    const root = await richRoot();
    const ctx = await cli(root, 'show', 'toy.with-context');
    expect(ctx.code).toBe(0);
    expect(ctx.out).toContain('Lean context (the scaffold puts these lines before the theorem):');
    expect(ctx.out).toContain('  open Nat');
    expect(ctx.out).toContain('  local notation "!" n => Nat.factorial n');
    expect(ctx.out).toContain('Definitions the statement uses:');
    expect(ctx.out).toContain('def Toy.helper  (https://example.org/f.lean#L3)');
    expect(ctx.out).toContain('    def helper (n : ℕ) : ℕ := n + 1');

    const pr = await cli(root, 'show', 'toy.practice-one');
    expect(pr.out).toContain('status: practice');
    expect(pr.out).toContain('practice: a textbook exercise');
    expect(pr.out).toContain('difficulty: practice. One line: use Nat.add_comm.');

    const w = await cli(root, 'show', 'witness.toy-hard');
    expect(w.out).toContain('difficulty: very-hard. Beating the record needs new ideas.');

    const plain = await cli(root, 'show', 'toy.add-comm');
    expect(plain.out).not.toContain('Lean context');
    expect(plain.out).not.toContain('Definitions the statement uses');
    expect(plain.out).not.toContain('difficulty:');
  });
  test('an unknown id suggests at most 5 near ids and the import note', async () => {
    const root = await richRoot();
    const r = await cli(root, 'show', 'toy.add');
    expect(r.code).toBe(1);
    const near = r.out.split('\n').filter((l) => /^ {2}\S+$/.test(l));
    expect(near.length).toBeGreaterThan(0);
    expect(near.length).toBeLessThanOrEqual(5);
    expect(near).toContain('  toy.add-comm');
    expect(r.out).toContain('Only upstream-open problems, the witness problems and a small practice set are imported');
  });
  test('nearestIds ranks shared parts and typos first and respects the limit', () => {
    const ids = ['erdos1.erdos-1', 'erdos2.erdos-2', 'erdos10.erdos-10', 'kurepa.kurepa-conjecture', 'brocard.brocard-conjecture', 'zzz.unrelated', 'erdos3.erdos-3'];
    expect(nearestIds('kurepa-conjecture', ids)[0]).toBe('kurepa.kurepa-conjecture');
    expect(nearestIds('brocad.brocard-conjecture', ids)[0]).toBe('brocard.brocard-conjecture');
    expect(nearestIds('erdos', ids, 2)).toHaveLength(2);
    expect(nearestIds('erdos', ids).length).toBeLessThanOrEqual(5);
  });
});

describe('pick and list with practice and difficulty', () => {
  test('practice problems are never picked or listed unless asked for', async () => {
    const root = await richRoot();
    const rows = await loadAll(root);
    for (let s = 0; s < 40; s++) expect(pickProblem(rows, String(s))!.problem.id).not.toBe('toy.practice-one');
    expect(pickProblem(rows, '1', 'proof', undefined, { practice: true })!.problem.id).toBe('toy.practice-one');
    expect(pickProblem(rows, '1', 'witness', undefined, { practice: true })).toBeNull();

    expect((await cli(root, 'list')).out).not.toContain('toy.practice-one');
    expect((await cli(root, 'list', '--practice')).out).toContain('toy.practice-one');
    expect((await cli(root, 'list', '--status', 'practice')).out).toContain('toy.practice-one');
    expect((await cli(root, 'list', '--tag', 'practice')).out).toContain('toy.practice-one');
    const json = JSON.parse((await cli(root, 'list', '--practice', '--json')).out) as { id: string; difficulty: string | null }[];
    expect(json.find((r) => r.id === 'witness.toy-easy')!.difficulty).toBe('approachable');
    expect(json.find((r) => r.id === 'toy.add-comm')!.difficulty).toBeNull();
    expect((await cli(root, 'pick', '--practice', '--seed', '1', '--json')).out).toContain('toy.practice-one');
  });
  test('--max-difficulty keeps rated problems at most that hard and skips unrated ones', async () => {
    const root = await richRoot();
    const rows = await loadAll(root);
    for (let s = 0; s < 20; s++) {
      expect(pickProblem(rows, String(s), undefined, undefined, { maxDifficulty: 'approachable' })!.problem.id).toBe('witness.toy-easy');
    }
    const hard = new Set<string>();
    for (let s = 0; s < 40; s++) hard.add(pickProblem(rows, String(s), undefined, undefined, { maxDifficulty: 'very-hard' })!.problem.id);
    expect([...hard].sort()).toEqual(['witness.toy-easy', 'witness.toy-hard']);
    expect((await cli(root, 'pick', '--max-difficulty', 'impossible')).code).toBe(2);
    const none = await cli(root, 'pick', '--tier', 'proof', '--max-difficulty', 'hard');
    expect(none.code).toBe(1);
  });
  test('--tier witness prefers the lowest rated difficulty over fewer attempts', async () => {
    const root = await richRoot();
    const rows = await loadAll(root);
    // Unrated witness problems count as very-hard, so the approachable one always wins.
    for (let s = 0; s < 20; s++) expect(pickProblem(rows, String(s), 'witness')!.problem.id).toBe('witness.toy-easy');
    // Even when it has more attempts than the others.
    const busy = rows.map((r) => (r.problem.id === 'witness.toy-easy' ? { ...r, attempts: [...r.attempts, ...rows.find((x) => x.problem.id === 'witness.toy-best')!.attempts] } : r));
    expect(pickProblem(busy, '3', 'witness')!.problem.id).toBe('witness.toy-easy');
  });
  test('pick prints the difficulty note and a full new command with --model', async () => {
    const root = await richRoot();
    const r = await cli(root, 'pick', '--tier', 'witness', '--seed', '1');
    expect(r.code).toBe(0);
    expect(r.out).toContain('Difficulty: approachable. A direct construction reaches the record.');
    expect(r.out).toContain('bun frontier new witness.toy-easy --kind witness --login <your-github-login> --model "<model>:<provider>:author"');
    expect(r.out).toContain('--tool');
    const json = JSON.parse((await cli(root, 'pick', '--tier', 'witness', '--seed', '1', '--json')).out) as { new: string; difficulty: { level: string } };
    expect(json.difficulty.level).toBe('approachable');
    expect(json.new).toBe(newCommand((await loadProblem('witness.toy-easy', root))!));
    const proof = await loadProblem('toy.add-comm', root);
    expect(newCommand(proof as Problem)).toContain('--kind proof');
  });
});

describe('index counts with practice problems', () => {
  test('practice is counted apart and kept out of problems, by_tier and the headline statuses', async () => {
    const root = await richRoot();
    const idx = await buildIndex(root, new Date('2026-05-05T00:00:00Z'));
    expect(Index.safeParse(idx).success).toBe(true);
    expect(idx.counts.practice).toBe(1);
    expect(idx.counts.problems).toBe(idx.problems.length - 1);
    expect(idx.counts.by_status.practice).toBe(1);
    expect(idx.counts.by_tier.proof! + idx.counts.by_tier.witness!).toBe(idx.counts.problems);
    expect(idx.problems.find((p) => p.id === 'toy.practice-one')!.status).toBe('practice');
  });
  test('a verified proof on a practice problem stays practice and never makes proof-checked', async () => {
    const root = await richRoot();
    const problem = (await loadProblem('toy.practice-one', root))!;
    const { dir, attempt } = await scaffoldAttempt({ root, problem, kind: 'proof', login: 'zed', models: [{ name: 'm', provider: 'p', role: 'author' }] });
    ready(dir);
    writeFileSync(
      join(dir, 'verdict.json'),
      JSON.stringify({ schema: 1, attempt: attempt.id, checked_at: '2026-05-05T00:00:00.000Z', checker_version: 'x', checker: 'lean', result: 'verified', summary: 'proof checked' }),
    );
    const idx = await buildIndex(root, new Date('2026-05-05T00:00:00Z'));
    expect(idx.problems.find((p) => p.id === 'toy.practice-one')!.status).toBe('practice');
    expect(idx.counts.by_status['proof-checked']).toBe(1); // only toy.add-comm from the base fixture
    expect(existsSync(join(dir, 'verdict.json'))).toBe(true);
  });
});

describe('check output', () => {
  test('plainSummary drops a leading "rejected:" so the caller prefixes once', async () => {
    const { plainSummary } = await import('../../src/commands/check.ts');
    expect(plainSummary({ summary: 'rejected: uses sorry' })).toBe('uses sorry');
    expect(plainSummary({ summary: 'Rejected:   type mismatch' })).toBe('type mismatch');
    expect(plainSummary({ summary: 'uses sorry' })).toBe('uses sorry');
  });
});
