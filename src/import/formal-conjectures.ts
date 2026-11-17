import { existsSync } from 'node:fs';
import { mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { problemIdFromLeanName } from '../ids.ts';
import { writeYaml } from '../repo.ts';
import { PRACTICE_TAG, Problem, problemIssues, UpstreamResolution } from '../schema.ts';
import type { LeanDefinition } from '../schema.ts';
import { parseLeanFile, referencedDefs, referencesSorryDef, usedNotation } from './lean-parse.ts';
import type { Category, DefDecl, OpenDecl } from './lean-parse.ts';
import { PRACTICE, PRACTICE_BANNED, PRACTICE_MAX_PROOF_LINES } from './practice.ts';
import type { PracticeEntry } from './practice.ts';

export const SOURCE_NAME = 'formal-conjectures';
export const SOURCE_REPO = 'https://github.com/google-deepmind/formal-conjectures';
export const SOURCE_LICENCE = 'Apache-2.0';
/** Tag for problems whose statement depends on an upstream `sorry` definition (an unchecked answer). */
export const ANSWER_REQUIRED = 'answer-required';
export const NO_STATEMENT = '(No informal statement upstream. See the Lean statement.)';
/** Longest definition text stored per problem; longer ones are cut and end in `…`. */
export const DEFINITION_MAX_CHARS = 4000;

export interface ImportOptions {
  /** Directory of the formal-conjectures checkout. */
  checkout: string;
  /** Repo root to write `problems/` and `sources/` into. */
  root: string;
  /** Import date, YYYY-MM-DD. */
  date: string;
  /** Plan only; write nothing. */
  dryRun?: boolean;
  /** Practice declarations to import (default: the curated list in practice.ts). */
  practice?: readonly PracticeEntry[];
}

export interface Collision {
  name: string;
  assigned: string;
  path: string;
}

export interface ImportSummary {
  commit: string;
  leanToolchain: string;
  files: number;
  found: number;
  imported: number;
  /** Practice problems imported (part of `imported`). */
  practice: number;
  /** Problems kept as upstream_status `solved` (part of `imported`): already here, now settled upstream. */
  solved: string[];
  tags: Record<string, number>;
  noDocstring: number;
  collisions: Collision[];
  skippedLinks: string[];
  removed: string[];
  skipped: { path: string; reason: string }[];
  titleFallbacks: number;
}

async function git(cwd: string, ...args: string[]): Promise<string> {
  const p = Bun.spawn(['git', ...args], { cwd, stdout: 'pipe', stderr: 'pipe' });
  const [out, err] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text()]);
  if ((await p.exited) !== 0) throw new Error(`git ${args.join(' ')} failed in ${cwd}: ${err.trim()}`);
  return out.trim();
}

async function leanFiles(dir: string): Promise<string[]> {
  const out: string[] = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...(await leanFiles(p)));
    else if (e.name.endsWith('.lean')) out.push(p);
  }
  return out;
}

const LEAN_IDENT = /^[A-Za-z_\u00C0-\u02FF\u0370-\u03FF\u1F00-\u1FFF\u2100-\u214F\u{1D49C}-\u{1D59F}][A-Za-z0-9_'!?\u00C0-\u02FF\u0370-\u03FF\u1F00-\u1FFF\u2080-\u209C\u2100-\u214F\u{1D49C}-\u{1D59F}]*$/u;

/** `FormalConjectures/ErdosProblems/1.lean` → `FormalConjectures.ErdosProblems.«1»`. */
export function moduleName(path: string): string {
  return path
    .replace(/\.lean$/, '')
    .split('/')
    .map((c) => (LEAN_IDENT.test(c) ? c : `«${c}»`))
    .join('.');
}

/** `ErdosProblems` → `erdos-problems`; `OEIS` → `oeis`; `GreensOpenProblems` → `greens-open-problems`. */
export function kebab(s: string): string {
  return s
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/([A-Z]+)([A-Z][a-z])/g, '$1-$2')
    .replace(/[^A-Za-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .toLowerCase();
}

const LINK = /\[([^\]]+)\]\((https?:\/\/(?:[^()\s]|\([^()\s]*\))+)\)/g;
const BARE_REFERENCE = /\*References?:\*[ \t]*(https?:\/\/[^\s<>)\]]+)/g;

