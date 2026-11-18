/**
 * Two-block compression followed by exact four-mark repair.
 *
 * States use two increasing cuts from the five large c4 gaps.  The first
 * block is fixed, middle/last blocks receive distinct negative offsets from
 * [-8,-1], and both join inequalities and final span <= 622 are required.
 * Reflection-normalized mark vectors deduplicate equivalent states.
 */
import { createHash } from "node:crypto";
import { mkdirSync, renameSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const seed=[0,7,11,31,43,53,100,121,144,150,202,220,229,268,284,285,356,371,390,416,430,465,467,528,582,590,595,620,623];
const largeCuts=[6,10,16,23,24], cap=622, bound=32, started=Date.now();
const outDir=process.argv[2] ?? "."; mkdirSync(outDir,{recursive:true});
type Pair=[number,number]; type State={leftCut:number;rightCut:number;middleOffset:number;lastOffset:number;marks:number[];key:string};
function sha(x:number[]){return createHash("sha256").update(x.join(",")).digest("hex");}
function unique(m:number[]){const s=new Set<number>();for(let j=0;j<m.length;j++)for(let i=0;i<j;i++){const d=m[j]-m[i];if(d<=0||s.has(d))return false;s.add(d);}return true;}
function span(m:number[]){return Math.max(...m)-Math.min(...m);}
function pairs(m:number[]){const r=new Map<number,Pair[]>();for(let j=0;j<m.length;j++)for(let i=0;i<j;i++){const d=m[j]-m[i],e=r.get(d)??[];e.push([i,j]);r.set(d,e);}return r;}
function canonical(m:number[]){const n=m.map(x=>x-m[0]), r=n.map(x=>n[n.length-1]-x).reverse();return n.join(",")<r.join(",")?n.join(","):r.join(",");}
function deletedKey(s:Set<number>){return [...s].sort((a,b)=>a-b).join(",");}
function unresolved(ps:Map<number,Pair[]>,del:Set<number>){for(const es of ps.values()){const live=es.filter(([a,b])=>!del.has(a)&&!del.has(b));if(live.length>1)return [live[0],live[1]];}return undefined;}
function supersets(del:Set<number>,emit:(x:Set<number>)=>void){const a=[];for(let i=0;i<29;i++)if(!del.has(i))a.push(i);const need=4-del.size;function rec(at:number,p:number[]){if(p.length===need)return emit(new Set([...del,...p]));for(let i=at;i<=a.length-(need-p.length);i++)rec(i+1,[...p,a[i]]);}rec(0,[]);}
function branch(m:number[]){const ps=pairs(m),out=new Set<string>();let early=0;function rec(del:Set<number>){const c=unresolved(ps,del);if(!c){if(del.size<4){early++;supersets(del,x=>out.add(deletedKey(x)));}else out.add(deletedKey(del));return;}if(del.size===4)return;for(const x of new Set([...c[0],...c[1]])){const n=new Set(del);n.add(x);rec(n);}}rec(new Set());return {sets:out,early};}
function brute(m:number[]){const out=new Set<string>();for(let a=0;a<29;a++)for(let b=a+1;b<29;b++)for(let c=b+1;c<29;c++)for(let d=c+1;d<29;d++){const del=new Set([a,b,c,d]);if(unique(m.filter((_,i)=>!del.has(i))))out.add(`${a},${b},${c},${d}`);}return out;}
function singles(core:number[]){const used=new Set<number>();for(let j=0;j<core.length;j++)for(let i=0;i<j;i++)used.add(core[j]-core[i]);const lo=Math.max(...core)-cap,hi=Math.min(...core)+cap,out:number[]=[];for(let x=lo;x<=hi;x++){if(core.includes(x))continue;const ds=core.map(y=>Math.abs(x-y));if(ds.every(d=>d>0&&!used.has(d))&&new Set(ds).size===ds.length)out.push(x);}return out;}
function four(core:number[],s:number[]){let count=0;const found:number[][]=[];function rec(at:number,p:number[]){if(p.length===4){if(span([...core,...p])<=cap&&unique([...core,...p])){count++;found.push([...core,...p].sort((a,b)=>a-b));}return;}for(let i=at;i<=s.length-(4-p.length);i++)rec(i+1,[...p,s[i]]);}rec(0,[]);return {count,found};}
function atomic(name:string,o:unknown){const t=join(outDir,`.${name}.tmp`);writeFileSync(t,JSON.stringify(o,null,2)+"\n");renameSync(t,join(outDir,name));}
function states(){const raw:State[]=[];const seen=new Set<string>();for(let a=0;a<largeCuts.length;a++)for(let b=a+1;b<largeCuts.length;b++)for(let u=-1;u>=-bound;u--)for(let v=-1;v>=-bound;v--){if(u===v)continue;const l=largeCuts[a],r=largeCuts[b],m=seed.map((x,i)=>i<l?x:i<r?x+u:x+v);if(!(m[l-1]<m[l]&&m[r-1]<m[r]&&span(m)<=cap))continue;const key=canonical(m);if(seen.has(key))continue;seen.add(key);raw.push({leftCut:l,rightCut:r,middleOffset:u,lastOffset:v,marks:m,key});}return raw;}
const all=states();
// Exercise a zero and a nonzero deletion-set state against independent C(29,4) enumeration.
let zero:State|undefined;for(const s of all)if(branch(s.marks).sets.size===0){zero=s;break;}
if(!zero)throw new Error("domain did not contain a zero control state");
const nonzeroMarks=seed.map((x,i)=>i<24?x:x-3); // c7 independently established nonzero branch fixture.
const controls:any[]=[];
for(const item of [{label:"two-block zero",marks:zero.marks,state:zero},{label:"c7 suffix nonzero fixture",marks:nonzeroMarks,state:null}]){const got=branch(item.marks).sets,want=brute(item.marks);if([...got].sort().join(";")!==[...want].sort().join(";"))throw new Error(`branch/brute mismatch ${item.label}`);controls.push({label:item.label,state:item.state&&{leftCut:item.state.leftCut,rightCut:item.state.rightCut,middleOffset:item.state.middleOffset,lastOffset:item.state.lastOffset},branchSets:got.size,bruteSets:want.size});}
const reports:any[]=[];let generated=0,early=0,feasible=0,singleCoords=0,candidates=0;
for(let ordinal=0;ordinal<all.length;ordinal++){const s=all[ordinal],began=Date.now(),b=branch(s.marks);let good=0,sc=0,cc=0,examples:number[][]=[];for(const k of b.sets){const del=new Set(k.split(",").map(Number)),core=s.marks.filter((_,i)=>!del.has(i));if(span(core)<=cap&&unique(core)){good++;const f=singles(core),x=four(core,f);sc+=f.length;cc+=x.count;examples.push(...x.found);}}
 generated+=b.sets.size;early+=b.early;feasible+=good;singleCoords+=sc;candidates+=cc;const report={ordinal,leftCut:s.leftCut,rightCut:s.rightCut,middleOffset:s.middleOffset,lastOffset:s.lastOffset,key:s.key,generated:b.sets.size,clearEarly:b.early,validCores:good,singleCoordinates:sc,candidateCount:cc,candidates:examples,elapsedMs:Date.now()-began};reports.push(report);atomic(`checkpoint-${String(ordinal).padStart(3,"0")}.json`,report);atomic("progress.json",{seedSha256:sha(seed),completedStates:ordinal+1,totalStates:all.length,last:report,resumeCursor:ordinal+1===all.length?"complete":"next state ordinal "+(ordinal+1)});
}
const result={sourceCommit:"e1a9fe2b (PR 108 baseline recovery)",seed,seedSha256:sha(seed),cap,largeCuts,bound,domain:"all pairs of increasing cuts from [6,10,16,23,24], offsets u,v in [-32,-1], u!=v; first block fixed; join inequalities, span <=622, and reflection canonicalization",controls,stats:{states:all.length,generatedDeletionSets:generated,conflictsClearBeforeFour:early,coresFiltered:generated-feasible,coresFeasible:feasible,coresExhausted:feasible,coresUnfinished:0,singleInsertionFrontierCoordinates:singleCoords,actualCandidates:candidates},reports,elapsedMs:Date.now()-started,resumeCursor:"complete: every canonical two-block state in the stated cut/offset domain; all endpoint-branch deletion sets and all exact four-coordinate frontiers exhausted"};atomic("result.json",result);console.log(JSON.stringify(result,null,2));
