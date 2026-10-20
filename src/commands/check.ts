import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { parse as parseYamlText } from 'yaml';
import { parse, UsageError } from '../args.ts';
import { loadProblem, repoRoot, scanAttempts } from '../repo.ts';
import { Attempt, VerdictResult, writeupLeanFiles } from '../schema.ts';
import type { Problem } from '../schema.ts';
import { validateAttemptDir } from './validate.ts';

export const help = `Check an attempt with the checker for its problem's tier (Lean proof checker or witness verifier).

Usage: bun frontier check <attempt-dir> [--json]

Exit 0 unless the attempt itself is invalid (exit 1). A "rejected" verdict still exits 0: it is the answer.
Writeups are never checked (unchecked).`;

type CheckFn = (input: { repoRoot: string; problem: Problem; attempt: Attempt; attemptDir: string; progress?: boolean }) => Promise<VerdictResult>;

/** Load `src/check/<tier>.ts`; null when the module does not exist. */
export async function loadChecker(tier: string): Promise<CheckFn | null> {
  const file = join(import.meta.dir, '..', 'check', `${tier}.ts`);
  if (!existsSync(file)) return null;
  const mod = (await import(file)) as { check?: CheckFn };
  return mod.check ?? null;
}

/** A verdict's summary without the leading "rejected:" the checker may add, so callers can prefix it once. */
export function plainSummary(r: Pick<VerdictResult, 'summary'>): string {
  return r.summary.replace(/^\s*rejected:\s*/i, '');
}

/** Issues that only matter for submitting: unconfirmed declarations and the scaffold's placeholder claim. */
export function isSubmitOnlyIssue(message: string): boolean {
  return message.startsWith('declarations: not confirmed') || message.startsWith('claim is still the scaffold placeholder');
}

/** Parse attempt.yaml for a local check, treating unconfirmed declarations as confirmed (never written back). */
async function readForCheck(dir: string): Promise<Attempt> {
  const raw = parseYamlText(await readFile(join(dir, 'attempt.yaml'), 'utf8')) as Record<string, unknown>;
  return Attempt.parse({ ...raw, declarations: { rights: true, disclosure_complete: true } });
}

export type CheckOutcome = { invalid: string[] } | { problem: Problem; attempt: Attempt; result: VerdictResult };

export async function checkAttempt(
  root: string,
  dir: string,
  loader: (tier: string) => Promise<CheckFn | null> = loadChecker,
  opts: { progress?: boolean } = {},
): Promise<CheckOutcome> {
  const abs = resolve(dir);
  const issues = await validateAttemptDir(root, abs);
  // A local check judges the work, not the paperwork: an unconfirmed declaration or the placeholder claim
  // does not block it. `validate` and `submit` still require both, so nothing unconfirmed can be submitted.
  const blocking = issues.filter((i) => !isSubmitOnlyIssue(i.message));
  if (blocking.length) return { invalid: blocking.map((i) => `${i.path}: ${i.message}`) };
  const pending = issues.map((i) => i.message);
  const scanned = (await scanAttempts(undefined, root)).find((a) => a.dir === abs)!;
  const attempt = scanned.value ?? (await readForCheck(abs));
  if (pending.length && opts.progress) {
    console.error(`note: checked anyway; before submit: ${pending.join('; ')}`);
  }
  const problem = (await loadProblem(attempt.problem, root))!;
  if (attempt.kind === 'writeup') {
    const lean = writeupLeanFiles(attempt);
    const extra = lean.length ? ` ${lean.join(', ')} ${lean.length === 1 ? 'is' : 'are'} shown with the writeup but not compiled for a verdict.` : '';
    return { problem, attempt, result: { checker: 'none', result: 'unchecked', summary: `Writeups are not machine-checked.${extra}` } };
  }
  const checker = await loader(problem.tier);
  let result: VerdictResult;
  if (!checker) {
    result = { checker: 'none', result: 'error', summary: `no checker for tier ${problem.tier}` };
  } else {
    try {
      result = VerdictResult.parse(await checker({ repoRoot: root, problem, attempt, attemptDir: abs, progress: opts.progress }));
    } catch (e) {
      result = { checker: 'none', result: 'error', summary: `checker failed: ${(e as Error).message}` };
    }
  }
  return { problem, attempt, result };
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { json: { type: 'boolean' } });
  if (positionals.length !== 1) throw new UsageError('check needs exactly one attempt directory');
  // Progress lines go to stderr; --json keeps the output to the verdict alone.
  const outcome = await checkAttempt(repoRoot(), positionals[0]!, loadChecker, { progress: !values.json });
  if ('invalid' in outcome) {
    for (const line of outcome.invalid) console.error(line);
    return 1;
  }
  const r = outcome.result;
  if (values.json) console.log(JSON.stringify(r, null, 2));
  else if (r.result === 'rejected') console.log(`REJECTED: ${plainSummary(r)}`);
  else console.log(`${r.result}: ${r.summary}`);
  return 0;
}
