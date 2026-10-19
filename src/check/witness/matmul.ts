/**
 * Matrix multiplication schemes: a rank-r bilinear scheme for the product of two n x n matrices,
 * C = sum_s <a_s, A> <b_s, B> c_s, where <a, A> = sum_ij a_ij A_ij and c_s is added to C as it is stored.
 * Params: n (matrix size, 2..8), field ("Z": integer coefficients, "Q": rational coefficients).
 * Witness: {"terms": [{"a": n x n, "b": n x n, "c": n x n}, ...]}. An entry is an integer; over "Q" it may also be
 * a string "p/q" in lowest terms with q >= 2. Value: the number of terms r (to be minimised).
 *
 * Exactness: the scheme is valid iff the order-6 tensor sum_s a_s (x) b_s (x) c_s equals the matrix-multiplication
 * tensor T[(i,j),(j,l),(i,l)] = 1 (all other entries 0). Every entry is scaled to a common integer denominator, so the
 * comparison is exact BigInt arithmetic with no rounding.
 *
 * Complexity: O(r * n^6) BigInt operations (r <= 1000, n <= 8); the record 5x5 scheme (r = 93) takes well under 1 s.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

const MAX_TERMS = 1000;
const INT_STRING = /^-?(0|[1-9]\d{0,29})$/;
const FRACTION = /^(-?[1-9]\d{0,29})\/([2-9]|[1-9]\d{1,29})$/;

const gcd = (a: bigint, b: bigint): bigint => {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b) [a, b] = [b, a % b];
  return a;
};
const lcm = (a: bigint, b: bigint): bigint => (a / gcd(a, b)) * b;

function showFraction(num: bigint, den: bigint): string {
  const g = gcd(num, den) || 1n;
  const n = num / g;
  const d = den / g;
  return d === 1n ? `${n}` : `${n}/${d}`;
}

/** One coefficient as numerator/denominator, strictly parsed. */
function parseEntry(v: unknown, field: string, what: string): [bigint, bigint] {
  if (typeof v === 'number') return [BigInt(safeInt(v, what)), 1n];
  if (field === 'Q' && typeof v === 'string') {
    const m = FRACTION.exec(v);
    if (m) {
      const num = BigInt(m[1]!);
      const den = BigInt(m[2]!);
      if (gcd(num, den) !== 1n) fail(`${what} = "${v}" is not in lowest terms`);
      return [num, den];
    }
    if (INT_STRING.test(v)) return [BigInt(v), 1n];
  }
  return fail(
    field === 'Q'
      ? `${what} must be an integer or a string "p/q" in lowest terms with q >= 2 (got ${JSON.stringify(v)})`
      : `${what} must be an integer (got ${JSON.stringify(v)}); this problem works over the integers`,
  );
}

/** An n x n matrix as integers over their common denominator: entry (i,j) = ints[i*n+j] / den. */
function parseMatrix(value: unknown, n: number, field: string, what: string): { ints: bigint[]; den: bigint } {
  const rows = arrayOf(value, what);
  if (rows.length !== n) fail(`${what} has ${rows.length} rows, expected ${n}`);
  const parsed: Array<[bigint, bigint]> = [];
  rows.forEach((row, i) => {
    const cells = arrayOf(row, `${what} row ${i}`);
    if (cells.length !== n) fail(`${what} row ${i} has ${cells.length} entries, expected ${n}`);
    cells.forEach((cell, j) => parsed.push(parseEntry(cell, field, `${what}[${i}][${j}]`)));
  });
  let den = 1n;
  for (const [, d] of parsed) den = lcm(den, d);
  return { ints: parsed.map(([num, d]) => num * (den / d)), den };
}

export function verify(witness: unknown, params: Params): VerifyResult {
  const n = intParam(params, 'n', 2, 8);
  const field = params.field;
  if (field !== 'Z' && field !== 'Q') throw new Error(`verifier parameter "field" must be "Z" or "Q", got ${JSON.stringify(field)}`);
  const n2 = n * n;
  return guard(() => {
    const obj = objectWith(witness, ['terms']);
    const raw = arrayOf(obj.terms, '"terms"');
    if (raw.length < 1) fail('"terms" is empty');
    if (raw.length > MAX_TERMS) fail(`"terms" has ${raw.length} entries, at most ${MAX_TERMS} are accepted`);

    const terms = raw.map((t, s) => {
      const term = objectWith(t, ['a', 'b', 'c']);
      // term s is a_s (x) b_s (x) c_s with the denominators of the three matrices multiplied
      const a = parseMatrix(term.a, n, field, `term ${s} "a"`);
      const b = parseMatrix(term.b, n, field, `term ${s} "b"`);
      const c = parseMatrix(term.c, n, field, `term ${s} "c"`);
      return { a: a.ints, b: b.ints, c: c.ints, den: a.den * b.den * c.den };
    });

    // bring every term to one common denominator G, then the sum is an integer tensor
    let G = 1n;
    for (const t of terms) G = lcm(G, t.den);
    const sum = new Array<bigint>(n2 * n2 * n2).fill(0n);
    for (const t of terms) {
      const scale = G / t.den;
      for (let p = 0; p < n2; p++) {
        if (t.a[p] === 0n) continue;
        const ap = t.a[p]! * scale;
        for (let q = 0; q < n2; q++) {
          if (t.b[q] === 0n) continue;
          const apq = ap * t.b[q]!;
          const base = (p * n2 + q) * n2;
          for (let r = 0; r < n2; r++) if (t.c[r] !== 0n) sum[base + r]! += apq * t.c[r]!;
        }
      }
    }

    // target: A[i][j] * B[j][l] contributes to C[i][l]
    const target = new Set<number>();
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) for (let l = 0; l < n; l++) target.add(((i * n + j) * n2 + (j * n + l)) * n2 + (i * n + l));
    for (let idx = 0; idx < sum.length; idx++) {
      const want = target.has(idx) ? G : 0n;
      if (sum[idx] === want) continue;
      const r = idx % n2;
      const q = Math.floor(idx / n2) % n2;
      const p = Math.floor(idx / (n2 * n2));
      const at = (x: number) => `[${Math.floor(x / n)}][${x % n}]`;
      fail(
        `the scheme is not the matrix product: the coefficient of A${at(p)} * B${at(q)} in C${at(r)} is ${showFraction(sum[idx]!, G)}, ` +
          `but the product needs ${want === 0n ? '0' : '1'}`,
      );
    }
    return ok(terms.length);
  });
}