/** Markdown links and bare `*Reference:*` urls from the given texts, deduped by url, in order. */
export function extractReferences(texts: string[]): { label: string; url: string }[] {
  const seen = new Set<string>();
  const refs: { label: string; url: string }[] = [];
  const add = (label: string, url: string) => {
    url = url.replace(/[.,;:]+$/, '');
    if (seen.has(url) || !URL.canParse(url)) return;
    seen.add(url);
    refs.push({ label: label.replace(/\s+/g, ' ').trim(), url });
  };
  for (const text of texts) {
    const hits: { at: number; label: string; url: string }[] = [];
    for (const m of text.matchAll(LINK)) hits.push({ at: m.index!, label: m[1]!, url: m[2]! });
    for (const m of text.matchAll(BARE_REFERENCE)) {
      const url = m[1]!.replace(/[.,;:]+$/, '');
      hits.push({ at: m.index!, label: url, url });
    }
    hits.sort((a, b) => a.at - b.at);
    for (const h of hits) add(h.label, h.url);
  }
  return refs;
}

function titleFor(base: string, d: OpenDecl): string {
  const i = d.fullName.indexOf('.variants.');
  return i >= 0 ? `${base} (variant: ${d.fullName.slice(i + '.variants.'.length)})` : base;
}

function shortName(d: OpenDecl): string {
  const parts = d.fullName.match(/(?:«[^»]*»|[^.«»])+/g) ?? [d.fullName];
  return parts[parts.length - 1]!;
}

interface Pending {
  path: string;
  decl: OpenDecl;
  title: string;
  tags: string[];
  definitions: DefDecl[];
  practice: PracticeEntry | null;
  /** Already in the catalogue and now `research solved` (or `textbook`) upstream: kept, marked solved. */
  solved?: boolean;
}

/** Cut a definition's text at `max` UTF-16 units without splitting a surrogate pair; mark the cut. */
export function capText(text: string, max = DEFINITION_MAX_CHARS): string {
  if (text.length <= max) return text;
  let cut = max;
  const code = text.charCodeAt(cut - 1);
  if (code >= 0xd800 && code <= 0xdbff) cut--;
  return `${text.slice(0, cut)}…`;
}

/** Why a practice entry's upstream declaration does not qualify, or null when it does. */
export function practiceProblem(decl: OpenDecl): string | null {
  if (decl.category !== 'textbook') return 'not `category textbook` upstream';
  if (decl.isPrivate) return 'declared private';
  if (PRACTICE_BANNED.test(decl.maskedProof)) return 'upstream proof uses sorry, admit or native_decide';
  if (decl.proofLines > PRACTICE_MAX_PROOF_LINES) return `upstream proof has ${decl.proofLines} lines (max ${PRACTICE_MAX_PROOF_LINES})`;
  return null;
}

