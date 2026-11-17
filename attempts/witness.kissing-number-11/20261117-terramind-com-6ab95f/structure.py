"""Enumerate the coordinate types present in the 604, then an exact-size MILP.
Not an exhaustive enumeration of Z[sqrt(2)] directions or backbone deep holes.
"""
import itertools as it
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--expanded',action='store_true')
args=parser.parse_args()
prefix='expanded' if args.expanded else 'structured'
start=time.monotonic()
raw=np.array(json.loads((root/'baseline.json').read_text())['vectors'],dtype=np.int64)
p,q=raw[:,::2],raw[:,1::2]
back=raw[np.all(q==0,axis=1)]
extension=raw[np.any(q!=0,axis=1)]
base=(back[:,::2]+np.sqrt(2)*back[:,1::2])/6
accepted={tuple(r) for r in extension}
tested=0
print('START seed=none deterministic coordinate enumeration; MILP time_limit=900 threads=1',flush=True)
buffer=[]
def flush():
    global tested
    if not buffer:return
    a=np.array(buffer,dtype=np.int64)
    f=(a[:,::2]+np.sqrt(2)*a[:,1::2])/6
    valid=(f@base.T).max(axis=1)<=.5+1e-12
    accepted.update(tuple(r) for r in a[valid]); tested+=len(buffer);buffer.clear()
def add(pairs):
    buffer.append(pairs)
    if len(buffer)>=512:flush()
for pc in it.combinations(range(11),2):
    for qc in it.combinations([j for j in range(11) if j not in pc],3):
        for small in qc:
            for signs in it.product([-1,1],repeat=5):
                r=[0]*22
                for j,s in zip(pc,signs[:2]):r[2*j]=3*s
                for j,s in zip(qc,signs[2:]):r[2*j+1]=(1 if j==small else 2)*s
                add(r)
for qc in it.combinations(range(11),3):
    for big in qc:
        for signs in it.product([-1,1],repeat=3):
            r=[0]*22
            for j,s in zip(qc,signs):r[2*j+1]=(4 if j==big else 1)*s
            add(r)
for qc in it.combinations(range(11),2):
    for signs in it.product([-1,1],repeat=2):
        r=[0]*22
        for j,s in zip(qc,signs):r[2*j+1]=3*s
        add(r)
if args.expanded:
    # All pure-q integer shells sum(q_j^2)=18, and all disjoint p_j=+/-3
    # support-two shells with sum(q_j^2)=9. Each has norm squared 36.
    # Axis pruning is exact: a backbone +/-6e_j bounds |q_j| <= 2.
    axes={int(np.flatnonzero(r[::2])[0]) for r in back if np.count_nonzero(r)==1}
    def generate(pc,groups):
        available=tuple(j for j in range(11) if j not in pc)
        def recur(remaining,g,chosen):
            if not g:
                coords=tuple(pc)+tuple(j for j,m in chosen)
                mags=(3,)*len(pc)+tuple(m for j,m in chosen)
                for signs in it.product([-1,1],repeat=len(coords)):
                    r=[0]*22
                    for i,(j,m,s) in enumerate(zip(coords,mags,signs)):
                        r[2*j+(i>=len(pc))]=m*s
                    add(r)
                return
            mag,count=g[0]
            choices=[j for j in remaining if mag<3 or j not in axes]
            for selected in it.combinations(choices,count):
                recur(tuple(j for j in remaining if j not in selected),g[1:],chosen+[(j,mag) for j in selected])
        recur(available,groups,[])
    for pattern in [[(3,1),(2,2),(1,1)],[(3,1),(2,1),(1,5)],[(3,1),(1,9)],[(2,4),(1,2)],[(2,3),(1,6)]]:
        generate((),pattern);flush()
        print('EXPANDED q-only',pattern,'tested',tested,'pool',len(accepted),'elapsed',time.monotonic()-start,flush=True)
    for pattern in [[(3,1)],[(2,1),(1,5)],[(1,9)]]:
        for pc in it.combinations(range(11),2):generate(pc,pattern)
        flush()
        print('EXPANDED p-two',pattern,'tested',tested,'pool',len(accepted),'elapsed',time.monotonic()-start,flush=True)
flush()
pool=np.array(sorted(accepted),dtype=np.int64)
x=(pool[:,::2]+np.sqrt(2)*pool[:,1::2])/6
np.savez(root/(prefix+'-pool.npz'),vectors=pool)
assert np.max(abs(np.sum(x*x,axis=1)-1))<1e-12
index={tuple(r):i for i,r in enumerate(pool)}
original=[index[tuple(r)] for r in extension]
g=x@x.T
assert np.max((x[original]@x[original].T)-np.eye(108)*2)<=.5+1e-12
edges=np.transpose(np.nonzero(np.triu(g>.5+1e-12,1)))
print(json.dumps({'tested':tested,'feasible_pool':len(pool),'conflict_edges':len(edges),'baseline_extension_recovered':len(original),'elapsed':time.monotonic()-start}),flush=True)
A=coo_matrix((np.ones(2*len(edges)),(np.repeat(np.arange(len(edges)),2),edges.ravel())),shape=(len(edges),len(pool))).tocsr()
result=milp(-np.ones(len(pool)),integrality=np.ones(len(pool)),bounds=Bounds(0,1),
    constraints=LinearConstraint(A,-np.inf,1),
    options={'time_limit':900,'threads':1,'mip_rel_gap':0,'disp':True})
print('MILP',str(result),flush=True)
if result.x is not None:
    chosen=pool[result.x>.5]
    witness=np.vstack([back,chosen])
    (root/(prefix+'-best.json')).write_text(json.dumps({'vectors':witness.tolist()}))
    print('VALUE',len(witness),'elapsed',time.monotonic()-start,flush=True)
print('END',flush=True)
