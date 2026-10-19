import { describe, expect, test } from 'bun:test';
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { importFormalConjectures } from '../../src/import/formal-conjectures.ts';
import { loadProblems } from '../../src/repo.ts';
import { problemIssues } from '../../src/schema.ts';
import { fixtureWorkspace } from './helpers.ts';

const DATE = '2026-10-18';

function snapshot(root: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const n of readdirSync(join(root, 'problems'))) out[n] = readFileSync(join(root, 'problems', n), 'utf8');
  out['sources'] = readFileSync(join(root, 'sources', 'formal-conjectures.json'), 'utf8');
  return out;
}

describe('importFormalConjectures', () => {
  const { checkout, root } = fixtureWorkspace();
  const run = (date = DATE) => importFormalConjectures({ checkout, root, date });

  test('imports every open declaration, skips solved, and every problem validates', async () => {
    const s = await run();
    expect(s.skipped).toEqual([]);
    expect(s.found).toBe(10);
    expect(s.imported).toBe(10);
    const problems = await loadProblems(root);
    expect(problems).toHaveLength(10);
    for (const p of problems) expect(problemIssues(p)).toEqual([]);
    expect(problems.some((p) => p.lean!.decl === 'Erdos1.erdos_1')).toBe(false);
  });

  test('fills source, lean, title, tags, references', async () => {
    const problems = await loadProblems(root);
    const main = problems.find((p) => p.lean!.decl === 'Erdos1.erdos_1.open_main')!;
    expect(main.id).toBe('erdos1.erdos-1.open-main');
    // Several open main theorems share the file title, so each gets its short name appended.
    expect(main.title).toBe('Erdős Problem 1 (open_main)');
    expect(main.tags).toEqual(['erdos-problems']);
    expect(main.ams).toEqual([5, 11]);
    expect(main.field).toBe('mathematics');
    expect(main.tier).toBe('proof');
    expect(main.upstream_status).toBe('open');
    expect(main.lean!.module).toBe('FormalConjectures.ErdosProblems.«1»');
    expect(main.source.name).toBe('formal-conjectures');
    expect(main.source.licence).toBe('Apache-2.0');
    expect(main.source.path).toBe('FormalConjectures/ErdosProblems/1.lean');
    expect(main.source.url).toMatch(
      /^https:\/\/github\.com\/google-deepmind\/formal-conjectures\/blob\/[0-9a-f]{40}\/FormalConjectures\/ErdosProblems\/1\.lean#L\d+$/,
    );
    expect(main.references.map((r) => r.url)).toEqual([
      'https://www.erdosproblems.com/1',
      'https://example.org/paper_(v2)',
    ]);
    expect(main.statement).toStartWith('The main open statement');
  });

  test('variants get a suffixed title and the variant tag', async () => {
    const problems = await loadProblems(root);
    const v = problems.find((p) => p.lean!.decl === 'Erdos1.erdos_1.variants.weaker')!;
    expect(v.title).toBe('Erdős Problem 1 (variant: weaker)');
    expect(v.tags).toEqual(['erdos-problems', 'variant']);
  });

  test('titles are unique within a file; docstring-less decls get the fixed text', async () => {
    const problems = await loadProblems(root);
    const clash = problems.filter((p) => p.source.path === 'FormalConjectures/GreensOpenProblems/Clash.lean');
    expect(new Set(clash.map((p) => p.title)).size).toBe(clash.length);
    expect(clash.map((p) => p.title)).toContain('Clash (first_one)');
    const noDoc = problems.find((p) => p.lean!.decl === 'Erdos2.erdos_2')!;
    expect(noDoc.statement).toBe('(No informal statement upstream. See the Lean statement.)');
  });

  test('id collisions get -2 in declaration order and are reported', async () => {
    const s = await run();
    const problems = await loadProblems(root);
    const ids = problems.filter((p) => p.lean!.decl === 'Collide.clash').map((p) => p.id).sort();
    expect(ids).toEqual(['collide.clash', 'collide.clash-2']);
    expect(s.collisions).toHaveLength(1);
    expect(s.collisions[0]!.assigned).toBe('collide.clash-2');
    // Files sort by path: GreensOpenProblems/Clash.lean comes before Wikipedia/…, so it owns the plain id.
    const first = problems.find((p) => p.id === 'collide.clash')!;
    expect(first.source.path).toBe('FormalConjectures/GreensOpenProblems/Clash.lean');
  });

  test('writes sources/formal-conjectures.json from the checkout', () => {
    const src = JSON.parse(readFileSync(join(root, 'sources', 'formal-conjectures.json'), 'utf8'));
    expect(Object.keys(src)).toEqual(['repo', 'commit', 'lean_toolchain', 'licence', 'imported_at']);
    expect(src.commit).toMatch(/^[0-9a-f]{40}$/);
    expect(src.lean_toolchain).toBe('leanprover/lean4:v4.33.1');
    expect(src.licence).toBe('Apache-2.0');
    expect(src.imported_at).toBe(DATE);
  });

  test('a rerun, even on another date, leaves every file byte-identical', async () => {
    const before = snapshot(root);
    await run();
    expect(snapshot(root)).toEqual(before);
    await run('2031-01-01');
    expect(snapshot(root)).toEqual(before);
  });

  test('removes stale imported problems but never witness.* or other sources', async () => {
    writeFileSync(join(root, 'problems', 'witness.keep-me.yaml'), 'id: witness.keep-me\n');
    writeFileSync(join(root, 'problems', 'old.gone.yaml'), `id: old.gone\nsource:\n  name: formal-conjectures\nadded: '2020-01-01'\n`);
    writeFileSync(join(root, 'problems', 'other.source.yaml'), `id: other.source\nsource:\n  name: terramind\nadded: '2020-01-01'\n`);
    const s = await run();
    expect(s.removed).toEqual(['old.gone']);
    expect(existsSync(join(root, 'problems', 'old.gone.yaml'))).toBe(false);
    expect(existsSync(join(root, 'problems', 'witness.keep-me.yaml'))).toBe(true);
    expect(existsSync(join(root, 'problems', 'other.source.yaml'))).toBe(true);
  });

  test('an existing problem keeps its added date', async () => {
    const { checkout: c, root: r } = fixtureWorkspace();
    await importFormalConjectures({ checkout: c, root: r, date: '2026-01-02' });
    const s = await importFormalConjectures({ checkout: c, root: r, date: '2026-12-31' });
    expect(s.imported).toBe(10);
    const added = new Set((await loadProblems(r)).map((p) => p.added));
    expect([...added]).toEqual(['2026-01-02']);
  });

  test('problems that use an upstream sorry definition get the answer-required tag', async () => {
    const { checkout: c, root: r } = fixtureWorkspace();
    mkdirSync(join(c, 'FormalConjectures', 'Answer'));
    cpSync(join(import.meta.dir, '..', 'fixtures', 'import', 'answer', 'Answer.lean'), join(c, 'FormalConjectures', 'Answer', 'Answer.lean'));
    await importFormalConjectures({ checkout: c, root: r, date: DATE });
    const tags = Object.fromEntries((await loadProblems(r)).filter((p) => p.lean!.decl.startsWith('AnswerFix.')).map((p) => [p.lean!.decl, p.tags]));
    expect(tags['AnswerFix.erdos_9.parts.i']).toEqual(['answer', 'answer-required']);
    expect(tags['AnswerFix.Inner.uses_relative']).toEqual(['answer', 'answer-required']);
    expect(tags['AnswerFix.Inner.uses_real']).toEqual(['answer']);
    expect(tags['AnswerFix.ignores_unused']).toEqual(['answer']);
    const others = (await loadProblems(r)).filter((p) => !p.lean!.decl.startsWith('AnswerFix.'));
    expect(others.some((p) => p.tags.includes('answer-required'))).toBe(false);
  });
});
