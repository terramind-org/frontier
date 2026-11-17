import { describe, expect, test } from 'bun:test';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadAttempts, loadProblem, loadProblems, orderKeys, problemStatus, repoRoot, toJson, toYaml, writeYaml } from '../../src/repo.ts';
import { Problem } from '../../src/schema.ts';
import { GOOD } from './helpers.ts';

describe('repo access', () => {
  test('repoRoot walks up to package.json', () => {
    expect(repoRoot(join(GOOD, 'problems'))).toBe(GOOD);
  });
  test('loadProblems sorted by id; loadProblem', async () => {
    const ids = (await loadProblems(GOOD)).map((p) => p.id);
    expect(ids).toEqual([...ids].sort());
    expect((await loadProblem('toy.open-two', GOOD))?.tier).toBe('proof');
    expect(await loadProblem('nope', GOOD)).toBeNull();
  });
  test('loadAttempts filters by problem', async () => {
    expect((await loadAttempts('witness.toy-best', GOOD)).length).toBe(2);
    expect(await loadAttempts('toy.open-two', GOOD)).toEqual([]);
  });
});

describe('stable serialisation', () => {
  test('YAML keys follow schema order, long lines do not wrap, trailing newline', async () => {
    const [p] = await loadProblems(GOOD);
    const shuffled = Object.fromEntries(Object.entries({ ...p!, statement: 'x '.repeat(200), zzz: 1, aaa: 2 }).reverse());
    const text = toYaml(shuffled);
    const topKeys = text.split('\n').filter((l) => /^[a-z_]+:/.test(l)).map((l) => l.split(':')[0]);
    expect(topKeys).toEqual([...Object.keys(Problem.shape).filter((k) => k in shuffled), 'aaa', 'zzz']);
    expect(text.endsWith('\n')).toBe(true);
    expect(text.split('\n').find((l) => l.startsWith('statement:'))!.length).toBeGreaterThan(300);
  });
  test('round-trip file is byte-identical to the checked-in fixture', async () => {
    const [p] = await loadProblems(GOOD);
    const out = join(mkdtempSync(join(tmpdir(), 'frontier-yaml-')), 'p.yaml');
    await writeYaml(out, p);
    expect(readFileSync(out, 'utf8')).toBe(readFileSync(join(GOOD, 'problems', `${p!.id}.yaml`), 'utf8'));
  });
  test('JSON is 2-space indented with trailing newline; nested records sorted', () => {
    expect(toJson({ b: 1, a: { d: 1, c: 2 } })).toBe('{\n  "a": {\n    "c": 2,\n    "d": 1\n  },\n  "b": 1\n}\n');
    expect(Object.keys(orderKeys({ z: 1, a: 1 }) as object)).toEqual(['a', 'z']);
  });
});

describe('problemStatus', () => {
  const v = (result: any, witness?: any) => ({ result, witness });
  test('rule', () => {
    expect(problemStatus([])).toBe('open');
    expect(problemStatus([{ attempt: { kind: 'proof' }, verdict: null }])).toBe('open');
    expect(problemStatus([{ attempt: { kind: 'proof' }, verdict: v('rejected') }])).toBe('open');
    expect(problemStatus([{ attempt: { kind: 'proof' }, verdict: v('verified') }])).toBe('proof-checked');
    expect(problemStatus([{ attempt: { kind: 'disproof' }, verdict: v('verified') }])).toBe('disproof-checked');
    expect(problemStatus([{ attempt: { kind: 'witness' }, verdict: v('verified', { beats_best_known: true }) }])).toBe('record-improved');
    expect(problemStatus([{ attempt: { kind: 'witness' }, verdict: v('verified', { beats_best_known: false }) }])).toBe('open');
    expect(problemStatus([{ attempt: { kind: 'writeup' }, verdict: v('verified') }])).toBe('open');
    // Settled upstream: solved-upstream, unless an attempt here was checked.
    expect(problemStatus([], [], 'solved')).toBe('solved-upstream');
    expect(problemStatus([{ attempt: { kind: 'proof' }, verdict: v('rejected') }], [], 'solved')).toBe('solved-upstream');
    expect(problemStatus([{ attempt: { kind: 'proof' }, verdict: v('verified') }], [], 'solved')).toBe('proof-checked');
    expect(problemStatus([], [], 'partially-solved')).toBe('open');
  });
});
