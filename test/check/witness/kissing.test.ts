import { describe, expect, test } from 'bun:test';
import { sign, verify } from '../../../src/check/witness/kissing.ts';

/** The D_dim root system: all vectors with two entries +-1 and the rest 0, as pairs (p, q) with q = 0 (or q = s). */
function rootSystem(dim: number, scale: 'int' | 'sqrt2'): number[][] {
  const out: number[][] = [];
  for (let i = 0; i < dim; i++)
    for (let j = i + 1; j < dim; j++)
      for (const si of [1, -1])
        for (const sj of [1, -1]) {
          const v = new Array(2 * dim).fill(0);
          v[2 * i + (scale === 'sqrt2' ? 1 : 0)] = si;
          v[2 * j + (scale === 'sqrt2' ? 1 : 0)] = sj;
          out.push(v);
        }
  return out;
}

describe('kissing', () => {
  test('D_11 roots: 220 vectors, a valid kissing configuration (below the record 604)', () => {
    const vectors = rootSystem(11, 'int');
    expect(vectors.length).toBe(220);
    expect(verify({ vectors }, { dim: 11 })).toEqual({ valid: true, value: 220 });
  });

  test('the same configuration scaled by sqrt 2 (all q entries) is valid, with optional metadata keys', () => {
    const vectors = rootSystem(11, 'sqrt2');
    expect(verify({ n: 220, dim: 11, description: 'D11 scaled', vectors }, { dim: 11 })).toEqual({ valid: true, value: 220 });
  });

  test('a configuration whose points sit on different spheres is judged by the largest norm', () => {
    // dim 1: 1 and -1 touch the centre ball at distance 2 >= 1; fine.
    expect(verify({ vectors: [[1, 0], [-1, 0]] }, { dim: 1 })).toEqual({ valid: true, value: 2 });
  });

  test('exact sign of a + b sqrt 2 near zero: 99 - 70 sqrt2 is positive, 7 - 5 sqrt2 negative', () => {
    expect(sign([99n, -70n])).toBe(1);
    expect(sign([-99n, 70n])).toBe(-1);
    expect(sign([7n, -5n])).toBe(-1);
    expect(sign([0n, 0n])).toBe(0);
    expect(sign([0n, -3n])).toBe(-1);
    expect(sign([5n, 3n])).toBe(1);
  });

  test('rejects two nearby vectors', () => {
    // (2,0) and (2,1): norms 4 and 5, R2 = 5, |diff|^2 = 1 < 5
    const r = verify({ vectors: [[2, 0, 0, 0], [2, 0, 1, 0]] }, { dim: 2 });
    expect(r.valid).toBe(false);
    expect(r.reason).toContain('vectors 0 and 1 are too close');
  });

  test('rejects nearby vectors whose difference lives in the sqrt 2 part', () => {
    // u = (1, 0), v = (1, 99 - 70 sqrt2): |v - u|^2 = (99 - 70 sqrt2)^2, about 5e-5, below the largest norm
    const r = verify({ vectors: [[1, 0, 0, 0], [1, 0, 99, -70]] }, { dim: 2 });
    expect(r.valid).toBe(false);
    expect(r.reason).toContain('too close');
  });

  test('rejects zero and duplicate vectors', () => {
    expect(verify({ vectors: [[0, 0, 0, 0]] }, { dim: 2 })).toEqual({ valid: false, reason: 'vector 0 is zero' });
    expect(verify({ vectors: [[1, 0, 0, 0], [1, 0, 0, 0]] }, { dim: 2 }).reason).toBe('vectors 0 and 1 are equal');
  });

  test('rejects wrong lengths, non-integers, metadata mismatches and bad shapes', () => {
    expect(verify({ vectors: [[1, 0, 0]] }, { dim: 2 }).reason).toContain('has 3 integers, expected 2*dim = 4');
    expect(verify({ vectors: [[1.5, 0, 0, 0]] }, { dim: 2 }).reason).toContain('must be an integer');
    expect(verify({ dim: 3, vectors: [[1, 0, 0, 0]] }, { dim: 2 }).reason).toContain('"dim" is 3');
    expect(verify({ n: 2, vectors: [[1, 0, 0, 0]] }, { dim: 2 }).reason).toContain('"n" is 2');
    expect(verify({ vectors: [[1, 0, 0, 0]], junk: 1 }, { dim: 2 }).reason).toContain('unexpected key "junk"');
    expect(verify({ vectors: 3 }, { dim: 2 }).valid).toBe(false);
  });

  test('is fast: 220 vectors in dimension 11', () => {
    const t = performance.now();
    verify({ vectors: rootSystem(11, 'int') }, { dim: 11 });
    expect(performance.now() - t).toBeLessThan(10_000);
  });
});
