import { describe, expect, test } from 'bun:test';
import { verify } from '../../../src/check/witness/covering.ts';
import { fixture } from './helpers.ts';

const record = fixture('covering-13-7-4-size30.json') as { blocks: number[][] };
const P = { v: 13, k: 7, t: 4 };

describe('covering', () => {
  test('the La Jolla C(13,7,4) design with 30 blocks is valid', () => {
    expect(verify(record, P)).toEqual({ valid: true, value: 30 });
  });

  test('a tiny design: the 3 pairs-covering of 3 points, C(3,2,2) needs all 3 blocks', () => {
    expect(verify({ blocks: [[1, 2], [1, 3], [2, 3]] }, { v: 3, k: 2, t: 2 })).toEqual({ valid: true, value: 3 });
  });

  test('removing a block leaves a 4-subset uncovered, which is named', () => {
    const r = verify({ blocks: record.blocks.slice(1) }, P);
    expect(r.valid).toBe(false);
    expect(r.reason).toMatch(/^the 4-subset \{[\d, ]+\} is not contained in any block \(\d+ of 715 4-subsets uncovered\)$/);
  });

  test('the uncovered subset reported is really uncovered', () => {
    const r = verify({ blocks: record.blocks.slice(1) }, P);
    const m = /\{([\d, ]+)\}/.exec(r.reason!)!;
    const sub = m[1]!.split(', ').map(Number);
    expect(sub.length).toBe(4);
    expect(record.blocks.slice(1).some((b) => sub.every((x) => b.includes(x)))).toBe(false);
  });

  test('rejects a repeated element, out-of-range element, wrong block size', () => {
    const b = record.blocks.map((x) => [...x]);
    b[0] = [1, 1, 2, 3, 4, 5, 6];
    expect(verify({ blocks: b }, P).reason).toBe('block 0 repeats the element 1');
    b[0] = [1, 2, 3, 4, 5, 6, 14];
    expect(verify({ blocks: b }, P).reason).toBe('block 0 contains 14, outside 1..13');
    b[0] = [0, 2, 3, 4, 5, 6, 7];
    expect(verify({ blocks: b }, P).reason).toContain('outside 1..13');
    b[0] = [1, 2, 3, 4, 5, 6];
    expect(verify({ blocks: b }, P).reason).toBe('block 0 has 6 elements, expected 7');
  });

  test('rejects a repeated block, non-integers and bad shapes', () => {
    expect(verify({ blocks: [record.blocks[0], [...record.blocks[0]!].reverse()] }, P).reason).toBe('blocks 0 and 1 are the same set');
    expect(verify({ blocks: [[1, 2, 3, 4, 5, 6, 7.5]] }, P).reason).toContain('must be an integer');
    expect(verify({ blocks: 'x' }, P).valid).toBe(false);
    expect(verify({ blocks: [], extra: 1 }, P).reason).toContain('unexpected key');
  });

  test('an empty family is rejected as not covering', () => {
    expect(verify({ blocks: [] }, P).valid).toBe(false);
  });
});
