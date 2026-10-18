import { existsSync } from 'node:fs';
import { mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { parse as parseYaml } from 'yaml';
import { problemIdFromLeanName } from '../ids.ts';
import { writeYaml } from '../repo.ts';
import { Problem, problemIssues } from '../schema.ts';
import { parseLeanFile } from './lean-parse.ts';
import type { OpenDecl } from './lean-parse.ts';

export const SOURCE_NAME = 'formal-conjectures';
export const SOURCE_REPO = 'https://github.com/google-deepmind/formal-conjectures';
export const SOURCE_LICENCE = 'Apache-2.0';
export const NO_STATEMENT = '(No informal statement upstream. See the Lean statement.)';

export interface ImportOptions {
  /** Directory of the formal-conjectures checkout. */
  checkout: string;
  /** Repo root to write `problems/` and `sources/` into. */
  root: string;
  /** Import date, YYYY-MM-DD. */
  date: string;
  /** Plan only; write nothing. */
  dryRun?: boolean;
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
}

export async function importFormalConjectures(opts: ImportOptions): Promise<ImportSummary> {
  const { checkout, root, date } = opts;
  const commit = await git(checkout, 'rev-parse', 'HEAD');
  if (!/^[0-9a-f]{40}$/.test(commit)) throw new Error(`unexpected commit ${commit}`);
  const leanToolchain = (await readFile(join(checkout, 'lean-toolchain'), 'utf8')).trim();

  const base = join(checkout, 'FormalConjectures');
  const files = (await leanFiles(base)).map((f) => relative(checkout, f).split('\\').join('/')).sort();
  const summary: ImportSummary = {
    commit, leanToolchain, files: 0, found: 0, imported: 0, tags: {}, noDocstring: 0,
    collisions: [], skippedLinks: [], removed: [], skipped: [], titleFallbacks: 0,
  };

  const pending: Pending[] = [];
  for (const path of files) {
    const text = await readFile(join(checkout, path), 'utf8');
    if (!text.includes('category research open')) continue;
    let parsed;
    try {
      parsed = parseLeanFile(text);
    } catch (e) {
      summary.skipped.push({ path, reason: (e as Error).message });
      continue;
    }
    if (parsed.decls.length === 0) continue;
    summary.files++;
    summary.found += parsed.decls.length;
    const segs = path.split('/');
    const folder = segs.length > 2 ? segs[1]! : segs[1]!.replace(/\.lean$/, '');
    let fileTitle = parsed.title;
    if (!fileTitle) {
      summary.titleFallbacks++;
      fileTitle = segs.slice(1).join('/').replace(/\.lean$/, '');
    }
    const titles = parsed.decls.map((d) => titleFor(fileTitle, d));
    // Titles must be unique within a file: add the short name, then the full name, where they clash.
    const clash = (ts: string[]) => ts.map((t, i) => ts.indexOf(t) !== i || ts.lastIndexOf(t) !== i);
    let c = clash(titles);
    const withShort = titles.map((t, i) => (c[i] ? `${t} (${shortName(parsed.decls[i]!)})` : t));
    c = clash(withShort);
    const unique = withShort.map((t, i) => (c[i] ? `${titles[i]} (${parsed.decls[i]!.fullName})` : t));
    parsed.decls.forEach((decl, i) => {
      const tags = [kebab(folder)];
      if (decl.fullName.includes('.variants.')) tags.push('variant');
      pending.push({ path, decl, title: unique[i]!, tags });
    });
  }
  if (summary.skipped.length) return summary;

  // Ids, collisions in declaration order.
  const used = new Set<string>();
  const problems: Problem[] = [];
  const existing = await existingProblems(root);
  for (const { path, decl, title, tags } of pending) {
    const wanted = problemIdFromLeanName(decl.fullName);
    let id = wanted;
    for (let n = 2; used.has(id); n++) id = `${wanted}-${n}`;
    used.add(id);
    if (id !== wanted) summary.collisions.push({ name: decl.fullName, assigned: id, path });

    const moduleDocs = decl.moduleDocs;
    const refTexts = [...moduleDocs, ...(decl.docstring ? [decl.docstring] : [])];
    const allLinks = extractReferences(refTexts);
    const encoded = path.split('/').map(encodeURIComponent).join('/');
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
        url: `${SOURCE_REPO}/blob/${commit}/${encoded}#L${decl.line}`,
        licence: SOURCE_LICENCE,
      },
      upstream_status: 'open',
      lean: { module: moduleName(path), decl: decl.fullName, statement: decl.statement },
      added: existing.get(id) ?? date,
    });
    const issues = problemIssues(problem);
    if (issues.length) throw new Error(`${id}: ${issues.join('; ')}`);
    if (!decl.docstring) summary.noDocstring++;
    for (const t of tags) summary.tags[t] = (summary.tags[t] ?? 0) + 1;
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

/** Existing problems from this source (never `witness.*`): id → its `added` date. */
async function existingProblems(root: string): Promise<Map<string, string>> {
  const dir = join(root, 'problems');
  const out = new Map<string, string>();
  if (!existsSync(dir)) return out;
  for (const name of (await readdir(dir)).sort()) {
    if (!name.endsWith('.yaml') || name.startsWith('witness.')) continue;
    const raw = parseYaml(await readFile(join(dir, name), 'utf8')) as { source?: { name?: string }; added?: string } | null;
    if (raw?.source?.name === SOURCE_NAME && typeof raw.added === 'string') out.set(name.slice(0, -5), raw.added);
  }
  return out;
}
