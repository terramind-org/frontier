/**
 * Sorting networks: a fixed sequence of compare-exchange gates on n wires. Gate (i, j), i < j, puts the smaller value
 * on wire i and the larger on wire j. Params: n (wires, 2..24).
 * Witness: {"comparators": [[i, j], ...]}, gates in order, 0 <= i < j < n. Value: the number of gates (to be minimised).
 *
 * Exactness: by the 0-1 principle a network sorts all inputs iff it sorts all 2^n inputs of zeros and ones, so the check
 * is a proof, not a test. Wire w is held as one 2^n-bit BigInt whose bit x is the value on wire w for input x; a gate is
 * (AND, OR) of two such integers. The network sorts iff, for every i < n-1, no input has a 1 on wire i and a 0 on wire i+1.
 *
 * Complexity: O(gates * 2^n / 64) word operations; n = 18, 77 gates is milliseconds, n = 24 takes seconds.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

const MAX_GATES = 5000;

/** Bit x of the result is bit w of x, for x in [0, 2^n). */
function wirePattern(w: number, n: number): bigint {
  const total = 1n << BigInt(n);
  const half = 1n << BigInt(w); // 2^w zeros then 2^w ones, repeating
  let pattern = ((1n << half) - 1n) << half;
  let width = half << 1n;
  while (width < total) {
    pattern |= pattern << width;
    width <<= 1n;
  }
  return pattern;
}

export function verify(witness: unknown, params: Params): VerifyResult {
  const n = intParam(params, 'n', 2, 24);
  return guard(() => {
    const obj = objectWith(witness, ['comparators']);
    const raw = arrayOf(obj.comparators, '"comparators"');
    if (raw.length > MAX_GATES) fail(`"comparators" has ${raw.length} entries, at most ${MAX_GATES} are accepted`);
    const gates = raw.map((g, k) => {
      const pair = arrayOf(g, `comparator ${k}`);
      if (pair.length !== 2) fail(`comparator ${k} must be a pair [i, j], got ${pair.length} entries`);
      const i = safeInt(pair[0], `comparator ${k} wire i`);
      const j = safeInt(pair[1], `comparator ${k} wire j`);
      if (i < 0 || j >= n || i >= j) fail(`comparator ${k} = [${i}, ${j}] must satisfy 0 <= i < j < ${n}`);
      return [i, j] as const;
    });

    const wires = Array.from({ length: n }, (_, w) => wirePattern(w, n));
    for (const [i, j] of gates) {
      const lo = wires[i]! & wires[j]!;
      const hi = wires[i]! | wires[j]!;
      wires[i] = lo;
      wires[j] = hi;
    }
    for (let i = 0; i < n - 1; i++) {
      const unsorted = wires[i]! & ~wires[i + 1]!; // inputs whose output has wire i = 1 above wire i+1 = 0
      if (unsorted === 0n) continue;
      const x = (unsorted & -unsorted).toString(2).length - 1; // lowest such input
      const out = Array.from({ length: n }, (_, w) => (wires[w]! >> BigInt(x)) & 1n).join('');
      const input = Array.from({ length: n }, (_, w) => (x >> w) & 1).join('');
      fail(`the network does not sort the 0-1 input ${input} (wire 0 first): output ${out} has wire ${i} above wire ${i + 1}`);
    }
    return ok(gates.length);
  });
}
