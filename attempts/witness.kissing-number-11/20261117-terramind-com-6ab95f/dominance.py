"""Memory-bounded conflict graph, safe domination, then a capped-size MILP.

In an independent-set graph, a nonprotected v can be removed if a retained u
has closed N[u] contained in closed N[v]. Replacement of v by u preserves size.
Only candidate tests with floating separation >1e-12 become graph edges.
The resulting bound is a numerical solver result, not a formal certificate.
"""
import datetime
import json
import time
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
root=Path(__file__).resolve().parent;start=time.monotonic()
launch=datetime.datetime.fromisoformat((root/'launch-utc.txt').read_text().strip().replace('Z','+00:00')).timestamp()
rows=np.load(root/'integer-pool-all.npz')['vectors'];n=len(rows)
x=(rows[:,::2]+np.sqrt(2)*rows[:,1::2])/6
raw=np.array(json.loads((root/'baseline.json').read_text())['vectors'])
back=raw[np.all(raw[:,1::2]==0,axis=1)]
protected={tuple(r) for r in raw[np.any(raw[:,1::2]!=0,axis=1)]}
old={tuple(r) for r in np.load(root/'expanded-pool.npz')['vectors']}
protected_indices={i for i,r in enumerate(rows) if tuple(r) in protected}
old_indices=[i for i,r in enumerate(rows) if tuple(r) in old]
assert len(protected_indices)==108
print('START n',n,'block_rows=128 max_MILP_vertices=5000 max_MILP_seconds=300 threads=1',flush=True)
adj=np.empty((n,n),dtype=np.bool_)
for a in range(0,n,128):
    adj[a:a+128]=(x[a:a+128]@x.T)>.5+1e-12
np.fill_diagonal(adj,True)
assert adj[np.ix_(sorted(protected_indices),sorted(protected_indices))].sum()==108
degrees=adj.sum(axis=1)
old_indices.sort(key=lambda i:(degrees[i],i))
bits=[int.from_bytes(np.packbits(row,bitorder='little').tobytes(),'little') for row in adj]
active=(1<<n)-1;deleted=[];checks=0
print('GRAPH built elapsed',time.monotonic()-start,'closed_edges',(int(degrees.sum())+n)//2,flush=True)
# Limit each vertex to 128 low-degree old neighbors. Missing a dominator costs
# reduction strength, never correctness of the retained induced problem.
for v in sorted(range(n),key=lambda i:(-degrees[i],-i)):
    if v in protected_indices:continue
    bv=bits[v]&active;attempts=0
    for u in old_indices:
        if degrees[u]>degrees[v]:break
        if u==v or not ((active>>u)&1) or not adj[v,u]:continue
        if degrees[u]==degrees[v] and u>v:continue
        checks+=1;attempts+=1
        if ((bits[u]&active)&~bv)==0:
            active&=~(1<<v);deleted.append((v,u));break
        if attempts>=128:break
keep=[i for i in range(n) if (active>>i)&1]
np.savez(root/'dominance-reduced-pool.npz',vectors=rows[keep])
(root/'dominance-map.json').write_text(json.dumps({'deleted':deleted,'kept':keep}))
print('REDUCED',len(keep),'deleted',len(deleted),'checks',checks,'elapsed',time.monotonic()-start,flush=True)
if len(keep)>5000:
    print('END: reduced model still too large; no MILP attempted',flush=True)
    raise SystemExit(0)
small=adj[np.ix_(keep,keep)];np.fill_diagonal(small,False)
edges=np.transpose(np.nonzero(np.triu(small,1)))
del adj,bits,small
A=coo_matrix((np.ones(2*len(edges)),(np.repeat(np.arange(len(edges)),2),edges.ravel())),shape=(len(edges),len(keep))).tocsr()
remaining=min(300.,launch+7200-time.time())
if remaining<=0:raise SystemExit('shared deadline reached')
result=milp(-np.ones(len(keep)),integrality=np.ones(len(keep)),bounds=Bounds(0,1),
    constraints=LinearConstraint(A,-np.inf,1),options={'time_limit':remaining,'threads':1,'mip_rel_gap':0,'disp':True})
print('MILP',str(result),flush=True)
if result.x is not None:
    selected=rows[np.array(keep)[result.x>.5]]
    candidate=np.vstack([back,selected])
    (root/'dominance-best.json').write_text(json.dumps({'vectors':candidate.tolist()}))
    print('VALUE',len(candidate),'elapsed',time.monotonic()-start,flush=True)
print('END',flush=True)
