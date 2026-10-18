import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/ramsey.ts';
import { paley } from './helpers.ts';

const P = { ones_free: 4, zeros_free: 4 };

describe('ramsey', () => {
  // Constructions: the Paley graph on q = 1 mod 4 vertices is self-complementary; its clique number is 3 for q = 13,
  // 3 for q = 17 and 4 for q = 37, so it 2-colours K_q with no mono K4 (q = 17) or K5 (q = 37).
  test('Paley(17) has no monochromatic K4 (R(4,4) = 18)', () => {
    expect(verify(paley(17), P)).toEqual({ valid: true, value: 17 });
  });

  test('Paley(37) has no monochromatic K5', () => {
    expect(verify(paley(37), { ones_free: 5, zeros_free: 5 })).toEqual({ valid: true, value: 37 });
  });

  test('colour roles are not symmetric: Paley(17) as an (R(4,6)) witness is valid, a triangle-free ask is not', () => {
    expect(verify(paley(17), { ones_free: 6, zeros_free: 4 })).toEqual({ valid: true, value: 17 });
    const r = verify(paley(17), { ones_free: 3, zeros_free: 3 });
    expect(r.valid).toBe(false);
    expect(r.reason).toMatch(/form a K3 of colour-1 edges/);
  });

  test('rejects a monochromatic clique of colour 0 and names its vertices', () => {
    // 5 vertices, all edges colour 0: K4 of colour 0 at vertices 0,1,2,3
    const n = 5;
    const adjacency = Array.from({ length: n }, () => '0'.repeat(n));
    expect(verify({ n, adjacency }, P).reason).toBe('vertices 0, 1, 2, 3 form a K4 of colour-0 edges');
  });

  test('rejects a colour-1 K4 inside Paley(37) after adding edges', () => {
    const g = paley(37);
    // make vertices 0..4 a clique of colour 1
    const rows = g.adjacency.map((r) => r.split(''));
    for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) if (i !== j) rows[i]![j] = '1';
    const r = verify({ n: 37, adjacency: rows.map((x) => x.join('')) }, { ones_free: 5, zeros_free: 5 });
    expect(r.valid).toBe(false);
    expect(r.reason).toBe('vertices 0, 1, 2, 3, 4 form a K5 of colour-1 edges');
  });

  test('rejects asymmetric matrices, nonzero diagonal, wrong sizes, bad characters', () => {
    expect(verify({ n: 2, adjacency: ['01', '00'] }, P).reason).toContain('not symmetric');
    expect(verify({ n: 2, adjacency: ['10', '01'] }, P).reason).toContain('diagonal');
    expect(verify({ n: 3, adjacency: ['00', '00'] }, P).reason).toContain('has 2 rows, expected n = 3');
    expect(verify({ n: 2, adjacency: ['000', '000'] }, P).reason).toContain('row 0 has length 3');
    expect(verify({ n: 2, adjacency: ['02', '20'] }, P).reason).toContain("other than '0' or '1'");
    expect(verify({ n: 2, adjacency: [[0, 1], [1, 0]] }, P).valid).toBe(false);
    expect(verify({ n: 0, adjacency: [] }, P).reason).toContain('between 1 and 128');
    expect(verify({ n: 500, adjacency: [] }, P).reason).toContain('between 1 and 128');
    expect(verify({ n: 1.5, adjacency: [] }, P).valid).toBe(false);
    expect(verify({ n: 1 }, P).reason).toContain('missing the key "adjacency"');
  });

  test('is fast on 127 vertices', () => {
    const g = paley(113); // 113 = 1 mod 4, prime
    const t = performance.now();
    const r = verify(g, { ones_free: 8, zeros_free: 8 });
    expect(r.valid).toBe(true);
    expect(performance.now() - t).toBeLessThan(10_000);
  });
});
