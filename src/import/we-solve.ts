import { existsSync } from 'node:fs';
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { z } from 'zod';
import { isProblemId } from '../ids.ts';
import { FIELDS, isSafeRelativePath, OPEN_STATUS_UNVERIFIED_TAG, PARTIALLY_SOLVED_TAG, Problem, UpstreamResolution } from '../schema.ts';
import type { Reference } from '../schema.ts';
import {
  applyRule,
  catalogueKeyFromCode,
  collectReferences,
  countBy,
  countTitles,
  formalConjecturesKeys,
  gitHead,
  normaliseText,
  repoProblems,
  titleAndStatementMatch,
  wordSet,
  writeSourceProblems,
} from './prose.ts';
import type { Step } from './prose.ts';
import { archiveClass, rowPage } from './unsolvedmath.ts';
import type { UnsolvedMathData, UnsolvedMathRow } from './unsolvedmath.ts';

export const SOURCE_NAME = 'we-solve';
export const SOURCE_REPO = 'https://github.com/We-Solve/research';
export const LICENCES = ['CC-BY-4.0', 'CC-BY-SA-4.0'] as const;
export const SOURCE_LICENCE = 'CC-BY-4.0 or CC-BY-SA-4.0, per problem (its rights block)';

/** Settled statuses: any of them skips a record. Open and partially_solved keep it; unknown, other and independent skip it too (see openStatus). */
const SETTLED = new Set(['proved', 'disproved', 'solved']);

/** The fields of problem.yaml the importer reads; other fields are ignored. */
export const WeSolveRecord = z.object({
  problem_id: z.string().regex(/^prb_[0-9a-f]{32}$/),
  title: z.string().min(1),
  kind: z.string(),
  disciplines: z.array(z.object({ discipline: z.string(), role: z.string() })).min(1),
  statement_artifact: z.object({ path: z.string() }),
  external_ids: z
    .array(z.object({ scheme: z.string(), identifier: z.union([z.string(), z.number()]).transform(String), url: z.string().optional() }))
    .nullish()
    .transform((v) => v ?? []),
  sources: z
    .array(
      z.object({
        authority: z.string(),
        source_url: z.string().nullish(),
        raw_status: z.string().nullish(),
        normalised_status: z.string(),
      }),
    )
    .nullish()
    .transform((v) => v ?? []),
  relations: z
    .array(z.object({ type: z.string(), target_problem_id: z.string(), note: z.string().nullish() }))
    .nullish()
    .transform((v) => v ?? []),
  rights: z.object({ licence: z.string(), redistribution: z.string() }),
  extensions: z.record(z.string(), z.unknown()).nullish(),
});
export type WeSolveRecord = z.infer<typeof WeSolveRecord>;

export interface Loaded {
  record: WeSolveRecord;
  handle: string;
  /** Directory of the record, relative to the checkout. */
  path: string;
  /** Statement file as given. */
  tex: string;
}

/** we-solve handle prefix → Frontier tag for the catalogue it names. */
const CATALOGUE_TAG: Record<string, string> = {
  TOP: 'top-open-problems',
  ERDOS: 'erdos-problems',
  ECON: 'economics-catalogue',
  BIOCAT: 'biology-catalogue',
};

/** `TOP-12` < `TOP-100` < `ERDOS-…` in a stable natural order (prefix, then numbers numerically). */
export function compareHandles(a: string, b: string): number {
  const split = (h: string) => h.split(/(\d+)/).map((p) => (/^\d+$/.test(p) ? Number(p) : p));
  const x = split(a);
  const y = split(b);
  for (let i = 0; i < Math.max(x.length, y.length); i++) {
    const p = x[i];
    const q = y[i];
    if (p === undefined) return -1;
    if (q === undefined) return 1;
    if (p === q) continue;
    if (typeof p === 'number' && typeof q === 'number') return p - q;
    return String(p) < String(q) ? -1 : 1;
  }
  return 0;
}

