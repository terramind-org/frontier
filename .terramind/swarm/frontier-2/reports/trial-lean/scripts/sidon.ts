// greedy Sidon (Mian-Chowla): a1=1, next = least integer keeping all pairwise sums distinct
const LIM = 3_000_000;
const diff = new Uint8Array(LIM+1); // differences used
const A:number[]=[1];
let c=2;
while (A.length < 3000) {
  // c valid iff all differences c-a are unused and distinct among themselves (they are distinct automatically)
  let ok=true; for (const a of A){ const d=c-a; if(d>LIM||diff[d]){ok=false;break;} }
  if(ok){ for(const a of A) diff[c-a]=1; A.push(c); if (c>LIM/2) break; }
  c++;
}
console.log("terms",A.length,"last",A[A.length-1],"33 in A-A?",!!diff[33]);
const missing:number[]=[]; for(let d=1;d<=200;d++) if(!diff[d]) missing.push(d); console.log("missing <=200:",missing.join(","));
