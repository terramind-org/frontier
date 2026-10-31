const leg=(n:number,p:number)=>{let s=0; while(n){n=Math.floor(n/p); s+=n;} return s;};
const vp=(m:number,p:number)=>{let a=0; while(m%p===0){m/=p;a++;} return a;};
const primesOf=(m:number)=>{const r:number[]=[]; let x=m; for(let p=2;p*p<=x;p++){ if(x%p===0){r.push(p); while(x%p===0)x/=p;} } if(x>1) r.push(x); return r;};
const ok=(n:number)=>{ for(const p of new Set([...primesOf(n+1),...primesOf(n+2)])){ if(leg(2*n,p)-2*leg(n,p) < 2*(vp(n+1,p)+vp(n+2,p))) return false;} return true;};
const fams:[string,(j:number)=>number][]=[["2^j-1",j=>2**j-1],["2^j-2",j=>2**j-2],["2^j-3",j=>2**j-3],["3^j-1",j=>3**j-1],["3^j-2",j=>3**j-2],["3^j-3",j=>3**j-3]];
for(const [name,f] of fams){ const hits:string[]=[]; let tested=0; for(let j=1;j<60;j++){ const n=f(j); if(n<1||n>=1e7) continue; tested++; if(ok(n)) hits.push(`j=${j} n=${n}`);} console.log(name,"tested",tested,"hits",hits.join(", ")||"none"); }
console.log("ok(4093)",ok(4093),"ok(2045)",ok(2045));
