import { existsSync, realpathSync } from 'node:fs';
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { loadProblems, writeYaml } from '../repo.ts';
import { PRACTICE_TAG, Problem, problemIssues } from '../schema.ts';
import type { Reference } from '../schema.ts';

/**
 * Shared pieces of the prose-tier importers (we-solve, UnsolvedMath): the filter/dedupe ledger, text
 * normalisation for title-and-statement matching, catalogue keys that identify the same problem across
 * sources, and writing one source's problems without touching any other source's files.
 */

/** One filter or dedupe rule applied in order: how many records went in, how many it dropped, and why. */
export interface Step {
  rule: string;
  before: number;
  dropped: number;
  after: number;
  /** Dropped records by detailed reason. */
  reasons: Record<string, number>;
}

/** Run `rule` over `items`: `why` returns a reason to drop an item, or null to keep it. */
export function applyRule<T>(steps: Step[], rule: string, items: T[], why: (item: T) => string | null): T[] {
  const kept: T[] = [];
  const reasons: Record<string, number> = {};
  for (const item of items) {
    const r = why(item);
    if (r === null) kept.push(item);
    else reasons[r] = (reasons[r] ?? 0) + 1;
  }
  steps.push({ rule, before: items.length, dropped: items.length - kept.length, after: kept.length, reasons: sortCounts(reasons) });
  return kept;
}

export function sortCounts(counts: Record<string, number>): Record<string, number> {
  return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1)));
}

export function countBy<T>(items: T[], key: (item: T) => string | string[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const i of items) for (const k of [key(i)].flat()) out[k] = (out[k] ?? 0) + 1;
  return sortCounts(out);
}

// ---------------------------------------------------------------- text matching

