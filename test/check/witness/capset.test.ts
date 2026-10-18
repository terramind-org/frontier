import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/capset.ts';
import { bruteForceCap, fixture } from './helpers.ts';

const record = fixture('cap-set-f3-8-size512.json') as { points: number[][] };

describe('capset', () => {
  test('the public 512-point cap set in F_3^8 (FunSearch) is valid', () => {
    expect(verify(record, { n: 8 })).toEqual({ valid: true, value: 512 });
  });

  test('a 7-dimensional cap set built from the record: the points with last coordinate 0', () => {
    // A subset of a cap set is a cap set, and dropping a constant coordinate keeps it one.
    const slice = record.points.filter((p) => p[7] === 0).map((p) => p.slice(0, 7));
    expect(slice.length).toBeGreaterThan(100);
    const r = verify({ points: slice }, { n: 7 });
    expect(r).toEqual({ valid: true, value: slice.length });
    // Independent cubic check on a sample keeps the quadratic verifier honest.
    expect(bruteForceCap(slice.slice(0, 60))).toBe(true);
  });

  test('the 4-point cap set in F_3^2 is valid and the empty set has value 0', () => {
    expect(verify({ points: [[0, 0], [0, 1], [1, 0], [1, 1]] }, { n: 2 })).toEqual({ valid: true, value: 4 });
    expect(verify({ points: [] }, { n: 2 })).toEqual({ valid: true, value: 0 });
  });

  test('rejects three collinear points and names them', () => {
    const r = verify({ points: [[0, 0], [1, 1], [2, 2], [0, 1]] }, { n: 2 });
    expect(r.valid).toBe(false);
    expect(r.reason).toContain('points 0, 1, 2 are collinear (sum to 0 mod 3)');
  });

  test('rejects two record points plus the third point of their line', () => {
    const [a, b] = record.points as [number[], number[]];
    const c = a.map((x, d) => (6 - x - b[d]!) % 3);
    const r = verify({ points: [a, b, c] }, { n: 8 });
    expect(r.valid).toBe(false);
    expect(r.reason).toContain('points 0, 1, 2 are collinear (sum to 0 mod 3)');
  });

  test('rejects duplicate points', () => {
    const r = verify({ points: [[0, 1], [0, 1]] }, { n: 2 });
    expect(r).toEqual({ valid: false, reason: 'points 0 and 1 are equal (0,1)' });
  });

  test('rejects entries outside {0,1,2}, wrong lengths and non-integers', () => {
    expect(verify({ points: [[0, 3]] }, { n: 2 }).reason).toContain('expected 0, 1 or 2');
    expect(verify({ points: [[0, -1]] }, { n: 2 }).valid).toBe(false);
    expect(verify({ points: [[0, 1.5]] }, { n: 2 }).valid).toBe(false);
    expect(verify({ points: [['0', '1']] }, { n: 2 }).valid).toBe(false);
    expect(verify({ points: [[0, 1, 2]] }, { n: 2 }).reason).toContain('has 3 coordinates, expected 2');
  });

  test('rejects more points than F_3^n has, and bad shapes', () => {
    const tooMany = Array.from({ length: 10 }, () => [0, 0]);
    expect(verify({ points: tooMany }, { n: 2 }).reason).toContain('only 9 points');
    expect(verify([[0, 0]], { n: 2 }).reason).toContain('must be a JSON object');
    expect(verify({}, { n: 2 }).reason).toContain('missing the key "points"');
    expect(verify({ points: [], extra: 1 }, { n: 2 }).reason).toContain('unexpected key "extra"');
    expect(verify({ points: 'x' }, { n: 2 }).reason).toContain('must be an array');
  });

  test('runs in well under 10 s on the record', () => {
    const t = performance.now();
    verify(record, { n: 8 });
    expect(performance.now() - t).toBeLessThan(10_000);
  });
});