/** The statement as given, without the LaTeX preamble: the document body when there is one, else the whole file. */
export function statementBody(tex: string): string {
  const begin = tex.indexOf('\\begin{document}');
  const end = tex.lastIndexOf('\\end{document}');
  const body = begin >= 0 ? tex.slice(begin + '\\begin{document}'.length, end > begin ? end : undefined) : tex;
  return body.trim();
}

/** Read every problem record and its handle from a we-solve checkout, sorted by handle. */
export async function readWeSolve(checkout: string): Promise<Loaded[]> {
  const aliasesFile = join(checkout, 'browse', 'aliases.json');
  if (!existsSync(aliasesFile)) throw new Error(`${aliasesFile} not found; --path must be a We-Solve/research checkout`);
  const aliases = JSON.parse(await readFile(aliasesFile, 'utf8')) as { problems?: Record<string, { id: string }> };
  const handleOf = new Map<string, string>();
  for (const [handle, a] of Object.entries(aliases.problems ?? {}).sort((x, y) => compareHandles(x[0], y[0]))) {
    if (!handleOf.has(a.id)) handleOf.set(a.id, handle);
  }
  const out: Loaded[] = [];
  const base = join(checkout, 'problems');
  const shards = (await readdir(base, { withFileTypes: true })).filter((e) => e.isDirectory()).map((e) => e.name).sort();
  for (const shard of shards) {
    for (const dir of (await readdir(join(base, shard))).sort()) {
      const path = `problems/${shard}/${dir}`;
      const yamlFile = join(checkout, path, 'problem.yaml');
      if (!existsSync(yamlFile)) continue;
      const parsed = WeSolveRecord.safeParse(parseYaml(await readFile(yamlFile, 'utf8')));
      if (!parsed.success) throw new Error(`${path}/problem.yaml: ${parsed.error.issues.map((i) => `${i.path.join('.')}: ${i.message}`).join('; ')}`);
      const record = parsed.data;
      if (record.problem_id !== dir) throw new Error(`${path}/problem.yaml: problem_id ${record.problem_id} does not match its directory`);
      const handle = handleOf.get(record.problem_id);
      if (!handle) throw new Error(`${path}: no handle in browse/aliases.json`);
      if (!isSafeRelativePath(record.statement_artifact.path)) throw new Error(`${path}: unsafe statement path`);
      const tex = await readFile(join(checkout, path, record.statement_artifact.path), 'utf8');
      out.push({ record, handle, path, tex });
    }
  }
  return out.sort((a, b) => compareHandles(a.handle, b.handle));
}

export type OpenStatus = 'open' | 'partially-solved' | 'unverified';

/**
 * Whether a record is open, from its sources' normalised statuses: any settled status skips it; open
 * wins over partially solved. A record with no status at all (`sources: []`) or whose catalogue says its
 * open status is not certified (`open_status_certified: false`, status `unknown`) is open but unverified.
 * Returns the reason to skip otherwise.
 */
export function openStatus(r: WeSolveRecord): OpenStatus | { skip: string } {
  const statuses = new Set(r.sources.map((s) => s.normalised_status));
  for (const s of [...statuses].sort()) if (SETTLED.has(s)) return { skip: `status ${s}` };
  if (statuses.has('open')) return 'open';
  if (statuses.has('partially_solved')) return 'partially-solved';
  if (statuses.size === 0) return 'unverified';
  const uncertified = Object.values(r.extensions ?? {}).some(
    (e) => typeof e === 'object' && e !== null && (e as Record<string, unknown>).open_status_certified === false,
  );
  if ([...statuses].every((s) => s === 'unknown') && uncertified) return 'unverified';
  return { skip: `status ${[...statuses].sort().join('+')}` };
}

function umId(r: WeSolveRecord): string | null {
  return r.external_ids.find((e) => e.scheme === 'unsolvedmath-id')?.identifier ?? null;
}

