import { createHash } from 'node:crypto';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Index } from './schema.ts';
import type { Attempt, Problem, Verdict } from './schema.ts';

/**
 * The "index source": outside a clone, read-only commands (list, show, pick) read the published
 * `index.json` instead of the local `problems/` and `attempts/` files.
 */

export const DEFAULT_INDEX_URLS = [
  'https://github.com/terramind-org/frontier/releases/download/index/index.json',
  'https://terramind.org/frontier/index.json',
];
export const CACHE_TTL_MS = 60 * 60 * 1000;
export const CLONE_COMMAND = 'git clone https://github.com/terramind-org/frontier && cd frontier && bun install';

/** The frontier clone containing `start` (default cwd): the nearest directory above it with a package.json and a problems/ directory. */
export function findCloneRoot(start: string = process.cwd()): string | null {
  let dir = resolve(start);
  for (;;) {
    if (existsSync(join(dir, 'package.json')) && existsSync(join(dir, 'problems'))) return dir;
    const parent = dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

/** The text printed (exit 2) when a command that needs a clone runs outside one. */
export function cloneRequiredMessage(command: string): string {
  return [
    `frontier ${command} needs a clone of the Frontier repo (it reads and writes problems/ and attempts/ files).`,
    'Get one with:',
    `  ${CLONE_COMMAND}`,
    `then run \`bun frontier ${command}\` inside it. list, show and pick work anywhere.`,
  ].join('\n');
}

/** Index URLs to try, in order: FRONTIER_INDEX_URL alone if set, else the defaults. */
export function indexUrls(env: Record<string, string | undefined> = process.env): string[] {
  const custom = env.FRONTIER_INDEX_URL?.trim();
  return custom ? [custom] : DEFAULT_INDEX_URLS;
}

/** OS cache directory for the catalog. */
export function cacheDir(env: Record<string, string | undefined> = process.env, platform: string = process.platform): string {
  if (env.FRONTIER_CACHE_DIR) return env.FRONTIER_CACHE_DIR;
  const home = homedir();
  if (platform === 'darwin') return join(home, 'Library', 'Caches', 'terramind-frontier');
  if (platform === 'win32') return join(env.LOCALAPPDATA ?? join(home, 'AppData', 'Local'), 'terramind-frontier', 'Cache');
  return join(env.XDG_CACHE_HOME ?? join(home, '.cache'), 'terramind-frontier');
}

function cachePath(url: string, env: Record<string, string | undefined>): string {
  return join(cacheDir(env), `index-${createHash('sha256').update(url).digest('hex').slice(0, 16)}.json`);
}

export interface FetchOptions {
  env?: Record<string, string | undefined>;
  now?: number;
  /** Replaceable for tests. */
  fetchText?: (url: string) => Promise<string>;
}

async function defaultFetchText(url: string): Promise<string> {
  if (url.startsWith('file://')) return readFile(fileURLToPath(url), 'utf8');
  const res = await fetch(url, { signal: AbortSignal.timeout(15_000), headers: { accept: 'application/json' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.text();
}

function parseIndex(text: string): Index {
  return Index.parse(JSON.parse(text));
}

/**
 * The published Index: a cache file younger than an hour, else the first reachable URL (then cached),
 * else a stale cache with a warning, else an error saying the catalog is not public yet or there is no network.
 * `file://` URLs are read directly and never cached.
 */
export async function fetchIndex(opts: FetchOptions = {}): Promise<Index> {
  const env = opts.env ?? process.env;
  const now = opts.now ?? Date.now();
  const fetchText = opts.fetchText ?? defaultFetchText;
  const urls = indexUrls(env);
  const failures: string[] = [];
  let stale: { index: Index; url: string } | null = null;
  for (const url of urls) {
    const local = url.startsWith('file://');
    const path = cachePath(url, env);
    if (!local && existsSync(path)) {
      try {
        const index = parseIndex(readFileSync(path, 'utf8'));
        if (now - statSync(path).mtimeMs < CACHE_TTL_MS) return index;
        stale ??= { index, url };
      } catch {
        // corrupt cache: refetch
      }
    }
    try {
      const index = parseIndex(await fetchText(url));
      if (!local) {
        try {
          await mkdir(dirname(path), { recursive: true });
          await writeFile(path, JSON.stringify(index));
        } catch {
          // a read-only cache dir only costs a refetch next time
        }
      }
      return index;
    } catch (e) {
      failures.push(`  ${url}: ${(e as Error).message.split('\n')[0]}`);
    }
  }
  if (stale) {
    console.error(`warning: could not refresh the catalog, using a cached copy (from ${stale.url})`);
    return stale.index;
  }
  throw new Error(
    [
      "cannot load the problem catalog: it isn't public yet, or there is no network.",
      ...failures,
      'Set FRONTIER_INDEX_URL to another index.json (https:// or file://), or work in a clone:',
      `  ${CLONE_COMMAND}`,
    ].join('\n'),
  );
}

/** Index to the shape the loaders return. Attempt files are not in the index, so only the listed fields exist. */
export function indexToRows(index: Index) {
  return index.problems.map(({ status, attempts, ...problem }) => ({
    problem: problem as Problem,
    status,
    attempts: attempts.map(({ verdict, ...a }) => ({
      attempt: { ...a, schema: 1, problem: problem.id, files: [], people: [], licence: 'CC-BY-4.0' } as unknown as Attempt,
      dir: '',
      verdict: verdict as Verdict | null,
    })),
  }));
}

/** Rows for list/show/pick when no clone is around. */
export async function loadAllFromIndex(opts: FetchOptions = {}) {
  return indexToRows(await fetchIndex(opts));
}
