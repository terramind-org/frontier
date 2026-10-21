import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { basename, dirname, join } from 'node:path';
import { z } from 'zod';
import { kebab } from './formal-conjectures.ts';
import {
  applyRule,
  catalogueKeyFromCode,
  collectReferences,
  countBy,
  countTitles,
  formalConjecturesKeys,
  gitHead,
  normaliseText,
  titleAndStatementMatch,
  repoProblems,
  wordSet,
  writeSourceProblems,
} from './prose.ts';
import type { Step } from './prose.ts';
import { PARTIALLY_SOLVED_TAG, Problem } from '../schema.ts';

export const SOURCE_NAME = 'unsolvedmath';
export const SOURCE_REPO = 'https://huggingface.co/datasets/ulamai/UnsolvedMath';
export const SITE = 'https://www.unsolvedmath.com/problems';
export const DATA_FILE = 'problems.json';
/** Curation and metadata: CC BY 4.0. Rows derived from Oberwolfach Reports: CC BY-SA 4.0 (the reports' own licence). */
export const LICENCE = 'CC-BY-4.0';
export const LICENCE_SHARE_ALIKE = 'CC-BY-SA-4.0';
export const SOURCE_LICENCE = `${LICENCE}; ${LICENCE_SHARE_ALIKE} for rows derived from Oberwolfach Reports`;

/** The fields of a problems.json row the importers read; other fields are ignored. */
export const UnsolvedMathRow = z.object({
  id: z.number().int().nonnegative(),
  problem_number: z.string().min(1),
  title: z.string().min(1),
  statement: z.string(),
  background: z.string().nullish(),
  status: z.enum(['open', 'partially_solved', 'solved']),
  published: z.boolean(),
  archive_reason: z.string().nullish(),
  duplicate_of: z.array(z.union([z.string(), z.number()])).nullish(),
  category: z.object({ name: z.string() }),
  set: z.object({ name: z.string() }).nullish(),
  source_url: z.string().nullish(),
  literature_sources: z.array(z.object({ url: z.string(), label: z.string().nullish() })).nullish(),
  solution_reference: z.string().nullish(),
});
export type UnsolvedMathRow = z.infer<typeof UnsolvedMathRow>;

export interface UnsolvedMathData {
  revision: string;
  rows: UnsolvedMathRow[];
}

/**
 * Read problems.json from a download of the dataset. The revision is `revision` if given, else the HEAD
 * of a git clone at `dir`, else the snapshot directory name of a huggingface_hub cache
 * (`…/snapshots/<sha>/`).
 */
export async function readUnsolvedMath(dir: string, revision?: string): Promise<UnsolvedMathData> {
  const file = join(dir, DATA_FILE);
  if (!existsSync(file)) throw new Error(`${file} not found; --path must be a download of ${SOURCE_REPO}`);
  let rev = revision ?? (await gitHead(dir));
  if (!rev && /^[0-9a-f]{40}$/.test(basename(dir)) && basename(dirname(dir)) === 'snapshots') rev = basename(dir);
  if (!rev) throw new Error(`cannot tell the dataset revision of ${dir}; pass --revision <40-hex commit>`);
  if (!/^[0-9a-f]{40}$/.test(rev)) throw new Error(`revision must be a 40-hex commit, got ${rev}`);
  const raw = JSON.parse(await readFile(file, 'utf8')) as unknown;
  const rows = z.array(UnsolvedMathRow).parse(raw);
  const ids = new Set<number>();
  for (const r of rows) {
    if (ids.has(r.id)) throw new Error(`duplicate UnsolvedMath id ${r.id}`);
    ids.add(r.id);
  }
  return { revision: rev, rows: [...rows].sort((a, b) => a.id - b.id) };
}

