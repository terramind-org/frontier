import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/golomb.ts';

// The 29-mark ruler of length 623 from the Rokicki-Dogon dataset (https://cube20.org/golomb/), a list of numbers.
const RECORD_29 = [0, 7, 11, 31, 43, 53, 100, 121, 144, 150, 202, 220, 229, 268, 284, 285, 356, 371, 390, 416, 430, 465, 467, 528, 582, 590, 595, 620, 623];

describe('golomb', () => {
  test('the public 29-mark ruler of length 623 is valid', () => {
    expect(verify({ marks: RECORD_29 }, { marks: 29 })).toEqual({ valid: true, value: 623 });
  });

  test('the optimal 5-mark ruler 0 1 4 9 11 is valid', () => {
    expect(verify({ marks: [0, 1, 4, 9, 11] }, { marks: 5 })).toEqual({ valid: true, value: 11 });
  });

  test('Erdos-Turan construction 2pk + (k^2 mod p) gives a valid, longer 29-mark ruler', () => {
    const p = 29;
    const marks = Array.from({ length: p }, (_, k) => 2 * p * k + ((k * k) % p));
    const r = verify({ marks }, { marks: 29 });
    expect(r.valid).toBe(true);
    expect(r.value).toBe(2 * p * 28 + 1);
  });

  test('rejects a repeated difference and names it', () => {
    const r = verify({ marks: [0, 1, 2, 4, 7] }, { marks: 5 });
    expect(r.valid).toBe(false);
    expect(r.reason).toBe('difference 1 occurs twice: 1 - 0 and 2 - 1');
  });

  test('rejects a ruler whose last mark is moved onto an existing difference', () => {
    const r = verify({ marks: [0, 1, 4, 9, 10] }, { marks: 5 });
    expect(r).toEqual({ valid: false, reason: 'difference 9 occurs twice: 9 - 0 and 10 - 1' });
  });

  test('rejects a wrong count, a nonzero start, non-increasing marks, non-integers', () => {
    expect(verify({ marks: [0, 1, 4] }, { marks: 5 }).reason).toContain('has 3 entries, expected exactly 5');
    expect(verify({ marks: [1, 2, 4, 9, 11] }, { marks: 5 }).reason).toContain('first mark must be 0');
    expect(verify({ marks: [0, 4, 4, 9, 11] }, { marks: 5 }).reason).toContain('strictly increasing');
    expect(verify({ marks: [0, 1, 4, 9, 11.5] }, { marks: 5 }).reason).toContain('must be an integer');
    expect(verify({ marks: [0, 1, 4, 9, '11'] }, { marks: 5 }).valid).toBe(false);
    expect(verify({ marks: [0, 1, 4, 9, 2 ** 60] }, { marks: 5 }).valid).toBe(false);
    expect(verify({ marks: [0, 1, 4, 9, 11], x: 1 }, { marks: 5 }).reason).toContain('unexpected key');
  });
});
