import { afterAll, describe, expect, test } from 'bun:test';
import { mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { main } from '../../../src/cli.ts';
import { diagnose, formatDiagnosis } from '../../../src/commands/diagnose.ts';
import { repoRoot } from '../../../src/repo.ts';
import { fixture } from './helpers.ts';

const root = repoRoot();
const tmp = realpathSync(mkdtempSync(join(tmpdir(), 'frontier-diagnose-'))); // realpath: macOS /var is a symlink
afterAll(() => rmSync(tmp, { recursive: true, force: true }));

let counter = 0;
/** A witness.json in a fresh directory; with `problem` the directory also gets an attempt.yaml naming it. */
function witnessDir(witness: unknown, problem?: string): string {
  const dir = join(tmp, `w${counter++}`);
  mkdirSync(dir);
  writeFileSync(join(dir, 'witness.json'), typeof witness === 'string' ? witness : JSON.stringify(witness));
  if (problem) writeFileSync(join(dir, 'attempt.yaml'), `schema: 1\nid: x\nproblem: ${problem}\n`);
  return dir;
}

/** Run the CLI in the repo, capturing console output. */
async function cli(...argv: string[]): Promise<{ code: number; out: string }> {
  const out: string[] = [];
  const [log, err] = [console.log, console.error];
  console.log = (...a) => void out.push(a.join(' '));
  console.error = (...a) => void out.push(a.join(' '));
  try {
    return { code: await main(argv), out: out.join('\n') };
  } finally {
    console.log = log;
    console.error = err;
  }
}

const GOLOMB = 'witness.golomb-ruler-29';
const RECORD_29 = [0, 7, 11, 31, 43, 53, 100, 121, 144, 150, 202, 220, 229, 268, 284, 285, 356, 371, 390, 416, 430, 465, 467, 528, 582, 590, 595, 620, 623];

describe('diagnose', () => {
  test('a valid witness: value, valid, and how it compares with the best known value', async () => {
    const d = await diagnose(root, witnessDir({ marks: RECORD_29 }), GOLOMB);
    expect(d).toMatchObject({ problem: GOLOMB, verifier: 'golomb', valid: true, value: 623, best_known: 623, objective: 'minimize' });
    expect(d).toMatchObject({ ties_best_known: true, beats_best_known: false, violations: [], omitted: 0, truncated: false });
    const text = formatDiagnosis(d);
    expect(text).toContain('value:    623 (best known 623, lower is better)');
    expect(text).toContain('valid:    yes');
    expect(text).toContain('ties the best known value');
  });

  test('a valid witness better than the stored best known value says so; a worse one says that', async () => {
    // a copy of the repository's problem with a weaker record, so that the real 623 ruler beats it
    const copy = join(tmp, 'repo');
    mkdirSync(join(copy, 'problems'), { recursive: true });
    const original = readFileSync(join(root, 'problems', `${GOLOMB}.yaml`), 'utf8');
    expect(original).toContain('    value: 623\n');
    writeFileSync(join(copy, 'problems', `${GOLOMB}.yaml`), original.replace('    value: 623\n', '    value: 700\n'));
    const beats = await diagnose(copy, witnessDir({ marks: RECORD_29 }), GOLOMB);
    expect(beats).toMatchObject({ valid: true, value: 623, best_known: 700, beats_best_known: true, ties_best_known: false });
    expect(formatDiagnosis(beats)).toContain('beats the best known value');
    writeFileSync(join(copy, 'problems', `${GOLOMB}.yaml`), original.replace('    value: 623\n', '    value: 600\n'));
    const worse = await diagnose(copy, witnessDir({ marks: RECORD_29 }), GOLOMB);
    expect(worse).toMatchObject({ valid: true, beats_best_known: false, ties_best_known: false });
    expect(formatDiagnosis(worse)).toContain('does not reach the best known value');
  });

  test('the 512-point cap set is valid for its problem', async () => {
    const d = await diagnose(root, witnessDir(fixture('cap-set-f3-8-size512.json')), 'witness.cap-set-f3-8');
    expect(d).toMatchObject({ valid: true, value: 512, ties_best_known: true, beats_best_known: false, objective: 'maximize' });
  });

  test('every violation is listed: a 29-mark ruler 0..28 repeats almost every difference', async () => {
    const d = await diagnose(root, witnessDir({ marks: Array.from({ length: 29 }, (_, i) => i) }), GOLOMB);
    expect(d.valid).toBe(false);
    expect(d.value).toBe(28);
    // differences 1..28 occur 28, 27, ..., 1 times; every occurrence after the first is a violation
    const expected = Array.from({ length: 28 }, (_, i) => i).reduce((a, b) => a + b, 0);
    expect(d.violations.length + d.omitted).toBe(expected);
    expect(d.violations).toHaveLength(200);
    expect(d.omitted).toBe(expected - 200);
    const text = formatDiagnosis(d);
    expect(text).toContain(`violations (${expected}):`);
    expect(text).toContain('  1. difference 1 occurs twice: 1 - 0 and 2 - 1');
    expect(text).toContain(`and ${expected - 200} more not listed`);
  });

  test('a small number of violations is listed one by one with no tail', async () => {
    const marks = [...RECORD_29];
    marks[28] = 622; // moving the last mark breaks some number of differences; count them independently below
    const d = await diagnose(root, witnessDir({ marks }), GOLOMB);
    const seen = new Set<number>();
    let repeats = 0;
    for (let i = 0; i < 29; i++) for (let j = i + 1; j < 29; j++) (seen.has(marks[j]! - marks[i]!) ? repeats++ : seen.add(marks[j]! - marks[i]!));
    expect(d.violations).toHaveLength(repeats);
    expect(d.valid).toBe(repeats === 0);
    expect(d.omitted).toBe(0);
  });

  test('--problem can be left out for an attempt directory, and a conflicting one is refused', async () => {
    const dir = witnessDir({ marks: RECORD_29 }, GOLOMB);
    expect((await diagnose(root, dir, undefined)).problem).toBe(GOLOMB);
    await expect(diagnose(root, dir, 'witness.schur-7')).rejects.toThrow('differs from the problem in attempt.yaml');
  });

  test('a bare witness.json file works, and --problem is needed for it', async () => {
    const dir = witnessDir({ colors: [0, 1, 1, 0, 0] });
    const file = join(dir, 'witness.json');
    const d = await diagnose(root, file, 'witness.schur-7');
    expect(d).toMatchObject({ valid: false, value: 5 });
    expect(d.violations).toEqual(['1 + 4 = 5 all have colour 0']);
    await expect(diagnose(root, file, undefined)).rejects.toThrow('needs --problem');
  });

  test('a witness in the wrong shape gives its one reason; unreadable JSON is reported, not thrown', async () => {
    const shape = await diagnose(root, witnessDir({ points: [] }), GOLOMB);
    expect(shape.valid).toBe(false);
    expect(shape.value).toBeNull();
    expect(shape.violations).toEqual(['witness.json is missing the key "marks"']);
    const bad = await diagnose(root, witnessDir('{not json'), GOLOMB);
    expect(bad.violations[0]).toContain('witness.json is not valid JSON');
    expect(formatDiagnosis(bad)).toContain('value:    not available');
  });

  test('an unknown problem, a non-witness problem and a missing path are errors', async () => {
    const dir = witnessDir({ marks: [] });
    await expect(diagnose(root, dir, 'witness.nope')).rejects.toThrow('no problem with id witness.nope');
    await expect(diagnose(root, dir, 'erdos1.erdos_1.variants.weaker')).rejects.toThrow();
    await expect(diagnose(root, join(tmp, 'missing'), GOLOMB)).rejects.toThrow('does not exist');
    const empty = join(tmp, 'empty');
    mkdirSync(empty);
    await expect(diagnose(root, empty, GOLOMB)).rejects.toThrow('has no witness.json');
  });

  test('every witness problem in the repository has a verifier that accepts the all option', async () => {
    const { loadProblems } = await import('../../../src/repo.ts');
    const witnessProblems = (await loadProblems(root)).filter((p) => p.tier === 'witness');
    expect(witnessProblems).toHaveLength(14);
    for (const p of witnessProblems) {
      expect(['approachable', 'hard', 'very-hard'].includes(p.difficulty?.level ?? '')).toBe(true);
      expect(p.difficulty!.note.length).toBeGreaterThan(20);
    }
    for (const p of witnessProblems) {
      const d = await diagnose(root, witnessDir({}), p.id);
      expect(d.valid).toBe(false);
      expect(d.violations.length).toBeGreaterThan(0);
      expect(d.verifier).toBe(p.witness!.verifier);
    }
  });
});

describe('frontier diagnose (command line)', () => {
  test('prints the text report and exits 0 for an invalid witness', async () => {
    const r = await cli('diagnose', witnessDir({ marks: [0, 1, 2, 3, 4] }), '--problem', GOLOMB);
    expect(r.code).toBe(0);
    expect(r.out).toContain('valid:    no');
    expect(r.out).toContain('"marks" has 5 entries, expected exactly 29');
  });

  test('--json prints the same data as a JSON object', async () => {
    const r = await cli('diagnose', witnessDir({ marks: RECORD_29 }), '--problem', GOLOMB, '--json');
    expect(r.code).toBe(0);
    expect(JSON.parse(r.out)).toMatchObject({ problem: GOLOMB, valid: true, value: 623, violations: [] });
  });

  test('a usage mistake exits 2 and an unknown problem exits 1', async () => {
    expect((await cli('diagnose')).code).toBe(2);
    const r = await cli('diagnose', witnessDir({}), '--problem', 'witness.nope');
    expect(r.code).toBe(1);
    expect(r.out).toContain('no problem with id witness.nope');
  });

  test('--help is listed with the other commands', async () => {
    const r = await cli('diagnose', '--help');
    expect(r.code).toBe(0);
    expect(r.out).toContain('Usage: bun frontier diagnose');
  });
});
