import { describe, expect, test } from 'bun:test';
import { isAttemptId, isProblemId, newAttemptId, problemIdFromLeanName } from '../../src/ids.ts';

describe('problemIdFromLeanName', () => {
  test('design examples', () => {
    expect(problemIdFromLeanName('Erdos1.erdos_1')).toBe('erdos1.erdos-1');
    expect(problemIdFromLeanName('Erdos1.erdos_1.variants.weaker')).toBe('erdos1.erdos-1.variants.weaker');
  });
  test('unicode is reduced to ASCII', () => {
    expect(problemIdFromLeanName('Erdős.erdős_1')).toBe('erdos.erdos-1');
    expect(problemIdFromLeanName('Ünïcode.thm')).toBe('unicode.thm');
  });
  test('guillemets are dropped', () => {
    expect(problemIdFromLeanName('«1».foo_bar')).toBe('1.foo-bar');
    expect(problemIdFromLeanName('Foo.«weird name».x')).toBe('foo.weird-name.x');
  });
  test('digits-first segments and repeated separators', () => {
    expect(problemIdFromLeanName('Foo.2_bar__baz')).toBe('foo.2-bar-baz');
    expect(problemIdFromLeanName('_Foo.bar_')).toBe('foo.bar');
    expect(problemIdFromLeanName('Foo.bar\'')).toBe('foo.bar');
  });
  test('always produces a valid id, truncated to 120 chars', () => {
    const id = problemIdFromLeanName(`A.${'b_'.repeat(100)}c`);
    expect(id.length).toBeLessThanOrEqual(120);
    expect(isProblemId(id)).toBe(true);
  });
  test('collisions are not resolved here', () => {
    expect(problemIdFromLeanName('A.b_c')).toBe(problemIdFromLeanName('A.b.c'.replace('.c', '-c')));
  });
  test('nothing usable throws', () => {
    expect(() => problemIdFromLeanName('«»')).toThrow();
    expect(() => problemIdFromLeanName('日本')).toThrow();
  });
});

describe('ids', () => {
  test('isProblemId', () => {
    for (const ok of ['erdos1.erdos-1', 'witness.cap-set-f3-8', 'a1', '1.2']) expect(isProblemId(ok)).toBe(true);
    for (const bad of ['', 'a', '-a', 'a-', '.a', 'a.', 'A1', 'a_b', 'a b', 'a'.repeat(121)]) expect(isProblemId(bad)).toBe(false);
    expect(isProblemId('a'.repeat(120))).toBe(true);
    expect(isProblemId(42)).toBe(false);
  });
  test('newAttemptId', () => {
    const id = newAttemptId('Agrim', new Date('2026-10-18T23:59:00Z'));
    expect(id).toMatch(/^20261018-agrim-[0-9a-f]{6}$/);
    expect(isAttemptId(id)).toBe(true);
    expect(newAttemptId('x')).not.toBe(newAttemptId('x'));
    expect(() => newAttemptId('bad login')).toThrow();
  });
  test('isAttemptId', () => {
    expect(isAttemptId('20261018-agrim-3f9a1c')).toBe(true);
    expect(isAttemptId('20261018-a-b-3f9a1c')).toBe(true);
    for (const bad of ['20261018-Agrim-3f9a1c', '2026101-agrim-3f9a1c', '20261018-agrim-3f9a1', '20261018-agrim-3f9a1g', 'x']) {
      expect(isAttemptId(bad)).toBe(false);
    }
  });
});
