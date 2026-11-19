"""Audit the conditional lift's algebra; no rank improvement is claimed."""
import copy, importlib.util, pathlib, random, subprocess, sys
root=pathlib.Path('.terramind/scratch/matmul5')
spec=importlib.util.spec_from_file_location('lift',root/'lift.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
x,r=m.solve([2,4],[1,0]);assert x==2 and r==2
x,r=m.solve([2,2],[1,0]);assert x is None
base=m.readmask(root/'baseline.mask');rows=m.jacobian(base);z=m.tensor(base)
rng=random.Random(431);delta=rng.getrandbits(75*len(base))<<1
changed=copy.deepcopy(base)
for s,t in enumerate(changed):
 for k,a in enumerate(t):
  for i in range(25):a[i]+=2*((delta>>(1+s*75+k*25+i))&1)
z2=m.tensor(changed)
assert all((((b-a)//2)&1)==((row&delta).bit_count()&1) for a,b,row in zip(z,z2,rows))
# Complete positive path: the integer schoolbook tensor has zero lift residual.
terms=[]
for i in range(5):
 for j in range(5):
  for k in range(5):terms.append((1<<(5*i+j),1<<(5*j+k),1<<(5*k+i)))
p=root/'lift-schoolbook.mask';p.write_text('125\n'+'\n'.join(' '.join(map(str,t)) for t in terms)+'\n')
r=subprocess.run([sys.executable,'-I',str(root/'lift.py'),str(p),str(root/'lift-schoolbook.json'),'2'],check=True,capture_output=True,text=True)
print(r.stdout,end='')
print('LIFT SELFTEST: linear solve ACCEPT; inconsistent solve REJECT; full Jacobian directional identity ACCEPT; schoolbook integer positive path ACCEPT')
