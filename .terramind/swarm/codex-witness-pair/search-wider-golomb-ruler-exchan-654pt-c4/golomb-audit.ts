/**
 * Bounded deletion/recompletion audit for the 29-mark Golomb ruler.
 *
 * All search coordinates remain in the published ruler's frame.  For a core,
 * a completion of span <= cap must lie in [max(core)-cap, min(core)+cap].
 * Consequently, the only safe frozen-core skip is core span > cap; this is
 * equivalent to retaining both 0 and 623 for the 623 seed/cap 622 case.
 */

type SearchResult = {
  completed: number;
  endpointClasses: Record<string, number>;
  frozen: number;
  frozenEndpointClasses: Record<string, number>;
  leaves: number;
  firstUnfinished: number[] | null;
  candidate: number[] | null;
};

const seed623 = [0, 7, 11, 31, 43, 53, 100, 121, 144, 150, 202, 220, 229, 268, 284, 285, 356, 371, 390, 416, 430, 465, 467, 528, 582, 590, 595, 620, 623];
const seed585 = [0, 32, 39, 62, 81, 99, 170, 183, 197, 203, 231, 247, 255, 290, 343, 360, 364, 365, 433, 443, 479, 488, 490, 519, 544, 570, 582, 585];
const CAP = 622;
const started = Date.now();
const primaryDeadline = started + 25 * 60_000;
const finalDeadline = started + 30 * 60_000;
let activeDeadline = primaryDeadline;

function choose(n: number, k: number): number {
  if (k < 0 || k > n) return 0;
  k = Math.min(k, n - k);
  let r = 1;
  for (let i = 1; i <= k; i++) r = (r * (n - k + i)) / i;
  return r;
}

function* deletions(n: number, k: number, start = 0, acc: number[] = []): Generator<number[]> {
  if (acc.length === k) { yield acc; return; }
  for (let i = start; i <= n - (k - acc.length); i++) yield* deletions(n, k, i + 1, [...acc, i]);
}

function classOf(removed: number[], n: number): string {
  const lo = removed.includes(0), hi = removed.includes(n - 1);
  return lo && hi ? "both" : lo ? "left" : hi ? "right" : "neither";
}

function complete(core: number[], add: number, cap: number, stopAtFirst: boolean): { leaves: number; candidate: number[] | null } {
  const used = new Set<number>();
  for (let j = 0; j < core.length; j++) for (let i = 0; i < j; i++) used.add(core[j] - core[i]);
  const low = Math.max(core[core.length - 1] - cap, -cap * 2);
  const high = Math.min(core[0] + cap, cap * 2);
  let leaves = 0;
  let found: number[] | null = null;
  const present = new Set(core);

  function visit(chosen: number[], from: number): boolean {
    if (Date.now() >= activeDeadline) return true;
    if (chosen.length === add) {
      leaves++;
      const all = [...core, ...chosen].sort((a, b) => a - b);
      if (all[all.length - 1] - all[0] <= cap) found = all;
      return Boolean(found && stopAtFirst);
    }
    for (let x = from; x <= high; x++) {
      if (present.has(x)) continue;
      const ds: number[] = [];
      let ok = true;
      for (const y of core) { const d = Math.abs(x - y); if (d === 0 || used.has(d) || ds.includes(d)) { ok = false; break; } ds.push(d); }
      if (ok) for (const y of chosen) { const d = Math.abs(x - y); if (used.has(d) || ds.includes(d)) { ok = false; break; } ds.push(d); }
      if (!ok) continue;
      present.add(x); for (const d of ds) used.add(d);
      if (visit([...chosen, x], x + 1)) return true;
      for (const d of ds) used.delete(d); present.delete(x);
    }
    return false;
  }
  visit([], low);
  return { leaves, candidate: found };
}

function runStage(seed: number[], k: number, cap: number, insertions = k): SearchResult {
  const r: SearchResult = { completed: 0, endpointClasses: { neither: 0, left: 0, right: 0, both: 0 }, frozen: 0, frozenEndpointClasses: { neither: 0, left: 0, right: 0, both: 0 }, leaves: 0, firstUnfinished: null, candidate: null };
  for (const removed of deletions(seed.length, k)) {
    if (Date.now() >= activeDeadline) { r.firstUnfinished = removed; break; }
    const core = seed.filter((_, i) => !removed.includes(i));
    const cls = classOf(removed, seed.length);
    if (core[core.length - 1] - core[0] > cap) { r.frozen++; r.frozenEndpointClasses[cls]++; continue; } // exactly the frozen cores
    const got = complete(core, insertions, cap, true);
    r.completed++; r.endpointClasses[cls]++; r.leaves += got.leaves;
    if (got.candidate) { r.candidate = got.candidate; break; }
  }
  return r;
}

function control(name: string, core: number[], add: number, cap: number) {
  const got = complete(core, add, cap, false);
  return { name, core, add, cap, leaves: got.leaves, candidate: got.candidate };
}

const out: Record<string, unknown> = { started: new Date(started).toISOString(), cap: CAP, controls: [] };
// Optimal 4-mark ruler control: complete the 3-mark core at cap 6 but not cap 5.
(out.controls as unknown[]).push(control("four-mark [0,1,4]", [0, 1, 4], 1, 6));
(out.controls as unknown[]).push(control("four-mark [0,1,4]", [0, 1, 4], 1, 5));
// These require the both-endpoints-removed class: recover 0 and 623 from the 27-mark interior.
(out.controls as unknown[]).push(control("recover both 623 endpoints", seed623.slice(1, -1), 2, 623));

out.stages = {};
for (const k of [3, 4, 5]) {
  const got = runStage(seed623, k, CAP);
  const expected = choose(29, k) - choose(27, k);
  (out.stages as Record<string, unknown>)[`623-delete-${k}`] = { ...got, expected, assertion: got.completed === expected || got.firstUnfinished !== null || got.candidate !== null };
  if (got.candidate || got.firstUnfinished) break;
}

// The 585 check is bounded to the final five minutes: its own completion window is cap 622.
out.seed585 = {};
activeDeadline = finalDeadline;
for (const k of [0, 1, 2, 3]) {
  if (Date.now() >= activeDeadline) { (out.seed585 as Record<string, unknown>)[`delete-${k}`] = { firstUnfinished: "deadline" }; break; }
  const got = runStage(seed585, k, CAP, k + 1);
  (out.seed585 as Record<string, unknown>)[`delete-${k}`] = { ...got, expected: choose(28, k) };
  if (got.candidate || got.firstUnfinished) break;
}
out.elapsedMs = Date.now() - started;
out.exit = "completed";
console.log(JSON.stringify(out, null, 2));
