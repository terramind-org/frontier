import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/schur.ts';

/**
 * Standard construction S(k+1) >= 3 S(k) + 1: from a partition of [1, n] into k sum-free sets, put [n+1, 2n+1] in a
 * new set (2(n+1) > 2n+1, so it is sum-free) and give 2n+1+i the colour of i for i in [1, n]. Starting from
 * {1} (k = 1, n = 1) this reaches n = (3^k - 1) / 2.
 */
function schurPartition(k: number): number[] {
  let colors = [0];
  for (let c = 1; c < k; c++) {
    const n = colors.length;
    colors = [...colors, ...Array<number>(n + 1).fill(c), ...colors];
  }
  return colors;
}

describe('schur', () => {
  test('the constructed 7-colour partition of [1, 1093] is valid', () => {
    const colors = schurPartition(7);
    expect(colors.length).toBe(1093);
    expect(verify({ colors }, { k: 7 })).toEqual({ valid: true, value: 1093 });
  });

  test('small cases: [1,4] needs 2 colours, [1,5] does not fit in 2', () => {
    expect(verify({ colors: [0, 1, 1, 0] }, { k: 2 })).toEqual({ valid: true, value: 4 });
    expect(verify({ colors: [0, 1, 1, 0, 0] }, { k: 2 }).valid).toBe(false);
  });

  test('rejects x + x = z and names it', () => {
    expect(verify({ colors: [0, 0] }, { k: 2 }).reason).toBe('1 + 1 = 2 all have colour 0');
  });

  test('rejects x + y = z with x != y', () => {
    // class 0 = {2, 3, 5}, class 1 = {1, 4}
    expect(verify({ colors: [1, 0, 0, 1, 0] }, { k: 2 }).reason).toBe('2 + 3 = 5 all have colour 0');
  });

  test('moving 2 into the class of 1 in the 1093 partition is caught', () => {
    const colors = schurPartition(7);
    colors[1] = colors[0]!;
    expect(verify({ colors }, { k: 7 })).toEqual({ valid: false, reason: '1 + 1 = 2 all have colour 0' });
  });

  test('rejects out-of-range colours, non-integers, empty and oversized input', () => {
    expect(verify({ colors: [0, 2] }, { k: 2 }).reason).toContain('expected 0..1');
    expect(verify({ colors: [0, -1] }, { k: 2 }).valid).toBe(false);
    expect(verify({ colors: [0, 0.5] }, { k: 2 }).valid).toBe(false);
    expect(verify({ colors: [] }, { k: 2 }).reason).toContain('empty');
    expect(verify({ colors: Array(5001).fill(0) }, { k: 2 }).reason).toContain('at most 5000');
    expect(verify({ colors: 'abc' }, { k: 2 }).valid).toBe(false);
  });
});
