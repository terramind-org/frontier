/**
 * Kissing configurations in R^dim with coordinates in Z[sqrt 2]. Vectors v_1..v_N (nonzero, distinct) are a valid
 * configuration when every pair has angle >= 60 degrees. Exactly: with R2 = max |v_i|^2, require
 * |v_i - v_j|^2 >= R2 for all i < j (law of cosines: norms <= R and distances >= R force every angle >= 60).
 * Params: dim. Witness: {"vectors": [[p0,q0,p1,q1,...], ...]} with 2*dim integers per vector, coordinate k being
 * p_k + q_k*sqrt(2); optional keys "n" (count), "dim" and "description" are accepted and must agree.
 * Value: N.
 *
 * Arithmetic: a + b*sqrt2 is the BigInt pair (a, b); signs are decided exactly (no floats). Complexity:
 * O(N^2 dim) BigInt operations, about 0.3 s at N = 604, dim = 11. N is capped at 2000.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

const MAX_N = 2000;

/** x + b*sqrt(2) as a pair. */
type Q = [bigint, bigint];

/** Sign of x + b*sqrt2, exactly. */
export function sign([x, b]: Q): -1 | 0 | 1 {
  if (b === 0n) return x > 0n ? 1 : x < 0n ? -1 : 0;
  if (x === 0n) return b > 0n ? 1 : -1;
  if (x > 0n && b > 0n) return 1;
  if (x < 0n && b < 0n) return -1;
  // opposite signs: compare x^2 with 2 b^2
  const x2 = x * x;
  const b2 = 2n * b * b;
  if (x2 === b2) return 0; // impossible for integers (sqrt 2 is irrational) except x = b = 0, kept for safety
  return (x2 > b2) === (x > 0n) ? 1 : -1;
}

export function verify(witness: unknown, params: Params): VerifyResult {
  const dim = intParam(params, 'dim', 1, 64);
  return guard(() => {
    const obj = objectWith(witness, ['vectors'], ['n', 'dim', 'description']);
    const raw = arrayOf(obj.vectors, '"vectors"');
    if (raw.length > MAX_N) fail(`"vectors" has ${raw.length} entries; the verifier accepts at most ${MAX_N}`);
    if ('dim' in obj && obj.dim !== dim) fail(`witness "dim" is ${JSON.stringify(obj.dim)} but the problem is in dimension ${dim}`);
    if ('n' in obj && obj.n !== raw.length) fail(`witness "n" is ${JSON.stringify(obj.n)} but "vectors" has ${raw.length} entries`);
    if ('description' in obj && typeof obj.description !== 'string') fail('"description" must be a string');
    const P: bigint[][] = [];
    const Qs: bigint[][] = [];
    const seen = new Map<string, number>();
    for (let i = 0; i < raw.length; i++) {
      const v = arrayOf(raw[i], `vector ${i}`);
      if (v.length !== 2 * dim) fail(`vector ${i} has ${v.length} integers, expected 2*dim = ${2 * dim}`);
      const nums = v.map((x, d) => BigInt(safeInt(x, `vector ${i} entry ${d}`)));
      if (nums.every((x) => x === 0n)) fail(`vector ${i} is zero`);
      const key = nums.join(',');
      const prev = seen.get(key);
      if (prev !== undefined) fail(`vectors ${prev} and ${i} are equal`);
      seen.set(key, i);
      P.push(nums.filter((_, d) => d % 2 === 0));
      Qs.push(nums.filter((_, d) => d % 2 === 1));
    }
    const N = raw.length;
    // Gram entries: dot(u, v) = (sum p_u p_v + 2 q_u q_v) + (sum p_u q_v + q_u p_v) sqrt2
    const dot = (i: number, j: number): Q => {
      let a = 0n;
      let b = 0n;
      const pi = P[i]!, qi = Qs[i]!, pj = P[j]!, qj = Qs[j]!;
      for (let d = 0; d < dim; d++) {
        a += pi[d]! * pj[d]! + 2n * qi[d]! * qj[d]!;
        b += pi[d]! * qj[d]! + qi[d]! * pj[d]!;
      }
      return [a, b];
    };
    const norms = Array.from({ length: N }, (_, i) => dot(i, i));
    let maxIdx = 0;
    for (let i = 1; i < N; i++) {
      const diff: Q = [norms[i]![0] - norms[maxIdx]![0], norms[i]![1] - norms[maxIdx]![1]];
      if (sign(diff) > 0) maxIdx = i;
    }
    const R2 = norms[maxIdx]!;
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const g = dot(i, j);
        const d2: Q = [norms[i]![0] + norms[j]![0] - 2n * g[0] - R2[0], norms[i]![1] + norms[j]![1] - 2n * g[1] - R2[1]];
        if (sign(d2) < 0) {
          fail(`vectors ${i} and ${j} are too close: the angle between them is below 60 degrees (|v_i - v_j|^2 is less than the largest squared norm)`);
        }
      }
    }
    return ok(N);
  });
}
