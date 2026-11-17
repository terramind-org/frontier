import { resolve } from 'node:path';
import { parse, UsageError } from '../args.ts';
import { importFormalConjectures } from '../import/formal-conjectures.ts';
import type { Step } from '../import/prose.ts';
import { importUnsolvedMath, readUnsolvedMath } from '../import/unsolvedmath.ts';
import { importWeSolve } from '../import/we-solve.ts';
import { repoRoot } from '../repo.ts';

export const help = `Regenerate problems/*.yaml and sources/ from an upstream source.

Usage: bun frontier import formal-conjectures --path <checkout> [--date YYYY-MM-DD]
       bun frontier import we-solve --path <checkout> [--unsolvedmath <dir>] [--revision <sha>] [--date YYYY-MM-DD] [--dry-run]
       bun frontier import unsolvedmath --path <dir> [--revision <sha>] [--date YYYY-MM-DD] [--dry-run]

  formal-conjectures   Lean problems (tier proof); --path is a google-deepmind/formal-conjectures checkout
  we-solve             prose problems ws.<handle>; --path is a We-Solve/research clone (its HEAD is pinned)
  unsolvedmath         prose problems um.<id>; --path holds problems.json of huggingface.co/datasets/ulamai/UnsolvedMath

  --unsolvedmath  (we-solve) the UnsolvedMath download, to apply the cross-source rules: a we-solve record whose
                  UnsolvedMath row is archived, or now marked solved, is skipped
  --revision      the UnsolvedMath dataset revision (40-hex); not needed when the directory is a git clone or a
                  huggingface_hub snapshot
  --date          the import date written to new problems (default: today, UTC); an existing problem keeps its date
  --dry-run       report the counts, write nothing

Order: formal-conjectures, then we-solve, then unsolvedmath. Each later import skips what an earlier one has.
Only the named source's problems are written or removed.`;

function printSteps(steps: Step[]): void {
  for (const s of steps) {
    console.log(`  ${s.rule}: ${s.before} -> ${s.after} (-${s.dropped})`);
    for (const [reason, n] of Object.entries(s.reasons)) console.log(`      ${reason}: ${n}`);
  }
}

function printCounts(label: string, counts: Record<string, number>): void {
  console.log(`${label}: ${Object.entries(counts).map(([k, v]) => `${k} ${v}`).join(', ')}`);
}

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, {
    path: { type: 'string' },
    date: { type: 'string' },
    unsolvedmath: { type: 'string' },
    revision: { type: 'string' },
    'dry-run': { type: 'boolean' },
  });
  const source = positionals[0];
  if (positionals.length !== 1 || !['formal-conjectures', 'we-solve', 'unsolvedmath'].includes(source!)) {
    throw new UsageError('expected the source name: formal-conjectures, we-solve or unsolvedmath');
  }
  if (!values.path) throw new UsageError('--path is required');
  const date = values.date ?? new Date().toISOString().slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || Number.isNaN(Date.parse(date))) throw new UsageError('--date must be YYYY-MM-DD');
  if (values.unsolvedmath && source !== 'we-solve') throw new UsageError('--unsolvedmath is only for import we-solve');
  const dryRun = values['dry-run'] === true;
  const root = repoRoot();
  const path = resolve(values.path);

  if (source === 'we-solve') {
    const unsolvedmath = values.unsolvedmath ? await readUnsolvedMath(resolve(values.unsolvedmath), values.revision) : undefined;
    const s = await importWeSolve({ checkout: path, root, date, unsolvedmath, dryRun });
    console.log(`we-solve @ ${s.commit}${s.unsolvedmathRevision ? ` (cross-checked with UnsolvedMath @ ${s.unsolvedmathRevision})` : ''}`);
    console.log(`${s.records} records`);
    printSteps(s.steps);
    console.log(`${s.imported} problems ${dryRun ? 'would be written' : 'written'}, ${s.removed.length} removed`);
    if (!s.unsolvedmathRevision) console.log('note: without --unsolvedmath the cross-source rules (archived or solved in UnsolvedMath) were not applied');
    if (s.unsolvedmathRevision) printCounts('imported problems also listed by UnsolvedMath, matched by', s.unsolvedmathMatches);
    if (s.unknownUnsolvedMathIds) console.log(`records naming an UnsolvedMath id the dataset lacks (kept): ${s.unknownUnsolvedMathIds}`);
    printCounts('by field', s.byField);
    printCounts('by licence', s.byLicence);
    printCounts('by upstream status', s.byStatus);
    printCounts('by tag', s.byTag);
    console.log('Run `bun frontier import unsolvedmath` next so UnsolvedMath rows this import covers are skipped there.');
    return 0;
  }
  if (source === 'unsolvedmath') {
    const s = await importUnsolvedMath({ dir: path, root, date, revision: values.revision, dryRun });
    console.log(`UnsolvedMath @ ${s.revision}`);
    console.log(`${s.rows} rows`);
    printSteps(s.steps);
    console.log(`kept although a we-solve problem has the same title (statements differ): ${s.titleOnlyKept}`);
    console.log(`${s.imported} problems ${dryRun ? 'would be written' : 'written'}, ${s.removed.length} removed`);
    printCounts('by field', s.byField);
    printCounts('by licence', s.byLicence);
    printCounts('by upstream status', s.byStatus);
    return 0;
  }

  if (values.revision || dryRun) throw new UsageError('--revision and --dry-run are not options of import formal-conjectures');
  const s = await importFormalConjectures({ checkout: path, root, date });
  if (s.skipped.length) {
    console.error(`import aborted, nothing written; ${s.skipped.length} file(s) could not be parsed:`);
    for (const k of s.skipped) console.error(`  ${k.path}: ${k.reason}`);
    return 1;
  }
  console.log(`formal-conjectures @ ${s.commit} (${s.leanToolchain})`);
  console.log(`${s.found} open declarations in ${s.files} files + ${s.practice} practice -> ${s.imported} problems written, ${s.removed.length} removed`);
  if (s.solved.length) {
    console.log(`kept and marked solved (settled upstream since import): ${s.solved.length}`);
    for (const id of s.solved) console.log(`  ${id}`);
  }
  console.log(`without an upstream docstring: ${s.noDocstring}; files without a module-doc title: ${s.titleFallbacks}`);
  console.log(`id collisions: ${s.collisions.length}`);
  for (const c of s.collisions) console.log(`  ${c.name} (${c.path}) -> ${c.assigned}`);
  console.log('by tag:');
  for (const [tag, n] of Object.entries(s.tags).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))) {
    console.log(`  ${tag}: ${n}`);
  }
  return 0;
}
