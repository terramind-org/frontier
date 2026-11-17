import { verify } from '../../../src/check/witness/superperm.ts';
for (const path of process.argv.slice(2)) {
  const data = await Bun.file(path).json();
  const result = verify({ word: data.word }, { n: data.n });
  console.log(JSON.stringify({ path, n: data.n, ...result }));
  if (!result.valid) process.exitCode = 1;
}
