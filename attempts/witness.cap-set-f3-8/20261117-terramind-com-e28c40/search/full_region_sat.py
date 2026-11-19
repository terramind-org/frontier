"""Full-space exact cap feasibility via all line clauses and cardinality networks."""
import runpy,pathlib,time,threading,sys,resource
P=pathlib.Path(__file__).resolve().parent
m=runpy.run_path(str(P/'search.py')); np=m['np']; log=m['log']
from pysat.solvers import Solver
from pysat.card import CardEnc,EncType

def run(n,target,seconds,seed_hint):
    start=time.monotonic(); sp=m['Space'](n)
    solver=Solver(name='g4'); line_count=0
    for a in range(sp.m):
        b=np.arange(a+1,sp.m,dtype=np.int32); c=sp.t[a,b]; sel=c>b
        solver.append_formula([[-a-1,-int(bb)-1,-int(cc)-1] for bb,cc in zip(b[sel],c[sel])])
        line_count+=int(np.count_nonzero(sel))
        if a%1000==0: log('sat_build',n=n,target=target,point=a,lines=line_count,seconds=time.monotonic()-start,max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    assert line_count==sp.m*(sp.m-1)//6
    cardinal=CardEnc.atleast(lits=list(range(1,sp.m+1)),bound=target,encoding=EncType.cardnetwrk)
    solver.append_formula(cardinal.clauses); aux=cardinal.nv-sp.m; card_clauses=len(cardinal.clauses)
    del cardinal
    hint=set(sp.load(P/seed_hint))
    if n==4: hint=set(sorted(hint)[:12])
    assert sp.valid(hint)
    solver.set_phases([u+1 if u in hint else -u-1 for u in range(sp.m)])
    log('sat_model',n=n,target=target,lines=line_count,cardinality_clauses=card_clauses,aux_vars=aux,hint_size=len(hint),seconds=time.monotonic()-start,max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    remaining=max(.01,seconds-(time.monotonic()-start))
    timer=threading.Timer(remaining,solver.interrupt); timer.daemon=True; timer.start()
    try: status=solver.solve_limited(expect_interrupt=True)
    finally: timer.cancel()
    cap=None
    if status is True:
        cap={u-1 for u in solver.get_model() if 1<=u<=sp.m}
        assert len(cap)>=target and sp.valid(cap)
        sp.save(P/f'sat_region_{n}_{len(cap)}.json',cap)
    stats=solver.accum_stats(); solver.delete()
    log('sat_end',n=n,target=target,status='SAT' if status is True else 'UNSAT' if status is False else 'UNKNOWN',size=len(cap) if cap is not None else None,seconds=time.monotonic()-start,stats=stats,max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return cap

if __name__=='__main__':
    log('process_start',argv=sys.argv[1:])
    if sys.argv[1]=='control':
        out=run(4,20,60,'control20.json'); assert out is not None and len(out)>=20
    else: run(8,513,float(sys.argv[1]),'baseline.json')
    log('process_end',exit_status=0,max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
