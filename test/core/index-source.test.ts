import { afterEach, beforeEach, describe, expect, test } from 'bun:test';
import { mkdirSync, mkdtempSync, readdirSync, rmSync, utimesSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { COMMAND_MODULES, commandNames, main } from '../../src/cli.ts';
import {
  CACHE_TTL_MS,
  DEFAULT_INDEX_URLS,
  cacheDir,
  cloneRequiredMessage,
  fetchIndex,
  findCloneRoot,
  indexToRows,
  indexUrls,
} from '../../src/index-source.ts';
import { buildIndex } from '../../src/commands/index.ts';
import { GOOD } from './helpers.ts';

let tmp: string;
let env: Record<string, string | undefined>;
beforeEach(() => {
  tmp = mkdtempSync(join(tmpdir(), 'frontier-src-'));
  env = { FRONTIER_CACHE_DIR: join(tmp, 'cache') };
});
afterEach(() => rmSync(tmp, { recursive: true, force: true }));

describe('indexUrls', () => {
  test('defaults to GitHub release then terramind.org', () => {
    expect(indexUrls({})).toEqual(DEFAULT_INDEX_URLS);
    expect(DEFAULT_INDEX_URLS[1]).toBe('https://terramind.org/frontier/index.json');
  });
  test('FRONTIER_INDEX_URL replaces the defaults', () => {
    expect(indexUrls({ FRONTIER_INDEX_URL: 'file:///x/index.json' })).toEqual(['file:///x/index.json']);
  });
});

describe('cacheDir', () => {
  test('per OS', () => {
    expect(cacheDir({}, 'darwin')).toContain(join('Library', 'Caches', 'terramind-frontier'));
    expect(cacheDir({ XDG_CACHE_HOME: '/xdg' }, 'linux')).toBe(join('/xdg', 'terramind-frontier'));
    expect(cacheDir({ LOCALAPPDATA: 'C:\\L' }, 'win32')).toContain('terramind-frontier');
    expect(cacheDir({ FRONTIER_CACHE_DIR: '/c' }, 'linux')).toBe('/c');
  });
});

describe('fetchIndex', () => {
  async function sampleIndexText(): Promise<string> {
    return JSON.stringify(await buildIndex(GOOD, new Date('2026-01-01T00:00:00Z')));
  }

  test('reads file:// without caching', async () => {
    const file = join(tmp, 'index.json');
    writeFileSync(file, await sampleIndexText());
    const index = await fetchIndex({ env: { ...env, FRONTIER_INDEX_URL: `file://${file}` } });
    expect(index.problems.length).toBeGreaterThan(0);
    expect(() => readdirSync(env.FRONTIER_CACHE_DIR!)).toThrow();
  });

  test('caches an http fetch for an hour, then refetches', async () => {
    const text = await sampleIndexText();
    let calls = 0;
    const fetchText = async () => (calls++, text);
    const o = { env, fetchText };
    await fetchIndex({ ...o, now: Date.now() });
    await fetchIndex({ ...o, now: Date.now() });
    expect(calls).toBe(1);
    const later = Date.now() + CACHE_TTL_MS + 60_000;
    const cached = join(env.FRONTIER_CACHE_DIR!, readdirSync(env.FRONTIER_CACHE_DIR!)[0]!);
    utimesSync(cached, new Date(Date.now() - CACHE_TTL_MS - 60_000), new Date(Date.now() - CACHE_TTL_MS - 60_000));
    await fetchIndex({ ...o, now: later });
    expect(calls).toBe(2);
  });

  test('falls back to the second URL', async () => {
    const text = await sampleIndexText();
    const seen: string[] = [];
    const fetchText = async (url: string) => {
      seen.push(url);
      if (url === DEFAULT_INDEX_URLS[0]) throw new Error('HTTP 404');
      return text;
    };
    await fetchIndex({ env, fetchText });
    expect(seen).toEqual(DEFAULT_INDEX_URLS);
  });

  test('uses a stale cache when offline', async () => {
    const text = await sampleIndexText();
    await fetchIndex({ env, fetchText: async () => text });
    const dir = env.FRONTIER_CACHE_DIR!;
    for (const f of readdirSync(dir)) utimesSync(join(dir, f), new Date(0), new Date(0));
    const warn = console.error;
    const warned: string[] = [];
    console.error = (...a: unknown[]) => void warned.push(a.join(' '));
    const index = await fetchIndex({ env, fetchText: async () => { throw new Error('offline'); } }).finally(() => (console.error = warn));
    expect(warned[0]).toContain('cached copy');
    expect(index.problems.length).toBeGreaterThan(0);
  });

  test('says the catalog is not public yet or there is no network', async () => {
    const err = await fetchIndex({ env, fetchText: async () => { throw new Error('HTTP 404'); } }).catch((e: Error) => e);
    expect((err as Error).message).toContain("isn't public yet");
    expect((err as Error).message).toContain('no network');
    expect((err as Error).message).toContain('HTTP 404');
    expect((err as Error).message).toContain('git clone');
  });

  test('rejects an index that fails the schema', async () => {
    const err = await fetchIndex({ env, fetchText: async () => '{"schema":2}' }).catch((e: Error) => e);
    expect(err).toBeInstanceOf(Error);
  });
});

describe('indexToRows', () => {
  test('matches the local loaders on the fixture repo', async () => {
    const { loadAll } = await import('../../src/repo.ts');
    const local = await loadAll(GOOD);
    const rows = indexToRows(await buildIndex(GOOD));
    expect(rows.map((r) => [r.problem.id, r.status, r.attempts.length])).toEqual(
      local.map((r) => [r.problem.id, r.status, r.attempts.length]),
    );
    expect(rows[0]!.problem).not.toHaveProperty('attempts');
  });
});

describe('clone detection', () => {
  test('finds a clone (package.json plus problems/) and ignores other projects', () => {
    const clone = join(tmp, 'clone');
    mkdirSync(join(clone, 'problems'), { recursive: true });
    mkdirSync(join(clone, 'sub'));
    writeFileSync(join(clone, 'package.json'), '{"name":"@terramind/frontier"}');
    expect(findCloneRoot(join(clone, 'sub'))).toBe(clone);
    const other = join(tmp, 'other');
    mkdirSync(join(other, 'problems'), { recursive: true });
    writeFileSync(join(other, 'package.json'), '{"name":"something-else"}');
    rmSync(join(other, 'problems'), { recursive: true });
    expect(findCloneRoot(other)).toBeNull();
  });
  test('the message tells how to clone', () => {
    expect(cloneRequiredMessage('new')).toContain('git clone https://github.com/terramind-org/frontier && cd frontier && bun install');
  });
});

describe('cli outside a clone', () => {
  const run = async (cwd: string, ...argv: string[]) => {
    const prev = process.cwd();
    const errs: string[] = [];
    const orig = console.error;
    console.error = (...a: unknown[]) => void errs.push(a.join(' '));
    process.chdir(cwd);
    try {
      return { code: await main(argv), err: errs.join('\n') };
    } finally {
      process.chdir(prev);
      console.error = orig;
    }
  };
  test('clone-only commands exit 2 with the clone instructions', async () => {
    for (const cmd of ['new', 'check', 'submit', 'validate', 'diagnose']) {
      const r = await run(tmp, cmd, 'x');
      expect(r.code).toBe(2);
      expect(r.err).toContain('git clone');
    }
  });
});

// The npm package is the node bundle; nothing bun-only (import.meta.dir, import.meta.main) may run at its load time.
const node = Bun.which('node');
test.skipIf(!node)('the npm bundle runs under node outside a clone and carries its third-party licences', async () => {
  const repo = join(import.meta.dir, '..', '..');
  const build = Bun.spawnSync(['bun', 'scripts/build-cli.ts'], { cwd: repo });
  expect(build.exitCode).toBe(0);
  const bundle = join(repo, 'dist-cli', 'frontier.mjs');
  const head = (await Bun.file(bundle).text()).slice(0, 4000);
  expect(head).toContain('yaml@');
  expect(head).toContain('zod@');
  const help = Bun.spawnSync([node!, bundle, '--help'], { cwd: tmp });
  expect({ code: help.exitCode, err: help.stderr.toString() }).toEqual({ code: 0, err: '' });
  const file = join(tmp, 'index.json');
  writeFileSync(file, JSON.stringify(await buildIndex(GOOD, new Date('2026-01-01T00:00:00Z'))));
  const r = Bun.spawnSync([node!, bundle, 'list', '--json'], { cwd: tmp, env: { ...process.env, ...env, FRONTIER_INDEX_URL: `file://${file}` } });
  expect({ code: r.exitCode, err: r.stderr.toString() }).toEqual({ code: 0, err: '' });
  expect(JSON.parse(r.stdout.toString()).length).toBeGreaterThan(0);
}, 60_000);

test('COMMAND_MODULES covers every file in src/commands', () => {
  expect(Object.keys(COMMAND_MODULES).sort()).toEqual(commandNames());
});