export async function importFormalConjectures(opts: ImportOptions): Promise<ImportSummary> {
  const { checkout, root, date } = opts;
  const commit = await git(checkout, 'rev-parse', 'HEAD');
  if (!/^[0-9a-f]{40}$/.test(commit)) throw new Error(`unexpected commit ${commit}`);
  const leanToolchain = (await readFile(join(checkout, 'lean-toolchain'), 'utf8')).trim();

  const base = join(checkout, 'FormalConjectures');
  const files = (await leanFiles(base)).map((f) => relative(checkout, f).split('\\').join('/')).sort();
  const practiceList = opts.practice ?? PRACTICE;
  const practiceByPath = new Map<string, PracticeEntry[]>();
  for (const e of practiceList) practiceByPath.set(e.path, [...(practiceByPath.get(e.path) ?? []), e]);
  const summary: ImportSummary = {
    commit, leanToolchain, files: 0, found: 0, imported: 0, practice: 0, solved: [], tags: {}, noDocstring: 0,
    collisions: [], skippedLinks: [], removed: [], skipped: [], titleFallbacks: 0,
  };

  // Problems already imported are kept when upstream settles them (marked `solved`), never dropped.
  const existing = await existingProblems(root);
  const existingPaths = new Set([...existing.values()].map((e) => e.path));
  const pending: Pending[] = [];
  for (const path of files) {
    const text = await readFile(join(checkout, path), 'utf8');
    const wanted = practiceByPath.get(path) ?? [];
    practiceByPath.delete(path);
    const mayHoldSolved = existingPaths.has(path);
    if (!text.includes('category research open') && wanted.length === 0 && !mayHoldSolved) continue;
    let parsed;
    try {
      const categories: Category[] = ['research open'];
      if (wanted.length || mayHoldSolved) categories.push('textbook');
      if (mayHoldSolved) categories.push('research solved');
      parsed = parseLeanFile(text, { categories });
    } catch (e) {
      summary.skipped.push({ path, reason: (e as Error).message });
      continue;
    }
    const practiceDecls: { decl: OpenDecl; entry: PracticeEntry }[] = [];
    for (const entry of wanted) {
      const decl = parsed.decls.find((d) => d.category === 'textbook' && d.fullName === entry.decl);
      const why = decl ? practiceProblem(decl) : 'no such textbook declaration';
      if (why) summary.skipped.push({ path, reason: `practice ${entry.decl}: ${why}` });
      else practiceDecls.push({ decl: decl!, entry });
    }
    const opened = parsed.decls.filter((d) => d.category === 'research open');
    const practiceNames = new Set(wanted.map((e) => e.decl));
    // A non-practice problem we already have whose declaration upstream is now `research solved` or `textbook`.
    const solved = parsed.decls.filter((d) => {
      if (d.category === 'research open' || practiceNames.has(d.fullName)) return false;
      // Same declaration, not merely the same id: `v1_eq_1_finite` and `V1_eq_1_finite` share an id.
      const had = existing.get(problemIdFromLeanName(d.fullName));
      return had !== undefined && had.decl === d.fullName && had.upstreamStatus !== 'textbook';
    });
    if (opened.length === 0 && practiceDecls.length === 0 && solved.length === 0) continue;
    if (opened.length) summary.files++;
    summary.found += opened.length;
    const segs = path.split('/');
    const folder = segs.length > 2 ? segs[1]! : segs[1]!.replace(/\.lean$/, '');
    let fileTitle = parsed.title;
    if (!fileTitle) {
      summary.titleFallbacks++;
      fileTitle = segs.slice(1).join('/').replace(/\.lean$/, '');
    }
    // Titles must be unique within a file: add the short name, then the full name, where they clash.
    // Open problems and practice problems are titled separately, so adding practice never retitles.
    const uniqueTitles = (decls: OpenDecl[], prefix: string): string[] => {
      const titles = decls.map((d) => `${prefix}${titleFor(fileTitle, d)}`);
      const clash = (ts: string[]) => ts.map((t, i) => ts.indexOf(t) !== i || ts.lastIndexOf(t) !== i);
      let c = clash(titles);
      const withShort = titles.map((t, i) => (c[i] ? `${t} (${shortName(decls[i]!)})` : t));
      c = clash(withShort);
      return withShort.map((t, i) => (c[i] ? `${titles[i]} (${decls[i]!.fullName})` : t));
    };
    const definitionsFor = (decl: OpenDecl) =>
      referencedDefs(decl.context, [decl.statement, ...usedNotation(decl.context, decl.statement)], parsed.defs);
    const unique = uniqueTitles(opened, '');
    opened.forEach((decl, i) => {
      const tags = [kebab(folder)];
      if (decl.fullName.includes('.variants.')) tags.push('variant');
      // Upstream leaves a definition the statement uses as `sorry`: any attempt inherits `sorryAx`.
      if (referencesSorryDef(decl, parsed.sorryDefs)) tags.push(ANSWER_REQUIRED);
      pending.push({ path, decl, title: unique[i]!, tags, definitions: definitionsFor(decl), practice: null });
    });
    const solvedTitles = uniqueTitles(solved, '');
    solved.forEach((decl, i) => {
      const tags = [kebab(folder)];
      if (decl.fullName.includes('.variants.')) tags.push('variant');
      if (referencesSorryDef(decl, parsed.sorryDefs)) tags.push(ANSWER_REQUIRED);
      pending.push({ path, decl, title: solvedTitles[i]!, tags, definitions: definitionsFor(decl), practice: null, solved: true });
    });
    const practiceTitles = uniqueTitles(practiceDecls.map((p) => p.decl), 'Practice: ');
    practiceDecls.forEach(({ decl, entry }, i) => {
      const tags = [kebab(folder)];
      if (decl.fullName.includes('.variants.')) tags.push('variant');
      if (referencesSorryDef(decl, parsed.sorryDefs)) {
        summary.skipped.push({ path, reason: `practice ${entry.decl}: statement uses an upstream sorry definition` });
        return;
      }
      tags.push(PRACTICE_TAG);
      pending.push({ path, decl, title: practiceTitles[i]!, tags, definitions: definitionsFor(decl), practice: entry });
    });
  }
  for (const [path, entries] of practiceByPath) {
    for (const e of entries) summary.skipped.push({ path, reason: `practice ${e.decl}: file not found or unreadable` });
  }
  if (summary.skipped.length) return summary;

  // Ids, collisions in declaration order.
  const used = new Set<string>();
  const problems: Problem[] = [];
  for (const { path, decl, title, tags, definitions, practice, solved } of pending) {
    const wanted = problemIdFromLeanName(decl.fullName);
    let id = wanted;
    for (let n = 2; used.has(id); n++) id = `${wanted}-${n}`;
    used.add(id);
    if (id !== wanted) summary.collisions.push({ name: decl.fullName, assigned: id, path });

    const moduleDocs = decl.moduleDocs;
    const refTexts = [...moduleDocs, ...(decl.docstring ? [decl.docstring] : [])];
    const allLinks = extractReferences(refTexts);
    const encoded = path.split('/').map(encodeURIComponent).join('/');
    const blob = `${SOURCE_REPO}/blob/${commit}/${encoded}`;
    const defs: LeanDefinition[] = definitions.map((d) => ({
      name: d.fullName, kind: d.kind, text: capText(d.text), url: `${blob}#L${d.line}`,
    }));
    const problem = Problem.parse({
      schema: 1,
      id,
      title,
      field: 'mathematics',
      tier: 'proof',
      statement: decl.docstring && decl.docstring !== '' ? decl.docstring : NO_STATEMENT,
      ams: decl.ams,
      tags,
      references: allLinks,
      source: {
        name: SOURCE_NAME,
        repo: SOURCE_REPO,
        commit,
        path,
        url: `${blob}#L${decl.line}`,
        licence: SOURCE_LICENCE,
      },
      upstream_status: practice ? 'textbook' : solved ? 'solved' : 'open',
      ...(solved ? { upstream_resolution: resolutionFor(decl, existing.get(id), commit, date) } : {}),
      ...(practice ? { difficulty: { level: 'practice', note: practice.note } } : {}),
      lean: {
        module: moduleName(path),
        decl: decl.fullName,
        statement: decl.statement,
        context: decl.context,
        definitions: defs,
      },
      added: existing.get(id)?.added ?? date,
    });
    const issues = problemIssues(problem);
    if (issues.length) throw new Error(`${id}: ${issues.join('; ')}`);
    if (!decl.docstring) summary.noDocstring++;
    for (const t of tags) summary.tags[t] = (summary.tags[t] ?? 0) + 1;
    if (practice) summary.practice++;
    if (solved) summary.solved.push(id);
    problems.push(problem);
  }
  summary.imported = problems.length;

  const keep = new Set(problems.map((p) => p.id));
  for (const id of existing.keys()) if (!keep.has(id)) summary.removed.push(id);
  summary.removed.sort();
  if (opts.dryRun) return summary;

  for (const id of summary.removed) await rm(join(root, 'problems', `${id}.yaml`));
  for (const p of problems) await writeYaml(join(root, 'problems', `${p.id}.yaml`), p, Problem);

  const sourceFile = join(root, 'sources', `${SOURCE_NAME}.json`);
  let importedAt = date;
  if (existsSync(sourceFile)) {
    const prev = JSON.parse(await readFile(sourceFile, 'utf8')) as Record<string, string>;
    if (prev.commit === commit && prev.lean_toolchain === leanToolchain && typeof prev.imported_at === 'string') {
      importedAt = prev.imported_at;
    }
  }
  // Written directly (not via writeJson, which sorts unknown keys) to keep the documented key order.
  await mkdir(dirname(sourceFile), { recursive: true });
  const record = { repo: SOURCE_REPO, commit, lean_toolchain: leanToolchain, licence: SOURCE_LICENCE, imported_at: importedAt };
  await writeFile(sourceFile, `${JSON.stringify(record, null, 2)}\n`);
  return summary;
}

