// Bundle the CLI into one ESM file that runs under node (and bun): dist-cli/frontier.mjs.
import { chmodSync, mkdirSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = join(import.meta.dir, '..');
const result = await Bun.build({ entrypoints: [join(root, 'src/bin.ts')], target: 'node', format: 'esm', minify: false });
if (!result.success) {
  for (const l of result.logs) console.error(String(l));
  process.exit(1);
}
const out = join(root, 'dist-cli');
mkdirSync(out, { recursive: true });
const file = join(out, 'frontier.mjs');
writeFileSync(file, `#!/usr/bin/env node\n${await result.outputs[0]!.text()}`);
chmodSync(file, 0o755);
console.log(`wrote ${file} (${(statSync(file).size / 1024).toFixed(0)} KiB)`);
