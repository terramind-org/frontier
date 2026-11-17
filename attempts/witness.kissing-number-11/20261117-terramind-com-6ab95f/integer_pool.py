"""Add selected integer norm-36 types to the earlier quadratic-field pool."""
import itertools as it
import json
import time
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
root=Path(__file__).resolve().parent;started=time.monotonic()
raw=np.array(json.loads((root/'baseline.json').read_text())['vectors'])
back=raw[np.all(raw[:,1::2]==0,axis=1)];b=back[:,::2]/6
pool={tuple(r) for r in np.load(root/'expanded-pool.npz')['vectors']}
axes={int(np.flatnonzero(r[::2])[0]) for r in back if np.count_nonzero(r)==1}
buffer=[];tested=0
def flush():
    global tested
    if not buffer:return
    a=np.array(buffer,dtype=np.int64);x=a[:,::2]/6
    ok=(x@b.T).max(axis=1)<=.5+1e-12
    pool.update(tuple(r) for r in a[ok]);tested+=len(buffer);buffer.clear()
def generate(groups):
    def recur(remaining,g,chosen):
        if not g:
            for signs in it.product([-1,1],repeat=len(chosen)):
                row=[0]*22
                for (j,m),s in zip(chosen,signs):row[2*j]=m*s
                buffer.append(row)
                if len(buffer)>=512:flush()
            return
        mag,count=g[0]
        for coords in it.combinations([j for j in remaining if mag<=3 or j not in axes],count):
            recur(tuple(j for j in remaining if j not in coords),g[1:],chosen+[(j,mag) for j in coords])
    recur(tuple(range(11)),groups,[])
patterns=[[(6,1)],[(5,1),(3,1),(1,2)],[(5,1),(2,2),(1,3)],[(4,2),(2,1)],
          [(4,2),(1,4)],[(4,1),(3,2),(1,2)],[(4,1),(2,5)],[(3,4)]]
print('START integer-pool deterministic; MILP threads=1 time_limit=300',flush=True)
for p in patterns:
    generate(p);flush()
    print(json.dumps({'pattern':p,'tested':tested,'pool':len(pool),'elapsed':time.monotonic()-started}),flush=True)
rows=np.array(sorted(pool));x=(rows[:,::2]+np.sqrt(2)*rows[:,1::2])/6
assert np.max(abs(np.sum(x*x,axis=1)-1))<1e-12
np.savez(root/'integer-pool-all.npz',vectors=rows)
# Added after the initial run was stopped: never form the 19,034-square Gram
# matrix again. Optimize a seeded 5,000-direction subset containing the entire
# earlier pool. This is a subset search, not a bound on the enlarged pool.
if len(rows)>5000:
    seed=17112028; rng=np.random.default_rng(seed)
    old={tuple(r) for r in np.load(root/'expanded-pool.npz')['vectors']}
    keep=np.array([i for i,r in enumerate(rows) if tuple(r) in old])
    new=np.array([i for i,r in enumerate(rows) if tuple(r) not in old])
    selected=np.r_[keep,rng.choice(new,5000-len(keep),replace=False)]
    rows=rows[selected];x=x[selected]
    print('RESOURCE_GUARD seeded subset',len(rows),'seed',seed,flush=True)
edges=np.transpose(np.nonzero(np.triu(x@x.T>.5+1e-12,1)))
A=coo_matrix((np.ones(2*len(edges)),(np.repeat(np.arange(len(edges)),2),edges.ravel())),shape=(len(edges),len(rows))).tocsr()
print('MODEL',len(rows),'vertices',len(edges),'edges',flush=True)
r=milp(-np.ones(len(rows)),integrality=np.ones(len(rows)),bounds=Bounds(0,1),
    constraints=LinearConstraint(A,-np.inf,1),options={'threads':1,'time_limit':300,'mip_rel_gap':0,'disp':True})
print('MILP',str(r),flush=True)
if r.x is not None:
    result=np.vstack([back,rows[r.x>.5]])
    (root/'integer-pool-best.json').write_text(json.dumps({'vectors':result.tolist()}))
    print('VALUE',len(result),'elapsed',time.monotonic()-started,flush=True)
print('END',flush=True)
