"""Full line-orbit constraints for signed coordinate stabilizer subgroups."""
import runpy,pathlib,sys,time,itertools,json,resource
P=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(P/'search.py')); np=m['np']; cp=m['cp_model']; log=m['log']; pynauty=m['pynauty']

def generators(sp,a):
    a=np.array(sorted(a)); k=len(a); adj={i:[] for i in range(k+4*sp.n)}
    for d in range(sp.n):
        c=k+4*d
        for t in range(3):
            u=c+1+t; adj[c].append(u); adj[u].append(c)
        for i,t in enumerate(sp.v[a,d]):
            u=c+1+int(t); adj[i].append(u); adj[u].append(i)
    colors=[set(range(k)),{k+4*d for d in range(sp.n)}, {k+4*d+1 for d in range(sp.n)}, {k+4*d+t for d in range(sp.n) for t in (2,3)}]
    g=pynauty.Graph(k+4*sp.n,adjacency_dict=adj,vertex_coloring=colors)
    perms,size,exp,orbs,num=pynauty.autgrp(g); maps=[]; descriptions=[]
    for perm in perms:
        v=np.zeros_like(sp.v); desc=[]
        for d in range(sp.n):
            target=(perm[k+4*d]-k)//4
            trit=[perm[k+4*d+1+t]-(k+4*target+1) for t in range(3)]
            assert trit[0]==0 and sorted(trit)==[0,1,2]
            v[:,target]=np.array(trit)[sp.v[:,d]]; desc.append([d,target,trit])
        transform=v@sp.p
        assert set(transform[a])==set(a)
        maps.append(transform); descriptions.append(desc)
    log('automorphisms',n=sp.n,generators=len(maps),order_mantissa=size,order_exponent=exp,descriptions=descriptions)
    return maps

def run(n,choice,seconds,seed,calibrate=False,full_hint=False):
    st=time.monotonic(); sp=m['Space'](n)
    baseline=set(sp.load(P/('baseline.json' if n==8 else 'control20.json')))
    maps=generators(sp,baseline)
    neg=((-sp.v)%3)@sp.p
    if choice=='neg': maps=[neg]
    elif choice=='few': maps=[neg]+maps[:2]
    elif choice=='all': maps=[neg]+maps
    elif choice=='half': maps=[neg]+maps[:max(1,len(maps)//2)]
    parent=np.arange(sp.m)
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return int(i)
    for transform in maps:
        for i,j in enumerate(transform): parent[find(i)]=find(int(j))
    roots=[find(i) for i in range(sp.m)]; unique=sorted(set(roots)); pos={u:i for i,u in enumerate(unique)}
    om=np.array([pos[i] for i in roots],dtype=np.int32); k=len(unique)
    orbits=[set(np.flatnonzero(om==i)) for i in range(k)]
    log('exact_model_start',choice=choice,n=n,orbits=k,maps=len(maps))
    # Enumerate every affine line exactly once, then identify its orbit-variable set.
    codes=set()
    for a in range(sp.m):
        b=np.arange(a+1,sp.m,dtype=np.int32); c=sp.t[a,b]; sel=c>b; b=b[sel]; c=c[sel]
        triple=np.sort(np.column_stack((np.full(len(b),om[a]),om[b],om[c])),axis=1).astype(np.int64)
        codes.update(map(int,(triple[:,0]*k+triple[:,1])*k+triple[:,2]))
    model=cp.CpModel(); x=[model.new_bool_var(str(i)) for i in range(k)]
    for code in sorted(codes):
        c=code%k; code//=k; b=code%k; a=code//k
        q=sorted(set((a,b,c)))
        model.add_bool_or([x[i].Not() for i in q])
    del codes
    obj=sum(len(o)*v for o,v in zip(orbits,x)); model.maximize(obj)
    weak=baseline-set(next(o for o in orbits if o<=baseline))
    assert len(weak)<len(baseline) and sp.valid(weak)
    hint=baseline if n==8 and (choice=='half' or full_hint) and not calibrate else weak
    for o,v in zip(orbits,x): model.add_hint(v,int(o<=hint))
    if n==8 and (choice=='half' or full_hint) and not calibrate: model.add(obj>=len(baseline))
    log('exact_model_built',choice=choice,n=n,orbits=k,constraints=len(model.proto.constraints),seconds=time.monotonic()-st,weak_size=len(weak),hint_size=len(hint))
    solver=cp.CpSolver(); solver.parameters.num_search_workers=1; solver.parameters.random_seed=seed
    solver.parameters.max_time_in_seconds=max(.01,seconds-(time.monotonic()-st))
    class Progress(cp.CpSolverSolutionCallback):
        def __init__(self): super().__init__(); self.best=0
        def on_solution_callback(self):
            out=set().union(*(o for o,v in zip(orbits,x) if self.value(v)))
            assert sp.valid(out)
            if len(out)>self.best:
                self.best=len(out); sp.save(P/f'exact_{n}_{choice}_{len(out)}.json',out)
                log('exact_incumbent',choice=choice,n=n,size=len(out),bound=self.best_objective_bound,seconds=time.monotonic()-st)
            if calibrate and len(out)>=len(baseline): self.stop_search()
    cb=Progress(); status=solver.solve(model,cb)
    best=max(cb.best,len(weak))
    log('exact_end',choice=choice,n=n,status=solver.status_name(status),best=best,bound=solver.best_objective_bound if status in (cp.OPTIMAL,cp.FEASIBLE) else None,seconds=time.monotonic()-st)
    if calibrate: assert cb.best>=len(baseline)

if __name__=='__main__':
    log('process_start',argv=sys.argv[1:])
    run(int(sys.argv[1]),sys.argv[2],float(sys.argv[3]),int(sys.argv[4]),'control' in sys.argv,full_hint='full-hint' in sys.argv)
    log('process_end',exit_status=0,max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime)
