import { afterAll, describe, expect, test } from 'bun:test';
import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { check } from '../../../src/check/witness.ts';
import { checkAttempt } from '../../../src/commands/check.ts';
import { loadProblem, repoRoot, toYaml } from '../../../src/repo.ts';
import { Problem } from '../../../src/schema.ts';
import type { Attempt } from '../../../src/schema.ts';
import { fixture } from './helpers.ts';

const root = repoRoot();
const tmp = realpathSync(mkdtempSync(join(tmpdir(), 'frontier-witness-'))); // realpath: macOS /var is a symlink
afterAll(() => rmSync(tmp, { recursive: true, force: true }));

const record = fixture('cap-set-f3-8-size512.json') as { points: number[][] };

async function problemWith(id: string, bestKnown?: number): Promise<Problem> {
  const p = (await loadProblem(id, root))!;
  if (bestKnown !== undefined) p.witness!.best_known.value = bestKnown;
  return p;
}

function attemptStub(problem: string): Attempt {
  return {
    schema: 1, id: '20261019-tester-abc123', problem, kind: 'witness', title: 't', claim: 'c',
    files: ['attempt.yaml', 'witness.json'], submitter: { github: 'tester' }, people: [], models: [], mode: 'human_only',
    created: '2026-10-19', licence: 'CC-BY-4.0', declarations: { rights: true, disclosure_complete: true },
  } as Attempt;
}

let counter = 0;
function attemptDir(content: string | null): string {
  const dir = join(tmp, `a${counter++}`);
  mkdirSync(dir);
  if (content !== null) writeFileSync(join(dir, 'witness.json'), content);
  return dir;
}

async function run(problem: Problem, content: string | null) {
  return check({ repoRoot: root, problem, attempt: attemptStub(problem.id), attemptDir: attemptDir(content) });
}

describe('witness tier checker', () => {
  test('a valid cap set that equals the best known value ties it', async () => {
    const r = await run(await problemWith('witness.cap-set-f3-8'), JSON.stringify(record));
    expect(r.checker).toBe('witness');
    expect(r.result).toBe('verified');
    expect(r.witness).toEqual({ valid: true, value: 512, best_known: 512, beats_best_known: false, ties_best_known: true });
    expect(r.summary).toContain('value 512');
    expect(r.summary).toContain('ties the best known');
  });

  test('a valid witness above a lowered best known beats it (maximize)', async () => {
    const r = await run(await problemWith('witness.cap-set-f3-8', 500), JSON.stringify(record));
    expect(r.result).toBe('verified');
    expect(r.witness).toMatchObject({ value: 512, best_known: 500, beats_best_known: true, ties_best_known: false });
    expect(r.summary).toContain('beats the best known (500');
  });

  test('a valid witness below the best known neither beats nor ties it', async () => {
    const slice = record.points.filter((p) => p[7] === 0).map((p) => p.slice(0, 7));
    const r = await run(await problemWith('witness.cap-set-f3-7'), JSON.stringify({ points: slice }));
    expect(r.result).toBe('verified');
    expect(r.witness).toMatchObject({ valid: true, value: slice.length, best_known: 236, beats_best_known: false, ties_best_known: false });
    expect(r.summary).toContain('does not reach the best known 236');
  });

  test('minimize problems: a shorter ruler beats, an equal one ties, a longer one does not', async () => {
    const marks = [0, 7, 11, 31, 43, 53, 100, 121, 144, 150, 202, 220, 229, 268, 284, 285, 356, 371, 390, 416, 430, 465, 467, 528, 582, 590, 595, 620, 623];
    const json = JSON.stringify({ marks });
    const tie = await run(await problemWith('witness.golomb-ruler-29'), json);
    expect(tie.witness).toMatchObject({ value: 623, beats_best_known: false, ties_best_known: true });
    const beat = await run(await problemWith('witness.golomb-ruler-29', 624), json);
    expect(beat.witness).toMatchObject({ beats_best_known: true, ties_best_known: false });
    const worse = await run(await problemWith('witness.golomb-ruler-29', 600), json);
    expect(worse.witness).toMatchObject({ beats_best_known: false, ties_best_known: false });
  });

  test('every shipped witness problem has a working verifier and rejects an empty object with a reason', async () => {
    const ids = ['cap-set-f3-7', 'cap-set-f3-8', 'ramsey-5-5', 'ramsey-4-6', 'golomb-ruler-29', 'schur-7', 'kissing-number-11', 'covering-design-13-7-4'];
    for (const id of ids) {
      const r = await run(await problemWith(`witness.${id}`), '{}');
      expect(r.result).toBe('rejected');
      expect(r.witness?.reason).toContain('missing the key');
    }
  });

  test('an invalid witness is rejected with the verifier reason', async () => {
    const r = await run(await problemWith('witness.cap-set-f3-7'), JSON.stringify({ points: [[0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2]] }));
    expect(r.result).toBe('rejected');
    expect(r.summary).toBe('Invalid: points 0, 1, 2 are collinear (sum to 0 mod 3): (0,0,0,0,0,0,0), (1,1,1,1,1,1,1), (2,2,2,2,2,2,2)');
    expect(r.witness).toEqual({ valid: false, best_known: 236, beats_best_known: false, ties_best_known: false, reason: expect.stringContaining('collinear') });
  });

  test('missing and malformed witness.json are rejected', async () => {
    const p = await problemWith('witness.cap-set-f3-7');
    const missing = await run(p, null);
    expect(missing.result).toBe('rejected');
    expect(missing.summary).toContain('witness.json is missing');
    const bad = await run(p, '{not json');
    expect(bad.result).toBe('rejected');
    expect(bad.summary).toContain('not valid JSON');
  });

  test('an unknown verifier is an error, not a rejection', async () => {
    const p = await problemWith('witness.cap-set-f3-7');
    p.witness!.verifier = 'nope';
    const r = await run(p, '{}');
    expect(r.result).toBe('error');
    expect(r.summary).toContain('no verifier "nope"');
    p.witness!.verifier = '../x';
    expect((await run(p, '{}')).summary).toContain('invalid verifier name');
  });

  test('bun frontier check end to end on a fixture attempt', async () => {
    const repo = join(tmp, 'repo');
    mkdirSync(join(repo, 'problems'), { recursive: true });
    writeFileSync(join(repo, 'package.json'), '{"name":"x"}');
    const p = await problemWith('witness.cap-set-f3-8', 500);
    writeFileSync(join(repo, 'problems', `${p.id}.yaml`), toYaml(p, Problem));
    const a = attemptStub(p.id);
    const dir = join(repo, 'attempts', p.id, a.id);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, 'attempt.yaml'), toYaml(a));
    writeFileSync(join(dir, 'witness.json'), JSON.stringify(record));
    const out = await checkAttempt(repo, dir);
    if ('invalid' in out) throw new Error(out.invalid.join('\n'));
    expect(out.result.result).toBe('verified');
    expect(out.result.witness?.beats_best_known).toBe(true);
    // and through the real CLI
    const proc = Bun.spawn(['bun', join(root, 'src/cli.ts'), 'check', dir], { cwd: repo, stdout: 'pipe', stderr: 'pipe' });
    const text = await new Response(proc.stdout).text();
    const err = await new Response(proc.stderr).text();
    expect([await proc.exited, err]).toEqual([0, '']);
    expect(text).toContain('verified: Valid witness for witness.cap-set-f3-8 with value 512; beats the best known (500');
  });
});
