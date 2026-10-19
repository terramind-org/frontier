import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/matmul.ts';
import { kronecker, schoolbook, STRASSEN } from './cs-constructions.ts';

describe('matmul', () => {
  test('the schoolbook scheme is valid at rank n^3 for n = 2, 3, 5', () => {
    for (const n of [2, 3, 5]) expect(verify({ terms: schoolbook(n) }, { n, field: 'Z' })).toEqual({ valid: true, value: n ** 3 });
  });

  test("Strassen's 7-term scheme is valid for 2x2", () => {
    expect(verify({ terms: STRASSEN }, { n: 2, field: 'Z' })).toEqual({ valid: true, value: 7 });
  });

  test("Strassen composed with itself (Kronecker product) is a valid rank-49 scheme for 4x4 over Q", () => {
    const terms = kronecker(STRASSEN, STRASSEN);
    expect(terms).toHaveLength(49);
    expect(verify({ terms }, { n: 4, field: 'Q' })).toEqual({ valid: true, value: 49 });
  });

  test('rational coefficients: scaling a by 1/2 and b by 2 (term 0), a by 3 and c by 1/3 (term 3) keeps the scheme valid; mixed denominators are exact', () => {
    const terms: any[] = JSON.parse(JSON.stringify(STRASSEN));
    const half = (m: number[][]) => m.map((row) => row.map((x) => (x === 0 ? 0 : x === 1 ? '1/2' : '-1/2')));
    const twice = (m: number[][]) => m.map((row) => row.map((x) => 2 * x));
    terms[0] = { a: half(terms[0].a), b: twice(terms[0].b), c: terms[0].c };
    const third = (m: number[][]) => m.map((row) => row.map((x) => (x === 0 ? 0 : x === 1 ? '1/3' : '-1/3')));
    terms[3] = { a: terms[3].a.map((r: number[]) => r.map((x) => 3 * x)), b: terms[3].b, c: third(terms[3].c) };
    expect(verify({ terms }, { n: 2, field: 'Q' })).toEqual({ valid: true, value: 7 });
  });

  test('a dropped term is rejected and the first wrong coefficient is named', () => {
    const r = verify({ terms: STRASSEN.slice(1) }, { n: 2, field: 'Z' });
    expect(r.valid).toBe(false);
    expect(r.reason).toMatch(/^the scheme is not the matrix product: the coefficient of A\[0\]\[0\] \* B\[0\]\[0\] in C\[0\]\[0\] is 0, but the product needs 1$/);
  });

  test('one perturbed coefficient is rejected', () => {
    const terms = JSON.parse(JSON.stringify(schoolbook(3)));
    terms[10].c[1][1] += 1;
    const r = verify({ terms }, { n: 3, field: 'Z' });
    expect(r.valid).toBe(false);
    expect(r.reason).toContain('is not the matrix product');
  });

  test('an extra cancelling-free term (wrong sum) is rejected with the surplus coefficient', () => {
    const terms = [...schoolbook(2), schoolbook(2)[0]!];
    const r = verify({ terms }, { n: 2, field: 'Z' });
    expect(r.reason).toBe('the scheme is not the matrix product: the coefficient of A[0][0] * B[0][0] in C[0][0] is 2, but the product needs 1');
  });

  test('rejects wrong shapes, empty terms and unknown keys', () => {
    const ok = schoolbook(2);
    expect(verify({ terms: [] }, { n: 2, field: 'Z' }).reason).toBe('"terms" is empty');
    expect(verify({ terms: ok, extra: 1 }, { n: 2, field: 'Z' }).reason).toContain('unexpected key');
    expect(verify({}, { n: 2, field: 'Z' }).reason).toContain('missing the key');
    expect(verify({ terms: [{ ...ok[0]!, d: 1 }] }, { n: 2, field: 'Z' }).reason).toContain('unexpected key "d"');
    expect(verify({ terms: [{ a: ok[0]!.a, b: ok[0]!.b }] }, { n: 2, field: 'Z' }).reason).toContain('missing the key "c"');
    expect(verify({ terms: [{ ...ok[0]!, a: [[1, 0]] }] }, { n: 2, field: 'Z' }).reason).toBe('term 0 "a" has 1 rows, expected 2');
    expect(verify({ terms: [{ ...ok[0]!, a: [[1, 0], [0]] }] }, { n: 2, field: 'Z' }).reason).toBe('term 0 "a" row 1 has 1 entries, expected 2');
    expect(verify({ terms: new Array(1001).fill(ok[0]) }, { n: 2, field: 'Z' }).reason).toContain('at most 1000');
  });

  test('rejects bad coefficients: non-integers over Z, fractions not in lowest terms, malformed strings, huge numbers', () => {
    const base = schoolbook(2)[0]!;
    const withA = (v: unknown) => ({ terms: [{ ...base, a: [[v, 0], [0, 0]] }] });
    expect(verify(withA(1.5), { n: 2, field: 'Z' }).reason).toContain('term 0 "a"[0][0] must be an integer');
    expect(verify(withA('1/2'), { n: 2, field: 'Z' }).reason).toContain('works over the integers');
    expect(verify(withA('2/4'), { n: 2, field: 'Q' }).reason).toBe('term 0 "a"[0][0] = "2/4" is not in lowest terms');
    expect(verify(withA('1/1'), { n: 2, field: 'Q' }).reason).toContain('must be an integer or a string "p/q"');
    expect(verify(withA('1/0'), { n: 2, field: 'Q' }).reason).toContain('must be an integer or a string "p/q"');
    expect(verify(withA('x'), { n: 2, field: 'Q' }).valid).toBe(false);
    expect(verify(withA(0.5), { n: 2, field: 'Q' }).valid).toBe(false);
    expect(verify(withA(2 ** 60), { n: 2, field: 'Z' }).valid).toBe(false);
    expect(verify(withA(null), { n: 2, field: 'Q' }).valid).toBe(false);
  });

  test('bad problem parameters are programming errors, not rejections', () => {
    expect(() => verify({ terms: [] }, { n: 2, field: 'R' })).toThrow('field');
    expect(() => verify({ terms: [] }, { n: 1, field: 'Z' })).toThrow('"n"');
  });
});
