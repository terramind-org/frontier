/**
 * Superpermutations: a string over the symbols 1..n in which every one of the n! orderings of the n symbols occurs
 * as a run of n consecutive characters. Params: n (2..9, so each symbol is one digit).
 * Witness: {"word": "1234512314..."}, digits 1..n only, no whitespace. Value: the length of the word (to be minimised).
 *
 * Exactness: every window of n characters with n distinct symbols is a permutation; the check counts the distinct
 * ones and requires n!. The first missing permutation, in lexicographic order, is named on failure.
 *
 * Complexity: O(L * n) for a word of length L, plus O(n! * n) only when naming a missing permutation.
 */
import { fail, guard, intParam, objectWith, ok } from './common.ts';
import type { Params, VerifyResult } from './common.ts';

const MAX_LENGTH = 2_000_000;

function firstMissing(n: number, seen: Set<string>): string {
  const used = new Array<boolean>(n + 1).fill(false);
  const prefix: number[] = [];
  const walk = (): string | null => {
    if (prefix.length === n) {
      const p = prefix.join('');
      return seen.has(p) ? null : p;
    }
    for (let s = 1; s <= n; s++) {
      if (used[s]) continue;
      used[s] = true;
      prefix.push(s);
      const hit = walk();
      prefix.pop();
      used[s] = false;
      if (hit) return hit;
    }
    return null;
  };
  return walk() ?? '';
}

export function verify(witness: unknown, params: Params): VerifyResult {
  const n = intParam(params, 'n', 2, 9);
  return guard(() => {
    const obj = objectWith(witness, ['word']);
    const word = obj.word;
    if (typeof word !== 'string') fail('"word" must be a string');
    if (word.length > MAX_LENGTH) fail(`"word" has ${word.length} characters, at most ${MAX_LENGTH} are accepted`);
    if (word.length < n) fail(`"word" has ${word.length} characters, fewer than ${n}`);
    const digits = new Set(Array.from({ length: n }, (_, k) => String(k + 1)));
    for (let k = 0; k < word.length; k++) {
      if (!digits.has(word[k]!)) fail(`character ${k} is ${JSON.stringify(word[k])}, expected a digit from 1 to ${n}`);
    }
    let factorial = 1;
    for (let k = 2; k <= n; k++) factorial *= k;
    const seen = new Set<string>();
    for (let k = 0; k + n <= word.length; k++) {
      const window = word.slice(k, k + n);
      if (new Set(window).size === n) seen.add(window);
    }
    if (seen.size !== factorial) {
      fail(`only ${seen.size} of the ${factorial} permutations of ${n} symbols occur; the first missing one is ${firstMissing(n, seen)}`);
    }
    return ok(word.length);
  });
}
