"""Conditional Hensel lift of an accepted GF(2) mask tensor to integer coefficients.
Run from repo root: python3 -I lift.py INPUT.mask OUTPUT.json [levels=8].
At each level solve the full linearized Brent system by exact GF(2) elimination.
Free variables are set to zero: failure of this path does not disprove liftability.
The output exists only after an exact integer tensor identity succeeds.
"""
import json, pathlib, sys, time
N=25

def readmask(path):
 v=list(map(int,pathlib.Path(path).read_text().split()))
 assert len(v)==1+3*v[0]
 return [[[int(v[1+3*s+k]>>i&1) for i in range(N)] for k in range(3)] for s in range(v[0])]

def tensor(t):
 z=[0]*(N**3)
 for a,b,c in t:
  for i,x in enumerate(a):
   if not x: continue
   for j,y in enumerate(b):
    if not y: continue
    base=(i*N+j)*N
    for k,v in enumerate(c):
     if v: z[base+k]+=x*y*v
 return z

def target():
 z=[0]*(N**3)
 for i in range(5):
  for j in range(5):
   for k in range(5): z[((i*5+j)*N+j*5+k)*N+k*5+i]=1
 return z

def jacobian(t):
 # Each row is a bitset over 75*r coefficient variables. rhs is stored at bit 0.
 rows=[0]*(N**3)
 for s,(a,b,c) in enumerate(t):
  aa=[i for i,x in enumerate(a) if x&1];bb=[j for j,x in enumerate(b) if x&1];cc=[k for k,x in enumerate(c) if x&1]
  for i in range(N):
   bit=1<<(1+s*75+i)
   for j in bb:
    for k in cc: rows[(i*N+j)*N+k]^=bit
  for j in range(N):
   bit=1<<(1+s*75+N+j)
   for i in aa:
    for k in cc: rows[(i*N+j)*N+k]^=bit
  for k in range(N):
   bit=1<<(1+s*75+2*N+k)
   for i in aa:
    for j in bb: rows[(i*N+j)*N+k]^=bit
 return rows

def solve(rows,rhs):
 piv={}
 for a,b in zip(rows,rhs):
  row=a|b
  while row>1:
   p=row.bit_length()-1
   if p not in piv: piv[p]=row;break
   row^=piv[p]
  if row==1: return None,len(piv)
 x=0
 for p,row in sorted(piv.items()):
  if (row&1)^((row&x).bit_count()&1): x|=1<<p
 return x,len(piv)

def export(t,path):
 terms=[]
 for a,b,d in t:
  mats=[[[m[5*i+j] for j in range(5)] for i in range(5)] for m in (a,b,d)]
  mats[2]=list(map(list,zip(*mats[2])))
  terms.append(dict(zip(('a','b','c'),mats)))
 pathlib.Path(path).write_text(json.dumps(dict(terms=terms)))

def main():
 t=readmask(sys.argv[1]);want=target();z=tensor(t)
 assert all((x-y)%2==0 for x,y in zip(z,want)), 'input fails GF(2) identity'
 rows=jacobian(t);mod=2;start=time.monotonic()
 for level in range(1,int(sys.argv[3]) if len(sys.argv)>3 else 8):
  rhs=[((y-x)//mod)&1 for x,y in zip(z,want)]
  delta,rank=solve(rows,rhs)
  print(f'level={level} modulus={mod} jacobian_rank={rank} elapsed={time.monotonic()-start:.3f} consistent={delta is not None}',flush=True)
  if delta is None: return 1
  for s,term in enumerate(t):
   for k,m in enumerate(term):
    for i in range(N): m[i]+=mod*((delta>>(1+s*75+k*N+i))&1)
  mod*=2;z=tensor(t)
  assert all((x-y)%mod==0 for x,y in zip(z,want))
  signed=[[[v-mod if v>=mod//2 else v for v in m] for m in term] for term in t]
  if tensor(signed)==want:
   export(signed,sys.argv[2]);print(f'EXACT_INTEGER_IDENTITY rank={len(t)} modulus={mod}',flush=True);return 0
 print('No exact integer identity on the zero-free-variable lift path.',flush=True);return 1
if __name__=='__main__': sys.exit(main())
