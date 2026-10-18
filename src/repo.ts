import { existsSync, lstatSync } from 'node:fs';
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { parse as parseYamlText, stringify } from 'yaml';
import type { z } from 'zod';
import { Attempt, Index, Problem, Verdict } from './schema.ts';
import type { ProblemStatus, VerdictResult } from './schema.ts';

/** Walk up from `start` (default cwd) to the directory holding package.json. */
export function repoRoot(start: string = process.cwd()): string {
  let dir = resolve(start);
  for (;;) {
    if (existsSync(join(dir, 'package.json'))) return dir;
    const parent = dirname(dir);
    if (parent === dir) throw new Error(`no package.json found above ${start}`);
    dir = parent;
  }
}

// ---------------------------------------------------------------- stable serialisation

type Schema = z.ZodType | undefined;

function unwrap(schema: Schema): Schema {
  let s: any = schema;
  for (let i = 0; s && i < 10; i++) {
    const def = s.def ?? s._def;
    if (!def) return undefined;
    if (def.innerType) s = def.innerType;
    else if (def.type === 'pipe') s = def.in;
    else return s;
  }
  return s;
}

/** Re-key `value` so object keys follow the schema's key order, unknown keys after, alphabetically. */
export function orderKeys(value: unknown, schema?: Schema): unknown {
  const s: any = unwrap(schema);
  if (Array.isArray(value)) {
    return value.map((v) => orderKeys(v, s?.def?.type === 'array' ? s.def.element : undefined));
  }
  if (value === null || typeof value !== 'object') return value;
  const obj = value as Record<string, unknown>;
  const shape: Record<string, Schema> | undefined = s?.def?.type === 'object' ? s.shape : undefined;
  const known = shape ? Object.keys(shape).filter((k) => k in obj) : [];
  const rest = Object.keys(obj)
    .filter((k) => !known.includes(k))
    .sort();
  const out: Record<string, unknown> = {};
  for (const k of known) out[k] = orderKeys(obj[k], shape![k]);
  for (const k of rest) {
    const child = s?.def?.type === 'record' ? s.def.valueType : undefined;
    out[k] = orderKeys(obj[k], child);
  }
  return out;
}

/** Pick the schema for a record by its shape when the caller did not pass one. */
function guessSchema(data: unknown): Schema {
  if (data === null || typeof data !== 'object') return undefined;
  const d = data as Record<string, unknown>;
  if ('counts' in d && 'problems' in d) return Index;
  if ('checked_at' in d) return Verdict;
  if ('tier' in d && 'statement' in d) return Problem;
  if ('kind' in d && 'claim' in d) return Attempt;
  return undefined;
}

export function toYaml(data: unknown, schema?: z.ZodType): string {
  const ordered = orderKeys(data, schema ?? guessSchema(data));
  const text = stringify(ordered, { lineWidth: 0 });
  return text.endsWith('\n') ? text : `${text}\n`;
}

export function toJson(data: unknown, schema?: z.ZodType): string {
  return `${JSON.stringify(orderKeys(data, schema ?? guessSchema(data)), null, 2)}\n`;
}

export async function writeYaml(path: string, data: unknown, schema?: z.ZodType): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, toYaml(data, schema));
}

export async function writeJson(path: string, data: unknown, schema?: z.ZodType): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, toJson(data, schema));
}

// ---------------------------------------------------------------- scanning

export function formatZodError(err: z.ZodError): string[] {
  return err.issues.map((i) => {
    const where = i.path.length ? i.path.join('.') : '(root)';
    return `${where}: ${i.message}`;
  });
}

export interface Scanned<T> {
  /** Path relative to the repo root, forward slashes. */
  path: string;
  value: T | null;
  /** Readable parse errors; empty iff `value` is set. */
  errors: string[];
}

async function readStructured<T>(
  root: string,
  rel: string,
  kind: 'yaml' | 'json',
  schema: z.ZodType<T>,
): Promise<Scanned<T>> {
  let raw: unknown;
  try {
    const text = await readFile(join(root, rel), 'utf8');
    raw = kind === 'yaml' ? parseYamlText(text) : JSON.parse(text);
  } catch (e) {
    return { path: rel, value: null, errors: [`cannot read: ${(e as Error).message}`] };
  }
  const parsed = schema.safeParse(raw);
  if (parsed.success) return { path: rel, value: parsed.data, errors: [] };
  return { path: rel, value: null, errors: formatZodError(parsed.error) };
}

async function listDir(dir: string): Promise<string[]> {
  try {
    return (await readdir(dir)).sort();
  } catch {
    return [];
  }
}

export async function scanProblems(root: string = repoRoot()): Promise<Scanned<Problem>[]> {
  const names = (await listDir(join(root, 'problems'))).filter((n) => n.endsWith('.yaml'));
  return Promise.all(names.map((n) => readStructured(root, `problems/${n}`, 'yaml', Problem)));
}