/** Lowercase ASCII words: accents dropped, punctuation and TeX commands' backslashes become spaces. */
export function normaliseText(s: string): string {
  return s
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

/** The distinct words of at least three characters. */
export function wordSet(s: string): Set<string> {
  return new Set(normaliseText(s).split(' ').filter((w) => w.length >= 3));
}

/** Fraction of `needle`'s distinct words that also occur in `haystack` (0 when `needle` has none). */
export function coverage(needle: Set<string>, haystack: Set<string>): number {
  if (needle.size === 0) return 0;
  let hit = 0;
  for (const w of needle) if (haystack.has(w)) hit++;
  return hit / needle.size;
}

/**
 * Title-and-statement match: the normalised titles are equal, each title occurs exactly once in its own
 * source (survey sections such as "Algebraic Stories — Lefschetz properties" title several different
 * problems, so a shared title says nothing), and this share of the UnsolvedMath statement's words occurs in
 * the we-solve statement. Calibrated on the 4,643 we-solve records that name their UnsolvedMath id: 90%
 * of those pairs reach 0.5, while words alone cannot tell sibling questions of one survey apart.
 */
export const MATCH_MIN_COVERAGE = 0.5;

/** Normalised title → how many of `titles` have it. */
export function countTitles(titles: string[]): Map<string, number> {
  const out = new Map<string, number>();
  for (const t of titles.map(normaliseText)) out.set(t, (out.get(t) ?? 0) + 1);
  return out;
}

export function titleAndStatementMatch(o: {
  /** How often the title occurs in each source. */
  titleCountUnsolvedMath: number;
  titleCountWeSolve: number;
  unsolvedMathWords: Set<string>;
  weSolveWords: Set<string>;
}): boolean {
  return o.titleCountUnsolvedMath === 1 && o.titleCountWeSolve === 1 && coverage(o.unsolvedMathWords, o.weSolveWords) >= MATCH_MIN_COVERAGE;
}

// ---------------------------------------------------------------- links

const MD_LINK = /\[([^\]]*)\]\((https?:\/\/(?:[^()\s]|\([^()\s]*\))+)\)/g;
const TEX_HREF = /\\href\{(https?:\/\/[^}\s]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}/g;
const TEX_URL = /\\url\{(https?:\/\/[^}\s]+)\}/g;
const BARE_URL = /https?:\/\/[^\s<>"'{}\\\])]+(?:\([^\s()]*\)[^\s<>"'{}\\\])]*)?/g;

function cleanUrl(url: string): string {
  return url.replace(/[.,;:]+$/, '').replace(/\\([#%_&])/g, '$1');
}

function cleanLabel(label: string): string {
  return label
    .replace(/\\[a-zA-Z]+\*?/g, ' ')
    .replace(/[{}$]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * References in document order, deduplicated by url: the fixed ones first, then Markdown links,
 * `\href`, `\url` and bare http(s) urls in the texts. Only http(s) urls that parse are kept.
 */
export function collectReferences(fixed: Reference[], texts: string[]): Reference[] {
  const seen = new Set<string>();
  const out: Reference[] = [];
  const add = (label: string, url: string) => {
    url = cleanUrl(url);
    if (seen.has(url) || !/^https?:\/\//.test(url) || !URL.canParse(url)) return;
    seen.add(url);
    out.push({ label: cleanLabel(label) || url, url });
  };
  for (const r of fixed) add(r.label, r.url);
  for (const text of texts) {
    const hits: { at: number; label: string; url: string }[] = [];
    const covered: [number, number][] = [];
    for (const re of [MD_LINK, TEX_HREF]) {
      for (const m of text.matchAll(re)) {
        const [label, url] = re === MD_LINK ? [m[1]!, m[2]!] : [m[2]!, m[1]!];
        hits.push({ at: m.index!, label, url });
        covered.push([m.index!, m.index! + m[0].length]);
      }
    }
    for (const m of text.matchAll(TEX_URL)) {
      hits.push({ at: m.index!, label: m[1]!, url: m[1]! });
      covered.push([m.index!, m.index! + m[0].length]);
    }
    for (const m of text.matchAll(BARE_URL)) {
      if (covered.some(([a, b]) => m.index! >= a && m.index! < b)) continue;
      hits.push({ at: m.index!, label: cleanUrl(m[0]), url: m[0] });
    }
    hits.sort((a, b) => a.at - b.at);
    for (const h of hits) add(h.label, h.url);
  }
  return out;
}

// ---------------------------------------------------------------- catalogue keys

/**
 * UnsolvedMath codes of the Millennium Prize problems, as the formal-conjectures file each corresponds to.
 * These are the only catalogue entries matched by name rather than by number.
 */
export const MILLENNIUM: Record<string, string> = {
  'MPP-001': 'PvsNP',
  'MPP-002': 'RiemannHypothesis',
  'MPP-003': 'YangMills',
  'MPP-004': 'NavierStokes',
  'MPP-005': 'BSD',
  'MPP-006': 'Hodge',
  'MPP-007': 'Poincare',
};

/**
 * Keys naming a problem in a numbered catalogue that formal-conjectures also follows, from an
 * UnsolvedMath code: `EP-428` → `erdosproblems:428`, `KOU-1.35` → `kourovka:1.35`, `HIL-012` →
 * `hilbert:12`, `MPP-002` → `millennium:RiemannHypothesis`. Ben Green's list is left out on purpose:
 * UnsolvedMath's `GREEN-n` numbers do not follow Green's numbering (GREEN-061 is n-queens, Green's 61 is not).
 */
export function catalogueKeyFromCode(code: string): string | null {
  let m = /^EP-(\d+)$/.exec(code);
  if (m) return `erdosproblems:${Number(m[1])}`;
  m = /^KOU-(\d+\.\d+)$/.exec(code);
  if (m) return `kourovka:${m[1]}`;
  m = /^HIL-(\d+)$/.exec(code);
  if (m) return `hilbert:${Number(m[1])}`;
  if (MILLENNIUM[code]) return `millennium:${MILLENNIUM[code]}`;
  return null;
}

/** The catalogue key of a formal-conjectures source path, or null. */
export function catalogueKeyFromFcPath(path: string): string | null {
  let m = /^FormalConjectures\/ErdosProblems\/(\d+)\.lean$/.exec(path);
  if (m) return `erdosproblems:${Number(m[1])}`;
  m = /^FormalConjectures\/Kourovka\/(\d+)_(\d+)[a-z]*\.lean$/.exec(path);
  if (m) return `kourovka:${m[1]}.${m[2]}`;
  m = /^FormalConjectures\/HilbertProblems\/(\d+)\.lean$/.exec(path);
  if (m) return `hilbert:${Number(m[1])}`;
  m = /^FormalConjectures\/Millennium\/([A-Za-z]+)\.lean$/.exec(path);
  if (m) return `millennium:${m[1]}`;
  return null;
}

/** Catalogue key → the first (by id) open formal-conjectures problem with that key; practice problems never count. */
export function formalConjecturesKeys(problems: Problem[]): Map<string, string> {
  const out = new Map<string, string>();
  for (const p of problems) {
    if (p.source.name !== 'formal-conjectures' || p.tags.includes(PRACTICE_TAG) || !p.source.path) continue;
    const key = catalogueKeyFromFcPath(p.source.path);
    if (key && !out.has(key)) out.set(key, p.id);
  }
  return out;
}

// ---------------------------------------------------------------- writing

/** Every problem in the repo (validated). Empty when there is no problems/ directory. */
export async function repoProblems(root: string): Promise<Problem[]> {
  return existsSync(join(root, 'problems')) ? loadProblems(root) : [];
}

export interface WriteResult {
  written: number;
  removed: string[];
}

/**
 * Replace one source's problems: write `problems` (keeping the `added` date of a problem that already
 * exists), delete that source's problems that are no longer imported, and write sources/<name>.json.
 * Problems of other sources are never touched.
 */
export async function writeSourceProblems(
  root: string,
  sourceName: string,
  existing: Problem[],
  problems: Problem[],
  record: { repo: string; commit: string; licence: string; date: string },
  dryRun = false,
): Promise<WriteResult> {
  const mine = new Map(existing.filter((p) => p.source.name === sourceName).map((p) => [p.id, p]));
  const others = new Set(existing.filter((p) => p.source.name !== sourceName).map((p) => p.id));
  const keep = new Set<string>();
  const final: Problem[] = [];
  for (const p of problems) {
    if (others.has(p.id)) throw new Error(`${p.id} already exists from another source`);
    if (keep.has(p.id)) throw new Error(`duplicate id ${p.id}`);
    keep.add(p.id);
    const withDate = Problem.parse({ ...p, added: mine.get(p.id)?.added ?? p.added });
    const issues = problemIssues(withDate);
    if (issues.length) throw new Error(`${p.id}: ${issues.join('; ')}`);
    final.push(withDate);
  }
  const removed = [...mine.keys()].filter((id) => !keep.has(id)).sort();
  if (dryRun) return { written: final.length, removed };

  for (const id of removed) await rm(join(root, 'problems', `${id}.yaml`));
  for (const p of final) await writeYaml(join(root, 'problems', `${p.id}.yaml`), p, Problem);

  const sourceFile = join(root, 'sources', `${sourceName}.json`);
  let importedAt = record.date;
  if (existsSync(sourceFile)) {
    const prev = JSON.parse(await readFile(sourceFile, 'utf8')) as Record<string, string>;
    if (prev.commit === record.commit && typeof prev.imported_at === 'string') importedAt = prev.imported_at;
  }
  await mkdir(dirname(sourceFile), { recursive: true });
  const out = { repo: record.repo, commit: record.commit, licence: record.licence, imported_at: importedAt };
  await writeFile(sourceFile, `${JSON.stringify(out, null, 2)}\n`);
  return { written: final.length, removed };
}

async function gitOut(dir: string, ...args: string[]): Promise<string | null> {
  const p = Bun.spawn(['git', ...args], { cwd: dir, stdout: 'pipe', stderr: 'ignore' });
  const out = (await new Response(p.stdout).text()).trim();
  return (await p.exited) === 0 ? out : null;
}

/**
 * The HEAD commit of the git checkout whose top level is `dir`, or null when `dir` is not the top of a
 * checkout (a directory inside some other repository does not count).
 */
export async function gitHead(dir: string): Promise<string | null> {
  const top = await gitOut(dir, 'rev-parse', '--show-toplevel');
  if (top === null || realpathSync(top) !== realpathSync(dir)) return null;
  const head = await gitOut(dir, 'rev-parse', 'HEAD');
  return head && /^[0-9a-f]{40}$/.test(head) ? head : null;
}
