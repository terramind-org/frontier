import { describe, expect, test } from 'bun:test';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { main } from '../../src/cli.ts';
import { checkAttempt } from '../../src/commands/check.ts';
import { buildIndex } from '../../src/commands/index.ts';
import { scaffoldAttempt } from '../../src/commands/new.ts';
import { newCommand, pickProblem } from '../../src/commands/pick.ts';
import { validateRepo } from '../../src/commands/validate.ts';
import { loadAll, loadProblem, toYaml } from '../../src/repo.ts';
import { Attempt, attemptIssues, Problem, problemIssues } from '../../src/schema.ts';
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

/** A prose problem made from a fixture proof problem: no lean block, tier prose. */
async function addProse(root: string, id: string, patch: (p: any) => void = () => {}): Promise<Problem> {
  const p = structuredClone((await loadProblem('toy.open-two', root))!) as any;
  p.id = id;
  p.tier = 'prose';
  p.field = 'economics';
  p.title = `Prose ${id}`;
  delete p.lean;
  patch(p);
  writeFileSync(join(root, 'problems', `${id}.yaml`), toYaml(p));
  return Problem.parse(p);
}

describe('prose tier', () => {
  test('schema: prose has neither lean nor witness nor difficulty; partially-solved status and tag go together', async () => {
    const root = copyFixture('good');
    const p = await addProse(root, 'ws.prose-one');
    expect(problemIssues(p)).toEqual([]);
    const proof = (await loadProblem('toy.open-two', root))!;
    expect(problemIssues({ ...p, lean: proof.lean })).toEqual(['tier "prose" must have neither a `lean` nor a `witness` block']);
    expect(problemIssues({ ...p, difficulty: { level: 'hard', note: 'n' } })).toEqual(['tier "prose" has no difficulty rating']);
    expect(problemIssues({ ...p, upstream_status: 'partially-solved' })).toHaveLength(1);
    expect(problemIssues({ ...p, upstream_status: 'partially-solved', tags: ['partially-solved'] })).toEqual([]);
    for (const field of ['mathematics', 'computer-science', 'physics', 'economics', 'biology']) {
      expect(Problem.safeParse({ ...p, field }).success).toBe(true);
    }
    expect(Problem.safeParse({ ...p, field: 'chemistry' }).success).toBe(false);
    expect(Problem.safeParse({ ...p, external_ids: ['unsolvedmath:12', 'erdosproblems:3'] }).success).toBe(true);
    expect(Problem.safeParse({ ...p, external_ids: ['no scheme'] }).success).toBe(false);
  });

  test('attempts on prose may only be writeups', async () => {
    const root = copyFixture('good');
    const p = await addProse(root, 'ws.prose-one');
    const base = {
      schema: 1, id: '20261021-alice-abcdef', problem: p.id, title: 't', claim: 'c', submitter: { github: 'alice' },
      people: [], models: [], mode: 'human_only', created: '2026-10-21', licence: 'CC-BY-4.0',
      declarations: { rights: true, disclosure_complete: true },
    } as const;
    expect(attemptIssues(Attempt.parse({ ...base, kind: 'writeup', files: ['writeup.md'] }), p)).toEqual([]);
    for (const [kind, file] of [['proof', 'solution.lean'], ['disproof', 'solution.lean'], ['witness', 'witness.json']] as const) {
      expect(attemptIssues(Attempt.parse({ ...base, kind, files: [file] }), p)).toEqual([
        `kind "${kind}" is not allowed on a "prose" problem: prose problems take only writeups, which are never machine-checked`,
      ]);
    }
  });

  test('new refuses non-writeup kinds and scaffolds a writeup; check never runs a checker on it', async () => {
    const root = copyFixture('good');
    await addProse(root, 'ws.prose-one');
    const refused = await cli(root, 'new', 'ws.prose-one', '--kind', 'proof', '--login', 'alice');
    expect(refused.code).toBe(2);
    expect(refused.out).toContain('ws.prose-one is a prose problem: only --kind writeup is accepted');
    const ok = await cli(root, 'new', 'ws.prose-one', '--kind', 'writeup', '--login', 'alice');
    expect(ok.code).toBe(0);
    expect(ok.out).toContain('never machine-checked');
    const p = (await loadProblem('ws.prose-one', root))!;
    const { dir } = await scaffoldAttempt({ root, problem: p, kind: 'writeup', login: 'bob' });
    ready(dir);
    let loaded = false;
    const o = await checkAttempt(root, dir, async () => {
      loaded = true;
      return null;
    });
    expect(loaded).toBe(false);
    expect('result' in o && o.result.checker).toBe('none');
    expect('result' in o && o.result.result).toBe('unchecked');
  });

  test('pick never picks prose without --tier prose; with it, the new command is a writeup', async () => {
    const root = copyFixture('good');
    await addProse(root, 'ws.prose-one');
    await addProse(root, 'um.2');
    const rows = await loadAll(root);
    for (let seed = 0; seed < 40; seed++) expect(pickProblem(rows, String(seed))!.problem.tier).not.toBe('prose');
    const prose = pickProblem(rows, '1', 'prose')!;
    expect(prose.problem.tier).toBe('prose');
    expect(newCommand(prose.problem)).toContain('--kind writeup');
    const r = await cli(root, 'pick', '--tier', 'prose', '--seed', '1');
    expect(r.code).toBe(0);
    expect(r.out).toContain('--kind writeup');
    expect(r.out).toContain('never machine-checked');
    expect((await cli(root, 'pick', '--tier', 'essay')).code).toBe(2);
  });

  test('list --tier prose, show explains the tier, index counts prose as open', async () => {
    const root = copyFixture('good');
    await addProse(root, 'ws.prose-one', (p) => {
      p.tags = ['open-status-unverified'];
      p.external_ids = ['we-solve:prb_0007fc1635b9497fbfd2a64523550ac0'];
    });
    const list = JSON.parse((await cli(root, 'list', '--tier', 'prose', '--json')).out) as { id: string; field: string; status: string }[];
    expect(list).toEqual([expect.objectContaining({ id: 'ws.prose-one', field: 'economics', status: 'open' })]);
    const show = (await cli(root, 'show', 'ws.prose-one')).out;
    expect(show).toContain('tier: prose   field: economics   status: open');
    expect(show).toContain('A labelled AI review of a writeup is an opinion, not a verdict');
    expect(show).toContain('open status unverified');
    expect(show).toContain('Also known as: we-solve:prb_0007fc1635b9497fbfd2a64523550ac0');
    expect((await validateRepo(root)).issues).toEqual([]);
    const idx = await buildIndex(root, new Date('2026-10-21T00:00:00Z'));
    expect(idx.counts.by_tier).toEqual({ proof: 4, witness: 2, prose: 1 });
    expect(idx.counts.problems).toBe(7);
    expect(idx.problems.find((p) => p.id === 'ws.prose-one')!.status).toBe('open');
  });

  test('a prose problem with a lean block fails validate', async () => {
    const root = copyFixture('good');
    const f = join(root, 'problems', 'toy.open-two.yaml');
    const raw = parseYaml(readFileSync(f, 'utf8'));
    writeFileSync(f, toYaml({ ...raw, tier: 'prose' }));
    const issues = (await validateRepo(root)).issues.map((i) => `${i.path}: ${i.message}`);
    expect(issues).toContain('problems/toy.open-two.yaml: tier "prose" must have neither a `lean` nor a `witness` block');
  });
});