export interface ScannedAttempt extends Scanned<Attempt> {
  /** Absolute attempt directory. */
  dir: string;
  /** Directory relative to the root. */
  relDir: string;
  /** Problem directory name (`attempts/<problem>/…`). */
  problemDir: string;
  /** Attempt directory name. */
  dirName: string;
  verdict: Verdict | null;
  verdictErrors: string[];
}

export async function scanAttempts(
  problemId?: string,
  root: string = repoRoot(),
): Promise<ScannedAttempt[]> {
  const problemDirs = problemId ? [problemId] : await listDir(join(root, 'attempts'));
  const out: ScannedAttempt[] = [];
  for (const problemDir of problemDirs) {
    const pdir = join(root, 'attempts', problemDir);
    if (!existsSync(pdir) || !lstatSync(pdir).isDirectory()) continue;
    for (const dirName of await listDir(pdir)) {
      const dir = join(pdir, dirName);
      if (!lstatSync(dir).isDirectory()) continue;
      const relDir = `attempts/${problemDir}/${dirName}`;
      const scanned = await readStructured(root, `${relDir}/attempt.yaml`, 'yaml', Attempt);
      let verdict: Verdict | null = null;
      let verdictErrors: string[] = [];
      if (existsSync(join(dir, 'verdict.json'))) {
        const v = await readStructured(root, `${relDir}/verdict.json`, 'json', Verdict);
        verdict = v.value;
        verdictErrors = v.errors;
      }
      out.push({ ...scanned, dir, relDir, problemDir, dirName, verdict, verdictErrors });
    }
  }
  return out;
}

function throwIssues(items: { path: string; errors: string[] }[]): void {
  const lines = items.flatMap((i) => i.errors.map((e) => `${i.path}: ${e}`));
  if (lines.length) throw new Error(lines.join('\n'));
}

// ---------------------------------------------------------------- loading

export async function loadProblems(root: string = repoRoot()): Promise<Problem[]> {
  const scanned = await scanProblems(root);
  throwIssues(scanned);
  return scanned.map((s) => s.value!).sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

export async function loadProblem(id: string, root: string = repoRoot()): Promise<Problem | null> {
  const rel = `problems/${id}.yaml`;
  if (!existsSync(join(root, rel))) return null;
  const s = await readStructured(root, rel, 'yaml', Problem);
  throwIssues([s]);
  return s.value;
}

export async function loadAttempts(
  problemId?: string,
  root: string = repoRoot(),
): Promise<{ attempt: Attempt; dir: string; verdict: Verdict | null }[]> {
  const scanned = await scanAttempts(problemId, root);
  throwIssues(scanned);
  throwIssues(scanned.map((s) => ({ path: `${s.relDir}/verdict.json`, errors: s.verdictErrors })));
  return scanned.map((s) => ({ attempt: s.value!, dir: s.dir, verdict: s.verdict }));
}

// ---------------------------------------------------------------- status

interface Judged {
  attempt: Pick<Attempt, 'kind'>;
  verdict: Pick<VerdictResult, 'result' | 'witness'> | null;
}

/**
 * Status rule: proof-checked if a `proof` attempt has a verified verdict; disproof-checked likewise
 * for `disproof`; record-improved if a verified `witness` verdict beats the best known; else open.
 */
export function problemStatus(attempts: Judged[]): ProblemStatus {
  const has = (pred: (a: Judged) => boolean) => attempts.some(pred);
  const verified = (a: Judged) => a.verdict?.result === 'verified';
  if (has((a) => a.attempt.kind === 'proof' && verified(a))) return 'proof-checked';
  if (has((a) => a.attempt.kind === 'disproof' && verified(a))) return 'disproof-checked';
  if (has((a) => a.attempt.kind === 'witness' && verified(a) && a.verdict?.witness?.beats_best_known === true)) {
    return 'record-improved';
  }
  return 'open';
}

// ---------------------------------------------------------------- everything at once

export interface ProblemWithAttempts {
  problem: Problem;
  status: ProblemStatus;
  attempts: { attempt: Attempt; dir: string; verdict: Verdict | null }[];
}

/** All problems (sorted by id) with their attempts (sorted by id) and computed status. Throws on invalid data. */
export async function loadAll(root: string = repoRoot()): Promise<ProblemWithAttempts[]> {
  const [problems, attempts] = await Promise.all([loadProblems(root), loadAttempts(undefined, root)]);
  const byProblem = new Map<string, ProblemWithAttempts['attempts']>();
  for (const a of attempts) {
    const list = byProblem.get(a.attempt.problem) ?? [];
    list.push(a);
    byProblem.set(a.attempt.problem, list);
  }
  return problems.map((problem) => {
    const list = (byProblem.get(problem.id) ?? []).sort((x, y) => (x.attempt.id < y.attempt.id ? -1 : 1));
    return { problem, status: problemStatus(list.map((a) => ({ attempt: a.attempt, verdict: a.verdict }))), attempts: list };
  });
}
