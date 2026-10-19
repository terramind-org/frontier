import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/sortnet.ts';
import { batcher } from './cs-constructions.ts';

/** Independent check: run every 0-1 input through the gates one at a time. */
function sortsAllBinaryInputs(n: number, gates: Array<[number, number]>): boolean {
  for (let x = 0; x < 1 << n; x++) {
    const w = Array.from({ length: n }, (_, k) => (x >> k) & 1);
    for (const [i, j] of gates) if (w[i]! > w[j]!) [w[i], w[j]] = [w[j]!, w[i]!];
    for (let k = 0; k + 1 < n; k++) if (w[k]! > w[k + 1]!) return false;
  }
  return true;
}

describe('sortnet', () => {
  test('the optimal 5-gate network on 4 wires is valid', () => {
    expect(verify({ comparators: [[0, 1], [2, 3], [0, 2], [1, 3], [1, 2]] }, { n: 4 })).toEqual({ valid: true, value: 5 });
  });

  test("Batcher's odd-even merge sort is valid for n = 2..20 and matches the known gate counts", () => {
    const known: Record<number, number> = { 2: 1, 3: 3, 4: 5, 8: 19, 16: 63 }; // OEIS A006282
    for (let n = 2; n <= 20; n++) {
      const gates = batcher(n);
      expect(verify({ comparators: gates }, { n })).toEqual({ valid: true, value: gates.length });
      if (known[n] !== undefined) expect(gates.length).toBe(known[n]!);
    }
  });

  test('valid networks above the record sizes at n = 13 and n = 18 do not reach the best known', () => {
    for (const n of [13, 18]) {
      const gates = batcher(n);
      const r = verify({ comparators: gates }, { n });
      expect(r.valid).toBe(true);
      expect(r.value!).toBeGreaterThan(n === 13 ? 45 : 77);
    }
  });

  test('agrees with a brute-force 0-1 check on random networks (valid and invalid)', () => {
    let seed = 12345;
    const rand = (m: number) => ((seed = (seed * 1103515245 + 12345) % 2 ** 31), seed % m);
    let valid = 0;
    let invalid = 0;
    for (let t = 0; t < 300; t++) {
      const n = 3 + rand(5);
      const base = batcher(n);
      // either drop one gate (often breaks it) or insert up to two random gates (often keeps it sorting)
      const gates = [...base];
      if (rand(2)) gates.splice(rand(gates.length), 1);
      else {
        for (let k = rand(3); k > 0; k--) {
          const i = rand(n - 1);
          gates.splice(rand(gates.length + 1), 0, [i, i + 1 + rand(n - 1 - i)]);
        }
      }
      const r = verify({ comparators: gates }, { n });
      expect(r.valid).toBe(sortsAllBinaryInputs(n, gates));
      if (r.valid) valid++;
      else invalid++;
    }
    expect(valid).toBeGreaterThan(10);
    expect(invalid).toBeGreaterThan(10);
  });

  test('a network missing its last gate is rejected with a concrete 0-1 counterexample', () => {
    const gates = [[0, 1], [2, 3], [0, 2], [1, 3]];
    const r = verify({ comparators: gates }, { n: 4 });
    expect(r.valid).toBe(false);
    expect(r.reason).toBe('the network does not sort the 0-1 input 1010 (wire 0 first): output 0101 has wire 1 above wire 2');
  });

  test('rejects out-of-range, reversed and malformed gates, non-integers and unknown keys', () => {
    expect(verify({ comparators: [[0, 4]] }, { n: 4 }).reason).toBe('comparator 0 = [0, 4] must satisfy 0 <= i < j < 4');
    expect(verify({ comparators: [[0, 1], [3, 2]] }, { n: 4 }).reason).toBe('comparator 1 = [3, 2] must satisfy 0 <= i < j < 4');
    expect(verify({ comparators: [[1, 1]] }, { n: 4 }).reason).toContain('0 <= i < j');
    expect(verify({ comparators: [[-1, 1]] }, { n: 4 }).reason).toContain('0 <= i < j');
    expect(verify({ comparators: [[0, 1, 2]] }, { n: 4 }).reason).toBe('comparator 0 must be a pair [i, j], got 3 entries');
    expect(verify({ comparators: [[0, 0.5]] }, { n: 4 }).reason).toContain('must be an integer');
    expect(verify({ comparators: [['0', '1']] }, { n: 4 }).valid).toBe(false);
    expect(verify({ comparators: 'x' }, { n: 4 }).reason).toBe('"comparators" must be an array');
    expect(verify({ comparators: [], other: 1 }, { n: 4 }).reason).toContain('unexpected key');
    expect(verify({}, { n: 4 }).reason).toContain('missing the key');
    expect(verify({ comparators: new Array(5001).fill([0, 1]) }, { n: 4 }).reason).toContain('at most 5000');
  });

  test('the empty network sorts only a single wire; n = 2 needs exactly one gate', () => {
    expect(verify({ comparators: [] }, { n: 2 }).valid).toBe(false);
    expect(verify({ comparators: [[0, 1]] }, { n: 2 })).toEqual({ valid: true, value: 1 });
  });

  test('n = 24 stays within a few seconds', () => {
    const start = performance.now();
    const gates = batcher(24);
    expect(verify({ comparators: gates }, { n: 24 })).toEqual({ valid: true, value: gates.length });
    expect(performance.now() - start).toBeLessThan(10_000);
  });
});
