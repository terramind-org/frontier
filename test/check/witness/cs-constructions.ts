/** Documented constructions used as test witnesses for the computer-science verifiers (no third-party data). */

export type Mat = number[][];
export interface Term { a: Mat; b: Mat; c: Mat }

const zeros = (n: number): Mat => Array.from({ length: n }, () => new Array<number>(n).fill(0));
const mat = (n: number, cells: Array<[number, number, number]>): Mat => {
  const m = zeros(n);
  for (const [i, j, v] of cells) m[i]![j] = v;
  return m;
};

/** Schoolbook scheme: one term per (i,j,l), a = E_ij, b = E_jl, c = E_il; rank n^3. */
export function schoolbook(n: number): Term[] {
  const terms: Term[] = [];
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) for (let l = 0; l < n; l++) terms.push({ a: mat(n, [[i, j, 1]]), b: mat(n, [[j, l, 1]]), c: mat(n, [[i, l, 1]]) });
  return terms;
}

/** Strassen (1969), rank 7 for 2x2: C11 = M1+M4-M5+M7, C12 = M3+M5, C21 = M2+M4, C22 = M1-M2+M3+M6. */
export const STRASSEN: Term[] = [
  { a: mat(2, [[0, 0, 1], [1, 1, 1]]), b: mat(2, [[0, 0, 1], [1, 1, 1]]), c: mat(2, [[0, 0, 1], [1, 1, 1]]) }, // M1
  { a: mat(2, [[1, 0, 1], [1, 1, 1]]), b: mat(2, [[0, 0, 1]]), c: mat(2, [[1, 0, 1], [1, 1, -1]]) }, // M2
  { a: mat(2, [[0, 0, 1]]), b: mat(2, [[0, 1, 1], [1, 1, -1]]), c: mat(2, [[0, 1, 1], [1, 1, 1]]) }, // M3
  { a: mat(2, [[1, 1, 1]]), b: mat(2, [[1, 0, 1], [0, 0, -1]]), c: mat(2, [[0, 0, 1], [1, 0, 1]]) }, // M4
  { a: mat(2, [[0, 0, 1], [0, 1, 1]]), b: mat(2, [[1, 1, 1]]), c: mat(2, [[0, 0, -1], [0, 1, 1]]) }, // M5
  { a: mat(2, [[1, 0, 1], [0, 0, -1]]), b: mat(2, [[0, 0, 1], [0, 1, 1]]), c: mat(2, [[1, 1, 1]]) }, // M6
  { a: mat(2, [[0, 1, 1], [1, 1, -1]]), b: mat(2, [[1, 0, 1], [1, 1, 1]]), c: mat(2, [[0, 0, 1]]) }, // M7
];

/** Kronecker product of two schemes: a scheme for (n1*n2) x (n1*n2) matrices of rank r1*r2. */
export function kronecker(s: Term[], t: Term[]): Term[] {
  const n1 = s[0]!.a.length;
  const n2 = t[0]!.a.length;
  const n = n1 * n2;
  const prod = (x: Mat, y: Mat): Mat => {
    const m = zeros(n);
    for (let i1 = 0; i1 < n1; i1++) for (let j1 = 0; j1 < n1; j1++) for (let i2 = 0; i2 < n2; i2++) for (let j2 = 0; j2 < n2; j2++) m[i1 * n2 + i2]![j1 * n2 + j2] = x[i1]![j1]! * y[i2]![j2]!;
    return m;
  };
  return s.flatMap((u) => t.map((v) => ({ a: prod(u.a, v.a), b: prod(u.b, v.b), c: prod(u.c, v.c) })));
}

/** Batcher's odd-even merge sort (Knuth, TAOCP vol. 3, 5.3.4; iterative form from Wikipedia), valid for any n. */
export function batcher(n: number): Array<[number, number]> {
  const gates: Array<[number, number]> = [];
  for (let p = 1; p < n; p *= 2) {
    for (let k = p; k >= 1; k = Math.floor(k / 2)) {
      for (let j = k % p; j <= n - 1 - k; j += 2 * k) {
        for (let i = 0; i <= Math.min(k - 1, n - j - k - 1); i++) {
          if (Math.floor((i + j) / (2 * p)) === Math.floor((i + j + k) / (2 * p))) gates.push([i + j, i + j + k]);
        }
      }
    }
  }
  return gates;
}

/** A valid, long superpermutation: start from 12...n and keep appending an unseen permutation that overlaps the end of
 *  the word as much as possible. Every permutation is appended, so every one is a window; the length is not minimal. */
export function greedySuperpermutation(n: number): string {
  const all: string[] = [];
  const walk = (prefix: string, rest: number[]): void => {
    if (!rest.length) return void all.push(prefix);
    for (const s of rest) walk(prefix + s, rest.filter((x) => x !== s));
  };
  walk('', Array.from({ length: n }, (_, k) => k + 1));
  const byPrefix = Array.from({ length: n }, () => new Map<string, Set<string>>());
  for (const p of all) for (let k = 0; k < n; k++) {
    const m = byPrefix[k]!;
    const key = p.slice(0, k);
    if (!m.has(key)) m.set(key, new Set());
    m.get(key)!.add(p);
  }
  const take = (p: string): void => byPrefix.forEach((m, k) => m.get(p.slice(0, k))!.delete(p));
  let word = all[0]!;
  take(word);
  for (let left = all.length - 1; left > 0; left--) {
    for (let k = n - 1; k >= 0; k--) {
      const next = byPrefix[k]!.get(word.slice(word.length - k))?.values().next().value;
      if (next !== undefined) {
        word += next.slice(k);
        take(next);
        break;
      }
    }
  }
  return word;
}
