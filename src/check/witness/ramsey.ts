/**
 * Ramsey colourings: a 2-colouring of the edges of K_n with no K_s in colour 1 and no K_t in colour 0.
 * Params: ones_free (s), zeros_free (t). Witness: {"n": 42, "adjacency": ["0011...", ...]}, n strings of n
 * characters '0'/'1', symmetric, zero diagonal; a '1' is a colour-1 edge, a '0' off the diagonal a colour-0 edge.
 * Value: n.
 *
 * Complexity: clique search with bitsets (BigInt) and a size bound, O(n^s)-ish worst case but milliseconds for
 * n <= 60 and s, t <= 6. n is capped at 128 so a hostile witness cannot stall the checker.
 */
import { arrayOf, fail, guard, intParam, objectWith, ok, safeInt } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

const MAX_N = 128;

function popcount(x: bigint): number {
  let c = 0;
  while (x > 0n) {
    x &= x - 1n;
    c++;
  }
  return c;
}

/** Find a clique of `size` vertices in the graph given as neighbour bitsets, or null. */
function findClique(adj: bigint[], size: number): number[] | null {
  const n = adj.length;
  const chosen: number[] = [];
  const extend = (cand: bigint, need: number): boolean => {
    if (need === 0) return true;
    if (popcount(cand) < need) return false;
    while (cand > 0n) {
      const low = cand & -cand;
      const v = low.toString(2).length - 1;
      cand ^= low; // later candidates only: each clique is found from its smallest vertex
      chosen.push(v);
      if (extend(cand & adj[v]!, need - 1)) return true;
      chosen.pop();
      if (popcount(cand) < need) return false;
    }
    return false;
  };
  return extend((1n << BigInt(n)) - 1n, size) ? [...chosen] : null;
}

export function verify(witness: unknown, params: Params): VerifyResult {
  const s = intParam(params, 'ones_free', 2, 12);
  const t = intParam(params, 'zeros_free', 2, 12);
  return guard(() => {
    const obj = objectWith(witness, ['n', 'adjacency']);
    const n = safeInt(obj.n, '"n"');
    if (n < 1 || n > MAX_N) fail(`"n" must be between 1 and ${MAX_N} (got ${n})`);
    const rows = arrayOf(obj.adjacency, '"adjacency"');
    if (rows.length !== n) fail(`"adjacency" has ${rows.length} rows, expected n = ${n}`);
    const ones: bigint[] = new Array(n).fill(0n);
    const zeros: bigint[] = new Array(n).fill(0n);
    const grid: string[] = [];
    for (let i = 0; i < n; i++) {
      const row = rows[i];
      if (typeof row !== 'string') return fail(`row ${i} must be a string of '0' and '1'`);
      if (row.length !== n) fail(`row ${i} has length ${row.length}, expected ${n}`);
      if (!/^[01]*$/.test(row)) fail(`row ${i} contains a character other than '0' or '1'`);
      grid.push(row);
    }
    for (let i = 0; i < n; i++) {
      if (grid[i]![i] !== '0') fail(`diagonal entry (${i},${i}) must be '0'`);
      for (let j = i + 1; j < n; j++) {
        if (grid[i]![j] !== grid[j]![i]) fail(`matrix is not symmetric at (${i},${j}) and (${j},${i})`);
        if (grid[i]![j] === '1') {
          ones[i]! |= 1n << BigInt(j);
          ones[j]! |= 1n << BigInt(i);
        } else {
          zeros[i]! |= 1n << BigInt(j);
          zeros[j]! |= 1n << BigInt(i);
        }
      }
    }
    const k1 = findClique(ones, s);
    if (k1) fail(`vertices ${k1.join(', ')} form a K${s} of colour-1 edges`);
    const k0 = findClique(zeros, t);
    if (k0) fail(`vertices ${k0.join(', ')} form a K${t} of colour-0 edges`);
    return ok(n);
  });
}