export interface ExistingProblem {
  added: string;
  /** Upstream file it was imported from. */
  path: string;
  /** Lean declaration it was imported from. */
  decl: string;
  upstreamStatus: string;
  /** Statement as last imported (for a problem that was open then, the open statement). */
  statement: string;
  resolution?: UpstreamResolution;
}

/**
 * Bibliography entries `- [Key] text` from module docs that `note` cites as `[Key]` (not a `[label](url)`
 * link), in citation order. The url is the entry's first link, else its arXiv id's abstract page.
 */
export function citedEntries(note: string, moduleDocs: string[]): { key: string; text: string; url?: string }[] {
  const entries = new Map<string, string>();
  for (const doc of moduleDocs) {
    let key: string | null = null;
    let text = '';
    const flush = () => { if (key && !entries.has(key)) entries.set(key, text.trim()); key = null; text = ''; };
    for (const line of doc.split('\n')) {
      const m = /^\s*[-*]\s+\[([A-Za-z][\w+.-]*)\](?!\()\s*(.*)$/.exec(line);
      if (m) { flush(); key = m[1]!; text = m[2]!; }
      else if (key && /^\s+\S/.test(line)) text += ` ${line.trim()}`;
      else flush();
    }
    flush();
  }
  const out: { key: string; text: string; url?: string }[] = [];
  for (const m of note.matchAll(/\[([A-Za-z][\w+.-]*)(?:,[^\]]*)?\](?!\()/g)) {
    const key = m[1]!;
    const entry = entries.get(key);
    if (!entry || out.some((c) => c.key === key)) continue;
    const link = /\]\((https?:\/\/[^\s)]+)\)/.exec(entry)?.[1] ?? /(https?:\/\/[^\s)>\]]+)/.exec(entry)?.[1];
    const arxiv = /arXiv:\s*(\d{4}\.\d{4,5})/i.exec(entry)?.[1];
    const url = link ?? (arxiv ? `https://arxiv.org/abs/${arxiv}` : undefined);
    const text = entry.replace(/\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/https?:\/\/\S+/g, '').replace(/\s+/g, ' ').trim().replace(/[.,;]$/, '') || key;
    out.push({ key, text, ...(url && URL.canParse(url) ? { url } : {}) });
  }
  return out;
}

