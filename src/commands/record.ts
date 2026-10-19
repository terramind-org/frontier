import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { parse, UsageError } from '../args.ts';
import { repoRoot, writeJson } from '../repo.ts';
import { Attempt, Verdict, VerdictResult } from '../schema.ts';

export const help = `Write verdict.json for an attempt from a checker's VerdictResult JSON. Run by CI on main only.

Usage: bun frontier record <attempt-dir> --result-file <path> [--run-url <url>] [--force]

  --result-file <path>  JSON file holding a VerdictResult (the output of \`frontier check --json\` or lean-check)
  --run-url <url>       the Actions run that produced the result
  --force               overwrite an existing verdict.json
The verdict gets the attempt id, the current time and the current git commit as checker_version.`;

async function gitHead(root: string): Promise<string> {
  const p = Bun.spawn(['git', 'rev-parse', 'HEAD'], { cwd: root, stdout: 'pipe', stderr: 'pipe' });
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  if (code !== 0) throw new Error(`git rev-parse HEAD failed: ${err.trim()}`);
  return out.trim();
}

export interface RecordOptions {
  resultFile: string;
  runUrl?: string;
  force?: boolean;
  now?: Date;
}

/** Build and write `<attemptDir>/verdict.json`; returns the verdict. Never runs attempt code. */
export async function recordVerdict(root: string, attemptDir: string, opts: RecordOptions): Promise<Verdict> {
  const dir = resolve(attemptDir);
  const target = join(dir, 'verdict.json');
  if (existsSync(target) && !opts.force) {
    throw new Error(`${target} already exists (verdicts are immutable; use --force to overwrite)`);
  }
  const yamlPath = join(dir, 'attempt.yaml');
  if (!existsSync(yamlPath)) throw new Error(`${dir} has no attempt.yaml`);
  const attempt = Attempt.parse(parseYaml(await readFile(yamlPath, 'utf8')));

  let raw: unknown;
  try {
    raw = JSON.parse(await readFile(resolve(opts.resultFile), 'utf8'));
  } catch (e) {
    throw new Error(`cannot read ${opts.resultFile}: ${(e as Error).message}`);
  }
  const parsed = VerdictResult.safeParse(raw);
  if (!parsed.success) {
    throw new Error(`${opts.resultFile} is not a VerdictResult: ${parsed.error.issues.map((i) => `${i.path.join('.') || '(root)'}: ${i.message}`).join('; ')}`);
  }

  const verdict = Verdict.parse({
    ...parsed.data,
    schema: 1,
    attempt: attempt.id,
    checked_at: (opts.now ?? new Date()).toISOString(),
    checker_version: await gitHead(root),
    ...(opts.runUrl ? { run_url: opts.runUrl } : {}),
  });
  await writeJson(target, verdict, Verdict);
  return verdict;
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, {
    'result-file': { type: 'string' },
    'run-url': { type: 'string' },
    force: { type: 'boolean' },
  });
  if (positionals.length !== 1) throw new UsageError('record needs exactly one attempt directory');
  const resultFile = values['result-file'];
  if (typeof resultFile !== 'string') throw new UsageError('record needs --result-file');
  const verdict = await recordVerdict(repoRoot(), positionals[0]!, {
    resultFile,
    runUrl: values['run-url'] as string | undefined,
    force: values.force === true,
  });
  console.log(`recorded ${verdict.result} for ${verdict.attempt}`);
  return 0;
}
