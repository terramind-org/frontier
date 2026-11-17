// verify a JSON scheme with the repo's matmul verifier for any n: bun attempts/<problem>/<attempt>/verify-n.ts <file.json> <n>
import { readFileSync } from "node:fs";
import { verify } from "../../../src/check/witness/matmul.ts";
const [file, n] = [process.argv[2]!, Number(process.argv[3])];
const r = verify(JSON.parse(readFileSync(file, "utf8")), { n, field: "Z" } as never);
console.log(JSON.stringify({ file, n, valid: r.valid, value: (r as { value?: number }).value, reason: (r as { reason?: string }).reason }));