/**
 * How upstream settled `decl`: kept from the existing problem once recorded (a maintainer may have added
 * `outcome` and `summary`); otherwise, the first time, what upstream added to the docstring we imported
 * while it was open (all of the new docstring if upstream rewrote it), plus the formal proof it links.
 */
export function resolutionFor(decl: OpenDecl, prev: ExistingProblem | undefined, commit: string, date: string): UpstreamResolution {
  const proof = decl.formalProof && URL.canParse(decl.formalProof) ? decl.formalProof : undefined;
  if (prev?.resolution) {
    return UpstreamResolution.parse({ ...prev.resolution, ...(prev.resolution.formal_proof || !proof ? {} : { formal_proof: proof }) });
  }
  const now = (decl.docstring ?? '').trim();
  const before = (prev?.statement ?? '').trim();
  let note = before && now.startsWith(before) ? now.slice(before.length).trim() : now;
  const marked = decl.category === 'textbook' ? '`category textbook`' : '`category research solved`';
  if (!note) note = `formal-conjectures marks this ${marked}${proof ? ' and links a formal proof' : ''}; its docstring adds nothing more.`;
  const citations = citedEntries(note, decl.moduleDocs);
  return UpstreamResolution.parse({
    note,
    references: extractReferences([note]),
    ...(citations.length ? { citations } : {}),
    ...(proof ? { formal_proof: proof } : {}),
    detected: { commit, date },
  });
}

/** Existing problems from this source (never `witness.*`): id → its `added` date, upstream path and status. */
async function existingProblems(root: string): Promise<Map<string, ExistingProblem>> {
  const dir = join(root, 'problems');
  const out = new Map<string, ExistingProblem>();
  if (!existsSync(dir)) return out;
  for (const name of (await readdir(dir)).sort()) {
    if (!name.endsWith('.yaml') || name.startsWith('witness.')) continue;
    const raw = parseYaml(await readFile(join(dir, name), 'utf8')) as {
      source?: { name?: string; path?: string };
      added?: string;
      upstream_status?: string;
      lean?: { decl?: string };
      statement?: string;
      upstream_resolution?: unknown;
    } | null;
    if (raw?.source?.name === SOURCE_NAME && typeof raw.added === 'string') {
      out.set(name.slice(0, -5), {
        added: raw.added, path: raw.source.path ?? '', decl: raw.lean?.decl ?? '', upstreamStatus: raw.upstream_status ?? 'open',
        statement: raw.statement ?? '',
        ...(raw.upstream_resolution ? { resolution: UpstreamResolution.parse(raw.upstream_resolution) } : {}),
      });
    }
  }
  return out;
}
