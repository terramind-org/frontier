import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/superperm.ts';
import { greedySuperpermutation } from './cs-constructions.ts';

describe('superperm', () => {
  test('the minimal superpermutations for n = 2 and n = 3 are valid', () => {
    expect(verify({ word: '121' }, { n: 2 })).toEqual({ valid: true, value: 3 });
    expect(verify({ word: '123121321' }, { n: 3 })).toEqual({ valid: true, value: 9 });
  });

  test('the n = 4 word of length 33 is valid', () => {
    expect(verify({ word: '123412314231243121342132413214321' }, { n: 4 })).toEqual({ valid: true, value: 33 });
  });

  test('greedy constructions are valid for n = 5, 6, 7 and not shorter than the classical bound n!+(n-1)!+(n-2)!+n-3', () => {
    const bound = (n: number) => { const f = (k: number): number => (k <= 1 ? 1 : k * f(k - 1)); return f(n) + f(n - 1) + f(n - 2) + n - 3; };
    for (const n of [5, 6, 7]) {
      const word = greedySuperpermutation(n);
      const r = verify({ word }, { n });
      expect(r.valid).toBe(true);
      expect(r.value).toBe(word.length);
      expect(word.length).toBeGreaterThanOrEqual(bound(n));
    }
    expect(bound(7)).toBe(5884);
  });

  test('a word missing a permutation is rejected and names the first one missing', () => {
    expect(verify({ word: '12312' }, { n: 3 })).toEqual({ valid: false, reason: 'only 3 of the 6 permutations of 3 symbols occur; the first missing one is 132' });
    const word = greedySuperpermutation(5).slice(0, -1); // drops the last permutation's final character
    expect(verify({ word }, { n: 5 }).reason).toContain('only 119 of the 120 permutations');
  });

  test('windows with a repeated symbol do not count', () => {
    expect(verify({ word: '112233' }, { n: 3 }).reason).toContain('only 0 of the 6');
  });

  test('rejects bad characters, wrong types, short words, whitespace and unknown keys', () => {
    expect(verify({ word: '1234' }, { n: 3 }).reason).toBe('character 3 is "4", expected a digit from 1 to 3');
    expect(verify({ word: '123 121321' }, { n: 3 }).reason).toContain('character 3 is " "');
    expect(verify({ word: '123121321\n' }, { n: 3 }).valid).toBe(false);
    expect(verify({ word: '12' }, { n: 3 }).reason).toBe('"word" has 2 characters, fewer than 3');
    expect(verify({ word: 123121321 }, { n: 3 }).reason).toBe('"word" must be a string');
    expect(verify({ word: ['1', '2'] }, { n: 2 }).valid).toBe(false);
    expect(verify({ word: '121', x: 1 }, { n: 2 }).reason).toContain('unexpected key');
    expect(verify({}, { n: 2 }).reason).toContain('missing the key');
    expect(verify({ word: '1'.repeat(2_000_001) }, { n: 2 }).reason).toContain('at most 2000000');
  });
});
