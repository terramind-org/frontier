import { resolve } from 'node:path';
import { parse, UsageError } from '../args.ts';
import { importFormalConjectures } from '../import/formal-conjectures.ts';
import { repoRoot } from '../repo.ts';

export const help = `Regenerate problems/*.yaml and sources/ from an upstream checkout.

Usage: bun frontier import formal-conjectures --path <checkout> [--date YYYY-MM-DD]

  --path   a google-deepmind/formal-conjectures checkout (its HEAD is the pinned commit)
  --date   the import date written to new problems (default: today, UTC); an existing problem keeps its date`;

export async function run(args: string[]): Promise<number> {
  const { values, positionals } = parse(args, { path: { type: 'string' }, date: { type: 'string' } });
  if (positionals.length !== 1 || positionals[0] !== 'formal-conjectures') {
    throw new UsageError('expected the source name: formal-conjectures');
  }
  if (!values.path) throw new UsageError('--path <checkout> is required');
  const date = values.date ?? new Date().toISOString().slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || Number.isNaN(Date.parse(date))) throw new UsageError('--date must be YYYY-MM-DD');

  const s = await importFormalConjectures({ checkout: resolve(values.path), root: repoRoot(), date });
  if (s.skipped.length) {
    console.error(`import aborted, nothing written; ${s.skipped.length} file(s) could not be parsed:`);
    for (const k of s.skipped) console.error(`  ${k.path}: ${k.reason}`);
    return 1;
  }
  console.log(`formal-conjectures @ ${s.commit} (${s.leanToolchain})`);
  console.log(`${s.found} open declarations in ${s.files} files -> ${s.imported} problems written, ${s.removed.length} removed`);
  console.log(`without an upstream docstring: ${s.noDocstring}; files without a module-doc title: ${s.titleFallbacks}`);
  console.log(`id collisions: ${s.collisions.length}`);
  for (const c of s.collisions) console.log(`  ${c.name} (${c.path}) -> ${c.assigned}`);
  console.log('by tag:');
  for (const [tag, n] of Object.entries(s.tags).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))) {
    console.log(`  ${tag}: ${n}`);
  }
  return 0;
}
