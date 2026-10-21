import { lstatSync, existsSync, readdirSync } from 'node:fs';
import { join, resolve, relative, sep } from 'node:path';
import { parse } from '../args.ts';
import { repoRoot, scanAttempts, scanProblems } from '../repo.ts';
import type { ProblemWithAttempts, ScannedAttempt } from '../repo.ts';
import { attemptIssues, isSafeRelativePath, problemIssues } from '../schema.ts';
import type { Problem } from '../schema.ts';

export const help = `Validate problems and attempts against the schemas and the PR rules.

Usage: bun frontier validate [paths...] [--changed <git-range>]

  paths...            only report issues under these files or directories
  --changed <range>   PR mode: the diff for <range> (e.g. origin/main...HEAD) may only add files under
                      one new attempts/<problem>/<attempt>/, never verdict.json or review.json, never edit problems/.
Prints one "path: message" line per issue and exits 1 if there are any.`;

export const MAX_FILE_BYTES = 1024 * 1024;

/** Files only CI on main writes: the checker's verdict and the AI review (an opinion). A submission never adds them. */
export const CI_ONLY_FILES: Record<string, string> = {
  'verdict.json': 'verdict.json is written by CI on main, never by a submitter',
  'review.json': 'review.json (the AI review, an opinion) is written by CI on main, never by a submitter',
};

export interface Issue {
  path: string;
  message: string;
}

function attemptDirIssues(a: ScannedAttempt, problems: Map<string, Problem>): Issue[] {
  const issues: Issue[] = [];
  const add = (path: string, message: string) => issues.push({ path, message });
  const yamlPath = `${a.relDir}/attempt.yaml`;
  for (const e of a.errors) add(yamlPath, e);
  for (const e of a.verdictErrors) add(`${a.relDir}/verdict.json`, `not a valid Verdict: ${e}`);
  for (const e of a.reviewErrors) add(`${a.relDir}/review.json`, `not a valid Review: ${e}`);

  // Every file in the attempt directory: regular files only, size-capped.
  for (const name of readdirSync(a.dir)) {
    const st = lstatSync(join(a.dir, name));
    if (st.isSymbolicLink()) add(`${a.relDir}/${name}`, 'symbolic links are not allowed');
    else if (st.isFile() && st.size > MAX_FILE_BYTES) add(`${a.relDir}/${name}`, `file is larger than 1 MB (${st.size} bytes)`);
  }

  const attempt = a.value;
  if (!attempt) return issues;
  if (attempt.id !== a.dirName) add(yamlPath, `id "${attempt.id}" must equal the directory name "${a.dirName}"`);
  if (attempt.problem !== a.problemDir) {
    add(yamlPath, `problem "${attempt.problem}" must equal the parent directory name "${a.problemDir}"`);
  }
  if (a.verdict && a.verdict.attempt !== attempt.id) {
    add(`${a.relDir}/verdict.json`, `verdict is for "${a.verdict.attempt}", not "${attempt.id}"`);
  }
  if (a.review && a.review.attempt !== attempt.id) {
    add(`${a.relDir}/review.json`, `review is for "${a.review.attempt}", not "${attempt.id}"`);
  }
  if (a.review && attempt.kind !== 'writeup') {
    add(`${a.relDir}/review.json`, `only writeups get an AI review; this attempt is a ${attempt.kind}`);
  }
  const problem = problems.get(attempt.problem);
  if (!problem) add(yamlPath, `problem "${attempt.problem}" does not exist`);
  else for (const m of attemptIssues(attempt, problem)) add(yamlPath, m);

  for (const f of attempt.files) {
    if (!isSafeRelativePath(f)) continue; // already reported by attemptIssues
    const full = join(a.dir, f);
    if (!existsSync(full) && !isLink(full)) add(`${a.relDir}/${f}`, 'listed in files but does not exist');
    else if (isLink(full)) add(`${a.relDir}/${f}`, 'symbolic links are not allowed');
    else if (!lstatSync(full).isFile()) add(`${a.relDir}/${f}`, 'listed in files but is not a regular file');
  }
  return issues;
}

function isLink(p: string): boolean {
  try {
    return lstatSync(p).isSymbolicLink();
  } catch {
    return false;
  }
}

/** Validate one attempt directory (absolute or relative to root) against the repo. */
export async function validateAttemptDir(root: string, dir: string): Promise<Issue[]> {
  const rel = relative(root, resolve(dir)).split(sep).join('/');
  const [problems, attempts] = await Promise.all([scanProblems(root), scanAttempts(undefined, root)]);
  const byId = new Map(problems.flatMap((p) => (p.value ? [[p.value.id, p.value] as const] : [])));
  const a = attempts.find((x) => x.relDir === rel);
  if (!a) return [{ path: rel, message: 'not an attempt directory (expected attempts/<problem>/<attempt>/)' }];
  return attemptDirIssues(a, byId);
}

export interface RepoValidation {
  issues: Issue[];
  problems: number;
  attempts: number;
  /** The parsed problems and attempts, so a caller (index) need not read the repo again; complete only when `issues` is empty. */
  loaded: { problems: Problem[]; attempts: ProblemWithAttempts['attempts'] };
}

