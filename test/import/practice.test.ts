import { describe, expect, test } from 'bun:test';
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { importFormalConjectures, practiceProblem } from '../../src/import/formal-conjectures.ts';
import { parseLeanFile } from '../../src/import/lean-parse.ts';
import { PRACTICE, PRACTICE_MAX_PROOF_LINES } from '../../src/import/practice.ts';
import type { PracticeEntry } from '../../src/import/practice.ts';
import { loadAll, loadProblems } from '../../src/repo.ts';
import { problemIssues } from '../../src/schema.ts';
import { fixtureWorkspace } from './helpers.ts';

const PATH = 'FormalConjectures/Drills/Drills.lean';
const long = Array.from({ length: PRACTICE_MAX_PROOF_LINES }, () => '  skip').join('\n');
const DRILLS = `/-!
# Drills
-/

namespace Drills

/-- A good one. -/
@[category textbook, AMS 11]
theorem good (n : ℕ) : n + 0 = n := by
  simp -- PROOF-MARKER

@[category textbook]
theorem uses_sorry : 1 = 1 := by
  sorry

@[category textbook]
theorem uses_native : 1 = 1 := by
  native_decide

@[category textbook]
private theorem hidden : 2 = 2 := by
  rfl

@[category textbook]
theorem too_long : 3 = 3 := by
${long}
  rfl

/-- An open one in the same file. -/
@[category research open]
theorem drill_open : True := by
  sorry

end Drills
`;

function workspace() {
  const ws = fixtureWorkspace();
  mkdirSync(join(ws.checkout, 'FormalConjectures', 'Drills'));
  writeFileSync(join(ws.checkout, PATH), DRILLS);
  return ws;
}
const entry = (decl: string): PracticeEntry => ({ path: PATH, decl, note: `Practice: ${decl}.` });

describe('practice declarations', () => {
  const parsed = parseLeanFile(DRILLS, { categories: ['research open', 'textbook'] });
  const d = (name: string) => parsed.decls.find((x) => x.fullName === name)!;

  test('the parser collects textbook declarations only when asked', () => {
    expect(parseLeanFile(DRILLS).decls.map((x) => x.fullName)).toEqual(['Drills.drill_open']);
    expect(parsed.decls.map((x) => [x.fullName, x.category])).toEqual([
      ['Drills.good', 'textbook'],
      ['Drills.uses_sorry', 'textbook'],
      ['Drills.uses_native', 'textbook'],
      ['Drills.hidden', 'textbook'],
      ['Drills.too_long', 'textbook'],
      ['Drills.drill_open', 'research open'],
    ]);
  });

  test('proof length and the qualification rule', () => {
    expect(d('Drills.good').proofLines).toBe(2);
    expect(d('Drills.too_long').proofLines).toBe(PRACTICE_MAX_PROOF_LINES + 2);
    expect(practiceProblem(d('Drills.good'))).toBeNull();
    expect(practiceProblem(d('Drills.uses_sorry'))).toContain('sorry');
    expect(practiceProblem(d('Drills.uses_native'))).toContain('native_decide');
    expect(practiceProblem(d('Drills.hidden'))).toBe('declared private');
    expect(practiceProblem(d('Drills.too_long'))).toContain('lines');
    expect(practiceProblem(d('Drills.drill_open'))).toContain('textbook');
  });

  test('a listed entry imports as practice: tag, textbook, difficulty, own title; no proof text', async () => {
    const { checkout, root } = workspace();
    const s = await importFormalConjectures({ checkout, root, date: '2026-10-18', practice: [entry('Drills.good')] });
    expect(s.skipped).toEqual([]);
    expect(s.practice).toBe(1);
    const p = (await loadProblems(root)).find((x) => x.id === 'drills.good')!;
    expect(p.tags).toEqual(['drills', 'practice']);
    expect(p.upstream_status).toBe('textbook');
    expect(p.difficulty).toEqual({ level: 'practice', note: 'Practice: Drills.good.' });
    expect(p.title).toBe('Practice: Drills');
    expect(p.lean!.statement).toBe('theorem good (n : ℕ) : n + 0 = n');
    expect(p.lean!.context).toEqual(['open Drills']);
    expect(problemIssues(p)).toEqual([]);
    const yaml = readFileSync(join(root, 'problems', 'drills.good.yaml'), 'utf8');
    expect(yaml).not.toContain('PROOF-MARKER');
    expect(yaml).not.toContain('simp');
    // The open declaration of the same file keeps its plain title; unlisted textbook ones stay out.
    expect((await loadProblems(root)).find((x) => x.id === 'drills.drill-open')!.title).toBe('Drills');
    expect(existsSync(join(root, 'problems', 'drills.uses-sorry.yaml'))).toBe(false);
    // Practice problems always have status `practice`.
    expect((await loadAll(root)).find((x) => x.problem.id === 'drills.good')!.status).toBe('practice');
  });

  test('an entry that does not qualify aborts the import and writes nothing', async () => {
    const { checkout, root } = workspace();
    const s = await importFormalConjectures({
      checkout, root, date: '2026-10-18',
      practice: [entry('Drills.uses_sorry'), entry('Drills.hidden'), entry('Drills.too_long'), entry('Drills.nope'),
        { path: 'FormalConjectures/Missing.lean', decl: 'X.y', note: 'n' }],
    });
    expect(s.skipped.map((k) => k.reason)).toEqual([
      'practice Drills.uses_sorry: upstream proof uses sorry, admit or native_decide',
      'practice Drills.hidden: declared private',
      `practice Drills.too_long: upstream proof has ${PRACTICE_MAX_PROOF_LINES + 2} lines (max ${PRACTICE_MAX_PROOF_LINES})`,
      'practice Drills.nope: no such textbook declaration',
      'practice X.y: file not found or unreadable',
    ]);
    expect(existsSync(join(root, 'problems')) ? readdirSync(join(root, 'problems')) : []).toEqual([]);
  });
});

describe('the curated practice list', () => {
  test('12–20 entries, unique, spread over sources, including Erdos1.erdos_1.variants.weaker', () => {
    expect(PRACTICE.length).toBeGreaterThanOrEqual(12);
    expect(PRACTICE.length).toBeLessThanOrEqual(20);
    expect(new Set(PRACTICE.map((e) => e.decl)).size).toBe(PRACTICE.length);
    expect(PRACTICE.some((e) => e.decl === 'Erdos1.erdos_1.variants.weaker')).toBe(true);
    expect(new Set(PRACTICE.map((e) => e.path.split('/')[1])).size).toBeGreaterThanOrEqual(6);
    for (const e of PRACTICE) expect(e.note).toStartWith('Practice: ');
  });

  test('problems/ holds exactly the listed practice problems, each valid', async () => {
    const practice = (await loadProblems()).filter((p) => p.tags.includes('practice'));
    expect(practice.map((p) => p.lean!.decl).sort()).toEqual(PRACTICE.map((e) => e.decl).sort());
    for (const p of practice) {
      expect(p.upstream_status).toBe('textbook');
      expect(p.difficulty!.level).toBe('practice');
      expect(problemIssues(p)).toEqual([]);
    }
  });
});
