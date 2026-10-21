import { parse, UsageError } from '../args.ts';
import { loadAll } from '../repo.ts';
import type { ProblemWithAttempts } from '../repo.ts';
import { PRACTICE_TAG, PROSE_NOTE, TIERS } from '../schema.ts';
import type { Problem } from '../schema.ts';

export const help = `Pick an open problem with the fewest attempts; ties are broken by a seeded shuffle.

Usage: bun frontier pick [--tier proof|witness|prose] [--tag <tag>] [--seed <n>] [--max-difficulty approachable|hard|very-hard]
                         [--practice] [--json]
  --tier   proof or witness (machine-checked), or prose: open problems of any discipline stated in words, which
           take only writeups and are never machine-checked. Without --tier, prose problems are never picked.
  --max-difficulty   only problems rated at most this hard (unrated problems are skipped); with --tier witness the
                     easiest rated level among the candidates is preferred anyway
  --practice         pick a practice problem (textbook exercise) instead; they are skipped otherwise
  --tag    only problems with this tag; \`answer-required\` problems (no automatic check) are skipped unless asked for
  --seed   integer or any string; default is today's date, so a day's pick is stable`;

/** FNV-1a hash of the seed string to a 32-bit state. */
export function seedState(seed: string): number {
  let h = 0x811c9dc5;
  for (const ch of seed) {
    h ^= ch.codePointAt(0)!;
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** mulberry32: small deterministic PRNG returning [0, 1). */
export function mulberry32(state: number): () => number {
  let a = state;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const DIFFICULTY_RANK = { practice: 0, approachable: 1, hard: 2, 'very-hard': 3 } as const;

export interface PickOptions {
  /** Pick among practice problems instead of open ones. */
  practice?: boolean;
  /** Only problems rated at most this hard; unrated problems are left out. */
  maxDifficulty?: 'approachable' | 'hard' | 'very-hard';
}

/**
 * Open problems with the fewest attempts, one of them chosen by the seed. Deterministic for a given input.
 * Practice problems are never picked unless `opts.practice`; prose problems only with `tier` "prose". For
 * witness problems the easiest rated level among the candidates is preferred before attempt counts are compared.
 */
export function pickProblem(
  rows: ProblemWithAttempts[],
  seed: string,
  tier?: string,
  tag?: string,
  opts: PickOptions = {},
): ProblemWithAttempts | null {
  const wanted = opts.practice ? 'practice' : 'open';
  const max = opts.maxDifficulty ? DIFFICULTY_RANK[opts.maxDifficulty] : Infinity;
  let open = rows.filter(
    (r) =>
      r.status === wanted &&
      (tier ? r.problem.tier === tier : r.problem.tier !== 'prose') &&
      (tag ? r.problem.tags.includes(tag) : !r.problem.tags.includes('answer-required')) &&
      (opts.maxDifficulty === undefined || (r.problem.difficulty !== undefined && DIFFICULTY_RANK[r.problem.difficulty.level] <= max)),
  );
  if (tier === 'witness' && open.length) {
    const rank = (r: ProblemWithAttempts) => (r.problem.difficulty ? DIFFICULTY_RANK[r.problem.difficulty.level] : DIFFICULTY_RANK['very-hard']);
    const easiest = Math.min(...open.map(rank));
    open = open.filter((r) => rank(r) === easiest);
  }
  if (!open.length) return null;
  const fewest = Math.min(...open.map((r) => r.attempts.length));
  const tied = open.filter((r) => r.attempts.length === fewest).sort((a, b) => (a.problem.id < b.problem.id ? -1 : 1));
  return tied[Math.floor(mulberry32(seedState(seed))() * tied.length)]!;
}

/** The copy-pasteable `new` command for a pick; the placeholders are the agent's login and model. */
export function newCommand(p: Problem): string {
  const kind = p.tier === 'proof' ? 'proof' : p.tier === 'witness' ? 'witness' : 'writeup';
  return `bun frontier new ${p.id} --kind ${kind} --login <your-github-login> --model "<model>:<provider>:author"`;
}

export async function run(args: string[]): Promise<number> {
  const { values } = parse(args, {
    tier: { type: 'string' },
    seed: { type: 'string' },
    tag: { type: 'string' },
    practice: { type: 'boolean' },
    'max-difficulty': { type: 'string' },
    json: { type: 'boolean' },
  });
  if (values.tier && !(TIERS as readonly string[]).includes(values.tier)) throw new UsageError('--tier must be proof, witness or prose');
  const maxD = values['max-difficulty'];
  if (maxD !== undefined && maxD !== 'approachable' && maxD !== 'hard' && maxD !== 'very-hard') {
    throw new UsageError('--max-difficulty must be approachable, hard or very-hard');
  }
  const seed = values.seed ?? new Date().toISOString().slice(0, 10);
  const practice = values.practice === true || values.tag === PRACTICE_TAG;
  const chosen = pickProblem(await loadAll(undefined, { skipDrafts: true }), seed, values.tier, values.tag, { practice, maxDifficulty: maxD });
  if (!chosen) {
    console.error('No open problem matches.');
    return 1;
  }
  const { problem: p } = chosen;
  const kinds = p.tier === 'proof' ? 'proof or disproof' : p.tier === 'witness' ? 'witness' : 'writeup only';
  const cmd = newCommand(p);
  if (values.json) {
    console.log(
      JSON.stringify(
        { id: p.id, title: p.title, tier: p.tier, attempts: chosen.attempts.length, seed, difficulty: p.difficulty ?? null, new: cmd },
        null,
        2,
      ),
    );
  } else {
    console.log(`${p.id}  (${p.tier}, ${chosen.attempts.length} attempts)
${p.title}
`);
    if (p.difficulty) console.log(`Difficulty: ${p.difficulty.level}. ${p.difficulty.note}
`);
    console.log(`Read it:    bun frontier show ${p.id}`);
    console.log(`Attempt it: ${cmd}`);
    if (p.tier === 'prose') console.log(PROSE_NOTE);
    const alt =
      p.tier === 'proof' ? 'use --kind disproof or writeup where that fits; ' : p.tier === 'witness' ? 'a writeup is --kind writeup; ' : '';
    console.log(`            (${kinds}; ${alt}add --tool "<name>:<role>" for each non-AI tool)`);
  }
  return 0;
}
