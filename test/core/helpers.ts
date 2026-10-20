import { cpSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
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

/** Replace the scaffold's placeholder claim in `<dir>/attempt.yaml`, as a submitter must. */
export function fillClaim(dir: string, claim = 'A test claim.'): void {
  const file = join(dir, 'attempt.yaml');
  writeFileSync(file, readFileSync(file, 'utf8').replace('Describe exactly what this attempt claims.', claim));
}

export async function sh(cwd: string, ...cmd: string[]): Promise<string> {
  const p = Bun.spawn(cmd, { cwd, stdout: 'pipe', stderr: 'pipe' });
  const [out, err, code] = await Promise.all([new Response(p.stdout).text(), new Response(p.stderr).text(), p.exited]);
  if (code !== 0) throw new Error(`${cmd.join(' ')} failed: ${err}`);
  return out;
}

/** Set both declarations to true, as a submitter does after the human agreed. */
export function confirmDeclarations(dir: string): void {
  const file = join(dir, 'attempt.yaml');
  writeFileSync(
    file,
    readFileSync(file, 'utf8').replace('rights: false', 'rights: true').replace('disclosure_complete: false', 'disclosure_complete: true'),
  );
}

/** Make a scaffolded attempt submittable: real claim, confirmed declarations. */
export function ready(dir: string, claim = 'A test claim.'): void {
  fillClaim(dir, claim);
  confirmDeclarations(dir);
}
