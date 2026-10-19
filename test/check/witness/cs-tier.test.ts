import { afterAll, describe, expect, test } from 'bun:test';
import { mkdirSync, mkdtempSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { checkAttempt } from '../../../src/commands/check.ts';
import { loadProblem, repoRoot, toYaml } from '../../../src/repo.ts';
import { Problem } from '../../../src/schema.ts';
import type { Attempt } from '../../../src/schema.ts';
import { batcher, greedySuperpermutation, kronecker, schoolbook, STRASSEN } from './cs-constructions.ts';

const root = repoRoot();
const tmp = realpathSync(mkdtempSync(join(tmpdir(), 'frontier-cs-witness-'))); // realpath: macOS /var is a symlink
afterAll(() => rmSync(tmp, { recursive: true, force: true }));

const CASES = [
  { id: 'witness.matmul-rank-3x3x3', best: 23, value: 27, witness: { terms: schoolbook(3) } },
  { id: 'witness.matmul-rank-4x4x4', best: 48, value: 49, witness: { terms: kronecker(STRASSEN, STRASSEN) } },
  { id: 'witness.matmul-rank-5x5x5', best: 93, value: 125, witness: { terms: schoolbook(5) } },
  { id: 'witness.sorting-network-size-13', best: 45, value: batcher(13).length, witness: { comparators: batcher(13) } },
  { id: 'witness.sorting-network-size-18', best: 77, value: batcher(18).length, witness: { comparators: batcher(18) } },
  { id: 'witness.superpermutation-7', best: 5905, value: greedySuperpermutation(7).length, witness: { word: greedySuperpermutation(7) } },
];

function attemptStub(problem: string): Attempt {
  return {
    schema: 1, id: '20261019-tester-abc123', problem, kind: 'witness', title: 't', claim: 'c',
    files: ['attempt.yaml', 'witness.json'], submitter: { github: 'tester' }, people: [], models: [], mode: 'human_only',
    created: '2026-10-19', licence: 'CC-BY-4.0', declarations: { rights: true, disclosure_complete: true },
  } as Attempt;
}

let counter = 0;
/** A scratch repo holding one shipped problem (best_known optionally replaced) and one attempt with this witness.json. */
async function scratchAttempt(id: string, witness: unknown, bestKnown?: number): Promise<{ repo: string; dir: string }> {
  const repo = join(tmp, `repo${counter++}`);
  mkdirSync(join(repo, 'problems'), { recursive: true });
  writeFileSync(join(repo, 'package.json'), '{"name":"x"}');
  const p = (await loadProblem(id, root))!;
  if (bestKnown !== undefined) p.witness!.best_known.value = bestKnown;
  writeFileSync(join(repo, 'problems', `${p.id}.yaml`), toYaml(p, Problem));
  const a = attemptStub(id);
  const dir = join(repo, 'attempts', id, a.id);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'attempt.yaml'), toYaml(a));
  writeFileSync(join(dir, 'witness.json'), JSON.stringify(witness));
  return { repo, dir };
}

describe('computer-science witness problems, end to end', () => {
  for (const c of CASES) {
    test(`${c.id}: a valid longer witness is verified and does not reach the best known ${c.best}`, async () => {
      const { repo, dir } = await scratchAttempt(c.id, c.witness);
      const out = await checkAttempt(repo, dir);
      if ('invalid' in out) throw new Error(out.invalid.join('\n'));
      expect(out.result.result).toBe('verified');
      expect(out.result.witness).toEqual({ valid: true, value: c.value, best_known: c.best, beats_best_known: false, ties_best_known: false });
    });

    test(`${c.id}: the same witness beats a worse best known, through the real CLI`, async () => {
      const { repo, dir } = await scratchAttempt(c.id, c.witness, c.value + 1);
      const proc = Bun.spawn(['bun', join(root, 'src/cli.ts'), 'check', dir], { cwd: repo, stdout: 'pipe', stderr: 'pipe' });
      const text = await new Response(proc.stdout).text();
      const err = await new Response(proc.stderr).text();
      expect([await proc.exited, err]).toEqual([0, '']);
      expect(text).toContain(`verified: Valid witness for ${c.id} with value ${c.value}; beats the best known (${c.value + 1}`);
    });

    test(`${c.id}: an empty object is rejected with a reason`, async () => {
      const { repo, dir } = await scratchAttempt(c.id, {});
      const out = await checkAttempt(repo, dir);
      if ('invalid' in out) throw new Error(out.invalid.join('\n'));
      expect(out.result.result).toBe('rejected');
      expect(out.result.witness?.reason).toContain('missing the key');
    });
  }

  test('an invalid witness is rejected with the verifier reason and the best known value', async () => {
    const { repo, dir } = await scratchAttempt('witness.sorting-network-size-13', { comparators: batcher(13).slice(0, -1) });
    const out = await checkAttempt(repo, dir);
    if ('invalid' in out) throw new Error(out.invalid.join('\n'));
    expect(out.result.result).toBe('rejected');
    expect(out.result.summary).toContain('Invalid: the network does not sort the 0-1 input');
    expect(out.result.witness).toMatchObject({ valid: false, best_known: 45, beats_best_known: false });
  });
});
