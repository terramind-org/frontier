import { describe, expect, test } from 'bun:test';
import { MAX_VIOLATIONS, SCAN_LIMIT } from '../../../src/check/witness/common.ts';
import { verify as capset } from '../../../src/check/witness/capset.ts';
import { verify as covering } from '../../../src/check/witness/covering.ts';
import { verify as golomb } from '../../../src/check/witness/golomb.ts';
import { verify as kissing } from '../../../src/check/witness/kissing.ts';
import { verify as matmul } from '../../../src/check/witness/matmul.ts';
import { verify as ramsey } from '../../../src/check/witness/ramsey.ts';
import { verify as schur } from '../../../src/check/witness/schur.ts';
import { verify as sortnet } from '../../../src/check/witness/sortnet.ts';
import { verify as superperm } from '../../../src/check/witness/superperm.ts';
import { fixture } from './helpers.ts';

const all = { all: true };

/** Deterministic pseudo-random numbers, so a failing case can be rerun. */
function lcg(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 1103515245 + 12345) % 2147483648;
    return s / 2147483648;
  };
}

describe('all mode: default behaviour is untouched', () => {
  test('without options a result has no violations field, and a rejection keeps its single reason', () => {
    expect(golomb({ marks: [0, 1, 4, 9, 11] }, { marks: 5 })).toEqual({ valid: true, value: 11 });
    const r = golomb({ marks: [0, 1, 2, 3, 4] }, { marks: 5 });
    expect(r).toEqual({ valid: false, reason: 'difference 1 occurs twice: 1 - 0 and 2 - 1' });
    expect('violations' in r).toBe(false);
  });

  test('a valid witness has an empty violation list and the same value', () => {
    expect(golomb({ marks: [0, 1, 4, 9, 11] }, { marks: 5 }, all)).toEqual({ valid: true, value: 11, violations: [], omitted: 0 });
    const record = fixture('cap-set-f3-8-size512.json');
    expect(capset(record, { n: 8 }, all)).toEqual({ valid: true, value: 512, violations: [], omitted: 0 });
    expect(covering(fixture('covering-13-7-4-size30.json'), { v: 13, k: 7, t: 4 }, all).value).toBe(30);
  });

  test('the first violation of all mode names the same problem as the default reason', () => {
    const cases: Array<[unknown, ReturnType<typeof golomb>]> = [
      [{ marks: [0, 1, 2, 3, 4] }, golomb({ marks: [0, 1, 2, 3, 4] }, { marks: 5 })],
      [{ marks: [0, 4, 4, 9, 11] }, golomb({ marks: [0, 4, 4, 9, 11] }, { marks: 5 })],
      [{ marks: [1, 2, 4, 9, 11] }, golomb({ marks: [1, 2, 4, 9, 11] }, { marks: 5 })],
    ];
    for (const [witness, plain] of cases) {
      expect(golomb(witness, { marks: 5 }, all).reason).toBe(plain.reason!);
    }
  });
});

describe('all mode: shape errors still stop the run', () => {
  test('a malformed witness gives exactly one violation, the reason', () => {
    const r = capset({ points: [[0, 1, 5]] }, { n: 3 }, all);
    expect(r.valid).toBe(false);
    expect(r.violations).toEqual([r.reason!]);
    expect(r.reason).toContain('expected 0, 1 or 2');
    expect(golomb({ marks: [0, 1.5] }, { marks: 2 }, all).violations).toEqual(['mark 1 must be an integer (got 1.5)']);
    expect(golomb([], { marks: 2 }, all).violations).toEqual(['witness.json must be a JSON object']);
  });
});

