/**
 * Golomb rulers: m integer marks starting at 0 whose pairwise differences are all distinct.
 * Params: marks (m). Witness: {"marks": [0, a1, ..., a_{m-1}]}, strictly increasing integers.
 * Value: the length, i.e. the largest mark (to be minimised).
 *
 * Complexity: O(m^2) differences with a hash set.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

export function verify(witness: unknown, params: Params): VerifyResult {
  const m = intParam(params, 'marks', 2, 5000);
  return guard(() => {
    const obj = objectWith(witness, ['marks']);
    const raw = arrayOf(obj.marks, '"marks"');
    if (raw.length !== m) fail(`"marks" has ${raw.length} entries, expected exactly ${m}`);
    const marks = raw.map((x, i) => safeInt(x, `mark ${i}`));
    if (marks[0] !== 0) fail(`the first mark must be 0 (got ${marks[0]})`);
    for (let i = 1; i < m; i++) {
      if (marks[i]! <= marks[i - 1]!) fail(`marks must be strictly increasing: mark ${i} = ${marks[i]} is not above mark ${i - 1} = ${marks[i - 1]}`);
    }
    const seen = new Map<number, [number, number]>();
    for (let i = 0; i < m; i++) {
      for (let j = i + 1; j < m; j++) {
        const d = marks[j]! - marks[i]!;
        const prev = seen.get(d);
        if (prev) {
          fail(`difference ${d} occurs twice: ${marks[prev[1]]} - ${marks[prev[0]]} and ${marks[j]} - ${marks[i]}`);
        }
        seen.set(d, [i, j]);
      }
    }
    return ok(marks[m - 1]!);
  });
}
