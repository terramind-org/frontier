"""Exact F3 cap exchanges and separation-based symmetry models; own implementation."""
import os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys, json, time, hashlib, itertools, pathlib, datetime, resource
import numpy as np
import pynauty
from ortools.sat.python import cp_model

ROOT=pathlib.Path(__file__).resolve().parent

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(event, **kw):
    print(json.dumps(dict(utc=utc(),event=event,**kw)),flush=True)
def digest(a): return hashlib.sha256(np.asarray(sorted(a),dtype='<i2').tobytes()).hexdigest()

class Space:
    def __init__(self,n):
        self.n=n; self.m=3**n
        self.p=3**np.arange(n-1,-1,-1,dtype=np.int32)
        self.v=np.array(list(itertools.product(range(3),repeat=n)),dtype=np.int8)
        self.t=np.empty((self.m,self.m),dtype=np.int16)
        for a in range(self.m): self.t[a]=((-self.v[a]-self.v)%3)@self.p
    def load(self,f): return np.asarray(json.load(open(f))['points'],dtype=np.int32)@self.p
    def save(self,f,a):
        pathlib.Path(f).parent.mkdir(parents=True,exist_ok=True)
        f=pathlib.Path(f); tmp=f.with_name(f.name+f'.{os.getpid()}.tmp')
        tmp.write_text(json.dumps({'points':self.v[sorted(a)].tolist()})); tmp.replace(f)
    def blocks(self,a):
        a=np.asarray(sorted(a),dtype=np.int32)
        i,j=np.triu_indices(len(a),1)
        return np.bincount(self.t[a[i],a[j]],minlength=self.m)
    def valid(self,a):
        a=list(a)
        return len(set(a))==len(a) and not self.blocks(a)[a].any()
    def canonical(self,a):
        # Colored incidence graph: zero fixed, values 1 and 2 interchangeable per coordinate.
        a=np.asarray(sorted(a)); k=len(a); adj={i:[] for i in range(k+4*self.n)}
        for d in range(self.n):
            c=k+4*d
            for t in range(3):
                u=c+1+t; adj[c].append(u); adj[u].append(c)
            for i,x in enumerate(self.v[a,d]):
                u=c+1+int(x); adj[i].append(u); adj[u].append(i)
        colors=[set(range(k)),{k+4*d for d in range(self.n)},
                {k+4*d+1 for d in range(self.n)},
                {k+4*d+t for d in range(self.n) for t in (2,3)}]
        g=pynauty.Graph(k+4*self.n,adjacency_dict=adj,vertex_coloring=colors)
        return hashlib.sha256(pynauty.certificate(g)).hexdigest()
    def freed(self,kept):
        blocked=self.blocks(kept)>0; blocked[list(kept)]=True
        return np.flatnonzero(~blocked)
    def exchange(self,a,r,limit,seed,exclude=True,tabu=(),force=()):
        start=time.monotonic(); a=set(a); r=set(r); kept=a-r
        f=self.freed(kept); pos=np.full(self.m,-1,dtype=np.int32); pos[f]=np.arange(len(f))
        model=cp_model.CpModel(); x=[model.new_bool_var(str(int(i))) for i in f]
        in_k=np.zeros(self.m,bool); in_k[list(kept)]=True
        pairs=triples=0
        for i,u in enumerate(f):
            vv=f[i+1:]; tt=self.t[u,vv]
            for jj in np.flatnonzero(in_k[tt]):
                model.add_at_most_one(x[i],x[i+1+int(jj)]); pairs+=1
            for jj in np.flatnonzero((pos[tt]>np.arange(i+1,len(f)))):
                j=i+1+int(jj); h=int(pos[tt[jj]])
                model.add_bool_or([x[i].Not(),x[j].Not(),x[h].Not()]); triples+=1
        if exclude and r: model.add(sum(x[int(pos[u])] for u in r)<=len(r)-1)
        # Only exact labelled caps compatible with this kept set give a no-good.
        for old in tabu:
            if kept<=old and len(old)==len(a):
                q=old-kept
                if all(pos[u]>=0 for u in q): model.add(sum(x[int(pos[u])] for u in q)<=len(q)-1)
        for u in force:
            if pos[u]>=0: model.add(x[int(pos[u])]==1)
        for u in r: model.add_hint(x[int(pos[u])],1)
        model.maximize(sum(x))
        build=time.monotonic()-start
        solver=cp_model.CpSolver(); solver.parameters.num_search_workers=1
        solver.parameters.max_time_in_seconds=max(.01,limit-build)
        solver.parameters.random_seed=seed
        status=solver.solve(model)
        out=kept|{int(f[i]) for i,v in enumerate(x) if solver.value(v)} if status in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None
        if out is not None: assert self.valid(out)
        row=dict(seed=seed,r=len(r),f=len(f),pairs=pairs,triples=triples,
                 r_hash=digest(r),f_hash=digest(f),start_hash=digest(a),status=solver.status_name(status),
                 bound=float(solver.best_objective_bound)+len(kept),
                 size=len(out) if out is not None else None,restore=out==a if out is not None else None,
                 build_seconds=build,seconds=time.monotonic()-start)
        log('exchange',**row)
        return out,row

