import { describe, expect, test } from 'bun:test';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse } from 'yaml';

const DIR = join(import.meta.dir, '..', '..', '.github', 'workflows');
const files = readdirSync(DIR).filter((f) => f.endsWith('.yml'));
const workflows = new Map(files.map((f) => [f, parse(readFileSync(join(DIR, f), 'utf8')) as any]));

/** Every permissions block: workflow level and per job. */
function permissionBlocks(wf: any): { where: string; value: unknown }[] {
  const out = [{ where: 'workflow', value: wf.permissions }];
  for (const [id, job] of Object.entries<any>(wf.jobs ?? {})) out.push({ where: `job ${id}`, value: job.permissions });
  return out;
}

/** Scopes each file may grant as write. */
const WRITE_ALLOWED: Record<string, string[]> = {
  'record.yml': ['contents'],
  'index.yml': ['contents'],
  'automerge.yml': ['contents', 'pull-requests'],
};

function usesOf(wf: any): string[] {
  const uses: string[] = [];
  for (const job of Object.values<any>(wf.jobs ?? {})) {
    if (typeof job.uses === 'string') uses.push(job.uses);
    for (const step of job.steps ?? []) if (typeof step.uses === 'string') uses.push(step.uses);
  }
  return uses;
}

describe('workflows', () => {
  test('the expected workflows exist', () => {
    for (const f of ['pr.yml', 'record.yml', 'index.yml', 'automerge.yml', 'lean-check.yml']) expect(files).toContain(f);
  });

  test('no workflow uses pull_request_target', () => {
    for (const [f, wf] of workflows) {
      const on = wf.on ?? wf[true as any];
      const triggers = typeof on === 'string' ? [on] : Array.isArray(on) ? on : Object.keys(on);
      expect({ f, triggers: triggers.includes('pull_request_target') }).toEqual({ f, triggers: false });
      expect(readFileSync(join(DIR, f), 'utf8')).not.toMatch(/^\s*pull_request_target\s*:/m);
    }
  });

  test('write permissions only where they are needed', () => {
    for (const [f, wf] of workflows) {
      const allowed = WRITE_ALLOWED[f] ?? [];
      for (const { where, value } of permissionBlocks(wf)) {
        if (value === undefined) continue;
        expect(typeof value === 'object' && value !== null).toBe(true); // no write-all / read-all shorthand
        for (const [scope, level] of Object.entries(value as Record<string, string>)) {
          if (level === 'write') expect({ f, where, scope, ok: allowed.includes(scope) }).toEqual({ f, where, scope, ok: true });
        }
      }
    }
  });

  test('every workflow sets a top-level permissions block', () => {
    for (const [f, wf] of workflows) expect({ f, set: wf.permissions !== undefined }).toEqual({ f, set: true });
  });

  test('record.yml has exactly one job with write permission', () => {
    const jobs = Object.entries<any>(workflows.get('record.yml').jobs).filter(([, j]) => j.permissions?.contents === 'write');
    expect(jobs.map(([id]) => id)).toEqual(['record']);
    expect(workflows.get('record.yml').permissions.contents).toBe('read');
  });

  test('every third-party action is pinned to a full commit sha', () => {
    for (const [f, wf] of workflows) {
      for (const uses of usesOf(wf)) {
        if (uses.startsWith('./')) continue;
        expect({ f, uses, pinned: /@[0-9a-f]{40}$/.test(uses) }).toEqual({ f, uses, pinned: true });
      }
    }
    const text = files.map((f) => readFileSync(join(DIR, f), 'utf8')).join('\n');
    for (const m of text.matchAll(/^\s*(?:-\s*)?uses:\s*(\S+)(.*)$/gm)) {
      if (!m[1]!.startsWith('./')) expect(m[2]).toMatch(/#\s*v\d/); // the version is in a comment
    }
  });

  test('automerge is gated on the AUTO_MERGE variable and never checks out code', () => {
    const wf = workflows.get('automerge.yml');
    for (const job of Object.values<any>(wf.jobs)) {
      expect(job.if).toContain("vars.AUTO_MERGE == 'true'");
      for (const step of job.steps) expect(String(step.uses ?? '')).not.toContain('checkout');
    }
  });

  test('automerge never merges a code PR: every file must be a file inside one attempt directory', () => {
    const run: string = workflows.get('automerge.yml').jobs.automerge.steps.find((s: any) => /pulls\/.*\/files/.test(String(s.run ?? ''))).run;
    const m = /\[\[ "\$name" =~ (\^attempts[^\s]*\$) \]\]/.exec(run);
    expect(m).not.toBeNull();
    const re = new RegExp(m![1]!);
    const ok = 'attempts/toy.add-comm/20260102-alice-aaaaaa/solution.lean';
    expect(re.test(ok)).toBe(true);
    for (const bad of ['src/commands/validate.ts', '.github/workflows/pr.yml', 'README.md', 'problems/toy.add-comm.yaml', 'attempts/toy.add-comm/notes.md', 'attempts/x/y/z/w.md']) {
      expect(re.test(bad)).toBe(false);
    }
    expect(run).toContain('!= added');
    expect(run).toContain('more than one attempt directory');
  });

  test('only lean-cache.yml saves a cache, only on main, and never touches attempts', () => {
    for (const [f, wf] of workflows) {
      for (const [id, job] of Object.entries<any>(wf.jobs ?? {})) {
        for (const step of job.steps ?? []) {
          const uses = String(step.uses ?? '');
          if (/^actions\/cache(\/save)?@/.test(uses)) expect({ f, id, saves: true }).toEqual({ f: 'lean-cache.yml', id: 'warm', saves: true });
        }
      }
    }
    const warm = workflows.get('lean-cache.yml').jobs.warm;
    expect(warm.if).toBe("github.ref == 'refs/heads/main'");
    const on = workflows.get('lean-cache.yml').on;
    expect(Object.keys(on).sort()).toEqual(['push', 'schedule', 'workflow_dispatch']);
    expect(on.push.branches).toEqual(['main']);
    expect(readFileSync(join(DIR, 'lean-cache.yml'), 'utf8')).not.toMatch(/attempts\/|check-attempt/);
  });

  test('lean-check: the job that runs attempt code cannot read the cache API; the judge confirms its entry around the restore', () => {
    const jobs = workflows.get('lean-check.yml').jobs;
    expect(jobs.build.permissions).toEqual({ contents: 'read' });
    const names: string[] = jobs.check.steps.map((s: any) => s.name);
    const restore = jobs.check.steps.findIndex((s: any) => String(s.uses ?? '').startsWith('actions/cache/restore@'));
    expect(names[restore - 1]).toBe('Confirm the Lean cache entry before restoring');
    expect(names[restore + 1]).toBe('Confirm the Lean cache entry after restoring');
    expect(jobs.check.steps[restore].if).toBe("steps.trusted.outputs.ok == 'true'");
    expect(jobs.check.steps[restore].with['restore-keys']).toBeUndefined();
    // The same cache path everywhere (it is part of the cache version).
    expect(jobs.build.steps.find((s: any) => String(s.uses ?? '').startsWith('actions/cache/restore@')).with.path).toBe('lean/.lake');
    expect(jobs.check.steps[restore].with.path).toBe('lean/.lake');
    const save = workflows.get('lean-cache.yml').jobs.warm.steps.find((s: any) => String(s.uses ?? '').startsWith('actions/cache/save@'));
    expect(save.with.path).toBe('lean/.lake');
  });

  test('pr.yml fails only on invalid submissions or checker errors, not on a rejected verdict', () => {
    const text = readFileSync(join(DIR, 'pr.yml'), 'utf8');
    expect(text).toContain('!= verified ] && [ "$result" != rejected');
  });
});

describe('actionlint', () => {
  const bin = Bun.which('actionlint');
  test.skipIf(!bin)('all workflows are clean', async () => {
    const p = Bun.spawn([bin!, ...files.map((f) => join(DIR, f))], { stdout: 'pipe', stderr: 'pipe' });
    const [out, code] = await Promise.all([new Response(p.stdout).text(), p.exited]);
    expect({ code, out }).toEqual({ code: 0, out: '' });
  });
});
