import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { parse, UsageError } from '../args.ts';
import { loadProblem, repoRoot, scanAttempts } from '../repo.ts';
import { VerdictResult } from '../schema.ts';
import type { Attempt, Problem } from '../schema.ts';
import { validateAttemptDir } from './validate.ts';

export const help = `Check an attempt with the checker for its problem's tier (Lean proof checker or witness verifier).

Usage: bun frontier check <attempt-dir> [--json]

Exit 0 unless the attempt itself is invalid (exit 1). A "rejected" verdict still exits 0: it is the answer.
Writeups are never checked (unchecked).`;

type CheckFn = (input: { repoRoot: string; problem: Problem; attempt: Attempt; attemptDir: string }) => Promise<VerdictResult>;

/** Load `src/check/<tier>.ts`; null when the module does not exist. */
export async function loadChecker(tier: string): Promise<CheckFn | null> {
  const file = join(import.meta.dir, '..', 'check', `${tier}.ts`);
  if (!existsSync(file)) return null;
  const mod = (await import(file)) as { check?: CheckFn };
  return mod.check ?? null;
}

export type CheckOutcome = { invalid: string[] } | { problem: Problem; attempt: Attempt; result: VerdictResult };

export async function checkAttempt(
  root: string,
  dir: string,
  loader: (tier: string) => Promise<CheckFn | null> = loadChecker,
): Promise<CheckOutcome> {
  const abs = resolve(dir);
  const issues = await validateAttemptDir(root, abs);
  if (issues.length) return { invalid: issues.map((i) => `${i.path}: ${i.message}`) };
  const scanned = (await scanAttempts(undefined, root)).find((a) => a.dir === abs)!;
  const attempt = scanned.value!;
  const problem = (await loadProblem(attempt.problem, root))!;
  if (attempt.kind === 'writeup') {
    return { problem, attempt, result: { checker: 'none', result: 'unchecked', summary: 'Writeups are not machine-checked.' } };
  }
  const checker = await loader(problem.tier);
  let result: VerdictResult;
  if (!checker) {
    result = { checker: 'none', result: 'error', summary: `no checker for tier ${problem.tier}` };
  } else {
    try {
      result = VerdictResult.parse(await checker({ repoRoot: root, problem, attempt, attemptDir: abs }));
    } catch (e) {
      result = { checker: 'none', result: 'error', summary: `checker failed: ${(e as Error).message}` };
    }
  }
  return { problem, attempt, result };
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { json: { type: 'boolean' } });
  if (positionals.length !== 1) throw new UsageError('check needs exactly one attempt directory');
  const outcome = await checkAttempt(repoRoot(), positionals[0]!);
  if ('invalid' in outcome) {
    for (const line of outcome.invalid) console.error(line);
    return 1;
  }
  const r = outcome.result;
  if (values.json) console.log(JSON.stringify(r, null, 2));
  else if (r.result === 'rejected') console.log(`REJECTED: ${r.summary}`);
  else console.log(`${r.result}: ${r.summary}`);
  return 0;
}