export async function validateRepo(root: string): Promise<RepoValidation> {
  const issues: Issue[] = [];
  const problems = await scanProblems(root);
  const byId = new Map<string, Problem>();
  for (const p of problems) {
    for (const e of p.errors) issues.push({ path: p.path, message: e });
    if (!p.value) continue;
    byId.set(p.value.id, p.value);
    if (p.path !== `problems/${p.value.id}.yaml`) {
      issues.push({ path: p.path, message: `file name must be ${p.value.id}.yaml` });
    }
    for (const m of problemIssues(p.value)) issues.push({ path: p.path, message: m });
  }
  const attemptsRoot = join(root, 'attempts');
  if (existsSync(attemptsRoot)) {
    for (const entry of readdirSync(attemptsRoot)) {
      const st = lstatSync(join(attemptsRoot, entry));
      if (!st.isDirectory()) issues.push({ path: `attempts/${entry}`, message: 'unexpected file; expected attempts/<problem>/<attempt>/' });
      else if (!byId.has(entry)) issues.push({ path: `attempts/${entry}`, message: `problem "${entry}" does not exist` });
    }
  }
  const attempts = await scanAttempts(undefined, root);
  const seen = new Set<string>();
  for (const a of attempts) {
    issues.push(...attemptDirIssues(a, byId));
    if (a.value) {
      if (seen.has(a.value.id)) issues.push({ path: `${a.relDir}/attempt.yaml`, message: `duplicate attempt id "${a.value.id}"` });
      seen.add(a.value.id);
    }
  }
  const loaded = {
    problems: [...byId.values()],
    attempts: attempts.flatMap((a) => (a.value ? [{ attempt: a.value, dir: a.dir, verdict: a.verdict, review: a.review }] : [])),
  };
  return { issues, problems: problems.length, attempts: attempts.length, loaded };
}

async function git(root: string, args: string[]): Promise<string> {
  const p = Bun.spawn(['git', ...args], { cwd: root, stdout: 'pipe', stderr: 'pipe' });
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  if (code !== 0) throw new Error(`git ${args.join(' ')} failed: ${err.trim()}`);
  return out;
}

/**
 * PR rules. A PR that touches nothing under attempts/ is a code PR: the attempt rules do not apply (the full
 * `bun run check` still does). A PR that touches attempts/ is an attempt PR and must only add files under exactly
 * one new attempts/<problem>/<attempt>/, with no verdict.json and nothing else changed.
 */
export async function changedIssues(root: string, range: string): Promise<{ issues: Issue[]; attemptDir: string | null }> {
  const raw = await git(root, ['diff', '--name-status', '--no-renames', '-z', range]);
  const parts = raw.split('\0');
  const changes: { status: string; path: string }[] = [];
  for (let i = 0; i + 1 < parts.length; i += 2) changes.push({ status: parts[i]!, path: parts[i + 1]! });

  if (!changes.some((c) => c.path.startsWith('attempts/'))) return { issues: [], attemptDir: null };

  const issues: Issue[] = [];
  const dirs = new Set<string>();
  for (const c of changes) {
    const m = /^attempts\/([^/]+)\/([^/]+)\/(.+)$/.exec(c.path);
    if (c.path.startsWith('problems/')) {
      issues.push({ path: c.path, message: 'a submission must not touch problems/' });
    } else if (!m) {
      issues.push({ path: c.path, message: 'a submission may only add files under attempts/<problem>/<attempt>/' });
    } else {
      dirs.add(`attempts/${m[1]}/${m[2]}`);
      if (c.status !== 'A') issues.push({ path: c.path, message: `a submission may only add files (git status ${c.status})` });
      const base = m[3]!.split('/').pop()!;
      if (Object.hasOwn(CI_ONLY_FILES, base)) issues.push({ path: c.path, message: CI_ONLY_FILES[base]! });
    }
  }
  if (dirs.size > 1) {
    issues.push({ path: [...dirs].sort().join(', '), message: 'a submission must add exactly one attempt directory' });
  }
  const attemptDir = dirs.size === 1 ? [...dirs][0]! : null;
  if (attemptDir && dirs.size === 1) {
    // The directory must be new: nothing under it at the base of the range.
    const dots = range.match(/\.{2,3}/);
    let base = range;
    if (dots) {
      const [left, right] = range.split(dots[0]);
      base = dots[0] === '...' ? (await git(root, ['merge-base', left || 'HEAD', right || 'HEAD'])).trim() : left || 'HEAD';
    }
    const existing = (await git(root, ['ls-tree', '-r', '--name-only', base, '--', attemptDir])).trim();
    if (existing) issues.push({ path: attemptDir, message: 'attempt directory already exists; attempts are immutable, file a new one' });
    const full = await validateRepo(root);
    issues.push(...full.issues.filter((i) => i.path === attemptDir || i.path.startsWith(`${attemptDir}/`)));
  }
  return { issues, attemptDir };
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { changed: { type: 'string' } });
  const root = repoRoot();
  let issues: Issue[];
  let summary: string;
  if (values.changed !== undefined) {
    const r = await changedIssues(root, values.changed);
    issues = r.issues;
    summary = r.attemptDir ? `ok: ${r.attemptDir}` : 'ok: no attempt changes (code PR)';
  } else {
    const r = await validateRepo(root);
    issues = r.issues;
    summary = `ok: ${r.problems} problems, ${r.attempts} attempts`;
    if (positionals.length) {
      const prefixes = positionals.map((p) => relative(root, resolve(p)).split(sep).join('/'));
      issues = issues.filter((i) => prefixes.some((p) => i.path === p || i.path.startsWith(`${p}/`) || p.startsWith(`${i.path}/`)));
      summary = `ok: ${positionals.join(', ')}`;
    }
  }
  if (issues.length) {
    for (const i of issues) console.log(`${i.path}: ${i.message}`);
    return 1;
  }
  console.log(summary);
  return 0;
}