/**
 * The catalogue key (`erdosproblems:N`, `kourovka:X.Y`, …) of a record, preferring the current code of its
 * UnsolvedMath row over the code we-solve recorded (older UnsolvedMath snapshots reused some codes).
 */
export function recordCatalogueKey(r: WeSolveRecord, row?: UnsolvedMathRow): string | null {
  const erdos = r.external_ids.find((e) => e.scheme === 'erdosproblems');
  if (erdos && /^\d+$/.test(erdos.identifier)) return `erdosproblems:${Number(erdos.identifier)}`;
  const code = row?.problem_number ?? r.external_ids.find((e) => e.scheme === 'unsolvedmath-code')?.identifier;
  return code ? catalogueKeyFromCode(code) : null;
}

export interface UnsolvedMathMatch {
  row: UnsolvedMathRow;
  how: 'id' | 'number' | 'title';
}

interface RowIndex {
  byId: Map<number, UnsolvedMathRow>;
  byKey: Map<string, UnsolvedMathRow>;
  byTitle: Map<string, { row: UnsolvedMathRow; words: Set<string> }[]>;
  /** How often each normalised title occurs among the we-solve records. */
  weSolveTitles: Map<string, number>;
}

/** Published rows by catalogue key and by normalised title (first by id wins); every row by id. */
function indexRows(rows: UnsolvedMathRow[], records: Loaded[]): RowIndex {
  const index: RowIndex = { byId: new Map(), byKey: new Map(), byTitle: new Map(), weSolveTitles: countTitles(records.map((l) => l.record.title)) };
  for (const r of [...rows].sort((a, b) => a.id - b.id)) {
    index.byId.set(r.id, r);
    if (!r.published) continue;
    const key = catalogueKeyFromCode(r.problem_number);
    if (key && !index.byKey.has(key)) index.byKey.set(key, r);
    const t = normaliseText(r.title);
    index.byTitle.set(t, [...(index.byTitle.get(t) ?? []), { row: r, words: wordSet(r.statement) }]);
  }
  return index;
}

/**
 * A record's UnsolvedMath row: the id we-solve records (archived rows included, so the archive rule can
 * see them), else a published row with the same catalogue number, else one with the same title whose
 * statement's words mostly occur in the record's statement.
 */
function matchRow(l: Loaded, index: RowIndex): UnsolvedMathMatch | null {
  const id = umId(l.record);
  const byId = id ? index.byId.get(Number(id)) : undefined;
  if (byId) return { row: byId, how: 'id' };
  const key = recordCatalogueKey(l.record);
  const byKey = key ? index.byKey.get(key) : undefined;
  if (byKey) return { row: byKey, how: 'number' };
  const title = normaliseText(l.record.title);
  const same = index.byTitle.get(title) ?? [];
  const match =
    same.length === 1 &&
    titleAndStatementMatch({
      titleCountUnsolvedMath: same.length,
      titleCountWeSolve: index.weSolveTitles.get(title) ?? 0,
      unsolvedMathWords: same[0]!.words,
      weSolveWords: wordSet(statementBody(l.tex)),
    });
  return match ? { row: same[0]!.row, how: 'title' } : null;
}

/** `scheme:identifier` aliases of a record (we-solve's own id first), with its matched UnsolvedMath row's. */
export function recordExternalIds(l: Loaded, key: string | null, row?: UnsolvedMathRow): string[] {
  const scheme: Record<string, string> = { 'unsolvedmath-id': 'unsolvedmath' };
  const ids = l.record.external_ids
    .filter((e) => !(row && e.scheme === 'unsolvedmath-code')) // the row's current code replaces a possibly stale one
    .map((e) => `${scheme[e.scheme] ?? e.scheme}:${e.identifier.replace(/\s+/g, '_')}`);
  if (row) ids.push(`unsolvedmath:${row.id}`, `unsolvedmath-code:${row.problem_number.replace(/\s+/g, '_')}`);
  if (key) ids.push(key);
  return [`we-solve:${l.record.problem_id}`, ...[...new Set(ids)].sort()];
}

