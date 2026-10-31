const spf = new Int32Array(4_000_010);
for (let i=2;i<spf.length;i++) if(!spf[i]) for(let j=i;j<spf.length;j+=i) if(!spf[j]) spf[j]=i;
const leg=(n:number,p:number)=>{let s=0; while(n){n=Math.floor(n/p); s+=n;} return s;};
const ok=(n:number)=>{ for (const m of [n+1,n+2]) { let x=m; while(x>1){ const p=spf[x]; let a=0; while(x%p===0){x/=p;a++;} if (leg(2*n,p)-2*leg(n,p) < 2*a) return false; } } return true; };
let c=0; const marks=[1e4,1e5,1e6,2e6]; let mi=0; let first=-1;
for(let n=1;n<=2e6;n++){ if(ok(n)){c++; if(first<0) first=n;} if(n===marks[mi]){ console.log("n <=",n,": count",c, "density", (c/n).toFixed(4)); mi++; } }
console.log("first", first);