/** Oberwolfach-derived rows carry the reports' CC BY-SA 4.0. */
export function rowLicence(r: Pick<UnsolvedMathRow, 'problem_number' | 'set'>): string {
  return r.problem_number.startsWith('OWR-') || r.set?.name === 'oberwolfach_reports_open_problems' ? LICENCE_SHARE_ALIKE : LICENCE;
}

/** UnsolvedMath's category as a Frontier field, following we-solve's mapping of the same rows. */
export function rowField(r: Pick<UnsolvedMathRow, 'category'>): Problem['field'] {
  if (r.category.name === 'computer_science') return 'computer-science';
  if (r.category.name === 'physics') return 'physics';
  return 'mathematics';
}

export function rowPage(r: Pick<UnsolvedMathRow, 'problem_number'>): string {
  return `${SITE}/${encodeURIComponent(r.problem_number)}`;
}

/** Why an archived row was archived, coarsely: duplicates apart from everything else. */
export function archiveClass(r: UnsolvedMathRow): string {
  if ((r.duplicate_of?.length ?? 0) > 0 || /duplicate|merged/i.test(r.archive_reason ?? '')) return 'archived upstream as a duplicate or merged record';
  if (/unrecoverable/i.test(r.archive_reason ?? '')) return 'archived upstream: statement unrecoverable';
  return 'archived upstream: not an open problem (answered, non-mathematical, fragment, …)';
}

export interface UnsolvedMathOptions {
  /** Directory holding problems.json. */
  dir: string;
  root: string;
  date: string;
  revision?: string;
  dryRun?: boolean;
}

export interface UnsolvedMathSummary {
  revision: string;
  rows: number;
  steps: Step[];
  /** Rows kept although a we-solve problem has the same title, because their statements differ. */
  titleOnlyKept: number;
  imported: number;
  removed: string[];
  byField: Record<string, number>;
  byLicence: Record<string, number>;
  byStatus: Record<string, number>;
}

interface WsIndex {
  byAlias: Map<string, string>;
  byTitle: Map<string, { id: string; words: Set<string> }[]>;
}

function indexWeSolve(problems: Problem[]): WsIndex {
  const byAlias = new Map<string, string>();
  const byTitle = new Map<string, { id: string; words: Set<string> }[]>();
  for (const p of problems) {
    if (p.source.name !== 'we-solve') continue;
    for (const a of p.external_ids ?? []) if (!byAlias.has(a)) byAlias.set(a, p.id);
    const t = normaliseText(p.title);
    byTitle.set(t, [...(byTitle.get(t) ?? []), { id: p.id, words: wordSet(p.statement) }]);
  }
  return { byAlias, byTitle };
}

/**
 * Import UnsolvedMath's open and partially solved problems as prose problems `um.<id>`. Run after the
 * we-solve import: rows already represented by a we-solve problem are skipped (rule b), as are rows for
 * problems formal-conjectures formalises (rule a).
 */
