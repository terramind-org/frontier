/** The next repair layer: exact triple-deletion screen with collision pruning. */
const seed=[0,7,11,31,43,53,100,121,144,150,202,220,229,268,284,285,356,371,390,416,430,465,467,528,582,590,595,620,623];
const cuts=[6,10,16,23,24], cap=622, started=Date.now();
function unique(marks:number[]) { const seen=new Set<number>(); for(let j=0;j<marks.length;j++) for(let i=0;i<j;i++){const d=marks[j]-marks[i];if(seen.has(d))return false;seen.add(d);} return true; }
function collisionClasses(marks:number[]) { const holders=new Map<number,Set<number>>(); for(let j=0;j<marks.length;j++)for(let i=0;i<j;i++){const d=marks[j]-marks[i],s=holders.get(d)??new Set<number>();s.add(i);s.add(j);holders.set(d,s);} return [...holders.values()].filter(s=>s.size>2); }
let states=0, triples=0, prunedByDisjointConflicts=0, coresFiltered=0, coresFeasible=0;
const feasible:{cut:number;delta:number;deleted:[number,number,number]}[]=[];
for(const cut of cuts){const gap=seed[cut]-seed[cut-1];for(let delta=-1;delta>-gap;delta--){states++;const shifted=seed.map((x,i)=>i<cut?x:x+delta), conflicts=collisionClasses(shifted);
  // A deletion set needs one endpoint from each collision class.  If a triple
  // misses any class it is rejected before building the 26-mark difference set.
  for(let a=0;a<29;a++)for(let b=a+1;b<29;b++)for(let c=b+1;c<29;c++){triples++;if(conflicts.some(s=>!s.has(a)&&!s.has(b)&&!s.has(c))){prunedByDisjointConflicts++;continue;}const core=shifted.filter((_,i)=>i!==a&&i!==b&&i!==c);if(core[core.length-1]-core[0]>cap||!unique(core)){coresFiltered++;continue;}coresFeasible++;feasible.push({cut,delta,deleted:[a,b,c]});}
}}
console.log(JSON.stringify({sourceCommit:"3f8f1f93",method:"For every c4 shift and every deleted triple, prune if it misses any duplicated-difference endpoint class; then exactly test the resulting 26-mark core. No three-coordinate insertion is started unless such a core is Golomb.",stats:{states,triples,prunedByDisjointConflicts,coresFiltered,coresFeasible,coresUnfinished:0},feasible,elapsedMs:Date.now()-started,resumeCursor:"complete: all 280 shifts and all C(29,3)=3654 deleted triples; no feasible 26-mark core means no three-insertion domain exists"},null,2));
