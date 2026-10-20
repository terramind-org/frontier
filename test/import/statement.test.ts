import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { solutionDeclaration } from '../../src/commands/new.ts';
import { parseLeanFile, proofStart, statementEnd } from '../../src/import/lean-parse.ts';
import { loadProblems, repoRoot } from '../../src/repo.ts';

const FIXTURES = join(import.meta.dir, '..', 'fixtures', 'import');

/** Statement of `theorem t …` cut by the parser (no comments in these snippets). */
const cut = (src: string) => src.slice(0, statementEnd(src, 0)).trim();

describe('statementEnd skips binder `:=`', () => {
  test('let, letI, have, haveI, let_fun and set binders at depth 0', () => {
    expect(cut('theorem t : let a := 1\n  a = 1 := by rfl')).toBe('theorem t : let a := 1\n  a = 1');
    expect(cut('theorem t : letI k := 2\n  k = 2 := by rfl')).toBe('theorem t : letI k := 2\n  k = 2');
    expect(cut('theorem t : letI : Fact p := ⟨h⟩\n  P := by sorry')).toBe('theorem t : letI : Fact p := ⟨h⟩\n  P');
    expect(cut('theorem t : have h : 1 = 1 := rfl; True := trivial')).toBe('theorem t : have h : 1 = 1 := rfl; True');
    expect(cut('theorem t : haveI := inst; P := by sorry')).toBe('theorem t : haveI := inst; P');
    expect(cut('theorem t : let_fun x := 1; x = 1 := rfl')).toBe('theorem t : let_fun x := 1; x = 1');
    expect(cut('theorem t : set x := 1 with hx; x = 1 := rfl')).toBe('theorem t : set x := 1 with hx; x = 1');
  });

  test('several binders in a row, and binders with a type ascription', () => {
    expect(cut('theorem t : letI a := 1; letI b : ℕ := 2\n  a + b = 3 := by decide')).toBe(
      'theorem t : letI a := 1; letI b : ℕ := 2\n  a + b = 3',
    );
  });

  test('names that only start like a binder keyword are not binders', () => {
    expect(cut('theorem t (letter : ℕ) : letter = letter := rfl')).toBe('theorem t (letter : ℕ) : letter = letter');
    expect(cut('theorem t (haveIt : P) : P := haveIt')).toBe('theorem t (haveIt : P) : P');
    expect(cut('theorem t : x.let = 1 := rfl')).toBe('theorem t : x.let = 1');
    // A variable called `set` (no name after it) is not a `set` binder.
    expect(cut('theorem t (set : Finset ℕ) : set = set := rfl')).toBe('theorem t (set : Finset ℕ) : set = set');
  });

  test('structure-instance fields and binder defaults sit inside brackets', () => {
    expect(cut('theorem t : ({ val := 1 } : Fin 2) = 1 := rfl')).toBe('theorem t : ({ val := 1 } : Fin 2) = 1');
    expect(cut('theorem t : ({ p with x := 2 } : Pt).x = 2 := rfl')).toBe('theorem t : ({ p with x := 2 } : Pt).x = 2');
    expect(cut('theorem t (h : n = n := rfl) : n = n := h')).toBe('theorem t (h : n = n := rfl) : n = n');
  });

  test('a depth-0 `where` body ends the statement; its field `:=`s are not used', () => {
    expect(cut('theorem t : Nonempty ℕ ∧ True where\n  left := ⟨0⟩\n  right := trivial')).toBe('theorem t : Nonempty ℕ ∧ True');
    expect(cut('theorem t (somewhere : ℕ) : somewhere = somewhere := rfl')).toBe('theorem t (somewhere : ℕ) : somewhere = somewhere');
  });

  test('no proof: throws; proofStart returns null and ignores comments', () => {
    expect(() => statementEnd('theorem t : True', 0)).toThrow();
    expect(proofStart('theorem t : True')).toBeNull();
    const src = 'theorem t : -- a note with := inside\n  letI k := 2\n  k = 2 := by rfl';
    expect(src.slice(0, proofStart(src)!).trim()).toBe('theorem t : -- a note with := inside\n  letI k := 2\n  k = 2');
  });
});

describe('the statements once truncated at a binder (cycle-3 fix list, item 2)', () => {
  const parsed = parseLeanFile(readFileSync(join(FIXTURES, 'truncated', 'Truncated.lean'), 'utf8'));
  const expected = JSON.parse(readFileSync(join(FIXTURES, 'truncated', 'expected.json'), 'utf8')) as Record<string, string>;

  test('all 11 fixtures parse (the 10 listed ids plus oeisa179537.conjecture4)', () => {
    expect(parsed.decls.map((d) => d.ownName).sort()).toEqual(Object.keys(expected).sort());
    expect(parsed.decls).toHaveLength(11);
  });

  for (const [name, statement] of Object.entries(expected)) {
    test(`${name}: full statement, binder and body kept`, () => {
      const d = parsed.decls.find((x) => x.ownName === name)!;
      expect(d.statement).toBe(statement);
      expect(d.statement).not.toMatch(/(?:let|letI|have|haveI)\s+[^\s:]*(?:\s*:[^=]*)?$/);
    });
  }

  test('the scaffold keeps the binder and its value (new.ts cuts the proof the same way)', () => {
    const d = parsed.decls.find((x) => x.ownName === 'erdos_727.variants.k_2')!;
    expect(solutionDeclaration(d.statement, false)).toBe(
      'theorem solution : letI k := 2\n    Set.Infinite {n : ℕ | (Nat.factorial (n + k)) ^ 2 ∣ Nat.factorial (2 * n)}',
    );
    expect(solutionDeclaration(`${d.statement} := by\n  sorry`, false)).toBe(solutionDeclaration(d.statement, false));
  });
});

/** True when the brackets of a Lean statement (comments removed) are balanced and properly nested. */
function balanced(s: string): boolean {
  const text = s.replace(/--[^\n]*/g, '').replace(/"(?:[^"\\]|\\.)*"/g, '""');
  const pairs: Record<string, string> = { ')': '(', ']': '[', '}': '{', '⟩': '⟨', '⦄': '⦃' };
  const stack: string[] = [];
  for (const c of text) {
    if ('([{⟨⦃'.includes(c)) stack.push(c);
    else if (c in pairs && stack.pop() !== pairs[c]) return false;
  }
  return stack.length === 0;
}

describe('every imported lean.statement in problems/', async () => {
  const problems = (await loadProblems(repoRoot(import.meta.dir))).filter((p) => p.lean);

  test('there are imported statements to check', () => {
    expect(problems.length).toBeGreaterThan(1000);
  });

  test('no statement ends inside a let/letI/have/haveI binder', () => {
    const bad = problems.filter((p) => /\b(?:let|letI|have|haveI)\s+[^\s:]*(?:\s*:[^=\n]*)?$/.test(p.lean!.statement)).map((p) => p.id);
    expect(bad).toEqual([]);
  });

  test('no statement has unbalanced brackets', () => {
    expect(problems.filter((p) => !balanced(p.lean!.statement)).map((p) => p.id)).toEqual([]);
  });
});