describe('golomb', () => {
  test('lists every repeated difference: 0..4 repeats 1 three times, 2 twice, 3 once', () => {
    const r = golomb({ marks: [0, 1, 2, 3, 4] }, { marks: 5 }, all);
    expect(r.valid).toBe(false);
    expect(r.value).toBe(4);
    expect(r.violations).toHaveLength(6);
    expect(r.violations!.filter((v) => v.startsWith('difference 1 '))).toHaveLength(3);
    expect(r.violations!.filter((v) => v.startsWith('difference 2 '))).toHaveLength(2);
    expect(r.violations!.filter((v) => v.startsWith('difference 3 '))).toHaveLength(1);
  });

  test('lists a wrong start, a wrong count and every non-increasing step together', () => {
    const r = golomb({ marks: [2, 1, 1, 9] }, { marks: 5 }, all);
    expect(r.violations).toEqual([
      '"marks" has 4 entries, expected exactly 5',
      'the first mark must be 0 (got 2)',
      'marks must be strictly increasing: mark 1 = 1 is not above mark 0 = 2',
      'marks must be strictly increasing: mark 2 = 1 is not above mark 1 = 1',
      'difference 8 occurs twice: 9 - 1 and 9 - 1', // the two equal marks give the same difference twice
    ]);
  });
});

describe('capset', () => {
  test('counts every collinear triple once, against a brute-force count, on random sets in F_3^3', () => {
    const rand = lcg(7);
    for (let round = 0; round < 6; round++) {
      const pts: number[][] = [];
      for (let code = 0; code < 27; code++) {
        if (rand() < 0.45) pts.push([Math.floor(code / 9), Math.floor(code / 3) % 3, code % 3]);
      }
      let triples = 0;
      for (let i = 0; i < pts.length; i++)
        for (let j = i + 1; j < pts.length; j++)
          for (let k = j + 1; k < pts.length; k++) if (pts[i]!.every((x, d) => (x + pts[j]![d]! + pts[k]![d]!) % 3 === 0)) triples++;
      const r = capset({ points: pts }, { n: 3 }, all);
      expect(r.violations!.length + r.omitted!).toBe(triples);
      expect(r.valid).toBe(triples === 0);
      expect(r.value).toBe(pts.length);
    }
  });

  test('all 27 points of F_3^3 form 117 lines; the 81 points of F_3^4 form 1080 and are capped at 200', () => {
    const f33 = Array.from({ length: 27 }, (_, c) => [Math.floor(c / 9), Math.floor(c / 3) % 3, c % 3]);
    expect(capset({ points: f33 }, { n: 3 }, all).violations).toHaveLength(117);
    const f34 = Array.from({ length: 81 }, (_, c) => [Math.floor(c / 27), Math.floor(c / 9) % 3, Math.floor(c / 3) % 3, c % 3]);
    const r = capset({ points: f34 }, { n: 4 }, all);
    expect(r.violations).toHaveLength(MAX_VIOLATIONS);
    expect(r.omitted).toBe(1080 - MAX_VIOLATIONS);
    expect(r.truncated).toBeUndefined();
    expect(r.value).toBe(81);
  });

  test('a repeated point is one violation and is not counted in the lines', () => {
    const r = capset({ points: [[0, 0], [1, 1], [0, 0], [2, 2]] }, { n: 2 }, all);
    expect(r.violations).toEqual([
      'points 0 and 2 are equal (0,0)',
      'points 0, 1, 3 are collinear (sum to 0 mod 3): (0,0), (1,1), (2,2)',
    ]);
  });
});

describe('covering', () => {
  test('lists every uncovered t-subset: one block of C(5,3,2) leaves 10 - 3 pairs', () => {
    const r = covering({ blocks: [[1, 2, 3]] }, { v: 5, k: 3, t: 2 }, all);
    expect(r.valid).toBe(false);
    expect(r.violations).toHaveLength(7);
    expect(r.violations![0]).toBe('the 2-subset {1, 4} is not contained in any block');
    expect(r.value).toBe(1);
  });

  test('also lists a repeated element and a repeated block', () => {
    const r = covering({ blocks: [[1, 1, 2], [1, 2, 3], [3, 2, 1]] }, { v: 3, k: 3, t: 2 }, all);
    expect(r.violations).toEqual(['block 0 repeats the element 1', 'blocks 1 and 2 are the same set']);
  });
});

