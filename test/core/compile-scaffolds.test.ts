import { describe, expect, test } from 'bun:test';
import { compileScaffold, firstErrorLine, hasError, sampleIds } from '../../scripts/compile-scaffolds.ts';
import { loadProblem, loadProblems } from '../../src/repo.ts';
import { copyFixture, GOOD } from './helpers.ts';

describe('scripts/compile-scaffolds helpers', () => {
  test('hasError ignores warnings and the sorry warning, sees errors', () => {
    const sorry = "/tmp/x/Scaffold.lean:6:8: warning: declaration uses 'sorry'";
    expect(hasError(sorry)).toBe(false);
    expect(hasError('')).toBe(false);
    expect(hasError("/tmp/x/Scaffold.lean:6:30: error: unexpected token ')'; expected term")).toBe(true);
    expect(hasError("/tmp/x/Scaffold.lean:1:0: error: object file 'a.olean' does not exist")).toBe(true);
    expect(hasError(`${sorry}\n/tmp/x/Scaffold.lean:9:2: error: unknown identifier 'x'`)).toBe(true);
  });
  test('firstErrorLine picks the first error and shortens the path', () => {
    const out = "/var/tmp/x/Scaffold.lean:6:8: warning: declaration uses 'sorry'\n/var/tmp/x/Scaffold.lean:9:2: error: unknown identifier 'x'\n/var/tmp/x/Scaffold.lean:10:2: error: second";
    expect(firstErrorLine(out)).toBe("Scaffold.lean:9:2: error: unknown identifier 'x'");
    expect(firstErrorLine('')).toBe('lean failed without output');
    expect(firstErrorLine('just text')).toBe('just text');
  });
  test('sampleIds is seeded, unique and skips answer-required and Lean-less problems', async () => {
    const problems = await loadProblems(GOOD);
    const all = problems.filter((p) => p.lean).map((p) => p.id);
    const a = sampleIds(problems, 3, 's1');
    expect(sampleIds(problems, 3, 's1')).toEqual(a);
    expect(new Set(a).size).toBe(a.length);
    expect(a.every((id) => all.includes(id))).toBe(true);
    expect(a.some((id) => id.startsWith('witness.'))).toBe(false);
    expect(sampleIds(problems, 99, 's1').sort()).toEqual([...all].sort());
    const tagged = problems.map((p) => (p.id === all[0] ? { ...p, tags: [...p.tags, 'answer-required'] } : p));
    expect(sampleIds(tagged, 99, 's1')).not.toContain(all[0]!);
  });
  test('a problem without a lean block fails without running Lean', async () => {
    const root = copyFixture('good');
    const witness = (await loadProblem('witness.toy-cap', root))!;
    const r = await compileScaffold(root, witness, 1000);
    expect(r).toMatchObject({ ok: false, detail: 'problem has no lean block' });
  });
});
