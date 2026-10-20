import { describe, expect, test } from 'bun:test';
import { cpSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { capText, DEFINITION_MAX_CHARS, importFormalConjectures } from '../../src/import/formal-conjectures.ts';
import { parseLeanFile, referencedDefs, usedNotation } from '../../src/import/lean-parse.ts';
import { loadProblems } from '../../src/repo.ts';
import { fixtureWorkspace } from './helpers.ts';

const FILE = join(import.meta.dir, '..', 'fixtures', 'import', 'context', 'Context.lean');
const parsed = parseLeanFile(readFileSync(FILE, 'utf8'));
const decl = (name: string) => parsed.decls.find((d) => d.fullName === name)!;
const NOTATION = 'local notation "!" n => lf n';

describe('lean.context', () => {
  test('enclosing namespace, upstream opens in file order, `open … in` before it, local notation', () => {
    expect(decl('Ctx.uses_all').context).toEqual([
      'open Ctx',
      'open Filter',
      'open scoped Nat',
      'open scoped Classical',
      NOTATION,
    ]);
  });

  test('an `open … in` applies to the next command only', () => {
    expect(decl('Ctx.not_this_one').context).toEqual(['open Ctx', 'open Filter', 'open scoped Nat', 'open Finset', NOTATION]);
    expect(decl('Ctx.erdos_9.variants.short').context).not.toContain('open scoped Classical');
  });

  test('a dotted declaration name opens its prefixes too (Lean elaborates it inside them)', () => {
    expect(decl('Ctx.erdos_9.variants.short').context.slice(0, 3)).toEqual([
      'open Ctx',
      'open Ctx.erdos_9',
      'open Ctx.erdos_9.variants',
    ]);
  });

  test('nested dotted namespaces open outermost first; opens inside them count', () => {
    expect(decl('Ctx.Inner.Deep.deep').context).toEqual([
      'open Ctx',
      'open Ctx.Inner',
      'open Ctx.Inner.Deep',
      'open Filter',
      'open scoped Nat',
      'open Topology',
      NOTATION,
    ]);
  });

  test('opens and local notation of a closed section, and global or scoped notation, are left out', () => {
    for (const d of parsed.decls) {
      expect(d.context).not.toContain('open Real');
      expect(d.context.some((l) => l.includes('gone') || l.includes('GLOBAL') || l.includes('SCOPED'))).toBe(false);
    }
  });

  test('multi-line local notation is kept verbatim, without trailing comments', () => {
    const p = parseLeanFile(
      'namespace N\nlocal notation "F(" s ", " n ")" =>\n  s + n -- trailing\n\n/-- d -/\n@[category research open]\ntheorem t : F(1, 2) = 3 := by\n  sorry\nend N\n',
    );
    expect(p.decls[0]!.context).toEqual(['open N', 'local notation "F(" s ", " n ")" =>\n  s + n']);
  });
});

describe('lean.definitions', () => {
  const names = (n: string) =>
    referencedDefs(decl(n).context, [decl(n).statement, ...usedNotation(decl(n).context, decl(n).statement)], parsed.defs).map((d) => d.fullName);

  test('local notation counts as used when one of its quoted atoms occurs in the statement', () => {
    expect(usedNotation(decl('Ctx.uses_all').context, decl('Ctx.uses_all').statement)).toEqual([NOTATION]);
    expect(usedNotation(decl('Ctx.not_this_one').context, decl('Ctx.not_this_one').statement)).toEqual([]);
  });

  test('collects def, abbrev, structure, inductive and class with full names and kinds', () => {
    expect(parsed.defs.map((d) => [d.fullName, d.kind])).toEqual([
      ['Ctx.lf', 'def'],
      ['Ctx.Pt', 'structure'],
      ['Ctx.Col', 'inductive'],
      ['Ctx.Shape', 'class'],
      ['Ctx.Big', 'abbrev'],
      ['Ctx.erdos_9.answer', 'def'],
      ['Ctx.erdos_10.answer', 'def'],
      ['Ctx.Nat.twice', 'def'],
    ]);
  });

  test('text runs from the doc comment (or attribute) to the end of the declaration', () => {
    const pt = parsed.defs.find((d) => d.ownName === 'Pt')!;
    expect(pt.text).toBe('/-- A point. -/\nstructure Pt where\n  x : ℕ\n  y : ℕ');
    const lines = readFileSync(FILE, 'utf8').split('\n');
    expect(lines[pt.line - 1]).toBe('/-- A point. -/');
    const big = parsed.defs.find((d) => d.ownName === 'Big')!;
    expect(big.text).toBe('@[reducible]\nabbrev Big : ℕ := 5');
  });

  test('referenced by name, through local notation, by field notation; unused ones left out', () => {
    expect(names('Ctx.uses_all')).toEqual(['Ctx.lf', 'Ctx.Pt', 'Ctx.Big', 'Ctx.Nat.twice']);
    expect(names('Ctx.Inner.Deep.deep')).toEqual(['Ctx.Col']);
  });

  test('a shared last segment (`….answer`) matches only the definition actually named', () => {
    expect(names('Ctx.erdos_9.variants.short')).toEqual(['Ctx.erdos_9.answer']);
  });

  test('capText cuts at the limit, marks the cut, and never splits a surrogate pair', () => {
    expect(capText('abc', 5)).toBe('abc');
    expect(capText('abcdef', 3)).toBe('abc…');
    expect(capText('ab𝓟cd', 3)).toBe('ab…');
    expect(DEFINITION_MAX_CHARS).toBe(4000);
  });
});

describe('import writes context and definitions', () => {
  test('fields, permalinks with #L, and the 4,000-character cap', async () => {
    const { checkout, root } = fixtureWorkspace();
    mkdirSync(join(checkout, 'FormalConjectures', 'Ctx'));
    cpSync(FILE, join(checkout, 'FormalConjectures', 'Ctx', 'Context.lean'));
    await importFormalConjectures({ checkout, root, date: '2026-10-18', practice: [] });
    const all = await loadProblems(root);
    const p = all.find((x) => x.lean!.decl === 'Ctx.uses_all')!;
    expect(p.lean!.context).toEqual(decl('Ctx.uses_all').context);
    expect(p.lean!.definitions.map((d) => d.name)).toEqual(['Ctx.lf', 'Ctx.Pt', 'Ctx.Big', 'Ctx.Nat.twice']);
    const lf = p.lean!.definitions[0]!;
    expect(lf.kind).toBe('def');
    expect(lf.text).toBe('/-- Left factorial (a stand-in). -/\ndef lf (n : ℕ) : ℕ := n');
    expect(lf.url).toMatch(/^https:\/\/github\.com\/google-deepmind\/formal-conjectures\/blob\/[0-9a-f]{40}\/FormalConjectures\/Ctx\/Context\.lean#L13$/);
    // Fixture problems without notation or opens still get their namespace.
    expect(all.find((x) => x.lean!.decl === 'Erdos2.erdos_2')!.lean!.context).toEqual(['open Erdos2']);
    expect(all.every((x) => x.lean!.definitions.every((d) => d.text.length <= DEFINITION_MAX_CHARS + 1))).toBe(true);
  });
});
