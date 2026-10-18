import { readFileSync } from 'node:fs';
import { join } from 'node:path';

export const FIXTURES = join(import.meta.dir, '..', '..', 'fixtures', 'witness');
export const fixture = (name: string): any => JSON.parse(readFileSync(join(FIXTURES, name), 'utf8'));

/** Paley graph on q vertices (q prime, q = 1 mod 4) as the Ramsey witness format. */
export function paley(q: number): { n: number; adjacency: string[] } {
  const squares = new Set<number>();
  for (let x = 1; x < q; x++) squares.add((x * x) % q);
  const adjacency = Array.from({ length: q }, (_, i) =>
    Array.from({ length: q }, (_, j) => (i !== j && squares.has((((i - j) % q) + q) % q) ? '1' : '0')).join(''),
  );
  return { n: q, adjacency };
}

/** Independent brute-force check that no three distinct points of `pts` sum to 0 mod 3. */
export function bruteForceCap(pts: number[][]): boolean {
  for (let i = 0; i < pts.length; i++)
    for (let j = i + 1; j < pts.length; j++)
      for (let k = j + 1; k < pts.length; k++)
        if (pts[i]!.every((x, d) => (x + pts[j]![d]! + pts[k]![d]!) % 3 === 0)) return false;
  return true;
}
