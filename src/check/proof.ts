import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { delimiter, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { VerdictResult } from '../schema.ts';
import type { Attempt, Problem } from '../schema.ts';

export interface CheckInput {
  repoRoot: string;
  problem: Problem;
  attempt: Attempt;
  attemptDir: string;
  /** Print the runner's progress lines ("[1/3] building attempt…") to stderr. Default true; `--json` turns it off. */
  progress?: boolean;
}

/** The Lean project that ships with this checker (not the repo being checked, which may be a fixture). */
// import.meta.url, not bun's import.meta.dir: this runs at load time in the node bundle (dist-cli) too.
export const LEAN_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'lean');
export const RUNNER = join(LEAN_DIR, 'check-attempt.sh');

const NOT_INSTALLED: VerdictResult = {
  checker: 'lean',
  result: 'error',
  summary: 'Lean is not installed here; CI will check this attempt',
};

const ANSWER_REQUIRED_UNCHECKED: VerdictResult = {
  checker: 'lean',
  result: 'unchecked',
  summary:
    'This problem asks for an answer that upstream leaves as sorry; automatic checking of answer problems is not supported yet. Submit a writeup.',
};

/** The runner's progress lines on stderr, e.g. "[2/3] kernel replay and statement check…". */
export const PROGRESS_LINE = /^\[\d\/\d\] /;

/** Directory holding `lake`: PATH first, then ~/.elan/bin. Null when Lean is not installed. */
export function findLakeDir(env: NodeJS.ProcessEnv = process.env): string | null {
  for (const dir of (env.PATH ?? '').split(delimiter)) {
    if (dir && existsSync(join(dir, 'lake'))) return dir;
  }
  const elan = join(env.HOME ?? homedir(), '.elan', 'bin');
  return existsSync(join(elan, 'lake')) ? elan : null;
}

/** Read a stream line by line, calling `onLine` for each complete line; resolves to the whole text. */
async function readLines(stream: ReadableStream<Uint8Array>, onLine: (line: string) => void): Promise<string> {
  const decoder = new TextDecoder();
  let all = '';
  let pending = '';
  for await (const chunk of stream) {
    const text = decoder.decode(chunk, { stream: true });
    all += text;
    pending += text;
    let nl: number;
    while ((nl = pending.indexOf('\n')) >= 0) {
      onLine(pending.slice(0, nl));
      pending = pending.slice(nl + 1);
    }
  }
  const rest = decoder.decode();
  all += rest;
  pending += rest;
  if (pending) onLine(pending);
  return all;
}

/**
 * The runner compiles the attempt as `Attempt/Solution.lean`; show the file the author edits instead.
 * Line and column numbers are unchanged, since the file is copied verbatim.
 */
export function mapSolutionPath(v: VerdictResult, shownPath: string): VerdictResult {
  const swap = (s: string) => s.replaceAll('Attempt/Solution.lean', shownPath);
  if (!v.lean) return { ...v, summary: swap(v.summary) };
  const lean = v.lean.reason === undefined ? v.lean : { ...v.lean, reason: swap(v.lean.reason) };
  return { ...v, summary: swap(v.summary), lean };
}

/** Run the two-phase runner on a solution file and parse its single JSON line. */
export async function runLeanCheck(
  solutionFile: string,
  decl: string,
  kind: 'proof' | 'disproof',
  opts: { env?: NodeJS.ProcessEnv; timeoutMs?: number; onProgress?: (line: string) => void } = {},
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
  const onStderr = (line: string) => {
    if (opts.onProgress && PROGRESS_LINE.test(line)) opts.onProgress(line);
  };
  const [out, err, code] = await Promise.all([
    new Response(proc.stdout).text(),
    readLines(proc.stderr, onStderr),
    proc.exited,
  ]);
  clearTimeout(timer);
  if (timedOut) return { checker: 'lean', result: 'error', summary: `Lean check timed out after ${Math.round(timeoutMs / 1000)}s` };
  const line = out.trim().split('\n').filter((l) => l.startsWith('{')).at(-1);
  if (code !== 0 || !line) {
    const detail = (err.trim().split('\n').filter((l) => !PROGRESS_LINE.test(l)).at(-1) ?? '').slice(0, 600);
    return { checker: 'lean', result: 'error', summary: `Lean checker failed (exit ${code})${detail ? `: ${detail}` : ''}` };
  }
  try {
    return VerdictResult.parse(JSON.parse(line));
  } catch (e) {
    return { checker: 'lean', result: 'error', summary: `Lean checker printed an unreadable verdict: ${(e as Error).message.slice(0, 200)}` };
  }
}

export async function check(input: CheckInput): Promise<VerdictResult> {
  const { problem, attempt, attemptDir, repoRoot } = input;
  if (!problem.lean) return { checker: 'lean', result: 'error', summary: `problem ${problem.id} has no lean block` };
  if (attempt.kind !== 'proof' && attempt.kind !== 'disproof') {
    return { checker: 'lean', result: 'error', summary: `the Lean checker does not check "${attempt.kind}" attempts` };
  }
  if (problem.tags.includes('answer-required')) return ANSWER_REQUIRED_UNCHECKED;
  const solution = join(attemptDir, 'solution.lean');
  const onProgress = input.progress === false ? undefined : (line: string) => void process.stderr.write(`${line}\n`);
  const verdict = await runLeanCheck(solution, problem.lean.decl, attempt.kind, { onProgress });
  const shown = relative(repoRoot, solution);
  return mapSolutionPath(verdict, shown && !shown.startsWith('..') ? shown : solution);
}
