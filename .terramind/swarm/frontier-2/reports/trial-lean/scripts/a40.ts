let found=0; const LIM=200000;
for (let b=2n;b<=BigInt(LIM);b++){ if (b%2n!==0n || b%5n===0n) continue; const s=(b**40n).toString(); if(!s.includes("0")){console.log("zeroless",b); found++;} }
console.log("searched even b, 5∤b, 2 ≤ b ≤",LIM,"found",found);