export interface WeSolveOptions {
  checkout: string;
  root: string;
  date: string;
  /** UnsolvedMath data, for the cross-source rules (rows UnsolvedMath archived or now lists as solved). */
  unsolvedmath?: UnsolvedMathData;
  dryRun?: boolean;
}

export interface WeSolveSummary {
  commit: string;
  unsolvedmathRevision: string | null;
  records: number;
  steps: Step[];
  imported: number;
  removed: string[];
  /** Records naming an UnsolvedMath id the given dataset does not have. */
  unknownUnsolvedMathIds: number;
  /** Imported problems that list an UnsolvedMath row too, by how the row was matched. */
  unsolvedmathMatches: Record<string, number>;
  byField: Record<string, number>;
  byLicence: Record<string, number>;
  byStatus: Record<string, number>;
  byTag: Record<string, number>;
}

class Groups {
  private parent = new Map<string, string>();
  find(x: string): string {
    let p = this.parent.get(x) ?? x;
    if (p !== x) {
      p = this.find(p);
      this.parent.set(x, p);
    }
    return p;
  }
  union(a: string, b: string): void {
    const [x, y] = [this.find(a), this.find(b)];
    if (x !== y) this.parent.set(y < x ? x : y, y < x ? y : x);
  }
}

/** Import we-solve's open problems as prose problems `ws.<handle>`. */
export async function importWeSolve(opts: WeSolveOptions): Promise<WeSolveSummary> {
  const commit = await gitHead(opts.checkout);
  if (!commit) throw new Error(`${opts.checkout} is not a git checkout; clone github.com/We-Solve/research`);
  const all = await readWeSolve(opts.checkout);
  const existing = await repoProblems(opts.root);
  const fc = formalConjecturesKeys(existing);
  const steps: Step[] = [];
  const status = new Map<string, OpenStatus>();
  // Records we already import, by we-solve problem id: they keep their Frontier id (we-solve may retire a
  // handle), and when settled upstream they stay, marked solved, instead of being dropped.
  const prior = new Map<string, Problem>();
  for (const p of existing) {
    if (p.source.name !== SOURCE_NAME) continue;
    // The first we-solve id is the record the problem was made from; later ones are merged duplicates.
    const own = (p.external_ids ?? []).find((e) => e.startsWith('we-solve:'));
    if (own) prior.set(own.slice('we-solve:'.length), p);
  }
  const settled = new Map<string, string>(); // problem_id → why it is settled

  let items = applyRule(steps, 'rights: redistribution permitted under CC BY 4.0 or CC BY-SA 4.0', all, (l) =>
    l.record.rights.redistribution === 'permitted' && (LICENCES as readonly string[]).includes(l.record.rights.licence)
      ? null
      : `rights ${l.record.rights.licence}/${l.record.rights.redistribution}`,
  );
  items = applyRule(steps, 'status open, partially_solved, or uncertified catalogue', items, (l) => {
    const s = openStatus(l.record);
    if (typeof s === 'object') {
      if (!prior.has(l.record.problem_id) || !/^status (proved|disproved|solved)$/.test(s.skip)) return s.skip;
      settled.set(l.record.problem_id, s.skip);
      return null;
    }
    status.set(l.record.problem_id, s);
    return null;
  });
  items = applyRule(steps, 'flagged duplicate or unrecoverable (c)', items, (l) => {
    if (/^duplicate\b/i.test(l.record.title)) return 'title starts "Duplicate"';
    if (/\bunrecoverable\b/i.test(l.tex)) return 'statement marked unrecoverable';
    return null;
  });
  assertFields(items);

  // (b) the UnsolvedMath row of each record: by the id it records, else by catalogue number, else by
  // title and statement. The match decides the cross-source rules and lists both sources.
  const umMatch = new Map<string, UnsolvedMathMatch>();
  let unknownUnsolvedMathIds = 0;
  if (opts.unsolvedmath) {
    const index = indexRows(opts.unsolvedmath.rows, all);
    for (const l of items) {
      const id = umId(l.record);
      if (id && !index.byId.has(Number(id))) unknownUnsolvedMathIds++;
      const m = matchRow(l, index);
      if (m) umMatch.set(l.record.problem_id, m);
    }
    items = applyRule(steps, 'UnsolvedMath archived the row (b/c)', items, (l) => {
      const row = umMatch.get(l.record.problem_id)?.row;
      return row && !row.published ? archiveClass(row) : null;
    });
    items = applyRule(steps, 'UnsolvedMath now lists it as solved (b)', items, (l) => {
      const row = umMatch.get(l.record.problem_id)?.row;
      if (row?.status !== 'solved') return null;
      if (prior.has(l.record.problem_id)) {
        if (!settled.has(l.record.problem_id)) settled.set(l.record.problem_id, 'UnsolvedMath solved');
        return null;
      }
      return `we-solve ${l.record.sources[0]?.normalised_status ?? 'no status'}, UnsolvedMath solved`;
    });
    // (d) Since late October 2026 we-solve also mirrors the unsolvedmath.com catalogue as records with no
    // handle of their own (only the `prb_` id). That catalogue is imported from UnsolvedMath itself (`um.*`),
    // so such a record we do not already hold is skipped: sourced from unsolvedmath.com, or matching a row.
    items = applyRule(steps, 'handle-less mirror of an UnsolvedMath row (d)', items, (l) => {
      if (!l.handle.startsWith('prb_') || prior.has(l.record.problem_id)) return null;
      const m = umMatch.get(l.record.problem_id);
      if (m) return `matches UnsolvedMath row by ${m.how}`;
      return l.record.sources.some((s) => s.authority === 'unsolvedmath.com') ? 'sourced from unsolvedmath.com' : null;
    });
  }
  const umRow = (l: Loaded) => umMatch.get(l.record.problem_id)?.row;

  // (c) one problem recorded more than once: same UnsolvedMath id, same catalogue number, or a
  // "Same conjecture/problem" relation. The record from the canonical catalogue (erdosproblems) wins,
  // then the first by handle; it inherits the others' external ids.
  const groups = new Groups();
  const byKey = new Map<string, string>();
  const keyOf = new Map<string, string | null>();
  const live = new Set(items.map((l) => l.record.problem_id));
  for (const l of items) {
    const id = l.record.problem_id;
    const key = recordCatalogueKey(l.record, umRow(l));
    keyOf.set(id, key);
    const u = umRow(l)?.id ?? umId(l.record);
    for (const k of [u ? `unsolvedmath:${u}` : null, key]) {
      if (!k) continue;
      const other = byKey.get(k);
      if (other) groups.union(other, id);
      else byKey.set(k, id);
    }
    for (const r of l.record.relations) {
      if (r.type === 'related' && /^same\b/i.test(r.note ?? '') && live.has(r.target_problem_id)) groups.union(id, r.target_problem_id);
    }
  }
  // The record a problem we hold was made from wins (its id stays stable), then the canonical catalogue's.
  const rank = (l: Loaded) =>
    prior.has(l.record.problem_id) ? 0 : l.record.external_ids.some((e) => e.scheme === 'erdosproblems') ? 1 : 2;
  const winner = new Map<string, Loaded>();
  for (const l of items) {
    const g = groups.find(l.record.problem_id);
    const w = winner.get(g);
    if (!w || rank(l) < rank(w)) winner.set(g, l); // items are in handle order, so ties keep the first
  }
  const merged = new Map<string, string[]>();
  for (const l of items) {
    const w = winner.get(groups.find(l.record.problem_id))!;
    const ids = recordExternalIds(l, keyOf.get(l.record.problem_id) ?? null, umRow(l));
    merged.set(w.record.problem_id, [...(merged.get(w.record.problem_id) ?? []), ...ids]);
  }
  items = applyRule(steps, 'same problem recorded twice (c)', items, (l) => {
    const w = winner.get(groups.find(l.record.problem_id))!;
    return w === l ? null : `duplicate of ${w.handle.split('-')[0]} record`;
  });

  items = applyRule(steps, 'formal-conjectures has it (a)', items, (l) => {
    const key = keyOf.get(l.record.problem_id);
    return key && fc.has(key) ? `${key.split(':')[0]} number matches a formal-conjectures problem` : null;
  });

  const problems = items.map((l) => {
    const own = recordExternalIds(l, keyOf.get(l.record.problem_id) ?? null, umRow(l));
    // A problem we hold keeps every alias it had: we-solve has dropped some (e.g. `unsolvedmath:<id>`), and
    // the UnsolvedMath import relies on them to skip rows we-solve already covers.
    const kept = (prior.get(l.record.problem_id)?.external_ids ?? []).filter((e) => !e.startsWith('we-solve:') || e !== own[0]);
    const rest = new Set([...own.slice(1), ...(merged.get(l.record.problem_id) ?? []), ...kept]);
    rest.delete(own[0]!);
    const ids = [own[0]!, ...[...rest].sort()];
    const had = prior.get(l.record.problem_id);
    const why = settled.get(l.record.problem_id);
    const resolution = why
      ? had?.upstream_resolution ?? settledResolution(l, why, umRow(l), commit, opts.date)
      : undefined;
    return toProblem(l, commit, opts.date, why ? 'solved' : status.get(l.record.problem_id)!, ids, umRow(l), {
      id: had?.id,
      catalogueTag: had?.tags[1],
      resolution,
    });
  });
  const { removed } = await writeSourceProblems(
    opts.root,
    SOURCE_NAME,
    existing,
    problems,
    { repo: SOURCE_REPO, commit, licence: SOURCE_LICENCE, date: opts.date },
    opts.dryRun,
  );
  return {
    commit,
    unsolvedmathRevision: opts.unsolvedmath?.revision ?? null,
    records: all.length,
    steps,
    imported: problems.length,
    removed,
    unknownUnsolvedMathIds,
    unsolvedmathMatches: countBy(items, (l) => umMatch.get(l.record.problem_id)?.how ?? 'none'),
    byField: countBy(problems, (p) => p.field),
    byLicence: countBy(problems, (p) => p.source.licence),
    byStatus: countBy(problems, (p) => p.upstream_status),
    byTag: countBy(problems, (p) => p.tags),
  };
}

