import { cpSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

export const FIXTURES = join(import.meta.dir, '..', 'fixtures', 'core');
export const GOOD = join(FIXTURES, 'good');
export const BAD = join(FIXTURES, 'bad');

/** A writable copy of a fixture repo. */
export function copyFixture(which: 'good' | 'bad'): string {
  const dir = mkdtempSync(join(tmpdir(), 'frontier-core-'));
  cpSync(join(FIXTURES, which), dir, { recursive: true });
  return dir;
}

export async function sh(cwd: string, ...cmd: string[]): Promise<string> {
  const p = Bun.spawn(cmd, { cwd, stdout: 'pipe', stderr: 'pipe' });
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  if (code !== 0) throw new Error(`${cmd.join(' ')} failed: ${err}`);
  return out;
}
