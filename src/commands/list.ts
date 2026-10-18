import { parse } from '../args.ts';
import { loadAll } from '../repo.ts';

export const help = `List problems.

Usage: bun frontier list [--tier proof|witness] [--status open|proof-checked|disproof-checked|record-improved]
                         [--tag <tag>] [--unattempted] [--json]`;

export async function run(args: string[]): Promise<number> {
  const { values } = parse(args, {
    tier: { type: 'string' },
    status: { type: 'string' },
    tag: { type: 'string' },
    unattempted: { type: 'boolean' },
    json: { type: 'boolean' },
  });
  const rows = (await loadAll())
    .filter((r) => !values.tier || r.problem.tier === values.tier)
    .filter((r) => !values.status || r.status === values.status)
    .filter((r) => !values.tag || r.problem.tags.includes(values.tag))
    .filter((r) => !values.unattempted || r.attempts.length === 0)
    .map((r) => ({
      id: r.problem.id,
      title: r.problem.title,
      tier: r.problem.tier,
      field: r.problem.field,
      status: r.status,
      attempts: r.attempts.length,
      tags: r.problem.tags,
    }));
  if (values.json) {
    console.log(JSON.stringify(rows, null, 2));
    return 0;
  }
  const w = (k: 'id' | 'tier' | 'status') => Math.max(k.length, ...rows.map((r) => r[k].length));
  const [wi, wt, ws] = [w('id'), w('tier'), w('status')];
  console.log(`${'ID'.padEnd(wi)}  ${'TIER'.padEnd(wt)}  ${'STATUS'.padEnd(ws)}  ATT  TITLE`);
  for (const r of rows) {
    console.log(`${r.id.padEnd(wi)}  ${r.tier.padEnd(wt)}  ${r.status.padEnd(ws)}  ${String(r.attempts).padStart(3)}  ${r.title}`);
  }
  console.log(`\n${rows.length} problem${rows.length === 1 ? '' : 's'}`);
  return 0;
}
