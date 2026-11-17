"""Exact CEGAR window synthesis, sequential exactly-one, unrestricted legal pairs.
CLI: window.py network.json n offset width target seconds seed output.json
All SAT candidates are checked on every binary input. No duplicate-gate pruning.
"""
import json, sys, time, random, datetime, pathlib
import numpy as np
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType

def emit(**x):
    print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**x)),flush=True)

def inputs(n):
    return ((np.arange(1<<n,dtype=np.uint32)[:,None]>>np.arange(n,dtype=np.uint32))&1).astype(np.uint8)

def apply(v,gates):
    v=v.copy()
    for i,j in gates:
        a,b=v[:,i].copy(),v[:,j].copy()
        v[:,i],v[:,j]=a&b,a|b
    return v

def failures(v):
    return np.flatnonzero((v[:,:-1]>v[:,1:]).any(axis=1))

def solve(gates,n,s,w,target,seconds,seed,output):
    start=time.monotonic(); end=start+seconds
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    pre,suf=gates[:s],gates[s+w:]
    P,multiplicities=np.unique(apply(inputs(n),pre),axis=0,return_counts=True)
    solver=Cadical153(); nv=0
    def new():
        nonlocal nv
        nv+=1; return nv
    choices=[[new() for _ in pairs] for _ in range(target)]
    for row in choices:
        cnf=CardEnc.equals(row,bound=1,top_id=nv,encoding=EncType.seqcounter)
        nv=cnf.nv; solver.append_formula(cnf.clauses)
    unt=[[new() for _ in range(n)] for _ in range(target)]
    for t in range(target):
        for wi in range(n):
            touch=[choices[t][k] for k,(i,j) in enumerate(pairs) if wi==i or wi==j]
            solver.add_clause([unt[t][wi]]+touch)
            for g in touch: solver.add_clause([-unt[t][wi],-g])
    added=set(); candidate_keys=set(); rounds=0;best_failure_count=None
    def add_vector(idx):
        if idx in added:return
        added.add(idx); cur=[new() for _ in range(n)]
        for wi in range(n):solver.add_clause([cur[wi] if P[idx,wi] else -cur[wi]])
        for t in range(target):
            nxt=[new() for _ in range(n)]
            for wi in range(n):
                u,a,b=unt[t][wi],cur[wi],nxt[wi]
                solver.add_clause([-u,-a,b]);solver.add_clause([-u,a,-b])
            for k,(i,j) in enumerate(pairs):
                g=choices[t][k];a,b,c,d=cur[i],cur[j],nxt[i],nxt[j]
                for clause in [[-g,a,-c],[-g,b,-c],[-g,-a,-b,c],[-g,-a,d],[-g,-b,d],[-g,a,b,-d]]:solver.add_clause(clause)
            cur=nxt
        for i,j in suf:
            a,b=cur[i],cur[j];lo,hi=new(),new()
            for clause in [[-lo,a],[-lo,b],[lo,-a,-b],[-hi,a,b],[hi,-a],[hi,-b]]:solver.add_clause(clause)
            cur[i],cur[j]=lo,hi
        for wi in range(n-1):solver.add_clause([-cur[wi],cur[wi+1]])
    rng=random.Random(seed); ids=list(range(len(P)));rng.shuffle(ids)
    bad0=set(map(int,failures(apply(P,suf))))
    seeds=[i for i in ids if i in bad0][:32]+ids[:20]
    for idx in seeds:add_vector(idx)
    emit(event='encoded',version='sequential-weighted-v2',n=n,s=s,w=w,target=target,seed=seed,prefix_vectors=len(P),vectors=len(added),vars=nv,clauses=solver.nof_clauses(),stats=solver.accum_stats())
    status='timeout'; full=None
    while time.monotonic()<end:
        solver.conf_budget(10000)
        answer=solver.solve_limited()
        emit(event='solve',answer=answer,round=rounds,secs=round(time.monotonic()-start,3),stats=solver.accum_stats(),vectors=len(added),distinct_candidates=len(candidate_keys))
        if answer is None:continue
        if answer is False:status='UNSAT';break
        rounds+=1; model=set(x for x in solver.get_model() if x>0)
        win=[pairs[k] for t in range(target) for k in range(len(pairs)) if choices[t][k] in model]
        key=tuple(win);candidate_keys.add(key)
        bad=failures(apply(P,win+suf))
        count=int(multiplicities[bad].sum())
        if best_failure_count is None or count<best_failure_count:
            best_failure_count=count
            pathlib.Path(output+'.near.json').write_text(json.dumps({'comparators':pre+win+suf}))
            emit(event='best_candidate',failing_inputs=count,total_gates=len(pre)+len(win)+len(suf),round=rounds)
        if len(bad)==0:
            full=pre+win+suf
            assert len(failures(apply(inputs(n),full)))==0
            pathlib.Path(output).write_text(json.dumps({'comparators':full}))
            status='SAT';break
        bad=list(map(int,bad));rng.shuffle(bad)
        for idx in bad[:24]:add_vector(idx)
    emit(event='result',status=status,n=n,s=s,w=w,target=target,seed=seed,best_failure_count=best_failure_count,secs=round(time.monotonic()-start,3),vectors=len(added),rounds=rounds,stats=solver.accum_stats(),distinct_candidates=len(candidate_keys),vars=nv,clauses=solver.nof_clauses())
    solver.delete();return status,full

if __name__=='__main__':
    f,n,s,w,t,sec,seed,out=sys.argv[1:]
    solve([tuple(x) for x in json.load(open(f))['comparators']],int(n),int(s),int(w),int(t),float(sec),int(seed),out)
