import { parse, UsageError } from '../args.ts';
import { loadAll } from '../repo.ts';
import type { ProblemWithAttempts } from '../repo.ts';

export const help = `Pick an open problem with the fewest attempts; ties are broken by a seeded shuffle.

Usage: bun frontier pick [--tier proof|witness] [--tag <tag>] [--seed <n>] [--json]
  --tag    only problems with this tag; \`answer-required\` problems (no automatic check) are skipped unless asked for
  --seed   integer or any string; default is today's date, so a day's pick is stable`;

/** FNV-1a hash of the seed string to a 32-bit state. */
function seedState(seed: string): number {
  let h = 0x811c9dc5;
  for (const ch of seed) {
    h ^= ch.codePointAt(0)!;
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** mulberry32: small deterministic PRNG returning [0, 1). */
function mulberry32(state: number): () => number {
  let a = state;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Open problems with the fewest attempts, one of them chosen by the seed. Deterministic for a given input. */
export function pickProblem(rows: ProblemWithAttempts[], seed: string, tier?: string, tag?: string): ProblemWithAttempts | null {
  const open = rows.filter(
    (r) =>
      r.status === 'open' &&
      (!tier || r.problem.tier === tier) &&
      (tag ? r.problem.tags.includes(tag) : !r.problem.tags.includes('answer-required')),
  );
  if (!open.length) return null;
  const fewest = Math.min(...open.map((r) => r.attempts.length));
  const tied = open.filter((r) => r.attempts.length === fewest).sort((a, b) => (a.problem.id < b.problem.id ? -1 : 1));
  return tied[Math.floor(mulberry32(seedState(seed))() * tied.length)]!;
}

export async function run(args: string[]): Promise<number> {
  const { values } = parse(args, { tier: { type: 'string' }, seed: { type: 'string' }, tag: { type: 'string' }, json: { type: 'boolean' } });
  if (values.tier && values.tier !== 'proof' && values.tier !== 'witness') throw new UsageError('--tier must be proof or witness');
  const seed = values.seed ?? new Date().toISOString().slice(0, 10);
  const chosen = pickProblem(await loadAll(), seed, values.tier, values.tag);
  if (!chosen) {
    console.error('No open problem matches.');
    return 1;
  }
  const { problem: p } = chosen;
  const kinds = p.tier === 'proof' ? 'proof or disproof' : 'witness';
  if (values.json) {
    console.log(JSON.stringify({ id: p.id, title: p.title, tier: p.tier, attempts: chosen.attempts.length, seed }, null, 2));
  } else {
    console.log(`${p.id}  (${p.tier}, ${chosen.attempts.length} attempts)\n${p.title}\n`);
    console.log(`Read it:    bun frontier show ${p.id}`);
    console.log(`Attempt it: bun frontier new ${p.id} --kind ${p.tier === 'proof' ? 'proof' : 'witness'} --login <your-github-login>   (${kinds})`);
  }
  return 0;
}