def region_removal(sp,a,rng,codim):
    # Alternate dense forms with coordinate-aligned subspaces. Both use the
    # exact projected pair condition for the full boundary, not a hitting set.
    aligned=bool(rng.integers(0,2))
    while True:
        if aligned:
            cols=rng.choice(sp.n,codim,replace=False)
            forms=np.eye(sp.n,dtype=np.int32)[cols]
        else: forms=rng.integers(0,3,(codim,sp.n),dtype=np.int32)
        vals=(sp.v@forms.T)%3
        if len(np.unique(vals,axis=0))==3**codim: break
    offset=rng.integers(0,3,codim); powers=3**np.arange(codim-1,-1,-1)
    inside=np.flatnonzero(np.all(vals==offset,axis=1)); aa=np.array(sorted(a))
    frequencies=np.bincount(vals[aa]@powers,minlength=3**codim)
    partners=((-vals[aa]-offset)%3)@powers
    r=set(map(int,aa[frequencies[partners]>0]))
    return r,dict(codim=codim,aligned=aligned,forms=forms.tolist(),offset=offset.tolist(),region_hash=digest(inside))

def orbit_model(sp,kind):
    neg=((-sp.v)%3)@sp.p
    perm=np.arange(sp.n)
    if kind=='neg-swap': perm[[0,1]]=perm[[1,0]]
    if kind=='neg-double-swap':
        perm[[0,1]]=perm[[1,0]]; perm[[2,3]]=perm[[3,2]]
    if kind=='neg-cycle4': perm[:4]=[1,2,3,0]
    pm=sp.v[:,perm]@sp.p
    mapping=np.full(sp.m,-1,dtype=np.int32); orbits=[]
    for u in range(sp.m):
        if mapping[u]>=0: continue
        todo=[u]; orb={u}
        while todo:
            v=todo.pop()
            for w in (int(neg[v]),int(pm[v])):
                if w not in orb: orb.add(w); todo.append(w)
        mapping[list(orb)]=len(orbits); orbits.append(orb)
    model=cp_model.CpModel(); x=[model.new_bool_var(str(i)) for i in range(len(orbits))]
    weights=[len(o) for o in orbits]; constraints=set()
    def add_line(a,b,c):
        q=tuple(sorted(set((int(mapping[a]),int(mapping[b]),int(mapping[c])))))
        if q in constraints or len(constraints)>=650000: return
        constraints.add(q)
        if len(q)==1: model.add(x[q[0]]==0)
        elif len(q)==2: model.add_at_most_one(x[q[0]],x[q[1]])
        else: model.add_bool_or([x[i].Not() for i in q])
    # Self-orbit triples and coordinate-parallel lines from the beginning.
    for orb in orbits:
        for a,b in itertools.combinations(sorted(orb),2):
            if int(sp.t[a,b]) in orb: add_line(a,b,int(sp.t[a,b]))
    for d in range(sp.n):
        for a in np.flatnonzero(sp.v[:,d]==0): add_line(int(a),int(a+sp.p[d]),int(a+2*sp.p[d]))
    model.maximize(sum(w*v for w,v in zip(weights,x)))
    return model,x,orbits,mapping,constraints,add_line

