// Bundle the CLI into one ESM file that runs under node (and bun): dist-cli/frontier.mjs.
// The bundle carries the licence text of every third-party package bundled into it, found from the bundler's
// `// node_modules/<package>/...` markers, so the notices always match what was actually bundled.
import { chmodSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = join(import.meta.dir, '..');
const result = await Bun.build({ entrypoints: [join(root, 'src/bin.ts')], target: 'node', format: 'esm', minify: false });
if (!result.success) {
  for (const l of result.logs) console.error(String(l));
  process.exit(1);
}
const code = await result.outputs[0]!.text();

const bundled = [...new Set([...code.matchAll(/^\/\/ node_modules\/((?:@[^/\s]+\/)?[^/\s]+)\//gm)].map((m) => m[1]!))].sort();
const notices = bundled.map((name) => {
  const dir = join(root, 'node_modules', name);
  const pkg = JSON.parse(readFileSync(join(dir, 'package.json'), 'utf8'));
  const file = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'LICENCE'].map((f) => join(dir, f)).find((f) => existsSync(f));
  if (!file) throw new Error(`${name} is bundled but has no LICENSE file to include`);
  return `${name}@${pkg.version} (${pkg.license})\n\n${readFileSync(file, 'utf8').trim()}`;
});
const banner = notices.length
  ? `/*!\n * Third-party code bundled into this file, with its licences:\n *\n${notices
      .join('\n\n---\n\n')
      .replaceAll('*/', '* /')
      .split('\n')
      .map((l) => (l ? ` * ${l}` : ' *'))
      .join('\n')}\n */\n`
  : '';

const out = join(root, 'dist-cli');
mkdirSync(out, { recursive: true });
const file = join(out, 'frontier.mjs');
writeFileSync(file, `#!/usr/bin/env node\n${banner}${code}`);
chmodSync(file, 0o755);
console.log(`wrote ${file} (${(statSync(file).size / 1024).toFixed(0)} KiB), bundling ${bundled.join(', ') || 'no third-party packages'}`);
