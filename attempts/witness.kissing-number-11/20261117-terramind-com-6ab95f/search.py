"""Reproducible local search. Run with -I and BLAS thread counts set to one.

Data is parsed only as JSON; no upstream source code is executed.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np
import scipy
from scipy.optimize import minimize, linprog

def sign(a, b):
    if b == 0: return (a > 0) - (a < 0)
    if a == 0: return (b > 0) - (b < 0)
    if a > 0 and b > 0: return 1
    if a < 0 and b < 0: return -1
    return 1 if ((a*a > 2*b*b) == (a > 0)) else -1

def exact_valid(rows):
    """Python integer implementation of the verifier's common-radius rule."""
    if not rows or len(rows) > 2000: return False
    if any(len(v) != 22 or any(type(x) is not int for x in v) for v in rows): return False
    if len({tuple(v) for v in rows}) != len(rows): return False
    if any(not any(v) for v in rows): return False
    def dot(v, w):
        return (sum(v[d]*w[d]+2*v[d+1]*w[d+1] for d in range(0,22,2)),
                sum(v[d]*w[d+1]+v[d+1]*w[d] for d in range(0,22,2)))
    norms = [dot(v,v) for v in rows]
    radius = norms[0]
    for n in norms:
        if sign(n[0]-radius[0], n[1]-radius[1]) > 0: radius = n
    for i, v in enumerate(rows):
        for j in range(i):
            a,b = dot(v, rows[j]); n,m = norms[i]; o,p = norms[j]
            if sign(n+o-2*a-radius[0],m+p-2*b-radius[1]) < 0: return False
    return True

def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)

