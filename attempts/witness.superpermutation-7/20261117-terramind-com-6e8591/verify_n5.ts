// Runs the repo's superperm verifier with n = 5 on JSON witness files (the CLI's diagnose only knows the n = 7 problem).
// Usage, from the repo root: bun attempts/witness.superpermutation-7/20261117-terramind-com-6e8591/verify_n5.ts <file.json>...
import { verify } from '../../../src/check/witness/superperm.ts';
for (const f of process.argv.slice(2)) {
  const w = JSON.parse(await Bun.file(f).text());
  console.log(f.split('/').pop(), JSON.stringify(verify(w, { n: 5 })));
}
