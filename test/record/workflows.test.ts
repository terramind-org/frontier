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
