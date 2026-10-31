const M = 400000;
const fac=(m:number)=>{const r:string[]=[]; let x=m; for(let p=2;p*p<=x;p++){let a=0; while(x%p===0){x/=p;a++;} if(a) r.push(a>1?`${p}^${a}`:`${p}`);} if(x>1) r.push(`${x}`); return r.join("·");};
const leg=(n:number,p:number)=>{let s=0; while(n){n=Math.floor(n/p); s+=n;} return s;};
const vp=(m:number,p:number)=>{let a=0; while(m%p===0){m/=p;a++;} return a;};
const primesOf=(m:number)=>{const r:number[]=[]; let x=m; for(let p=2;p*p<=x;p++){ if(x%p===0){r.push(p); while(x%p===0)x/=p;} } if(x>1) r.push(x); return r;};
const ok=(n:number)=>{ for(const p of new Set([...primesOf(n+1),...primesOf(n+2)])){ if(leg(2*n,p)-2*leg(n,p) < 2*(vp(n+1,p)+vp(n+2,p))) return false;} return true;};
let c=0; for(let n=1;n<=M;n++) if(ok(n)){ c++; if(c<=40) console.log(n, "n+1=",fac(n+1)," n+2=",fac(n+2), " base2:", n.toString(2)); }
// test families
const fam=(name:string,f:(j:number)=>number)=>{const r:string[]=[]; for(let j=1;j<40;j++){const n=f(j); if(n>0&&n<1e7) r.push(ok(n)?"Y":"."); } console.log(name,r.join(""));};
fam("2^j-2",j=>2**j-2); fam("2^j-3",j=>2**j-3); fam("3^j-2",j=>3**j-2); fam("3^j-1",j=>3**j-1);fam("3^j-3",j=>3**j-3);
fam("2^j",j=>2**j); fam("2^j+? ",j=>2**j-1);
