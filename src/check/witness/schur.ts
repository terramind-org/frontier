/**
 * Schur partitions: colour 1..N with k colours so that no colour class contains x, y, z (x = y allowed) with
 * x + y = z. Params: k (number of colours). Witness: {"colors": [c_1, ..., c_N]}, c_i in 0..k-1 the class of i.
 * Value: N (to be maximised).
 *
 * Complexity: sum over classes of |S|^2 / 2, about 4e5 steps at N = 1696. N is capped at 5000.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

const MAX_N = 5000;

export function verify(witness: unknown, params: Params): VerifyResult {
  const k = intParam(params, 'k', 1, 64);
  return guard(() => {
    const obj = objectWith(witness, ['colors']);
    const raw = arrayOf(obj.colors, '"colors"');
    const N = raw.length;
    if (N === 0) fail('"colors" is empty');
    if (N > MAX_N) fail(`"colors" has ${N} entries; the verifier accepts at most ${MAX_N}`);
    const colors = raw.map((x, i) => {
      const c = safeInt(x, `colour of ${i + 1}`);
      if (c < 0 || c >= k) fail(`colour of ${i + 1} is ${c}, expected 0..${k - 1}`);
      return c;
    });
    const classes: number[][] = Array.from({ length: k }, () => []);
    for (let i = 0; i < N; i++) classes[colors[i]!]!.push(i + 1);
    for (let c = 0; c < k; c++) {
      const members = classes[c]!;
      for (let i = 0; i < members.length; i++) {
        const a = members[i]!;
        for (let j = i; j < members.length; j++) {
          const b = members[j]!;
          const sum = a + b;
          if (sum > N) break;
          if (colors[sum - 1] === c) {
            fail(a === b ? `${a} + ${a} = ${sum} all have colour ${c}` : `${a} + ${b} = ${sum} all have colour ${c}`);
          }
        }
      }
    }
    return ok(N);
  });
}
