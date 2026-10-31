// n with ((n+2)!)^2 | (2n)!  <=> for all p: v_p((2n)!) >= 2 v_p((n+2)!)
const M = 2_000_000;
const spf = new Int32Array(M*2+5);
for (let i=2;i<spf.length;i++) if(!spf[i]) for(let j=i;j<spf.length;j+=i) if(!spf[j]) spf[j]=i;
const leg=(n:number,p:number)=>{let s=0; while(n){n=Math.floor(n/p); s+=n;} return s;};
const sols:number[]=[];
for (let n=1;n<=M;n++){
  // only primes dividing (n+1)(n+2) matter? No: v_p((n+2)!)^2 vs (2n)!: condition is v_p(C(2n,n)) >= 2*(v_p(n+1)+v_p(n+2)).
  let ok=true;
  for (const m of [n+1,n+2]) { let x=m; while(x>1){ const p=spf[x]; let a=0; while(x%p===0){x/=p;a++;}
      const need = 2*(((n+1)%p===0?vp(n+1,p):0)+((n+2)%p===0?vp(n+2,p):0));
      const have = leg(2*n,p)-2*leg(n,p);
      if (have<need){ok=false;break;} } if(!ok)break; }
  if(ok) sols.push(n);
}
function vp(m:number,p:number){let a=0; while(m%p===0){m/=p;a++;} return a;}
console.log("count",sols.length); console.log(sols.slice(0,60).join(" "));