describe('kissing', () => {
  const square = [[1, 0, 0, 0], [0, 0, 1, 0], [-1, 0, 0, 0], [0, 0, -1, 0]];

  test('the four axis vectors in the plane are valid', () => {
    expect(kissing({ vectors: square }, { dim: 2 }, all)).toEqual({ valid: true, value: 4, violations: [], omitted: 0 });
  });

  test('a repeated vector is reported, and so is every pair that is too close', () => {
    const r = kissing({ vectors: [...square, [1, 0, 0, 0]] }, { dim: 2 }, all);
    expect(r.violations).toContain('vectors 0 and 4 are equal');
    const close = r.violations!.filter((v) => v.includes('too close'));
    expect(close).toHaveLength(1); // only the copy against its original: the other pairs are at 90 or 180 degrees
    expect(close[0]!.startsWith('vectors 0 and 4 ')).toBe(true);
    expect(r.value).toBe(5);
  });

  test('a mismatched count is listed with the other violations', () => {
    const r = kissing({ vectors: square, n: 3 }, { dim: 2 }, all);
    expect(r.violations).toEqual(['witness "n" is 3 but "vectors" has 4 entries']);
  });
});

describe('matmul', () => {
  /** The 8-term textbook scheme for n x n matrices over the integers: a = E_ij, b = E_jl, c = E_il. */
  const naive = (n: number) => {
    const unit = (i: number, j: number): number[][] => Array.from({ length: n }, (_, r) => Array.from({ length: n }, (_, c) => (r === i && c === j ? 1 : 0)));
    const terms = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) for (let l = 0; l < n; l++) terms.push({ a: unit(i, j), b: unit(j, l), c: unit(i, l) });
    return terms;
  };

  test('the textbook scheme is valid', () => {
    expect(matmul({ terms: naive(2) }, { n: 2, field: 'Z' }, all)).toEqual({ valid: true, value: 8, violations: [], omitted: 0 });
  });

  test('one wrong coefficient is one violation; one dropped term is one violation; two dropped terms are two', () => {
    const wrong = naive(2);
    wrong[0]!.c[0]![0] = 2;
    const r = matmul({ terms: wrong }, { n: 2, field: 'Z' }, all);
    expect(r.violations).toEqual([
      'the scheme is not the matrix product: the coefficient of A[0][0] * B[0][0] in C[0][0] is 2, but the product needs 1',
    ]);
    expect(matmul({ terms: naive(2).slice(1) }, { n: 2, field: 'Z' }, all).violations).toHaveLength(1);
    const two = matmul({ terms: naive(2).slice(2) }, { n: 2, field: 'Z' }, all);
    expect(two.violations).toHaveLength(2);
    expect(two.value).toBe(6);
  });
});

describe('ramsey', () => {
  const complete = (n: number) => Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? '0' : '1')).join(''));

  test('the all-ones colouring of K_5 has C(5,3) = 10 triangles of colour 1', () => {
    const r = ramsey({ n: 5, adjacency: complete(5) }, { ones_free: 3, zeros_free: 3 }, all);
    expect(r.violations).toHaveLength(10);
    expect(r.violations![0]).toBe('vertices 0, 1, 2 form a K3 of colour-1 edges');
    expect(r.value).toBe(5);
  });

  test('the pentagon colouring of K_5 has no triangle in either colour', () => {
    const pentagon = Array.from({ length: 5 }, (_, i) =>
      Array.from({ length: 5 }, (_, j) => ((j - i + 5) % 5 === 1 || (i - j + 5) % 5 === 1 ? '1' : '0')).join(''),
    );
    expect(ramsey({ n: 5, adjacency: pentagon }, { ones_free: 3, zeros_free: 3 }, all).valid).toBe(true);
  });

  test('lists a nonzero diagonal and an asymmetry along with the cliques', () => {
    const r = ramsey({ n: 3, adjacency: ['100', '000', '010'] }, { ones_free: 3, zeros_free: 3 }, all);
    // the upper triangle decides the colours, so the asymmetric pair counts as colour 0 here
    expect(r.violations).toEqual([
      "diagonal entry (0,0) must be '0'",
      'matrix is not symmetric at (1,2) and (2,1)',
      'vertices 0, 1, 2 form a K3 of colour-0 edges',
    ]);
  });

  test('a huge number of cliques stops the scan at the limit and says so', () => {
    const r = ramsey({ n: 64, adjacency: complete(64) }, { ones_free: 5, zeros_free: 5 }, all);
    expect(r.truncated).toBe(true);
    expect(r.violations).toHaveLength(MAX_VIOLATIONS);
    expect(r.omitted).toBe(SCAN_LIMIT - MAX_VIOLATIONS);
    expect(r.valid).toBe(false);
    expect(r.value).toBe(64);
  });
});