def symmetric(sp,kind,seconds,seed,initial=None,goal=None):
    start=time.monotonic(); model,x,orbits,mapping,cons,add_line=orbit_model(sp,kind)
    log('symmetric_model',kind=kind,n=sp.n,orbits=len(orbits),initial_constraints=len(cons))
    best=set(); global_bound=sp.m; iteration=0; initial=set(initial) if initial is not None else set()
    hint=[int(o<=initial) for o in orbits]
    hintcap=set().union(*(o for o,h in zip(orbits,hint) if h)) if any(hint) else set()
    if hintcap and sp.valid(hintcap): best=hintcap
    for v,h in zip(x,hint): model.add_hint(v,h)
    while time.monotonic()-start<seconds:
        iteration+=1; solver=cp_model.CpSolver(); solver.parameters.num_search_workers=1
        solver.parameters.random_seed=seed+iteration
        solver.parameters.max_time_in_seconds=min(20,max(.01,seconds-(time.monotonic()-start)))
        status=solver.solve(model); global_bound=min(global_bound,solver.best_objective_bound) if status!=cp_model.UNKNOWN else global_bound
        if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):
            log('symmetric_solve',kind=kind,iteration=iteration,status=solver.status_name(status),bound=global_bound,best=len(best),constraints=len(cons))
            if status==cp_model.INFEASIBLE: break
            continue
        selected={i for i,v in enumerate(x) if solver.value(v)}
        a=set().union(*(orbits[i] for i in selected)) if selected else set()
        aa=np.array(sorted(a),dtype=np.int32); in_a=np.zeros(sp.m,bool); in_a[aa]=True
        old=len(cons)
        for i,u in enumerate(aa):
            bb=aa[i+1:]; cc=sp.t[u,bb]
            for j in np.flatnonzero(in_a[cc]&(cc>bb)): add_line(int(u),int(bb[j]),int(cc[j]))
        valid=len(cons)==old
        if valid and len(a)>len(best):
            assert sp.valid(a); best=a; sp.save(ROOT/f'sym_{sp.n}_{kind}_{len(best)}.json',best)
        log('symmetric_solve',kind=kind,iteration=iteration,status=solver.status_name(status),relaxation_size=len(a),valid=valid,bound=global_bound,best=len(best),constraints=len(cons),seconds=time.monotonic()-start,rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if valid and (status==cp_model.OPTIMAL or goal and len(best)>=goal): break
        # Cap memory well below 3 GB; preserve a valid relaxation upper bound if separated incompletely.
        if len(cons)>=650000:
            log('symmetric_stop',kind=kind,reason='constraint-memory-cap',constraints=len(cons)); break
        model.clear_hints()
        for i,v in enumerate(x): model.add_hint(v,int(orbits[i]<=best))
        model.add(sum(len(o)*v for o,v in zip(orbits,x))>=len(best))
    log('symmetric_end',kind=kind,n=sp.n,best=len(best),bound=global_bound,iterations=iteration,seconds=time.monotonic()-start)
    return best

def calibrate():
    sp=Space(8); a=set(sp.load(ROOT/'baseline.json')); assert len(a)==512 and sp.valid(a)
    b=a|{int(sp.t[min(a),sorted(a)[1]])}; assert not sp.valid(b); sp.save(ROOT/'broken.json',b)
    rng=np.random.default_rng(20261118)
    out,row=sp.exchange(a-set(rng.choice(sorted(a),5,replace=False)),set(),30,101,exclude=False)
    assert len(out)==512; sp.save(ROOT/'restored512.json',out)
    reflected=set((sp.v[sorted(a)]*np.array([1,1,1,1,1,2,1,1])%3)@sp.p)
    assert sp.canonical(a)==sp.canonical(reflected)
    out,row=sp.exchange(a,a-reflected,45,102,exclude=True)
    assert out is not None and len(out)==512 and out!=a
    log('calibration',name='excluded-refill',valid=True,size=len(out),canonical_same=sp.canonical(out)==sp.canonical(a))
    s4=Space(4)
    # A greedy complete cap provides a deliberately nonmaximal small start.
    cap=set()
    for u in rng.permutation(s4.m):
        if not s4.blocks(cap)[u]: cap.add(int(u))
    cap=set(sorted(cap)[:12])
    out,row=s4.exchange(cap,cap,100,103,exclude=False); assert out is not None and len(out)==20
    s4.save(ROOT/'control20.json',out)
    # Same region generator and refill engine must recover a deleted known point.
    weak=out-{min(out)}; rr,meta=region_removal(s4,weak,rng,2)
    recovered,row=s4.exchange(weak,rr,45,104,exclude=False)
    assert recovered is not None and len(recovered)>=20
    log('calibration_end',all_pass=True)

def walk(stage,seconds,seed,startfile):
    start=time.monotonic(); sp=Space(8)
    if stage=='smaller':
        if (ROOT/'continue-product.json').exists(): startfile='continue-product.json'
        else:
            options=list(ROOT.glob('best-smaller*.json'))
            if options: startfile=max(options,key=lambda f:len(json.loads(f.read_text())['points'])).name
    a=set(sp.load(ROOT/startfile)); original=set(a)
    log('selected_start',stage=stage,file=startfile,size=len(a),hash=digest(a))
    rng=np.random.default_rng(seed); seen={}; labelled={}; calls=0; minblock=sp.m; maxsize=len(a)
    def visit(a):
        nonlocal minblock,maxsize
        raw=digest(a); can=sp.canonical(a); counts=sp.blocks(a); outside=np.ones(sp.m,bool); outside[list(a)]=False
        mn=int(counts[outside].min()); minblock=min(minblock,mn); maxsize=max(maxsize,len(a))
        new=can not in seen
        if len(a)<=512 and stage not in ('plateau','region'):
            bestfile=ROOT/f'best-smaller-{len(a)}.json'
            if not bestfile.exists(): sp.save(bestfile,a)
        if raw not in labelled:
            sp.save(ROOT/'visited'/f'{raw}.json',a); labelled[raw]=set(a)
            vals,cnt=np.unique(counts[outside],return_counts=True)
            log('visit',stage=stage,hash=raw,canonical=can,new_canonical=new,size=len(a),min_block=mn,hist=dict(zip(map(str,vals),map(int,cnt))),distance=len(a^original),labelled=len(labelled),distinct=len(seen)+int(new))
        seen[can]=raw
        return new
    visit(a)
    while time.monotonic()-start<seconds:
        calls+=1; meta={}; force=(); mode='random'
        if stage=='region':
            r,meta=region_removal(sp,a,rng,int(rng.choice([2,3])))
            mode='region'
        elif calls%6==1:
            # The audit's planted alternative is a control, not a new symmetry class.
            d=int(rng.integers(0,8)); b=set((sp.v[sorted(a)]*np.where(np.arange(8)==d,2,1)%3)@sp.p)
            r=a-b; mode='coordinate-flip'
        elif calls%3==0:
            counts=sp.blocks(a); outside=[int(u) for u in np.argsort(counts) if u not in a]
            u=int(rng.choice(outside[:max(16,len(a)//8)])); pairs=[(v,int(sp.t[u,v])) for v in sorted(a) if int(sp.t[u,v]) in a and v<int(sp.t[u,v])]
            r={p[int(rng.integers(0,2))] for p in pairs}
            # add slack so a one-blocker 448 start can cross a plateau
            extra=int(rng.choice([8,32,96,160]))
            r.update(map(int,rng.choice(sorted(a-r),min(extra,len(a-r)),replace=False)))
            force=[u]; mode='target'
        else:
            k=min(len(a),int(rng.choice([128,192,256,320,384,416])))
            r=set(map(int,rng.choice(sorted(a),k,replace=False)))
        if not r:
            log('skip',stage=stage,reason='empty-removal',call=calls,mode=mode)
            continue
        f=sp.freed(a-r)
        log('neighbourhood',stage=stage,call=calls,mode=mode,r=len(r),f=len(f),**meta)
        # Region boundary often removes all of the cap; run those as a real full model,
        # but bound model size to fit this shared machine.
        if len(f)>2200:
            log('skip',stage=stage,reason='candidate-memory-cap',f=len(f),r=len(r));
            if stage=='region' and calls>=24: break
            continue
        limit=min(35 if stage!='region' else 90,seconds-(time.monotonic()-start))
        if limit<=0: break
        out,row=sp.exchange(a,r,limit,seed+calls,exclude=True,tabu=list(labelled.values())[-40:],force=force)
        if out is not None and len(out)>=len(a):
            fresh=visit(out)
            if len(out)>len(a) or fresh: a=out
            if len(out)>512:
                sp.save(ROOT/'candidate513.json',out); break
        if calls%15==0: log('progress',stage=stage,calls=calls,distinct=len(seen),labelled=len(labelled),min_block=minblock,best=maxsize,seconds=time.monotonic()-start)
    log('walk_end',stage=stage,calls=calls,distinct=len(seen),labelled=len(labelled),min_block=minblock,best=maxsize,seconds=time.monotonic()-start)

if __name__=='__main__':
    log('process_start',argv=sys.argv[1:],pid=os.getpid())
    if sys.argv[1]=='calibrate': calibrate()
    elif sys.argv[1]=='walk': walk(sys.argv[2],float(sys.argv[3]),int(sys.argv[4]),sys.argv[5])
    elif sys.argv[1]=='symmetric':
        sp=Space(int(sys.argv[2])); initial=sp.load(ROOT/'baseline.json') if sp.n==8 else []
        symmetric(sp,sys.argv[3],float(sys.argv[4]),int(sys.argv[5]),initial=initial)
    log('process_end',exit_status=0,max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime)
