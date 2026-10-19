import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { extractReferences, kebab, moduleName } from '../../src/import/formal-conjectures.ts';
import { parseLeanFile, referencesSorryDef } from '../../src/import/lean-parse.ts';
import { FIXTURE } from './helpers.ts';

const read = (p: string) => readFileSync(join(FIXTURE, 'FormalConjectures', p), 'utf8');

describe('parseLeanFile', () => {
  const file = parseLeanFile(read('ErdosProblems/1.lean'));
  const by = (name: string) => file.decls.find((d) => d.fullName === name)!;

  test('takes the title from the first module doc', () => {
    expect(file.title).toBe('Erdős Problem 1');
  });

  test('skips solved declarations and keeps open ones in order', () => {
    expect(file.decls.map((d) => d.fullName)).toEqual([
      'Erdos1.erdos_1.open_main',
      'Erdos1.erdos_1.variants.weaker',
      'Erdos1.Inner.Deeper.deep_lemma',
      'Erdos1.after_section',
    ]);
  });

  test('cuts the statement at the proof `:=`, not at the one in a binder default', () => {
    expect(by('Erdos1.erdos_1.open_main').statement).toBe('theorem erdos_1.open_main : ∃ C > (0 : ℝ), C * 2 = 3');
    expect(by('Erdos1.Inner.Deeper.deep_lemma').statement).toBe('lemma deep_lemma (n : ℕ) (h : n = (n : ℕ) := rfl) : n = n');
    expect(by('Erdos1.Inner.Deeper.deep_lemma').keyword).toBe('lemma');
  });

  test('records the line of the theorem keyword, with a multi-line attribute before it', () => {
    const lines = read('ErdosProblems/1.lean').split('\n');
    for (const d of file.decls) expect(lines[d.line - 1]).toMatch(new RegExp(`^(theorem|lemma) ${d.ownName.replace(/\./g, '\\.')}`));
  });

  test('an attribute with ] inside a string still parses', () => {
    expect(by('Erdos1.erdos_1.variants.weaker').ams).toEqual([5, 11]);
  });

  test('docstring is dedented, kept as written, and found across plain comments', () => {
    expect(by('Erdos1.erdos_1.open_main').docstring).toBe(
      'The main open statement, with $x \\le y$ in LaTeX.\nQuote: "a := b" inside a docstring.',
    );
    expect(by('Erdos1.after_section').docstring).toBe(
      'Docstring separated from the attribute by a comment.',
    );
  });

  test('section does not add to names, nested dotted namespace adds both parts', () => {
    expect(by('Erdos1.Inner.Deeper.deep_lemma').ams).toEqual([11, 5]);
  });

  test('a decl without a docstring has none; `let` and structure instances do not end the statement', () => {
    const f2 = parseLeanFile(read('ErdosProblems/2.lean'));
    expect(f2.decls[0]!.docstring).toBeNull();
    expect(f2.decls[0]!.statement).toBe('theorem erdos_2 : let N := 5\n    N = 5 ∧ ({ val := 1 } : Fin 2) = 1');
  });

  test('«» names stay as written', () => {
    const f2 = parseLeanFile(read('ErdosProblems/2.lean'));
    expect(f2.decls[1]!.fullName).toBe('Erdos2.«weird name».«inner»');
    expect(f2.decls[1]!.statement).toBe('theorem «weird name».«inner» (f : ℕ → ℕ := id) : f = f');
  });

  test('module docs before the declaration are attached', () => {
    expect(by('Erdos1.erdos_1.open_main').moduleDocs).toHaveLength(1);
  });
});

describe('helpers', () => {
  test('moduleName wraps non-identifier components', () => {
    expect(moduleName('FormalConjectures/ErdosProblems/1.lean')).toBe('FormalConjectures.ErdosProblems.«1»');
    expect(moduleName('FormalConjectures/Wikipedia/1-3_to_2-3.lean')).toBe('FormalConjectures.Wikipedia.«1-3_to_2-3»');
    expect(moduleName('FormalConjectures/Wikipedia/Collatz.lean')).toBe('FormalConjectures.Wikipedia.Collatz');
  });

  test('kebab', () => {
    expect(kebab('ErdosProblems')).toBe('erdos-problems');
    expect(kebab('OEIS')).toBe('oeis');
    expect(kebab('GreensOpenProblems')).toBe('greens-open-problems');
    expect(kebab('WrittenOnTheWallII')).toBe('written-on-the-wall-ii');
  });

  test('extractReferences dedupes by url, keeps order, handles parentheses and bare references', () => {
    const refs = extractReferences([
      'See [a](https://x.org/a_(v2)) and [b](https://x.org/b).',
      '[again](https://x.org/a_(v2)) *Reference:* https://en.wikipedia.org/wiki/Foo.\n[rel](docs/x.md)',
    ]);
    expect(refs).toEqual([
      { label: 'a', url: 'https://x.org/a_(v2)' },
      { label: 'b', url: 'https://x.org/b' },
      { label: 'https://en.wikipedia.org/wiki/Foo', url: 'https://en.wikipedia.org/wiki/Foo' },
    ]);
  });
});

describe('sorry definitions', () => {
  const parsed = parseLeanFile(readFileSync(join(import.meta.dir, '..', 'fixtures', 'import', 'answer', 'Answer.lean'), 'utf8'));
  const decl = (name: string) => parsed.decls.find((d) => d.fullName === name)!;
  const tagged = (name: string) => referencesSorryDef(decl(name), parsed.sorryDefs);

  test('collects defs and abbrevs whose body is exactly sorry, with full names', () => {
    expect(parsed.sorryDefs.map((d) => d.fullName)).toEqual([
      'AnswerFix.unused',
      'AnswerFix.erdos_9.parts.i.answer',
      'AnswerFix.Inner.guess',
    ]);
    expect(parsed.sorryDefs[1]!.ownName).toBe('erdos_9.parts.i.answer');
  });

  test('a def with a real body is not collected', () => {
    expect(parsed.sorryDefs.some((d) => d.fullName.endsWith('realBody'))).toBe(false);
  });

  test('a direct .answer def is referenced by its written name', () => {
    expect(tagged('AnswerFix.erdos_9.parts.i')).toBe(true);
  });

  test('a namespace-relative reference and a full-name reference both match', () => {
    expect(tagged('AnswerFix.Inner.uses_relative')).toBe(true);
    expect(tagged('AnswerFix.Inner.uses_via_outer')).toBe(true);
  });

  test('unreferenced sorry defs, real bodies and look-alike names do not match', () => {
    expect(tagged('AnswerFix.Inner.uses_real')).toBe(false);
    expect(tagged('AnswerFix.ignores_unused')).toBe(false);
    expect(tagged('AnswerFix.not_a_prefix')).toBe(false);
  });
});