/** Every record's primary discipline must be a Frontier field; a new discipline upstream needs a schema change first. */
function assertFields(items: Loaded[]): void {
  for (const l of items) {
    const d = primaryDiscipline(l.record);
    if (!(FIELDS as readonly string[]).includes(d)) throw new Error(`${l.path}: discipline "${d}" is not a Frontier field; add it to FIELDS`);
  }
}

function primaryDiscipline(r: WeSolveRecord): string {
  return (r.disciplines.find((d) => d.role === 'primary') ?? r.disciplines[0]!).discipline;
}

/** Frontier tag for a record that has only its `prb_` id as a handle, from the authority that lists it. */
const AUTHORITY_TAG: Record<string, string> = {
  'top-open-problems-catalogue': 'top-open-problems',
  'unsolvedmath.com': 'top-open-problems',
  'erdosproblems.com': 'erdos-problems',
};

/** Frontier id from a we-solve handle: `ws.<handle>`, or `ws.<hex>` for a handle that is only the `prb_` id. */
export function weSolveId(handle: string): string {
  return /^prb_[0-9a-f]{32}$/.test(handle) ? `ws.${handle.slice(4)}` : `ws.${handle.toLowerCase()}`;
}

/** How a record we hold was settled, from the statuses its sources now give (and UnsolvedMath's, if solved there). */
export function settledResolution(l: Loaded, why: string, row: UnsolvedMathRow | undefined, commit: string, date: string): UpstreamResolution {
  const parts = l.record.sources
    .filter((s) => SETTLED.has(s.normalised_status))
    .map((s) => `${s.authority} lists it as ${s.raw_status ?? s.normalised_status}`);
  if (why === 'UnsolvedMath solved' && row) parts.push(`UnsolvedMath lists it as solved${row.solution_reference ? `: ${row.solution_reference}` : ''}`);
  const references: Reference[] = [];
  for (const s of l.record.sources) if (SETTLED.has(s.normalised_status) && s.source_url && URL.canParse(s.source_url)) references.push({ label: s.authority, url: s.source_url });
  if (why === 'UnsolvedMath solved' && row) references.push({ label: `UnsolvedMath ${row.problem_number}`, url: rowPage(row) });
  const settledAs = [...new Set(l.record.sources.map((s) => s.normalised_status).filter((s) => SETTLED.has(s)))];
  return UpstreamResolution.parse({
    ...(settledAs.length === 1 && settledAs[0] !== 'solved' ? { outcome: settledAs[0] } : {}),
    note: `${parts.join('; ') || why}.`,
    references,
    detected: { commit, date },
  });
}

