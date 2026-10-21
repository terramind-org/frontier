import { existsSync, lstatSync } from 'node:fs';
import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { parse as parseYamlText, stringify } from 'yaml';
import type { z } from 'zod';
import { Attempt, Index, PRACTICE_TAG, Problem, Verdict } from './schema.ts';
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
  const out: string[] = [];
  let declarationsReported = false;
  for (const i of err.issues) {
    if (i.path[0] === 'declarations') {
      if (declarationsReported) continue; // one instruction covers both declarations
      declarationsReported = true;
      out.push(
        'declarations: not confirmed. Show the declarations (the right to submit under CC BY 4.0, and the complete model/tool/people disclosure) to your human, and set rights and disclosure_complete to true in attempt.yaml only after they agree',
      );
      continue;
    }
    out.push(`${i.path.length ? i.path.join('.') : '(root)'}: ${i.message}`);
  }
  return out;
}

export interface Scanned<T> {
  /** Path relative to the repo root, forward slashes. */
  path: string;
  value: T | null;
  /** Readable parse errors; empty iff `value` is set. */
  errors: string[];
}

/**
 * `yaml`: the `yaml` package, for hand-edited files (attempts). `generated-yaml`: Bun's native parser,
 * several times faster, for problems/, which only importers write (with `toYaml`); the two parsers agree
 * on every problem file, and problems/ holds many thousands of them.
 */
type Format = 'yaml' | 'generated-yaml' | 'json';

function parseText(text: string, kind: Format): unknown {
  if (kind === 'json') return JSON.parse(text);
  if (kind === 'generated-yaml') return Bun.YAML.parse(text);
  return parseYamlText(text);
}

async function readStructured<T>(
  root: string,
  rel: string,
  kind: Format,
  schema: z.ZodType<T>,
): Promise<Scanned<T>> {
  let raw: unknown;
  try {
    const text = await readFile(join(root, rel), 'utf8');
    raw = parseText(text, kind);
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
  return Promise.all(names.map((n) => readStructured(root, `problems/${n}`, 'generated-yaml', Problem)));
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
  const s = await readStructured(root, rel, 'generated-yaml', Problem);
  throwIssues([s]);
  return s.value;
}

export async function loadAttempts(
  problemId?: string,
  root: string = repoRoot(),
  opts: { skipDrafts?: boolean } = {},
): Promise<{ attempt: Attempt; dir: string; verdict: Verdict | null }[]> {
  let scanned = await scanAttempts(problemId, root);
  if (opts.skipDrafts) {
    // Read-only commands (list, pick, show) skip the user's own unfinished drafts — an attempt whose only
    // problem is unconfirmed declarations — instead of failing. `index` and `validate` stay strict.
    scanned = scanned.filter((s) => s.value || !s.errors.every((e) => e.startsWith('declarations:')));
  }
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
 * Status rule: a problem tagged `practice` is always `practice` (a verified proof there is an
 * exercise, never a headline). Otherwise proof-checked if a `proof` attempt has a verified verdict;
 * disproof-checked likewise for `disproof`; record-improved if a verified `witness` verdict beats the
 * best known; else open.
 */
export function problemStatus(attempts: Judged[], tags: readonly string[] = []): ProblemStatus {
  if (tags.includes(PRACTICE_TAG)) return 'practice';
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
export async function loadAll(root: string = repoRoot(), opts: { skipDrafts?: boolean } = {}): Promise<ProblemWithAttempts[]> {
  const [problems, attempts] = await Promise.all([loadProblems(root), loadAttempts(undefined, root, opts)]);
  return assemble(problems, attempts);
}

/** Problems with their attempts and status, from already loaded data. */
export function assemble(problems: Problem[], attempts: ProblemWithAttempts['attempts']): ProblemWithAttempts[] {
  const byProblem = new Map<string, ProblemWithAttempts['attempts']>();
  for (const a of attempts) {
    const list = byProblem.get(a.attempt.problem) ?? [];
    list.push(a);
    byProblem.set(a.attempt.problem, list);
  }
  const sorted = [...problems].sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
  return sorted.map((problem) => {
    const list = (byProblem.get(problem.id) ?? []).sort((x, y) => (x.attempt.id < y.attempt.id ? -1 : 1));
    return { problem, status: problemStatus(list.map((a) => ({ attempt: a.attempt, verdict: a.verdict })), problem.tags), attempts: list };
  });
}

// ---------------------------------------------------------------- unknown ids

function editDistance(a: string, b: string): number {
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(prev[j]! + 1, cur[j - 1]! + 1, prev[j - 1]! + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    prev = cur;
  }
  return prev[b.length]!;
}

/** Up to `limit` problem ids nearest to a mistyped `query`: shared id parts, substring hits, then edit distance. */
export function nearestIds(query: string, ids: readonly string[], limit = 5): string[] {
  const q = query.toLowerCase();
  const qParts = new Set(q.split(/[.\-_/]+/).filter(Boolean));
  const scored = ids.map((id) => {
    const parts = id.split(/[.\-]+/).filter(Boolean);
    const shared = parts.filter((p) => qParts.has(p)).length;
    const contains = id.includes(q) || q.includes(id) ? 1 : 0;
    const dist = editDistance(q, id.slice(0, Math.max(q.length, 1) + 8)) / Math.max(q.length, id.length, 1);
    return { id, score: shared * 3 + contains * 5 - dist * 4 };
  });
  return scored
    .sort((a, b) => b.score - a.score || (a.id < b.id ? -1 : 1))
    .slice(0, limit)
    .filter((s) => s.score > -2)
    .map((s) => s.id);
}

/** The message for an id that is not a problem: near ids and what is (not) imported. */
export function unknownIdMessage(id: string, ids: readonly string[]): string {
  const near = nearestIds(id, ids);
  return [
    `No problem "${id}".`,
    ...(near.length ? ['Nearest ids:', ...near.map((n) => `  ${n}`)] : []),
    'Only upstream-open problems, the witness problems, a small practice set and the open prose problems',
    '(ids ws.* and um.*) are imported, so a textbook result or a solved problem may be missing on purpose.',
    '`bun frontier list` shows everything.',
  ].join('\n');
}
