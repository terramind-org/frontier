import { describe, expect, test } from 'bun:test';
import { problemStatus } from '../../src/repo.ts';
import {
  attemptIssues,
  Index,
  PLACEHOLDER_CLAIM,
  Problem,
  problemIssues,
  ProblemStatus,
  writeupLeanFiles,
} from '../../src/schema.ts';
import type { Attempt } from '../../src/schema.ts';

const base = {
  schema: 1,
  id: 'x.thm',
  title: 'X',
  field: 'mathematics',
  tier: 'proof',
  statement: 'S',
  ams: [],
  tags: ['x'],
  references: [],
  source: { name: 'formal-conjectures', repo: 'https://example.org/r', url: 'https://example.org/r#L1', licence: 'Apache-2.0' },
  upstream_status: 'open',
  lean: {
    module: 'M',
    decl: 'X.thm',
    statement: 'theorem thm : True',
    context: ['open X', 'local notation "!" n => f n'],
    definitions: [{ name: 'X.f', kind: 'def', text: 'def f (n : ℕ) := n', url: 'https://example.org/r#L3' }],
  },
  added: '2026-10-18',
};

describe('Problem schema (cycle 3)', () => {
  test('lean.context and lean.definitions are required and typed', () => {
    expect(Problem.safeParse(base).success).toBe(true);
    const { context: _c, ...noContext } = base.lean;
    expect(Problem.safeParse({ ...base, lean: noContext }).success).toBe(false);
    const { definitions: _d, ...noDefs } = base.lean;
    expect(Problem.safeParse({ ...base, lean: noDefs }).success).toBe(false);
    const badKind = { ...base.lean, definitions: [{ ...base.lean.definitions[0], kind: 'instance' }] };
    expect(Problem.safeParse({ ...base, lean: badKind }).success).toBe(false);
    const badUrl = { ...base.lean, definitions: [{ ...base.lean.definitions[0], url: 'not a url' }] };
    expect(Problem.safeParse({ ...base, lean: badUrl }).success).toBe(false);
    expect(Problem.safeParse({ ...base, lean: { ...base.lean, extra: 1 } }).success).toBe(false);
  });

  test('upstream_status is open or textbook; difficulty is optional with four levels', () => {
    expect(Problem.safeParse({ ...base, upstream_status: 'solved' }).success).toBe(false);
    for (const level of ['practice', 'approachable', 'hard', 'very-hard']) {
      expect(Problem.safeParse({ ...base, difficulty: { level, note: 'n' } }).success).toBe(true);
    }
    expect(Problem.safeParse({ ...base, difficulty: { level: 'easy', note: 'n' } }).success).toBe(false);
    expect(Problem.safeParse({ ...base, difficulty: { level: 'hard', note: '' } }).success).toBe(false);
  });

  test('practice rules: tag, textbook and difficulty level go together', () => {
    const practice = Problem.parse({
      ...base, tags: ['x', 'practice'], upstream_status: 'textbook', difficulty: { level: 'practice', note: 'n' },
    });
    expect(problemIssues(practice)).toEqual([]);
    expect(problemIssues({ ...practice, upstream_status: 'open' })).toEqual(['a `practice` problem must have upstream_status "textbook"']);
    expect(problemIssues({ ...practice, difficulty: undefined })).toEqual(['a `practice` problem needs difficulty.level "practice"']);
    expect(problemIssues({ ...practice, tags: ['x'] })).toEqual([
      'upstream_status "textbook" is only for problems tagged `practice`',
      'difficulty.level "practice" is only for problems tagged `practice`',
    ]);
  });
});

describe('status and index counts', () => {
  test('a practice problem is always `practice`, even with a verified proof', () => {
    expect(ProblemStatus.options).toContain('practice');
    const verified = { attempt: { kind: 'proof' as const }, verdict: { result: 'verified' as const } };
    expect(problemStatus([verified], ['x', 'practice'])).toBe('practice');
    expect(problemStatus([verified], ['x'])).toBe('proof-checked');
    expect(problemStatus([], ['practice'])).toBe('practice');
  });

  test('Index.counts has practice', () => {
    const counts = { problems: 1, practice: 2, attempts: 0, verified: 0, by_tier: {}, by_status: {} };
    const idx = { schema: 1, generated_at: '2026-10-18T00:00:00.000Z', repo_commit: 'x', sources: [], counts, problems: [] };
    expect(Index.safeParse(idx).success).toBe(true);
    const { practice: _p, ...without } = counts;
    expect(Index.safeParse({ ...idx, counts: without }).success).toBe(false);
  });
});

describe('attempt rules (cycle 3)', () => {
  const problem = Problem.parse(base);
  const attempt: Attempt = {
    schema: 1, id: '20261018-alice-abc123', problem: 'x.thm', kind: 'writeup', title: 'T', claim: 'A real claim.',
    files: ['writeup.md', 'partial.lean', 'lemmas/more.lean'], submitter: { github: 'alice' }, people: [], models: [],
    mode: 'human_only', created: '2026-10-18', licence: 'CC-BY-4.0', declarations: { rights: true, disclosure_complete: true },
  };

  test('a writeup may carry extra .lean files', () => {
    expect(attemptIssues(attempt, problem)).toEqual([]);
    expect(writeupLeanFiles(attempt)).toEqual(['partial.lean', 'lemmas/more.lean']);
    expect(writeupLeanFiles({ kind: 'proof', files: ['solution.lean'] })).toEqual([]);
  });

  test('the scaffold placeholder claim is rejected, except while scaffolding', () => {
    const placeholder = { ...attempt, claim: PLACEHOLDER_CLAIM };
    expect(PLACEHOLDER_CLAIM).toBe('Describe exactly what this attempt claims.');
    expect(attemptIssues(placeholder, problem)).toEqual([
      'claim is still the scaffold placeholder; replace it with exactly what this attempt claims',
    ]);
    expect(attemptIssues({ ...attempt, claim: `  ${PLACEHOLDER_CLAIM}\n` }, problem)).toHaveLength(1);
    expect(attemptIssues(placeholder, problem, { scaffold: true })).toEqual([]);
  });
});
