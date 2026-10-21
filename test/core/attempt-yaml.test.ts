import { describe, expect, test } from 'bun:test';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { scaffoldAttempt } from '../../src/commands/new.ts';
import { validateAttemptDir } from '../../src/commands/validate.ts';
import { loadProblem, scanAttempts, toYaml, yamlErrorMessage } from '../../src/repo.ts';
import { PLACEHOLDER_CLAIM } from '../../src/schema.ts';
import { confirmDeclarations, copyFixture } from './helpers.ts';

const SENTENCE = 'We prove: for every odd n, φ(2n) = φ(n) # not a comment - "quoted" and a backslash \\ too.';

async function scaffold() {
  const root = copyFixture('good');
  const problem = (await loadProblem('toy.open-two', root))!;
  const { dir } = await scaffoldAttempt({ root, problem, kind: 'proof', login: 'zed', models: [{ name: 'm', provider: 'p', role: 'author' }] });
  return { root, dir, file: join(dir, 'attempt.yaml') };
}

async function scanned(root: string, dir: string) {
  return (await scanAttempts(undefined, root)).find((a) => a.dir === dir)!;
}

describe('attempt.yaml claim and title are double-quoted', () => {
  test('new writes title and claim as double-quoted scalars', async () => {
    const { file } = await scaffold();
    const text = readFileSync(file, 'utf8');
    expect(text).toContain(`claim: "${PLACEHOLDER_CLAIM}"\n`);
    expect(text).toMatch(/^title: "[^"\n]+"$/m);
  });

  test('a sentence with ": " typed inside the quotes stays valid YAML', async () => {
    const { root, dir, file } = await scaffold();
    // What an agent does: replace the text between the quotes, escaping only " and \ as the hint says.
    const escaped = SENTENCE.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
    writeFileSync(file, readFileSync(file, 'utf8').replace(PLACEHOLDER_CLAIM, escaped).replace(/^title: "[^"\n]*"$/m, 'title: "Proof: the odd case"'));
    confirmDeclarations(dir);
    const a = await scanned(root, dir);
    expect(a.errors).toEqual([]);
    expect(a.value!.claim).toBe(SENTENCE);
    expect(a.value!.title).toBe('Proof: the odd case');
    expect(await validateAttemptDir(root, dir)).toEqual([]);
  });

  test('a plain sentence with ": " needs no escaping inside the quotes', async () => {
    const { root, dir, file } = await scaffold();
    writeFileSync(file, readFileSync(file, 'utf8').replace(PLACEHOLDER_CLAIM, 'Proof checked: the statement holds for all odd n.'));
    confirmDeclarations(dir);
    expect((await scanned(root, dir)).value!.claim).toBe('Proof checked: the statement holds for all odd n.');
  });

  test('an unquoted claim with ": " fails with a hint to wrap it in double quotes', async () => {
    const { root, dir, file } = await scaffold();
    writeFileSync(file, readFileSync(file, 'utf8').replace(/^claim: .*$/m, 'claim: We prove: the odd case.'));
    const a = await scanned(root, dir);
    expect(a.value).toBeNull();
    expect(a.errors.join('\n')).toContain('wrap the claim in double quotes');
    const issues = await validateAttemptDir(root, dir);
    expect(issues.map((i) => i.message).join('\n')).toContain('wrap the claim in double quotes');
  });

  test('an unescaped " inside the quoted title gets the hint for the title', async () => {
    const { root, dir, file } = await scaffold();
    writeFileSync(file, readFileSync(file, 'utf8').replace(/^title: .*$/m, 'title: "The "odd" case"'));
    expect((await scanned(root, dir)).errors.join('\n')).toContain('wrap the title in double quotes');
  });

  test('errors elsewhere get no claim hint', () => {
    const text = 'schema: 1\nkind: proof: x\nclaim: "x"\n';
    let err: Error | undefined;
    try {
      parseYaml(text);
    } catch (e) {
      err = e as Error;
    }
    expect(err).toBeDefined();
    expect(yamlErrorMessage(text, err!)).not.toContain('Hint');
  });

  test('round trip: toYaml of an attempt quotes claim and title and parses back to the same value', () => {
    const attempt = { schema: 1, id: 'x', problem: 'p', kind: 'proof', title: 'A: b', claim: 'line one: "q"\nline two \\', files: ['solution.lean'] };
    const text = toYaml(attempt);
    expect(text).toContain('title: "A: b"\n');
    expect(text).toContain('claim: "line one: \\"q\\"\\nline two \\\\"\n');
    expect(parseYaml(text)).toEqual(attempt);
  });

  test('other records keep plain scalars (problems are not re-quoted)', () => {
    const text = toYaml({ id: 'toy.x', title: 'Plain title', tier: 'proof', statement: 's' });
    expect(text).toContain('title: Plain title\n');
  });
});