export function toProblem(
  l: Loaded,
  commit: string,
  date: string,
  status: OpenStatus | 'solved',
  externalIds: string[],
  row?: UnsolvedMathRow,
  keep: { id?: string; catalogueTag?: string; resolution?: UpstreamResolution } = {},
): Problem {
  const { record: r, handle } = l;
  const id = keep.id ?? weSolveId(handle);
  if (!isProblemId(id)) throw new Error(`${l.path}: handle ${handle} does not make a valid problem id`);
  const prefix = handle.replace(/-.*$/, '');
  const byAuthority = r.sources.map((s) => AUTHORITY_TAG[s.authority]).find((t) => t);
  const catalogue = keep.catalogueTag ?? CATALOGUE_TAG[prefix] ?? (handle.startsWith('prb_') ? byAuthority ?? 'we-solve-catalogue' : prefix.toLowerCase());
  const tags = ['we-solve', catalogue];
  if (status === 'partially-solved') tags.push(PARTIALLY_SOLVED_TAG);
  if (status === 'unverified') tags.push(OPEN_STATUS_UNVERIFIED_TAG);
  const permalink = `${SOURCE_REPO}/tree/${commit}/${l.path}`;
  const fixed: Reference[] = [{ label: `we-solve ${handle}`, url: permalink }];
  if (row) fixed.push({ label: `UnsolvedMath ${row.problem_number}`, url: rowPage(row) });
  for (const s of r.sources) if (s.source_url) fixed.push({ label: s.authority, url: s.source_url });
  for (const e of r.external_ids) if (e.url) fixed.push({ label: `${e.scheme} ${e.identifier}`, url: e.url });
  return Problem.parse({
    schema: 1,
    id,
    title: r.title.trim(),
    field: primaryDiscipline(r),
    tier: 'prose',
    statement: statementBody(l.tex),
    ams: [],
    tags,
    references: collectReferences(fixed, [l.tex]),
    source: {
      name: SOURCE_NAME,
      repo: SOURCE_REPO,
      commit,
      path: `${l.path}/${r.statement_artifact.path}`,
      url: permalink,
      licence: r.rights.licence,
    },
    upstream_status: status === 'partially-solved' ? 'partially-solved' : status === 'solved' ? 'solved' : 'open',
    ...(status === 'solved' ? { upstream_resolution: keep.resolution } : {}),
    external_ids: externalIds,
    added: date,
  });
}
