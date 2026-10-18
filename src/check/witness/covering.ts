/**
 * Covering designs C(v, k, t): a family of k-subsets (blocks) of {1..v} such that every t-subset lies in some block.
 * Params: v, k, t. Witness: {"blocks": [[1,2,3,4,7,11,13], ...]}, each block k distinct integers in 1..v, no block
 * repeated. Value: the number of blocks (to be minimised).
 *
 * Complexity: O(b * C(k,t)) to mark covered t-subsets (35 per block for k = 7, t = 4) plus O(C(v,t)) to find an
 * uncovered one. Requires v <= 52 (subsets are hashed as sums of 2^x) and C(v,t) <= 5,000,000.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

function binom(n: number, r: number): number {
  let c = 1;
  for (let i = 1; i <= r; i++) c = (c * (n - r + i)) / i;
  return Math.round(c);
}

/** Visit every t-subset of the sorted array `xs` as a hash (sum of 2^x). */
function forEachSubset(xs: number[], t: number, visit: (hash: number) => void): void {
  const rec = (start: number, left: number, hash: number): void => {
    if (left === 0) return visit(hash);
    for (let i = start; i <= xs.length - left; i++) rec(i + 1, left - 1, hash + 2 ** xs[i]!);
  };
  rec(0, t, 0);
}

export function verify(witness: unknown, params: Params): VerifyResult {
  const v = intParam(params, 'v', 1, 52);
  const k = intParam(params, 'k', 1, v);
  const t = intParam(params, 't', 1, k);
  const total = binom(v, t);
  if (total > 5_000_000) throw new Error(`covering parameters (${v},${k},${t}) have ${total} t-subsets, above the verifier limit`);
  return guard(() => {
    const obj = objectWith(witness, ['blocks']);
    const raw = arrayOf(obj.blocks, '"blocks"');
    const blocks: number[][] = [];
    const seenBlocks = new Map<string, number>();
    for (let i = 0; i < raw.length; i++) {
      const b = arrayOf(raw[i], `block ${i}`);
      if (b.length !== k) fail(`block ${i} has ${b.length} elements, expected ${k}`);
      const xs = b.map((x, d) => {
        const n = safeInt(x, `block ${i} element ${d}`);
        if (n < 1 || n > v) fail(`block ${i} contains ${n}, outside 1..${v}`);
        return n;
      });
      const sorted = [...xs].sort((a, c) => a - c);
      for (let d = 1; d < k; d++) if (sorted[d] === sorted[d - 1]) fail(`block ${i} repeats the element ${sorted[d]}`);
      const key = sorted.join(',');
      const prev = seenBlocks.get(key);
      if (prev !== undefined) fail(`blocks ${prev} and ${i} are the same set`);
      seenBlocks.set(key, i);
      blocks.push(sorted);
    }
    const covered = new Set<number>();
    for (const b of blocks) forEachSubset(b, t, (h) => covered.add(h));
    if (covered.size < total) {
      const points = Array.from({ length: v }, (_, i) => i + 1);
      let missing: number[] | null = null;
      const rec = (start: number, left: number, acc: number[], hash: number): void => {
        if (missing) return;
        if (left === 0) {
          if (!covered.has(hash)) missing = [...acc];
          return;
        }
        for (let i = start; i <= points.length - left && !missing; i++) {
          acc.push(points[i]!);
          rec(i + 1, left - 1, acc, hash + 2 ** points[i]!);
          acc.pop();
        }
      };
      rec(0, t, [], 0);
      fail(`the ${t}-subset {${(missing ?? []).join(', ')}} is not contained in any block (${total - covered.size} of ${total} ${t}-subsets uncovered)`);
    }
    return ok(blocks.length);
  });
}
