const M = 200000;
const phi = new Int32Array(M+1); for (let i=0;i<=M;i++) phi[i]=i;
for (let p=2;p<=M;p++) if (phi[p]===p) for (let k=p;k<=M;k+=p) phi[k]-=phi[k]/p;
const isP = (n:number)=>{ if(n<2) return false; for(let d=2;d*d<=n;d++) if(n%d===0) return false; return true;};
// LIS strictly increasing, patience
const tails:number[]=[]; let pi=0; let reported=0;
for (let n=1;n<=M;n++){ const v=phi[n]; let lo=0,hi=tails.length; while(lo<hi){const m=(lo+hi)>>1; if(tails[m]<v) lo=m+1; else hi=m;} tails[lo]=v; if(isP(n)) pi++;
 if (n>=2 && tails.length!==pi && reported<10){ console.log("N",n,"LIS",tails.length,"pi",pi); reported++; } }
console.log("done", tails.length, pi);
