/**
 * Search the published 29-mark 623 ruler by shifting a suffix across a large
 * gap, then repairing at most one mark. Coordinates are normalized to start
 * at zero. A candidate is accepted only when all pairwise differences differ.
 */
import { createHash } from "node:crypto";

const seed = [0, 7, 11, 31, 43, 53, 100, 121, 144, 150, 202, 220, 229, 268, 284, 285, 356, 371, 390, 416, 430, 465, 467, 528, 582, 590, 595, 620, 623];
const cap = 622;
const minGap = 40;
const started = Date.now();

type Candidate = { cut: number; delta: number; repaired: number; replacement: number; marks: number[] };
type CutResult = { cut: number; gap: number; deltas: number; shiftedValid: number; repairableStates: number; coreUnique: number; candidates: Candidate[] };

function canonical(marks: number[]): number[] {
  const translated = marks.map(x => x - marks[0]);
  const reflected = translated.map(x => translated[translated.length - 1] - x).reverse();
  return translated.join(",") < reflected.join(",") ? translated : reflected;
}
function digest(marks: number[]): string {
  return createHash("sha256").update(canonical(marks).join(",")).digest("hex");
}
function unique(marks: number[]): boolean {
  const seen = new Set<number>();
  for (let j = 0; j < marks.length; j++) for (let i = 0; i < j; i++) {
    const d = marks[j] - marks[i];
    if (d <= 0 || seen.has(d)) return false;
    seen.add(d);
  }
  return true;
}
function repairPositions(marks: number[]): number[] {
  const holders = new Map<number, Set<number>>();
  for (let j = 0; j < marks.length; j++) for (let i = 0; i < j; i++) {
    const d = marks[j] - marks[i];
    const s = holders.get(d) ?? new Set<number>();
    s.add(i); s.add(j); holders.set(d, s);
  }
  let possible: Set<number> | null = null;
  for (const entries of holders.values()) if (entries.size > 2) {
    possible = possible === null ? new Set(entries) : new Set([...possible].filter(i => entries.has(i)));
  }
  return [...(possible ?? [])].filter(i => i !== 0 && i !== marks.length - 1);
}
function validReplacement(core: number[], x: number): boolean {
  if (x <= 0 || x >= cap || core.includes(x)) return false;
  const all = [...core, x].sort((a, b) => a - b);
  return all[0] === 0 && all[all.length - 1] <= cap && unique(all);
}

const cuts: CutResult[] = [];
const candidates: Candidate[] = [];
for (let cut = 1; cut < seed.length; cut++) {
  const gap = seed[cut] - seed[cut - 1];
  if (gap < minGap) continue;
  const result: CutResult = { cut, gap, deltas: 0, shiftedValid: 0, repairableStates: 0, coreUnique: 0, candidates: [] };
  // Negative suffix shifts shorten the ruler. |delta|<gap preserves order.
  for (let delta = -1; delta > -gap; delta--) {
    result.deltas++;
    const shifted = seed.map((x, i) => i < cut ? x : x + delta);
    if (shifted[shifted.length - 1] > cap) throw new Error("suffix shift did not shorten");
    if (unique(shifted)) result.shiftedValid++;
    for (const repaired of repairPositions(shifted)) {
      result.repairableStates++;
      const core = shifted.filter((_, i) => i !== repaired);
      if (!unique(core)) continue;
      result.coreUnique++;
      for (let replacement = 1; replacement < cap; replacement++) {
        if (!validReplacement(core, replacement)) continue;
        const marks = [...core, replacement].sort((a, b) => a - b);
        const candidate = { cut, delta, repaired, replacement, marks };
        result.candidates.push(candidate); candidates.push(candidate);
      }
    }
  }
  cuts.push(result);
}

const output = {
  source: "https://cube20.org/golomb/rulers-all-00.zip (downloaded 2026-11-18)",
  seed,
  seedCanonicalSha256: digest(seed),
  cap,
  minGap,
  method: "Every suffix cut whose original adjacent gap is at least 40; every order-preserving negative shift; then every one-mark repair that covers every duplicated difference, with exact core and final uniqueness tests.",
  cuts,
  totalCandidates: candidates.length,
  inequivalentCandidates: [...new Map(candidates.map(c => [digest(c.marks), c])).values()].map(c => ({ ...c, canonicalSha256: digest(c.marks) })),
  elapsedMs: Date.now() - started,
  resumeCursor: "complete: cuts 6,10,16,23,24 (0-based suffix starts), delta range -1..-(gap-1), all repair positions implied by duplicated differences",
};
console.log(JSON.stringify(output, null, 2));
