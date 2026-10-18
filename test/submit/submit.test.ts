import { describe, expect, test } from 'bun:test';
import { readdirSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { scaffoldAttempt } from '../../src/commands/new.ts';
import { loadProblem } from '../../src/repo.ts';
import { prBody, submit } from '../../src/commands/submit.ts';
import type { Exec } from '../../src/commands/submit.ts';
import { copyFixture } from '../core/helpers.ts';

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
function fake(opts: { push?: boolean; gh?: boolean; auth?: boolean } = {}) {
  const calls: Call[] = [];
  const exec: Exec = async (cmd, args, o) => {
    const call: Call = { cmd, args, cwd: o?.cwd };
    if (cmd === 'git' && args[0] === 'add' && o?.cwd) call.files = walk(o.cwd);
    calls.push(call);
    const ok = (stdout = '') => ({ code: 0, stdout, stderr: '' });
    const line = `${cmd} ${args.join(' ')}`;
    if (line === 'gh --version') return opts.gh === false ? { code: 127, stdout: '', stderr: 'not found' } : ok('gh version 2');
    if (line === 'gh auth status') return opts.auth === false ? { code: 1, stdout: '', stderr: 'not logged in' } : ok();
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
});
