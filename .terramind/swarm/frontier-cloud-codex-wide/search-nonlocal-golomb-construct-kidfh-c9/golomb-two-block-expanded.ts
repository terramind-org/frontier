/**
 * c9: exact four-mark repair for two-block compressions outside c8.
 *
 * The coordinate domain is deliberately finite: two increasing cuts from the
 * inherited five, distinct offsets in [-64,-1], at least one offset <-32,
 * ordered joins, span <= 622, and reflection canonicalization.  The c8
 * canonical set is loaded and excluded, so this run has no overlap with its
 * [-32,-1] family.  Each cut pair is a durable partition; each state gets an
 * atomic record before the next one starts.
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const seed=[0,7,11,31,43,53,100,121,144,150,202,220,229,268,284,285,356,371,390,416,430,465,467,528,582,590,595,620,623];
const cuts=[6,10,16,23,24], cap=622, oldBound=32, bound=64, started=Date.now();
const out=process.argv[2] ?? ".", c8Result=process.argv[3]; mkdirSync(out,{recursive:true});
type Pair=[number,number]; type State={partition:string;ordinal:number;leftCut:number;rightCut:number;middleOffset:number;lastOffset:number;marks:number[];key:string};
const sha=(x:number[])=>createHash("sha256").update(x.join(",")).digest("hex");
function atomic(n:string,x:unknown){const t=join(out,`.${n}.tmp`);writeFileSync(t,JSON.stringify(x,null,2)+"\n");renameSync(t,join(out,n));}
function unique(m:number[]){const d=new Set<number>();for(let j=0;j<m.length;j++)for(let i=0;i<j;i++){const q=m[j]-m[i];if(q<=0||d.has(q))return false;d.add(q);}return true;}
function span(m:number[]){return Math.max(...m)-Math.min(...m);}
function canonical(m:number[]){const n=m.map(x=>x-m[0]),r=n.map(x=>n[n.length-1]-x).reverse();return n.join(",")<r.join(",")?n.join(","):r.join(",");}
function pairs(m:number[]){const r=new Map<number,Pair[]>();for(let j=0;j<m.length;j++)for(let i=0;i<j;i++){const d=m[j]-m[i], a=r.get(d)??[];a.push([i,j]);r.set(d,a);}return r;}
const dkey=(s:Set<number>)=>[...s].sort((a,b)=>a-b).join(",");
function unresolved(ps:Map<number,Pair[]>,d:Set<number>){for(const p of ps.values()){const live=p.filter(([a,b])=>!d.has(a)&&!d.has(b));if(live.length>1)return [live[0],live[1]];}return undefined;}
function addSupersets(d:Set<number>,add:(x:Set<number>)=>void){const keep=[];for(let i=0;i<29;i++)if(!d.has(i))keep.push(i);const need=4-d.size;function go(at:number,p:number[]){if(p.length===need){add(new Set([...d,...p]));return;}for(let i=at;i<=keep.length-(need-p.length);i++)go(i+1,[...p,keep[i]]);}go(0,[]);}
function branch(m:number[]){const ps=pairs(m),ans=new Set<string>();let early=0;function go(d:Set<number>){const c=unresolved(ps,d);if(!c){if(d.size<4){early++;addSupersets(d,x=>ans.add(dkey(x)));}else ans.add(dkey(d));return;}if(d.size===4)return;for(const x of new Set([...c[0],...c[1]])){const n=new Set(d);n.add(x);go(n);}}go(new Set());return {sets:ans,early};}
function brute(m:number[]){const ans=new Set<string>();for(let a=0;a<29;a++)for(let b=a+1;b<29;b++)for(let c=b+1;c<29;c++)for(let d=c+1;d<29;d++){const gone=new Set([a,b,c,d]);if(unique(m.filter((_,i)=>!gone.has(i))))ans.add(`${a},${b},${c},${d}`);}return ans;}
function frontier(core:number[]){const used=new Set<number>();for(let j=0;j<core.length;j++)for(let i=0;i<j;i++)used.add(core[j]-core[i]);const lo=Math.max(...core)-cap,hi=Math.min(...core)+cap,ans:number[]=[];for(let x=lo;x<=hi;x++){if(core.includes(x))continue;const ds=core.map(y=>Math.abs(x-y));if(ds.every(d=>d>0&&!used.has(d))&&new Set(ds).size===ds.length)ans.push(x);}return ans;}
function insertFour(core:number[],f:number[]){let n=0;const found:number[][]=[];function go(at:number,p:number[]){if(p.length===4){const m=[...core,...p];if(span(m)<=cap&&unique(m)){n++;found.push(m.sort((a,b)=>a-b));}return;}for(let i=at;i<=f.length-(4-p.length);i++)go(i+1,[...p,f[i]]);}go(0,[]);return {n,found};}
function oldKeys(){if(!c8Result||!existsSync(c8Result))throw new Error("missing c8 result for overlap exclusion");const parsed=JSON.parse(readFileSync(c8Result,"utf8"));if(parsed.seedSha256!==sha(seed)||parsed.bound!==32||parsed.stats.states!==9920)throw new Error("c8 manifest control mismatch");return new Set<string>(parsed.reports.map((x:any)=>x.key));}
const prior=oldKeys();
const groups=new Map<string,State[]>();let raw=0, duplicate=0, excluded=0;const seen=new Set<string>();
for(let ai=0;ai<cuts.length;ai++)for(let bi=ai+1;bi<cuts.length;bi++){
 const l=cuts[ai],r=cuts[bi],partition=`cuts-${l}-${r}`;const states:State[]=[];
 for(let u=-1;u>=-bound;u--)for(let v=-1;v>=-bound;v--){if(u===v||!(u<-oldBound||v<-oldBound))continue;raw++;const m=seed.map((x,i)=>i<l?x:i<r?x+u:x+v);if(!(m[l-1]<m[l]&&m[r-1]<m[r]&&span(m)<=cap))continue;const key=canonical(m);if(prior.has(key)){excluded++;continue;}if(seen.has(key)){duplicate++;continue;}seen.add(key);states.push({partition,ordinal:states.length,leftCut:l,rightCut:r,middleOffset:u,lastOffset:v,marks:m,key});}
 groups.set(partition,states);
}
const all=[...groups.values()].flat();
// Independent exact controls: an expanded-domain zero and the inherited known nonzero fixture.
const zero=all.find(s=>branch(s.marks).sets.size===0); if(!zero)throw new Error("no zero control");
const nonzero=seed.map((x,i)=>i<24?x:x-3); const controls:any[]=[];
for(const x of [{label:"expanded two-block zero",marks:zero.marks,state:zero},{label:"c7 suffix nonzero fixture",marks:nonzero,state:null}]){const a=branch(x.marks).sets,b=brute(x.marks);if([...a].sort().join(";")!==[...b].sort().join(";"))throw new Error(`control mismatch: ${x.label}`);controls.push({label:x.label,branchSets:a.size,bruteSets:b.size,state:x.state&&{partition:x.state.partition,ordinal:x.state.ordinal,leftCut:x.state.leftCut,rightCut:x.state.rightCut,middleOffset:x.state.middleOffset,lastOffset:x.state.lastOffset}});}
atomic("manifest.json",{sourceCommit:"5dfb8d2c",seedSha256:sha(seed),cuts,cap,oldBound,bound,rawOffsetPairs:raw,priorCanonicalStates:prior.size,canonicalCandidates:all.length,duplicateCanonicalStates:duplicate,excludedPriorCanonicalStates:excluded,controls,ordering:"cut pair lexicographic; middle offset -1..-64; last offset -1..-64; ordinal within partition"});
let generated=0,feasible=0,filtered=0,frontierCoords=0,candidates=0,completed=0;const partitionSummaries:any[]=[];
for(const [partition,states] of groups){let pg=0,pf=0,px=0,pc=0;
 for(const s of states){const b=branch(s.marks);let sg=0,sf=0,sx=0,sc=0,found:number[][]=[];for(const key of b.sets){sg++;const gone=new Set(key.split(",").map(Number)),core=s.marks.filter((_,i)=>!gone.has(i));if(!unique(core)||span(core)>cap)continue;sf++;const f=frontier(core),q=insertFour(core,f);sx+=f.length;sc+=q.n;found.push(...q.found);}
  generated+=sg;filtered+=sg-sf;feasible+=sf;frontierCoords+=sx;candidates+=sc;completed++;pg+=sg;pf+=sf;px+=sx;pc+=sc;
  const record={partition,ordinal:s.ordinal,leftCut:s.leftCut,rightCut:s.rightCut,middleOffset:s.middleOffset,lastOffset:s.lastOffset,key:s.key,generatedDeletionSets:sg,feasibleCores:sf,frontierCoordinates:sx,candidates:sc,found};atomic(`${partition}-${String(s.ordinal).padStart(5,"0")}.json`,record);atomic("progress.json",{completedStates:completed,totalStates:all.length,last:record,firstUnvisited:completed===all.length?"complete":all[completed]&&{partition:all[completed].partition,ordinal:all[completed].ordinal,middleOffset:all[completed].middleOffset,lastOffset:all[completed].lastOffset}});
 }
 const summary={partition,states:states.length,generatedDeletionSets:pg,feasibleCores:pf,frontierCoordinates:px,candidates:pc};partitionSummaries.push(summary);atomic(`${partition}-complete.json`,summary);
}
const result={sourceCommit:"5dfb8d2c",seed,seedSha256:sha(seed),controls,domain:"increasing cut pairs from [6,10,16,23,24]; distinct offsets [-64,-1], at least one < -32; ordered joins, span <=622; reflection canonicalization; c8 canonical states excluded",stats:{rawOffsetPairs:raw,excludedPriorCanonicalStates:excluded,duplicateCanonicalStates:duplicate,generatedCanonicalStates:all.length,completedStates:completed,unfinishedStates:all.length-completed,generatedDeletionSets:generated,coresFiltered:filtered,coresFeasible:feasible,coresExhausted:feasible,frontierCoordinates:frontierCoords,actualCandidates:candidates},partitionSummaries,elapsedMs:Date.now()-started,firstUnvisited:"complete"};atomic("result.json",result);console.log(JSON.stringify(result,null,2));
