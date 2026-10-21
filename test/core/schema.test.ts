import { describe, expect, test } from 'bun:test';
import { Attempt, Index, Problem, Verdict, VerdictResult, attemptIssues, isSafeRelativePath, problemIssues } from '../../src/schema.ts';
import { loadAll, loadAttempts, loadProblems } from '../../src/repo.ts';
import { GOOD } from './helpers.ts';

async function fixtures() {
  const problems = await loadProblems(GOOD);
  const byId = (id: string) => problems.find((p) => p.id === id)!;
  return { proofP: byId('toy.add-comm'), witnessP: byId('witness.toy-cap') };
}

describe('schemas', () => {
  test('fixture problems, attempts and verdicts parse', async () => {
    expect((await loadProblems(GOOD)).length).toBe(6);
    const attempts = await loadAttempts(undefined, GOOD);
    expect(attempts.length).toBe(5);
    expect(attempts.filter((a) => a.verdict).length).toBe(4);
  });
  test('rejects unknown keys, bad enums and bad ids', async () => {
    const { proofP } = await fixtures();
    expect(Problem.safeParse({ ...proofP, extra: 1 }).success).toBe(false);
    expect(Problem.safeParse({ ...proofP, tier: 'essay' }).success).toBe(false);
    expect(Problem.safeParse({ ...proofP, id: 'Bad_ID' }).success).toBe(false);
    expect(Problem.safeParse({ ...proofP, source: { ...proofP.source, commit: 'abc' } }).success).toBe(false);
    expect(Problem.safeParse({ ...proofP, added: 'yesterday' }).success).toBe(false);
    const { attempt } = (await loadAttempts('toy.add-comm', GOOD))[0]!;
    expect(Attempt.safeParse({ ...attempt, licence: 'MIT' }).success).toBe(false);
    expect(Attempt.safeParse({ ...attempt, declarations: { rights: false, disclosure_complete: true } }).success).toBe(false);
    expect(Attempt.safeParse({ ...attempt, id: 'nope' }).success).toBe(false);
    expect(Attempt.safeParse({ ...attempt, files: [] }).success).toBe(false);
    expect(Attempt.safeParse({ ...attempt, title: 'x'.repeat(201) }).success).toBe(false);
  });
  test('VerdictResult is loose, Verdict is strict and needs metadata', () => {
    const base = { checker: 'lean', result: 'verified', summary: 'ok' };
    expect(VerdictResult.safeParse(base).success).toBe(true);
    expect(VerdictResult.safeParse({ ...base, result: 'solved' }).success).toBe(false);
    expect(Verdict.safeParse(base).success).toBe(false);
  });
  test('index built from the fixture round-trips through Index', async () => {
    const { buildIndex } = await import('../../src/commands/index.ts');
    expect(Index.safeParse(await buildIndex(GOOD)).success).toBe(true);
  });
});

describe('problemIssues', () => {
  test('lean required iff tier proof, witness required iff tier witness', async () => {
    const { proofP, witnessP } = await fixtures();
    expect(problemIssues(proofP)).toEqual([]);
    expect(problemIssues(witnessP)).toEqual([]);
    expect(problemIssues({ ...proofP, lean: undefined })).toEqual(['tier "proof" requires a `lean` block']);
    expect(problemIssues({ ...witnessP, witness: undefined })).toEqual(['tier "witness" requires a `witness` block']);
    expect(problemIssues({ ...proofP, witness: witnessP.witness })).toHaveLength(1);
    expect(problemIssues({ ...witnessP, lean: proofP.lean })).toHaveLength(1);
  });
});

describe('attemptIssues', () => {
  test('valid attempts have no issues; kind/tier and file rules', async () => {
    const { proofP, witnessP } = await fixtures();
    const all = await loadAll(GOOD);
    const proofAttempt = all.find((r) => r.problem.id === 'toy.add-comm')!.attempts[0]!.attempt;
    expect(attemptIssues(proofAttempt, proofP)).toEqual([]);
    expect(attemptIssues({ ...proofAttempt, kind: 'disproof' }, proofP)).toEqual([]);
    expect(attemptIssues({ ...proofAttempt, kind: 'writeup', files: ['writeup.md'], problem: witnessP.id }, witnessP)).toEqual([]);
    expect(attemptIssues({ ...proofAttempt, kind: 'witness', files: ['witness.json'] }, proofP).join()).toContain('not allowed on a "proof" problem');
    expect(attemptIssues(proofAttempt, witnessP).join()).toContain('not allowed on a "witness" problem');
    expect(attemptIssues({ ...proofAttempt, files: ['notes.md'] }, proofP)).toEqual(['kind "proof" needs "solution.lean" in files']);
    expect(attemptIssues({ ...proofAttempt, kind: 'witness', files: ['solution.lean'] }, witnessP).join()).toContain('needs "witness.json"');
  });
  test('paths may not escape', async () => {
    const { proofP } = await fixtures();
    const a = (await loadAttempts('toy.add-comm', GOOD))[0]!.attempt;
    for (const f of ['../x.lean', '/etc/passwd', 'a/../../b', 'C:\\x', 'a//b', './a']) {
      expect(attemptIssues({ ...a, files: ['solution.lean', f] }, proofP).join()).toContain(`file "${f}"`);
    }
    expect(isSafeRelativePath('sub/dir/file.lean')).toBe(true);
  });
  test('models non-empty unless human_only', async () => {
    const { proofP } = await fixtures();
    const a = (await loadAttempts('toy.add-comm', GOOD))[0]!.attempt;
    expect(attemptIssues({ ...a, models: [], mode: 'ai_only' }, proofP).join()).toContain('requires at least one entry in models');
    expect(attemptIssues({ ...a, models: [], mode: 'human_ai' }, proofP)).toHaveLength(1);
    expect(attemptIssues({ ...a, models: [], mode: 'human_only' }, proofP)).toEqual([]);
  });
});
