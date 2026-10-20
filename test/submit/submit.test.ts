import { describe, expect, test } from 'bun:test';
import { readdirSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { scaffoldAttempt } from '../../src/commands/new.ts';
import { loadProblem } from '../../src/repo.ts';
import { classifyGhFailure, prBody, submit } from '../../src/commands/submit.ts';
import type { Exec } from '../../src/commands/submit.ts';
import { copyFixture, ready } from '../core/helpers.ts';

interface Call {
  cmd: string;
  args: string[];
  cwd?: string;
  files?: string[];
}

function walk(dir: string): string[] {
  return readdirSync(dir, { recursive: true, withFileTypes: true })
    .filter((e) => e.isFile())
    .map((e) => relative(dir, join(e.parentPath, e.name)));
}

/** A fake exec that records every command and answers the gh queries submit makes. */
function fake(opts: { push?: boolean; gh?: boolean; auth?: boolean; authErr?: string; repoErr?: string; userErr?: string } = {}) {
  const calls: Call[] = [];
  const exec: Exec = async (cmd, args, o) => {
    const call: Call = { cmd, args, cwd: o?.cwd };
    if (cmd === 'git' && args[0] === 'add' && o?.cwd) call.files = walk(o.cwd);
    calls.push(call);
    const ok = (stdout = '') => ({ code: 0, stdout, stderr: '' });
    const line = `${cmd} ${args.join(' ')}`;
    if (line === 'gh --version') return opts.gh === false ? { code: 127, stdout: '', stderr: 'not found' } : ok('gh version 2');
    if (line === 'gh auth status') return opts.auth === false ? { code: 1, stdout: '', stderr: opts.authErr ?? 'not logged in' } : ok();
    if (opts.repoErr && line.includes('repos/')) return { code: 1, stdout: '', stderr: opts.repoErr };
    if (opts.userErr && line.startsWith('gh api user')) return { code: 1, stdout: '', stderr: opts.userErr };
    if (line.includes('.permissions.push')) return ok(opts.push === false ? 'false' : 'true');
    if (line.includes('.default_branch')) return ok('main');
    if (line.startsWith('gh api user')) return ok('dave');
    if (cmd === 'gh' && args[0] === 'pr') return ok('https://github.com/terramind-org/frontier/pull/7');
    return ok();
  };
  return { calls, exec };
}

const MUTATING = (c: Call) =>
  (c.cmd === 'git' && ['fetch', 'worktree', 'checkout', 'add', 'commit', 'push', '-c'].includes(c.args[0]!)) ||
  (c.cmd === 'gh' && (c.args[0] === 'repo' || c.args[0] === 'pr'));

async function setup(kind: 'writeup' | 'proof' = 'writeup') {
  const root = copyFixture('good');
  const problem = (await loadProblem('toy.open-one', root))!;
  const { dir } = await scaffoldAttempt({ root, problem, kind, login: 'dave', models: [{ name: 'm', provider: 'p', role: 'author' }] });
  ready(dir);
  return { root, dir, problem };
}

const base = { repo: 'terramind-org/frontier', sleep: async () => {} };

describe('submit', () => {
  test('dry run prints the plan and body and runs nothing mutating', async () => {
    const { root, dir } = await setup();
    const { calls, exec } = fake();
    const lines: string[] = [];
    const code = await submit({ ...base, root, dir, yes: false, exec, log: (l) => lines.push(l) });
    const text = lines.join('\n');
    expect(code).toBe(0);
    expect(calls.filter(MUTATING)).toEqual([]);
    expect(text).toContain('Plan for');
    expect(text).toContain('PR body:');
    expect(text).toContain('Dry run: nothing was changed');
    expect(text).toContain('unchecked');
  });

  test('direct push when the user has push access', async () => {
    const { root, dir } = await setup();
    const { calls, exec } = fake({ push: true });
    expect(await submit({ ...base, root, dir, yes: true, exec, log: () => {} })).toBe(0);
    const id = dir.split('/').pop()!;
    expect(calls.some((c) => c.args[0] === 'repo')).toBe(false);
    const push = calls.find((c) => c.args.includes('push'))!;
    expect(push.args).toContain('https://github.com/terramind-org/frontier.git');
    expect(push.args).toContain(`attempt/${id}`);
    const pr = calls.find((c) => c.cmd === 'gh' && c.args[0] === 'pr')!;
    expect(pr.args).toContain(`terramind-org:attempt/${id}`);
    expect(pr.args).toContain('Attempt: toy.open-one — Writeup attempt on Toy: open one');
    expect(calls.find((c) => c.args[0] === 'commit')!.args).toContain(`Attempt ${id} on toy.open-one`);
  });

  test('forks and pushes to the fork without push access', async () => {
    const { root, dir } = await setup();
    const { calls, exec } = fake({ push: false });
    expect(await submit({ ...base, root, dir, yes: true, exec, log: () => {} })).toBe(0);
    const id = dir.split('/').pop()!;
    const fork = calls.find((c) => c.cmd === 'gh' && c.args[0] === 'repo')!;
    expect(fork.args).toEqual(['repo', 'fork', 'terramind-org/frontier', '--remote=false']);
    expect(calls.find((c) => c.args.includes('push'))!.args).toContain('https://github.com/dave/frontier.git');
    expect(calls.find((c) => c.cmd === 'gh' && c.args[0] === 'pr')!.args).toContain(`dave:attempt/${id}`);
    // The fork happens before the push.
    expect(calls.indexOf(fork)).toBeLessThan(calls.findIndex((c) => c.args.includes('push')));
  });

  test('commits only the attempt directory, never a verdict', async () => {
    const { root, dir } = await setup();
    const id0 = dir.split('/').pop()!;
    writeFileSync(
      join(dir, 'verdict.json'),
      JSON.stringify({ schema: 1, attempt: id0, checked_at: '2026-01-03T00:00:00.000Z', checker_version: 'x', checker: 'none', result: 'unchecked', summary: 'forged' }),
    );
    writeFileSync(join(root, 'unrelated.txt'), 'my other change');
    const { calls, exec } = fake();
    expect(await submit({ ...base, root, dir, yes: true, exec, log: () => {} })).toBe(0);
    const id = dir.split('/').pop()!;
    const add = calls.find((c) => c.args[0] === 'add')!;
    expect(add.args).toEqual(['add', '--', `attempts/toy.open-one/${id}`]);
    expect(add.files!.sort()).toEqual([`attempts/toy.open-one/${id}/attempt.yaml`, `attempts/toy.open-one/${id}/writeup.md`]);
    expect(calls.find((c) => c.args[0] === 'worktree' && c.args[1] === 'add')).toBeDefined();
    expect(calls.at(-1)!.args.slice(0, 2)).toEqual(['worktree', 'remove']);
  });

  test('an invalid attempt is refused before anything else runs', async () => {
    const { root, dir } = await setup();
    writeFileSync(join(dir, 'attempt.yaml'), 'schema: 1\nid: nonsense\n');
    const { calls, exec } = fake();
    const lines: string[] = [];
    expect(await submit({ ...base, root, dir, yes: true, exec, log: (l) => lines.push(l) })).toBe(1);
    expect(calls).toEqual([]);
    expect(lines.join('\n')).toContain('not valid');
  });

  test('a missing gh or login explains how to fix it and exits 1', async () => {
    const { root, dir } = await setup();
    for (const [opts, needle] of [
      [{ gh: false }, 'gh auth login'],
      [{ auth: false }, 'not logged in'],
    ] as const) {
      const { calls, exec } = fake(opts);
      const lines: string[] = [];
      expect(await submit({ ...base, root, dir, yes: true, exec, log: (l) => lines.push(l) })).toBe(1);
      expect(lines.join('\n')).toContain(needle);
      expect(calls.filter(MUTATING)).toEqual([]);
    }
  });

  test('a dry run without gh still shows the PR body and changes nothing', async () => {
    const { root, dir } = await setup();
    const { calls, exec } = fake({ gh: false });
    const lines: string[] = [];
    expect(await submit({ ...base, root, dir, yes: false, exec, log: (l) => lines.push(l) })).toBe(0);
    expect(calls.filter(MUTATING)).toEqual([]);
    expect(lines.join('\n')).toContain('PR body:');
    expect(lines.join('\n')).toContain('NOTE:');
  });

  test('a rejected proof warns and the verdict goes in the PR body', async () => {
    const { root, dir } = await setup('proof');
    const { exec } = fake();
    const lines: string[] = [];
    const check = async (_r: string, d: string) => {
      const real = await import('../../src/commands/check.ts');
      const o = await real.checkAttempt(root, d, async () => async () => ({ checker: 'lean' as const, result: 'rejected' as const, summary: 'contains sorry' }));
      return o;
    };
    expect(await submit({ ...base, root, dir, yes: false, exec, check, log: (l) => lines.push(l) })).toBe(0);
    const text = lines.join('\n');
    expect(text).toContain('WARNING');
    expect(text).toContain('rejected: contains sorry');
  });

  test('the PR body states the declarations and credits models and people', async () => {
    const { root, dir, problem } = await setup();
    const { checkAttempt } = await import('../../src/commands/check.ts');
    const o = await checkAttempt(root, dir);
    if ('invalid' in o) throw new Error(o.invalid.join('\n'));
    const body = prBody(o.attempt, problem, o.result, 'terramind-org/frontier');
    expect(body).toContain('CC BY 4.0');
    expect(body).toContain('complete disclosure');
    expect(body).toContain('m (p): author');
    expect(body).toContain('dave (@dave): submitter');
    expect(body).not.toMatch(/solved/i);
  });
  test('four distinct notes: gh missing, not logged in, repo not found, no network', async () => {
    const { root, dir } = await setup();
    const cases: [Parameters<typeof fake>[0], string, string][] = [
      [{ gh: false }, 'is not installed', 'gh-missing'],
      [{ auth: false, authErr: 'You are not logged into any GitHub hosts. To log in, run: gh auth login' }, 'not logged in', 'not-logged-in'],
      [{ repoErr: 'gh: Not Found (HTTP 404)' }, 'was not found, or your GitHub account cannot see it', 'repo-not-found'],
      [{ repoErr: 'error connecting to api.github.com' }, 'Cannot reach github.com', 'no-network'],
      [{ auth: false, authErr: 'dial tcp: lookup api.github.com: no such host' }, 'Cannot reach github.com', 'no-network'],
      [{ userErr: 'gh: Bad credentials (HTTP 401)' }, 'not logged in', 'not-logged-in'],
    ];
    const texts = new Set<string>();
    for (const [opts, needle, kind] of cases) {
      const real = fake(opts);
      const lines: string[] = [];
      expect(await submit({ ...base, root, dir, yes: true, exec: real.exec, log: (l) => lines.push(l) })).toBe(1);
      const text = lines.join('\n');
      expect(text).toContain(needle);
      expect(real.calls.filter(MUTATING)).toEqual([]);
      texts.add(text);
      // The dry run degrades to a generic plan with the same note and exits 0.
      const dry: string[] = [];
      const again = fake(opts);
      expect(await submit({ ...base, root, dir, yes: false, json: true, exec: again.exec, log: (l) => dry.push(l) })).toBe(0);
      const parsed = JSON.parse(dry.join('\n'));
      expect(parsed.tooling.kind).toBe(kind);
    }
    expect([...texts].filter((t) => t.includes('Cannot reach github.com')).length).toBe(2);
  });

  test('classifyGhFailure covers 401, 403, 404, timeouts and unknown errors', () => {
    const r = 'terramind-org/frontier';
    expect(classifyGhFailure('gh: HTTP 401: Bad credentials', 'x', r).kind).toBe('not-logged-in');
    expect(classifyGhFailure('gh: Not Found (HTTP 404)', 'x', r).kind).toBe('repo-not-found');
    expect(classifyGhFailure('gh: Resource not accessible (HTTP 403)', 'x', r).kind).toBe('repo-not-found');
    expect(classifyGhFailure('Get "https://api.github.com": dial tcp 1.2.3.4:443: i/o timeout', 'x', r).kind).toBe('no-network');
    expect(classifyGhFailure('something odd', 'read the thing', r)).toEqual({ kind: 'other', message: 'could not read the thing: something odd' });
  });

  test('--json dry run prints one object with plan, body and verdict, and nothing else', async () => {
    const { root, dir } = await setup();
    const { calls, exec } = fake();
    const lines: string[] = [];
    expect(await submit({ ...base, root, dir, yes: false, json: true, exec, log: (l) => lines.push(l) })).toBe(0);
    expect(lines).toHaveLength(1);
    const parsed = JSON.parse(lines[0]!);
    expect(parsed).toMatchObject({ ok: true, dry_run: true, verdict: { result: 'unchecked' }, tooling: { kind: 'ok' } });
    expect(parsed.body).toContain('### Claim');
    expect(parsed.plan.body).toBe(parsed.body);
    expect(parsed.plan.branch).toMatch(/^attempt\//);
    expect(calls.filter(MUTATING)).toEqual([]);
  });

  test('--json with an invalid attempt prints the issues; with --yes it adds the PR url', async () => {
    const { root, dir } = await setup();
    const real = fake();
    const done: string[] = [];
    expect(await submit({ ...base, root, dir, yes: true, json: true, exec: real.exec, log: (l) => done.push(l) })).toBe(0);
    expect(JSON.parse(done.join('\n'))).toMatchObject({ ok: true, dry_run: false, pr_url: 'https://github.com/terramind-org/frontier/pull/7' });

    writeFileSync(join(dir, 'attempt.yaml'), 'schema: 1\nid: nonsense\n');
    const bad: string[] = [];
    expect(await submit({ ...base, root, dir, yes: false, json: true, exec: real.exec, log: (l) => bad.push(l) })).toBe(1);
    expect(JSON.parse(bad.join('\n'))).toMatchObject({ ok: false, error: 'invalid' });
  });

  test('a rejected verdict is not prefixed twice', async () => {
    const { root, dir } = await setup('proof');
    const { exec } = fake();
    const lines: string[] = [];
    const check = async (_r: string, d: string) =>
      (await import('../../src/commands/check.ts')).checkAttempt(root, d, async () => async () => ({ checker: 'lean' as const, result: 'rejected' as const, summary: 'rejected: uses sorry' }));
    expect(await submit({ ...base, root, dir, yes: false, exec, check, log: (l) => lines.push(l) })).toBe(0);
    const text = lines.join('\n');
    expect(text).not.toContain('rejected: rejected');
    expect(text).not.toContain('REJECTED this attempt: rejected');
    expect(text).toContain('rejected: uses sorry');
  });

  test('submit refuses a scaffold whose declarations were never confirmed', async () => {
    const root = copyFixture('good');
    const problem = (await loadProblem('toy.open-one', root))!;
    const { dir } = await scaffoldAttempt({ root, problem, kind: 'writeup', login: 'dave' });
    const { calls, exec } = fake();
    const lines: string[] = [];
    for (const yes of [false, true]) {
      expect(await submit({ ...base, root, dir, yes, exec, log: (l) => lines.push(l) })).toBe(1);
    }
    expect(calls).toEqual([]);
    expect(lines.join('\n')).toContain('Show the declarations');
  });
});
