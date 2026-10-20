/**
 * Golomb rulers: m integer marks starting at 0 whose pairwise differences are all distinct.
 * Params: marks (m). Witness: {"marks": [0, a1, ..., a_{m-1}]}, strictly increasing integers.
 * Value: the length, i.e. the largest mark (to be minimised).
 *
 * Complexity: O(m^2) differences with a hash set.
 * With `{ all: true }` a wrong count, a nonzero start, every non-increasing step and every repeated difference
 * (each later occurrence against the first) is listed.
 */
import { arrayOf, fail, intParam, objectWith, run, safeInt } from './common.ts';
import type { Params, VerifyOptions, VerifyResult } from './common.ts';

export function verify(witness: unknown, params: Params, opts?: VerifyOptions): VerifyResult {
  const m = intParam(params, 'marks', 2, 5000);
  return run(opts, (viol) => {
    const obj = objectWith(witness, ['marks']);
    const raw = arrayOf(obj.marks, '"marks"');
    if (raw.length !== m) viol.add(`"marks" has ${raw.length} entries, expected exactly ${m}`);
    if (raw.length === 0) fail('"marks" is empty');
    const marks = raw.map((x, i) => safeInt(x, `mark ${i}`));
    const n = marks.length;
    viol.value = marks[n - 1]!;
    if (marks[0] !== 0) viol.add(`the first mark must be 0 (got ${marks[0]})`);
    for (let i = 1; i < n; i++) {
      if (marks[i]! <= marks[i - 1]!) {
        viol.add(`marks must be strictly increasing: mark ${i} = ${marks[i]} is not above mark ${i - 1} = ${marks[i - 1]}`);
      }
    }
    const seen = new Map<number, [number, number]>();
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const d = marks[j]! - marks[i]!;
        if (d <= 0) continue; // an order violation, already listed
        const prev = seen.get(d);
        if (prev) {
          viol.add(() => `difference ${d} occurs twice: ${marks[prev[1]]} - ${marks[prev[0]]} and ${marks[j]} - ${marks[i]}`);
        } else seen.set(d, [i, j]);
      }
    }
    return marks[n - 1]!;
  });
}
