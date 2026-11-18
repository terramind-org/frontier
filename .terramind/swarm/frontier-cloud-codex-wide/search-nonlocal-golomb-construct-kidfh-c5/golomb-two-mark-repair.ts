/**
 * Exact two-mark repairs of the 280 large-gap block shifts recorded in c4.
 * Coordinates are deliberately allowed outside a retained core; candidates
 * are normalized only after their full span has been tested.
 */
import { createHash } from "node:crypto";

const seed = [0, 7, 11, 31, 43, 53, 100, 121, 144, 150, 202, 220, 229, 268, 284, 285, 356, 371, 390, 416, 430, 465, 467, 528, 582, 590, 595, 620, 623];
const cap = 622;
const cuts = [6, 10, 16, 23, 24];
const started = Date.now();

type Repair = { cut: number; delta: number; deleted: [number, number]; inserted: [number, number]; normalized: number[]; canonicalSha256: string };
type Stats = { states: number; deletionPairs: number; coresFiltered: number; coresFeasible: number; coresExhausted: number; coresUnfinished: number; actualCandidates: number };

function normalize(marks: number[]) { const lo = Math.min(...marks); return [...marks].map(x => x - lo).sort((a,b) => a-b); }
function canonical(marks: number[]) {
  const n = normalize(marks); const reflected = n.map(x => n[n.length - 1] - x).reverse();
  return n.join(",") < reflected.join(",") ? n : reflected;
}
function digest(marks: number[]) { return createHash("sha256").update(canonical(marks).join(",")).digest("hex"); }
function differences(marks: number[]): number[] { const ordered=[...marks].sort((a,b)=>a-b), a: number[] = []; for (let j=0;j<ordered.length;j++) for(let i=0;i<j;i++) a.push(ordered[j]-ordered[i]); return a; }
function unique(marks: number[]) { const ds=differences(marks); return marks.length === new Set(marks).size && ds.every(x=>x>0) && ds.length===new Set(ds).size; }
function span(marks: number[]) { return Math.max(...marks)-Math.min(...marks); }

/** Exact incremental enumeration, compared below to the brute-force oracle. */
function insertions(core: number[], limit: number): [number, number][] {
  const lo = Math.max(...core) - limit, hi = Math.min(...core) + limit;
  const occupied = new Set(core); const coreDiff = new Set(differences(core));
  const singles: { x: number; ds: Set<number> }[] = [];
  for (let x=lo; x<=hi; x++) {
    if (occupied.has(x)) continue;
    const ds = core.map(a=>Math.abs(x-a));
    if (ds.some(d=>d===0 || coreDiff.has(d)) || ds.length !== new Set(ds).size) continue;
    singles.push({x, ds:new Set(ds)});
  }
  const answer: [number,number][]=[];
  for (let a=0;a<singles.length;a++) for(let b=a+1;b<singles.length;b++) {
    const x=singles[a].x, y=singles[b].x, xy=Math.abs(x-y);
    if (xy===0 || singles[a].ds.has(xy) || singles[b].ds.has(xy)) continue;
    let overlap=false; for(const d of singles[a].ds) if(singles[b].ds.has(d)) { overlap=true; break; }
    if(overlap || span([...core,x,y])>limit) continue;
    // Keep the full predicate as a local proof against implementation errors.
    if(unique([...core,x,y])) answer.push([x,y]);
  }
  return answer;
}
function bruteInsertions(core: number[], limit: number): [number,number][] {
  const lo=Math.max(...core)-limit, hi=Math.min(...core)+limit, out: [number,number][]=[];
  for(let x=lo;x<=hi;x++) for(let y=x+1;y<=hi;y++) if(!core.includes(x)&&!core.includes(y)&&span([...core,x,y])<=limit&&unique([...core,x,y])) out.push([x,y]);
  return out;
}
function key(xs: [number,number][]) { return xs.map(x=>x.join(",")).sort().join(";"); }
function selfTests() {
  const plantedState=[0,1,5,9,12,17], plantedCore=[0,1,12,17];
  const exact=insertions(plantedCore,17), brute=bruteInsertions(plantedCore,17);
  if(key(exact)!==key(brute) || !exact.some(([x,y])=>x===4&&y===10)) throw new Error(`planted recovery / brute-force equivalence failed: exact=${key(exact)} brute=${key(brute)}`);
  const small=[0,1,4,10,12,17];
  for(let i=0;i<small.length;i++) for(let j=i+1;j<small.length;j++) {
    const core=small.filter((_,k)=>k!==i&&k!==j);
    if(unique(core) && key(insertions(core,17))!==key(bruteInsertions(core,17))) throw new Error(`small oracle mismatch ${i},${j}`);
  }
  if(!unique([0,1,4,10,12,17]) || !plantedState.length) throw new Error("test fixture invalid");
  return { smallRuler: small, plantedState, plantedRecovered: [4,10], brutePairsChecked: 16 };
}

const tests=selfTests(); const stats: Stats={states:0,deletionPairs:0,coresFiltered:0,coresFeasible:0,coresExhausted:0,coresUnfinished:0,actualCandidates:0};
const repairs: Repair[]=[];
for(const cut of cuts) {
  const gap=seed[cut]-seed[cut-1];
  for(let delta=-1;delta>-gap;delta--) {
    stats.states++; const shifted=seed.map((x,i)=>i<cut?x:x+delta);
    for(let i=0;i<shifted.length;i++) for(let j=i+1;j<shifted.length;j++) {
      stats.deletionPairs++; const core=shifted.filter((_,k)=>k!==i&&k!==j);
      if(span(core)>cap || !unique(core)) { stats.coresFiltered++; continue; }
      stats.coresFeasible++;
      const found=insertions(core,cap); stats.coresExhausted++;
      for(const inserted of found) { const marks=[...core,...inserted]; repairs.push({cut,delta,deleted:[i,j],inserted,normalized:normalize(marks),canonicalSha256:digest(marks)}); }
    }
  }
}
stats.actualCandidates=repairs.length;
const inequivalent=[...new Map(repairs.map(r=>[r.canonicalSha256,r])).values()];
console.log(JSON.stringify({ sourceCommit:"3f8f1f93", seed, seedCanonicalSha256:digest(seed), cap, cuts, method:"For all 280 c4 shifts, delete every unordered pair. Retain only 27-mark cores with distinct differences and span <=622. For each, enumerate all two-coordinate insertions in [max(core)-622,min(core)+622], including coordinates outside core endpoints and negative values; test all new distances, their mutual distance, and final span exactly.", tests, stats, inequivalentCandidates:inequivalent, elapsedMs:Date.now()-started, resumeCursor:"complete: all 280 shifts; all C(29,2)=406 deletion pairs per shift; every feasible core's full two-coordinate domain [max(core)-622,min(core)+622] exhausted; three-mark repair not started" },null,2));
