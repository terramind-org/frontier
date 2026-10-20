/**
 * Cap sets in F_3^n: sets with no three distinct points on a line, i.e. no distinct a, b, c with a + b + c = 0.
 * Params: n (dimension). Witness: {"points": [[0,1,2,...], ...]} with each point n entries in {0,1,2}.
 * Value: the number of points.
 *
 * Complexity: O(N^2 n) for N points. For distinct a, b the third point c = -(a+b) is automatically distinct from
 * both, so one hash lookup per pair decides collinearity. N <= 3^n (<= 6561 for n = 8, ~2 s worst case).
 * With `{ all: true }` every duplicate point and every collinear triple (reported once, as i < j < k) is listed.
 */
import { arrayOf, fail, intParam, objectWith, run } from './common.ts';
import type { Params, VerifyOptions, VerifyResult } from './common.ts';

export function verify(witness: unknown, params: Params, opts?: VerifyOptions): VerifyResult {
  const n = intParam(params, 'n', 1, 12);
  return run(opts, (viol) => {
    const obj = objectWith(witness, ['points']);
    const raw = arrayOf(obj.points, '"points"');
    const max = 3 ** n;
    if (raw.length > max) fail(`"points" has ${raw.length} entries but F_3^${n} has only ${max} points`);
    const pts: Int8Array[] = [];
    const ids: number[] = []; // witness index of each kept point
    viol.value = raw.length;
    const codeOf = new Map<number, number>();
    for (let i = 0; i < raw.length; i++) {
      const p = arrayOf(raw[i], `point ${i}`);
      if (p.length !== n) fail(`point ${i} has ${p.length} coordinates, expected ${n}`);
      const v = new Int8Array(n);
      let code = 0;
      for (let d = 0; d < n; d++) {
        const x = p[d];
        if (x !== 0 && x !== 1 && x !== 2) {
          fail(`point ${i} has coordinate ${JSON.stringify(x)} at position ${d}, expected 0, 1 or 2`);
        }
        v[d] = x;
        code = code * 3 + x;
      }
      const prev = codeOf.get(code);
      if (prev !== undefined) {
        viol.add(`points ${ids[prev]} and ${i} are equal (${p.join(',')})`);
        continue;
      }
      codeOf.set(code, pts.length);
      ids.push(i);
      pts.push(v);
    }
    for (let i = 0; i < pts.length; i++) {
      const a = pts[i]!;
      for (let j = i + 1; j < pts.length; j++) {
        const b = pts[j]!;
        let code = 0;
        for (let d = 0; d < n; d++) code = code * 3 + ((6 - a[d]! - b[d]!) % 3);
        const k = codeOf.get(code);
        // all mode lists each triple once, from its two smallest members
        if (k !== undefined && (!viol.all || k > j)) {
          viol.add(() => `points ${ids[i]}, ${ids[j]}, ${ids[k]} are collinear (sum to 0 mod 3): (${a.join(',')}), (${b.join(',')}), (${pts[k]!.join(',')})`);
        }
      }
    }
    return raw.length;
  });
}