export async function importUnsolvedMath(opts: UnsolvedMathOptions): Promise<UnsolvedMathSummary> {
  const data = await readUnsolvedMath(opts.dir, opts.revision);
  const existing = await repoProblems(opts.root);
  const fc = formalConjecturesKeys(existing);
  const ws = indexWeSolve(existing);
  const steps: Step[] = [];
  let rows = data.rows;

  // (c) within the source: archived rows are UnsolvedMath's own duplicates and non-problems.
  rows = applyRule(steps, 'published only (c: archived duplicates and non-problems)', rows, (r) => (r.published ? null : archiveClass(r)));
  rows = applyRule(steps, 'status open or partially_solved', rows, (r) => (r.status === 'solved' ? 'status solved' : null));
  rows = applyRule(steps, 'empty statement', rows, (r) => (r.statement.trim() === '' ? 'empty statement' : null));
  // (c) exact repeats left after upstream's deduplication: same normalised title and statement.
  const seenText = new Set<string>();
  rows = applyRule(steps, 'same title and statement as an earlier row (c)', rows, (r) => {
    const key = `${normaliseText(r.title)}|${normaliseText(r.statement)}`;
    if (seenText.has(key)) return 'exact repeat';
    seenText.add(key);
    return null;
  });
  // (a) formal-conjectures already has the problem (Erdős, Kourovka, Hilbert, Millennium by number/name).
  rows = applyRule(steps, 'formal-conjectures has it (a)', rows, (r) => {
    const key = catalogueKeyFromCode(r.problem_number);
    return key && fc.has(key) ? `${key.split(':')[0]} number matches a formal-conjectures problem` : null;
  });
  // (b) we-solve has it: by the UnsolvedMath id it records, by catalogue number, then by title and statement.
  let titleOnlyKept = 0;
  const umTitles = countTitles(data.rows.filter((r) => r.published).map((r) => r.title));
  rows = applyRule(steps, 'we-solve has it (b)', rows, (r) => {
    if (ws.byAlias.has(`unsolvedmath:${r.id}`)) return 'a we-solve problem lists this UnsolvedMath id';
    const key = catalogueKeyFromCode(r.problem_number);
    if (key && ws.byAlias.has(key)) return `same ${key.split(':')[0]} number`;
    const title = normaliseText(r.title);
    const same = ws.byTitle.get(title) ?? [];
    if (
      same.length === 1 &&
      titleAndStatementMatch({
        titleCountUnsolvedMath: umTitles.get(title) ?? 0,
        titleCountWeSolve: same.length,
        unsolvedMathWords: wordSet(r.statement),
        weSolveWords: same[0]!.words,
      })
    ) {
      return 'same title and statement';
    }
    if (same.length) titleOnlyKept++;
    return null;
  });

  const problems = rows.map((r) => toProblem(r, data.revision, opts.date));
  const { removed } = await writeSourceProblems(
    opts.root,
    SOURCE_NAME,
    existing,
    problems,
    { repo: SOURCE_REPO, commit: data.revision, licence: SOURCE_LICENCE, date: opts.date },
    opts.dryRun,
  );
  return {
    revision: data.revision,
    rows: data.rows.length,
    steps,
    titleOnlyKept,
    imported: problems.length,
    removed,
    byField: countBy(problems, (p) => p.field),
    byLicence: countBy(problems, (p) => p.source.licence),
    byStatus: countBy(problems, (p) => p.upstream_status),
  };
}

export function toProblem(r: UnsolvedMathRow, revision: string, date: string): Problem {
  const partial = r.status === 'partially_solved';
  const tags = ['unsolvedmath'];
  if (r.set) tags.push(kebab(r.set.name));
  if (partial) tags.push(PARTIALLY_SOLVED_TAG);
  const key = catalogueKeyFromCode(r.problem_number);
  const fixed = [{ label: `UnsolvedMath ${r.problem_number}`, url: rowPage(r) }];
  if (r.source_url) fixed.push({ label: r.source_url, url: r.source_url });
  for (const s of r.literature_sources ?? []) fixed.push({ label: s.label ?? s.url, url: s.url });
  return Problem.parse({
    schema: 1,
    id: `um.${r.id}`,
    title: r.title.trim(),
    field: rowField(r),
    tier: 'prose',
    statement: r.statement.trim(),
    ams: [],
    tags,
    references: collectReferences(fixed, [r.statement, r.background ?? '', r.solution_reference ?? '']),
    source: {
      name: SOURCE_NAME,
      repo: SOURCE_REPO,
      commit: revision,
      path: DATA_FILE,
      url: `${SOURCE_REPO}/blob/${revision}/${DATA_FILE}`,
      licence: rowLicence(r),
    },
    upstream_status: partial ? 'partially-solved' : 'open',
    external_ids: [`unsolvedmath:${r.id}`, `unsolvedmath-code:${r.problem_number.replace(/\s+/g, '_')}`, ...(key ? [key] : [])],
    added: date,
  });
}
