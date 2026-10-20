#!/usr/bin/env bun
/**
 * Compile the `sorry` scaffold `bun frontier new` writes for each given problem, one at a time, with
 * `lake env lean` inside lean/ (the fast loop; it needs the shared Mathlib cache at lean/.lake).
 *
 *   bun scripts/compile-scaffolds.ts <problem-id>...
 *   bun scripts/compile-scaffolds.ts --sample N [--seed s]
 *   bun scripts/compile-scaffolds.ts --ids-file ids.txt          (one id per line, # comments allowed)
 *
 * Per id it prints `ok` or the first error line. A "declaration uses sorry" warning is the expected
 * result and counts as ok. Exits 1 if any scaffold fails for another reason (including a source
 * pre-check rejection), 2 on a usage mistake.
 */
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { parse, UsageError } from '../src/args.ts';
import { leanTemplate } from '../src/commands/new.ts';
import { mulberry32, seedState } from '../src/commands/pick.ts';
import { loadProblems, repoRoot } from '../src/repo.ts';
import type { Problem } from '../src/schema.ts';

export interface CompileOutcome {
  ok: boolean;
  /** `ok`, or the first error line. */
  detail: string;
  seconds: number;
}

/** First useful line of Lean's output: the first `error` line, else the first non-empty line. */
export function firstErrorLine(output: string): string {
  const lines = output
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean);
  const err = lines.find((l) => /\berror\b/i.test(l));
  return (err ?? lines[0] ?? 'lean failed without output').replace(/^.*?\/Scaffold\.lean:/, 'Scaffold.lean:');
}

/** Whether Lean's output holds an error (warnings, including the sorry warning, are fine). */
export function hasError(output: string): boolean {
  return output.split('\n').some((l) => /^\S.*:\d+:\d+: error\b/.test(l) || /^error\b/.test(l.trim()));
}

async function run(cmd: string[], cwd: string, timeoutMs: number): Promise<{ code: number; text: string; timedOut: boolean }> {
  const p = Bun.spawn(cmd, { cwd, stdout: 'pipe', stderr: 'pipe', stdin: 'ignore' });
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    p.kill();
  }, timeoutMs);
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  clearTimeout(timer);
  return { code, text: `${out}\n${err}`, timedOut };
}

/** Compile one problem's proof scaffold; never throws for a Lean failure. */
export async function compileScaffold(root: string, problem: Problem, timeoutMs: number): Promise<CompileOutcome> {
  const started = Date.now();
  const done = (ok: boolean, detail: string): CompileOutcome => ({ ok, detail, seconds: (Date.now() - started) / 1000 });
  if (!problem.lean) return done(false, 'problem has no lean block');
  let text: string;
  try {
    text = leanTemplate(problem, 'proof');
  } catch (e) {
    return done(false, `cannot build the scaffold: ${(e as Error).message}`);
  }
  const tmp = mkdtempSync(join(tmpdir(), 'frontier-scaffold-'));
  try {
    const file = join(tmp, 'Scaffold.lean');
    writeFileSync(file, text);
    // The checker's own source pre-check must accept the scaffold (it needs no Lean).
    const pre = await run(['bash', join(root, 'lean', 'check-attempt.sh'), '--precheck', file], root, 60_000);
    const reason = pre.text.trim();
    if (reason) return done(false, `pre-check: ${reason.split('\n')[0]}`);
    const r = await run(['lake', 'env', 'lean', file], join(root, 'lean'), timeoutMs);
    if (r.timedOut) return done(false, `timed out after ${Math.round(timeoutMs / 1000)}s`);
    if (r.code !== 0 || hasError(r.text)) return done(false, firstErrorLine(r.text));
    return done(true, 'ok');
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

/** Seeded sample of `n` ids from the problems whose scaffold `new` can write (Lean block, not answer-required). */
export function sampleIds(problems: Problem[], n: number, seed: string): string[] {
  const pool = problems
    .filter((p) => p.lean && !p.tags.includes('answer-required'))
    .map((p) => p.id)
    .sort();
  const rand = mulberry32(seedState(seed));
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [pool[i], pool[j]] = [pool[j]!, pool[i]!];
  }
  return pool.slice(0, n);
}

async function main(argv: string[]): Promise<number> {
  const { values, positionals } = parse(argv, {
    sample: { type: 'string' },
    seed: { type: 'string' },
    'ids-file': { type: 'string' },
    timeout: { type: 'string' },
    help: { type: 'boolean' },
  });
  if (values.help) {
    console.log('Usage: bun scripts/compile-scaffolds.ts <problem-id>... | --sample N [--seed s] | --ids-file file  [--timeout seconds]');
    return 0;
  }
  const root = repoRoot();
  const problems = await loadProblems(root);
  const ids = [...positionals];
  if (values['ids-file']) {
    ids.push(
      ...readFileSync(values['ids-file'], 'utf8')
        .split('\n')
        .map((l) => l.replace(/#.*/, '').trim())
        .filter(Boolean),
    );
  }
  if (values.sample !== undefined) {
    const n = Number(values.sample);
    if (!Number.isInteger(n) || n < 1) throw new UsageError('--sample needs a positive integer');
    ids.push(...sampleIds(problems, n, values.seed ?? 'compile-scaffolds'));
  }
  if (!ids.length) throw new UsageError('give problem ids, --sample N or --ids-file');
  const timeout = values.timeout === undefined ? 900 : Number(values.timeout);
  if (!(timeout > 0)) throw new UsageError('--timeout must be a positive number of seconds');

  const byId = new Map(problems.map((p) => [p.id, p]));
  const unique = [...new Set(ids)];
  let failed = 0;
  for (const [i, id] of unique.entries()) {
    const problem = byId.get(id);
    const r = problem ? await compileScaffold(root, problem, timeout * 1000) : { ok: false, detail: 'no such problem', seconds: 0 };
    if (!r.ok) failed++;
    console.log(`[${i + 1}/${unique.length}] ${r.ok ? 'ok  ' : 'FAIL'} ${id} (${r.seconds.toFixed(1)}s)${r.ok ? '' : `: ${r.detail}`}`);
  }
  console.log(`\n${unique.length - failed} ok, ${failed} failed of ${unique.length}`);
  return failed ? 1 : 0;
}

if (import.meta.main) {
  try {
    process.exit(await main(process.argv.slice(2)));
  } catch (e) {
    if (e instanceof UsageError) {
      console.error(e.message);
      process.exit(2);
    }
    throw e;
  }
}
