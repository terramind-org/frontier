import { cpSync, mkdtempSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export const FIXTURE = join(import.meta.dir, '..', 'fixtures', 'import', 'checkout');

function git(cwd: string, ...args: string[]): void {
  const p = Bun.spawnSync(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.org', ...args], { cwd });
  if (p.exitCode !== 0) throw new Error(`git ${args.join(' ')}: ${p.stderr.toString()}`);
}

/** A fresh git checkout of the fixture files (so `git rev-parse HEAD` works) and an empty repo root. */
export function fixtureWorkspace(): { checkout: string; root: string } {
  const base = mkdtempSync(join(tmpdir(), 'frontier-import-'));
  const checkout = join(base, 'checkout');
  const root = join(base, 'repo');
  cpSync(FIXTURE, checkout, { recursive: true });
  mkdirSync(root);
  git(checkout, 'init', '-q');
  git(checkout, 'add', '-A');
  git(checkout, 'commit', '-q', '-m', 'fixture');
  return { checkout, root };
}