describe('schur', () => {
  test('counts every monochromatic x + y = z against a brute-force count, on random colourings', () => {
    const rand = lcg(11);
    for (let round = 0; round < 8; round++) {
      const N = 30 + Math.floor(rand() * 40);
      const colors = Array.from({ length: N }, () => Math.floor(rand() * 3));
      let bad = 0;
      for (let x = 1; x <= N; x++)
        for (let y = x; x + y <= N; y++) if (colors[x - 1] === colors[y - 1] && colors[x - 1] === colors[x + y - 1]) bad++;
      const r = schur({ colors }, { k: 3 }, all);
      expect(r.violations!.length + r.omitted!).toBe(bad);
      expect(r.valid).toBe(bad === 0);
    }
  });

  test('an out-of-range colour is listed and left out of every class', () => {
    expect(schur({ colors: [0, 5, 1, 0] }, { k: 2 }, all).violations).toEqual(['colour of 2 is 5, expected 0..1']);
  });
});

describe('sortnet', () => {
  test('an empty network on 3 wires fails on both adjacent pairs, with counts', () => {
    const r = sortnet({ comparators: [] }, { n: 3 }, all);
    expect(r.valid).toBe(false);
    expect(r.value).toBe(0);
    expect(r.violations).toHaveLength(2);
    expect(r.violations![0]).toContain('2 of the 2^3 0-1 inputs end with wire 0 above wire 1');
    expect(r.violations![0]).toContain('the first is 100 (wire 0 first)');
  });

  test('a bad gate is listed and ignored, the network is judged without it', () => {
    const r = sortnet({ comparators: [[0, 1], [2, 1], [1, 2]] }, { n: 3 }, all);
    expect(r.violations![0]).toBe('comparator 1 = [2, 1] must satisfy 0 <= i < j < 3');
    expect(r.violations!.length).toBeGreaterThan(1);
  });

  test('a correct network has no violations', () => {
    expect(sortnet({ comparators: [[0, 1], [1, 2], [0, 1]] }, { n: 3 }, all)).toEqual({ valid: true, value: 3, violations: [], omitted: 0 });
  });
});

describe('superperm', () => {
  test('lists the missing permutations in lexicographic order', () => {
    const r = superperm({ word: '123' }, { n: 3 }, all);
    expect(r.violations).toEqual([
      'the permutation 132 does not occur',
      'the permutation 213 does not occur',
      'the permutation 231 does not occur',
      'the permutation 312 does not occur',
      'the permutation 321 does not occur',
    ]);
    expect(r.value).toBe(3);
  });

  test('the default reason still names only the first missing one', () => {
    expect(superperm({ word: '123' }, { n: 3 }).reason).toBe('only 1 of the 6 permutations of 3 symbols occur; the first missing one is 132');
  });

  test('a minimal superpermutation is valid', () => {
    expect(superperm({ word: '123121321' }, { n: 3 }, all)).toEqual({ valid: true, value: 9, violations: [], omitted: 0 });
  });
});