def maxdot(x):
    g = x@x.T
    np.fill_diagonal(g, -np.inf)
    return float(g.max())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--scratch',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=7200)
    parser.add_argument('--seed',type=int,default=17112026)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args(); root=args.scratch.resolve()
    raw=json.loads((root/'baseline.json').read_text())['vectors']
    assert exact_valid(raw), 'baseline rejected by exact inner checker'
    broken=[v[:] for v in raw]; broken[-1]=broken[0][:]
    assert not exact_valid(broken), 'duplicate accepted by exact inner checker'
    (root/'broken.json').write_text(json.dumps({'vectors':broken}))
    v=np.array(raw,dtype=float); base=(v[:,::2]+np.sqrt(2)*v[:,1::2])/6
    assert abs(np.linalg.norm(base,axis=1)-1).max()<1e-12
    assert maxdot(base)<.5+1e-12
    bad=base.copy(); bad[-1]=bad[0]
    assert maxdot(bad)>.99
    print('SELF_TEST exact baseline ACCEPT; duplicate REJECT; numerical baseline ACCEPT; duplicate REJECT',flush=True)
    if args.self_test: return
    started=time.monotonic(); deadline=started+args.seconds
    rng=np.random.default_rng(args.seed)
    backbone=base[np.all(v[:,1::2]==0,axis=1)]
    print(json.dumps({'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'seconds':args.seconds,'seed':args.seed,'numpy':np.__version__,'scipy':scipy.__version__,
        'baseline_sha256':hashlib.sha256((root/'baseline.json').read_bytes()).hexdigest(),
        'backbone':len(backbone),'extension':len(base)-len(backbone),
        'threads':{k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']},
        'plan':'1/6 hole search; 7/12 exchanges k=1..6; remaining full relaxation'}),flush=True)
    best=float('inf'); holes=[]; best_hole=None; counts={'hole':0,'lp':0,'exchange':0,'full':0}
    lastlog=started
    def progress(stage,force=False):
        nonlocal lastlog
        if force or time.monotonic()-lastlog>=20:
            print(json.dumps({'elapsed':time.monotonic()-started,'stage':stage,'best_max_dot_605':best,
                'best_min_angle_degrees':float(np.degrees(np.arccos(np.clip(best,-1,1)))) if best<=1 else None,
                'counts':counts}),flush=True); lastlog=time.monotonic()
    def record(x,stage):
        nonlocal best
        x=unit(x); score=maxdot(x)
        if score < best-1e-12:
            best=score; np.savez(root/'best605.npz',vectors=x,score=best)
            print(json.dumps({'new_best':best,'elapsed':time.monotonic()-started,'stage':stage}),flush=True)
        candidate_rows=None
        if score < .5+1e-9:
            # Recover contact configurations in the baseline's quadratic field.
            alphabet=[(p,q) for p in range(-12,13) for q in range(-12,13)]
            alphabet.sort(key=lambda a:abs(a[0])+abs(a[1]))
            values=np.array([(p+q*np.sqrt(2))/6 for p,q in alphabet])
            indices=np.abs(x[...,None]-values).argmin(axis=-1)
            if np.abs(x-values[indices]).max()<1e-7:
                candidate_rows=np.array([alphabet[j] for j in indices.ravel()]).reshape(605,22).tolist()
        if score < .5-1e-9:
            # Strict slack permits a safe exact integer candidate; repo decides.
            rounded=np.rint(x*10**12).astype(np.int64)
            pairs=np.zeros((605,22),dtype=np.int64); pairs[:,::2]=rounded
            candidate_rows=pairs.tolist()
        if candidate_rows is not None:
            out=root/'candidate605.json'; out.write_text(json.dumps({'vectors':candidate_rows}))
            command=[str(Path.home()/'.bun/bin/bun'),'frontier','diagnose',str(out),'--problem','witness.kissing-number-11']
            result=subprocess.run(command,capture_output=True,text=True)
            (root/'candidate605-diagnose.log').write_text(result.stdout+result.stderr)
            print('EXACT_CANDIDATE',result.returncode,result.stdout,result.stderr,flush=True)
            if exact_valid(candidate_rows) and result.returncode==0:
                raise RuntimeError('SUCCESS: candidate605.json passed exact checker and repository diagnose; inspect log')
        return score
    def hole_objective(z, fixed):
        u=unit(z); dots=fixed@u
        # Log-sum-exp smooth max, then SLSQP epigraph polish below.
        beta=160; top=dots.max(); w=np.exp(beta*(dots-top)); total=w.sum()
        grad=(w@fixed)/total
        return top+np.log(total)/beta,(grad-u*np.dot(grad,u))/np.linalg.norm(z)
    def polish_hole(z,fixed):
        u=unit(z); initial=np.r_[u,(fixed@u).max()]
        result=minimize(lambda a:a[-1],initial,jac=lambda a:np.r_[np.zeros(11),1.],method='SLSQP',
            constraints=[{'type':'ineq','fun':lambda a:a[-1]-fixed@a[:11],
                          'jac':lambda a:np.c_[-fixed,np.ones(len(fixed))]},
                         {'type':'eq','fun':lambda a:np.dot(a[:11],a[:11])-1,
                          'jac':lambda a:np.r_[2*a[:11],0]}],
            options={'maxiter':100,'ftol':1e-12})
        return unit(result.x[:11])
    # Random directions plus LP vertices of the polar of the 496-point backbone.
    while time.monotonic()<started+args.seconds/6:
        i=counts['hole']; z=unit(rng.normal(size=11))
        if i%3==0:
            lp=linprog(-z,A_ub=backbone,b_ub=np.full(len(backbone),.5),bounds=[(None,None)]*11,
                       method='highs',options={'threads':1})
            counts['lp']+=1
            if lp.success: z=unit(lp.x)
        elif i%3==1:
            z=unit(base[rng.integers(604)]+rng.normal(size=11)*.25)
        r=minimize(hole_objective,z,args=(base,),jac=True,method='L-BFGS-B',
                   options={'maxiter':150,'ftol':1e-13,'gtol':1e-10})
        z=polish_hole(r.x,base); score=record(np.vstack([base,z]),'hole')
        holes.append((score,z.copy()))
        holes.sort(key=lambda h:h[0]); holes=holes[:256]
        if best_hole is None or score<best_hole[0]: best_hole=(score,z.copy())
        counts['hole']+=1; progress('hole')
    np.savez(root/'holes.npz',directions=np.array([h[1] for h in holes]),scores=np.array([h[0] for h in holes]))
    # Keep 604-k points fixed; move k+1 nearby directions to remove overlap.
    def local_loss(z,fixed,m,threshold=.5):
        rawz=z.reshape(m,11); norms=np.linalg.norm(rawz,axis=1,keepdims=True); x=rawz/norms
        fixed_overlap=np.maximum(x@fixed.T-threshold,0)
        pair_overlap=np.maximum(x@x.T-threshold,0); np.fill_diagonal(pair_overlap,0)
        grad=2*fixed_overlap@fixed+2*pair_overlap@x
        val=np.sum(fixed_overlap**2)+np.sum(pair_overlap**2)/2
        grad=(grad-x*np.sum(grad*x,axis=1,keepdims=True))/norms
        return float(val),grad.ravel()
    while time.monotonic()<started+args.seconds*.75:
        i=counts['exchange']; k=1+i%6
        direction=holes[int(rng.integers(min(64,len(holes))))][1]
        nearest=np.argsort(base@direction)[::-1]
        if i%4==0:
            # Occasionally replace a connected neighborhood around one tight blocker.
            center=nearest[0]; near=np.argsort(base@base[center])[::-1]
            removed=np.unique(np.r_[center,near[1:k]])
        else: removed=nearest[:k]
        fixed=np.delete(base,removed,axis=0)
        movable=np.vstack([base[removed],direction])
        movable=unit(movable+rng.normal(size=movable.shape)*[0,.015,.05,.15][i%4])
        result=minimize(local_loss,movable.ravel(),args=(fixed,k+1),jac=True,method='L-BFGS-B',
                        options={'maxiter':1000,'ftol':1e-15,'gtol':1e-11,'maxls':40})
        final=unit(result.x.reshape(k+1,11)); record(np.vstack([fixed,final]),'exchange')
        counts['exchange']+=1; progress('exchange')
    # Broaden to moving all 605, seeded by best local exchanges or new hole insertions.
    while time.monotonic()<deadline:
        i=counts['full']
        if i%3==0: x=np.load(root/'best605.npz')['vectors']
        else:
            h=holes[int(rng.integers(min(64,len(holes))))][1]
            x=np.vstack([base,h])
        x=unit(x+rng.normal(size=x.shape)*[0,.003,.01,.03][i%4])
        def full_loss(z):
            if time.monotonic()>=deadline: raise TimeoutError('search deadline')
            rawz=z.reshape(605,11); norms=np.linalg.norm(rawz,axis=1,keepdims=True); y=rawz/norms
            overlap=np.maximum(y@y.T-.5,0); np.fill_diagonal(overlap,0)
            grad=2*overlap@y
            grad=(grad-y*np.sum(grad*y,axis=1,keepdims=True))/norms
            return float(np.sum(overlap**2)/2),grad.ravel()
        try:
            result=minimize(full_loss,x.ravel(),jac=True,method='L-BFGS-B',
                callback=lambda z:progress('full'),
                options={'maxiter':2500,'ftol':1e-16,'gtol':1e-10,'maxls':30,'maxcor':10})
            record(result.x.reshape(605,11),'full')
        except TimeoutError:
            break
        counts['full']+=1; progress('full')
    progress('finished',True)
    summary={'elapsed_seconds':time.monotonic()-started,'best_max_dot_605':best,
        'best_min_angle_degrees':float(np.degrees(np.arccos(best))), 'counts':counts,
        'status':'budget exhausted; no verified improvement'}
    (root/'summary.json').write_text(json.dumps(summary,indent=2))
    print('END',json.dumps(summary),flush=True)

if __name__=='__main__': main()
