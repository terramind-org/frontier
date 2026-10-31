// Flags problems whose stored lean.statement ends mid-binder or has unbalanced brackets,
// and confirms each against the upstream source (the statement must be a strict prefix of the
// upstream text before `:= by`).
import { readdirSync, readFileSync } from "fs";
import YAML from "yaml";
const OPEN = "([{⟨⦃", CLOSE = ")]}⟩⦄";
const FC = "lean/.lake/packages/formal_conjectures/";
let total = 0; const rows: string[] = [];
for (const f of readdirSync("problems").sort()) {
  const y: any = YAML.parse(readFileSync("problems/" + f, "utf8"));
  const s: string | undefined = y?.lean?.statement; if (!s) continue; total++;
  const t = s.trim(); const reasons: string[] = [];
  const m = /\b(letI|haveI|let|have|let_fun)\s+[^\s:]+(\s*:[^\n]*)?$/.exec(t);
  if (m) reasons.push(`ends mid-binder: "${m[0]}"`);
  let d = 0; for (const c of t) { if (OPEN.includes(c)) d++; else if (CLOSE.includes(c)) d--; }
  if (d !== 0) reasons.push(`unbalanced brackets (depth ${d})`);
  if (!reasons.length) continue;
  const src = readFileSync(FC + y.source.path, "utf8");
  const i = src.indexOf(t.split("\n")[0]);
  const upstream = i < 0 ? "?" : src.slice(i, src.indexOf(":= by", i + t.length) >= 0 ? src.indexOf(":= by", i + t.length) : i + 400).replace(/\s+/g, " ").trim();
  const confirmed = i >= 0 && upstream.length > t.replace(/\s+/g, " ").length;
  rows.push(`${y.id}\t${reasons.join("; ")}\tconfirmed truncated: ${confirmed}\tupstream: ${upstream.slice(0, 160)}`);
}
console.log(`lean statements: ${total}; flagged: ${rows.length}`); console.log(rows.join("\n"));
