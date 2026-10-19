import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { delimiter, join } from 'node:path';
import { VerdictResult } from '../schema.ts';
import type { Attempt, Problem } from '../schema.ts';

export interface CheckInput {
  repoRoot: string;
  problem: Problem;
  attempt: Attempt;
  attemptDir: string;
}

/** The Lean project that ships with this checker (not the repo being checked, which may be a fixture). */
export const LEAN_DIR = join(import.meta.dir, '..', '..', 'lean');
export const RUNNER = join(LEAN_DIR, 'check-attempt.sh');

const NOT_INSTALLED: VerdictResult = {
  checker: 'lean',
  result: 'error',
  summary: 'Lean is not installed here; CI will check this attempt',
};

/** Directory holding `lake`: PATH first, then ~/.elan/bin. Null when Lean is not installed. */
export function findLakeDir(env: NodeJS.ProcessEnv = process.env): string | null {
  for (const dir of (env.PATH ?? '').split(delimiter)) {
    if (dir && existsSync(join(dir, 'lake'))) return dir;
  }
  const elan = join(env.HOME ?? homedir(), '.elan', 'bin');
  return existsSync(join(elan, 'lake')) ? elan : null;
}

/** Run the two-phase runner on a solution file and parse its single JSON line. */
export async function runLeanCheck(
  solutionFile: string,
  decl: string,
  kind: 'proof' | 'disproof',
  opts: { env?: NodeJS.ProcessEnv; timeoutMs?: number } = {},
): Promise<VerdictResult> {
  const env = opts.env ?? process.env;
  const lakeDir = findLakeDir(env);
  if (!lakeDir) return NOT_INSTALLED;
  const proc = Bun.spawn(['bash', RUNNER, solutionFile, decl, kind], {
    env: { ...env, PATH: `${lakeDir}${delimiter}${env.PATH ?? ''}` },
    stdout: 'pipe',
    stderr: 'pipe',
  });
  // The runner enforces CHECK_TIMEOUT per phase; this outer limit catches a hung runner.
  const timeoutMs = opts.timeoutMs ?? (Number(env.CHECK_TIMEOUT ?? 1200) * 2 + 900) * 1000;
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    proc.kill('SIGKILL');
  }, timeoutMs);
  const [out, err, code] = await Promise.all([new Response(proc.stdout).text(), new Response(proc.stderr).text(), proc.exited]);
  clearTimeout(timer);
  if (timedOut) return { checker: 'lean', result: 'error', summary: `Lean check timed out after ${Math.round(timeoutMs / 1000)}s` };
  const line = out.trim().split('\n').filter((l) => l.startsWith('{')).at(-1);
  if (code !== 0 || !line) {
    const detail = (err.trim().split('\n').at(-1) ?? '').slice(0, 300);
    return { checker: 'lean', result: 'error', summary: `Lean checker failed (exit ${code})${detail ? `: ${detail}` : ''}` };
  }
  try {
    return VerdictResult.parse(JSON.parse(line));
  } catch (e) {
    return { checker: 'lean', result: 'error', summary: `Lean checker printed an unreadable verdict: ${(e as Error).message.slice(0, 200)}` };
  }
}

export async function check(input: CheckInput): Promise<VerdictResult> {
  const { problem, attempt, attemptDir } = input;
  if (!problem.lean) return { checker: 'lean', result: 'error', summary: `problem ${problem.id} has no lean block` };
  if (attempt.kind !== 'proof' && attempt.kind !== 'disproof') {
    return { checker: 'lean', result: 'error', summary: `the Lean checker does not check "${attempt.kind}" attempts` };
  }
  return runLeanCheck(join(attemptDir, 'solution.lean'), problem.lean.decl, attempt.kind);
}
