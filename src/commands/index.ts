import { existsSync, readdirSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { parse } from '../args.ts';
import { assemble, repoRoot, writeJson } from '../repo.ts';
import { Index, TIERS } from '../schema.ts';
import { validateRepo } from './validate.ts';

export const help = `Build dist/index.json (the Index schema) for terramind.org.

Usage: bun frontier index [--out dist/index.json]`;

async function gitHead(root: string): Promise<string> {
  const p = Bun.spawn(['git', 'rev-parse', 'HEAD'], { cwd: root, stdout: 'pipe', stderr: 'ignore' });
  const out = (await new Response(p.stdout).text()).trim();
  return (await p.exited) === 0 && out ? out : 'unknown';
}

async function readSources(root: string): Promise<Index['sources']> {
  const dir = join(root, 'sources');
  if (!existsSync(dir)) return [];
  const names = readdirSync(dir).filter((n) => n.endsWith('.json')).sort();
  const sources = [];
  for (const n of names) {
    const raw = JSON.parse(await readFile(join(dir, n), 'utf8')) as Record<string, unknown>;
    sources.push({ name: n.slice(0, -5), repo: raw.repo, commit: raw.commit, licence: raw.licence });
  }
  return sources as Index['sources'];
}

/** Build and validate the Index for the repo at `root`. Throws if any problem or attempt is invalid. */
export async function buildIndex(root: string, now: Date = new Date()): Promise<Index> {
  const { issues, loaded } = await validateRepo(root);
  if (issues.length) throw new Error(`repo is invalid:\n${issues.map((i) => `${i.path}: ${i.message}`).join('\n')}`);
  const all = assemble(loaded.problems, loaded.attempts);
  const by_tier: Record<string, number> = Object.fromEntries(TIERS.map((t) => [t, 0]));
  const by_status: Record<string, number> = { open: 0, 'proof-checked': 0, 'disproof-checked': 0, 'record-improved': 0, practice: 0 };
  let attempts = 0;
  let verified = 0;
  const problems = all.map(({ problem, status, attempts: list }) => {
    if (status !== 'practice') by_tier[problem.tier] = (by_tier[problem.tier] ?? 0) + 1; // by_tier sums to counts.problems
    by_status[status] = (by_status[status] ?? 0) + 1;
    attempts += list.length;
    return {
      ...problem,
      status,
      attempts: list.map(({ attempt: a, verdict, review }) => {
        if (verdict?.result === 'verified') verified++;
        return {
          id: a.id, kind: a.kind, title: a.title, claim: a.claim, submitter: a.submitter,
          models: a.models, mode: a.mode, created: a.created,
          verdict: verdict
            ? { checker: verdict.checker, result: verdict.result, summary: verdict.summary, lean: verdict.lean, witness: verdict.witness }
            : null,
          // An opinion, labelled "AI review (opinion)" with its disclaimer; status above never reads it.
          review: review
            ? { reviewed_at: review.reviewed_at, disclaimer: review.disclaimer, panel: review.panel, agreement: review.agreement, notes: review.notes }
            : null,
        };
      }),
    };
  });
  return Index.parse({
    schema: 1,
    generated_at: now.toISOString(),
    repo_commit: await gitHead(root),
    sources: await readSources(root),
    // Practice problems are exercises: counted apart, never in `problems`.
    counts: { problems: problems.length - by_status.practice!, practice: by_status.practice!, attempts, verified, by_tier, by_status },
    problems,
  });
}

export async function run(args: string[]): Promise<number> {
  const { values } = parse(args, { out: { type: 'string' } });
  const root = repoRoot();
  const index = await buildIndex(root);
  const out = resolve(root, values.out ?? 'dist/index.json');
  await writeJson(out, index, Index);
  const c = index.counts;
  console.log(`wrote ${out}`);
  console.log(`${c.problems} problems, ${c.attempts} attempts, ${c.verified} verified`);
  console.log(`by tier: ${Object.entries(c.by_tier).map(([k, v]) => `${k} ${v}`).join(', ')}`);
  console.log(`by status: ${Object.entries(c.by_status).map(([k, v]) => `${k} ${v}`).join(', ')}`);
  return 0;
}
