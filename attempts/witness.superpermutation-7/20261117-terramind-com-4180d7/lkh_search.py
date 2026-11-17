"""Independent overlap-path encoding and recorded LKH runs; no solver source included."""
import collections, datetime, hashlib, itertools, json, math, os, pathlib, random, subprocess, sys, time
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]
LKH = ROOT / 'lkh-download/repo/LKH'

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def emit(file, **row):
    row['utc'] = utc()
    with open(file, 'a') as f: f.write(json.dumps(row) + '\n')
    print(json.dumps(row), flush=True)
def path(word, n): return [word[i:i+n] for i in range(len(word)-n+1) if len(set(word[i:i+n])) == n]
def weight(a,b):
    return next(k for k in range(1,len(a)+1) if a[k:] == b[:-k])
def word(p): return p[0] + ''.join(b[-weight(a,b):] for a,b in zip(p,p[1:]))
def valid(w,n): return set(path(w,n)) == {''.join(p) for p in itertools.permutations('123456789'[:n])}
def stats(p): return dict(collections.Counter(weight(a,b) for a,b in zip(p,p[1:])))
def diagnose(w, dest):
    dest.write_text(json.dumps({'word':w}))
    r = subprocess.run(['bun','frontier','diagnose',str(dest.relative_to(REPO)), '--problem','witness.superpermutation-7'],cwd=REPO,capture_output=True,text=True)
    dest.with_suffix('.diagnose.log').write_text(r.stdout+r.stderr)
    assert 'valid:    yes' in r.stdout, r.stdout
    return r.returncode

def solve(p, wd, seed, cap, full=False, trials=5000, runs=5, candidates=20):
    wd.mkdir(parents=True,exist_ok=True)
    n=len(p[0]); m=len(p)+(1 if full else -1)
    # Dummy node: zero incoming/outgoing costs for open path; merged ends otherwise.
    starts = [p[0]]+p if full else [p[0]]+p[1:-1]
    ends = [p[-1]]+p if full else [p[-1]]+p[1:-1]
    aa=np.array([[int(c) for c in a] for a in starts],dtype=np.uint8)
    bb=np.array([[int(c) for c in b] for b in ends],dtype=np.uint8)
    cost=np.full((m,m),n,dtype=np.uint8)
    for k in range(n-1,0,-1):
        match=np.ones((m,m),dtype=bool)
        for j in range(n-k): match &= aa[:,k+j,None] == bb[None,:,j]
        cost[match]=k
    np.fill_diagonal(cost,0)
    if full: cost[0,:]=0; cost[:,0]=0
    prob=wd/'problem.atsp'; init=wd/'initial.tour'; out=wd/'result.tour'; par=wd/'run.par'
    with prob.open('w') as f:
        f.write(f'NAME: overlap\nTYPE: ATSP\nDIMENSION: {m}\nEDGE_WEIGHT_TYPE: EXPLICIT\nEDGE_WEIGHT_FORMAT: FULL_MATRIX\nEDGE_WEIGHT_SECTION\n')
        for row in cost: f.write(' '.join(map(str,row))+'\n')
        f.write('EOF\n')
    del cost,match
    init.write_text(f'TYPE: TOUR\nDIMENSION: {m}\nTOUR_SECTION\n'+'\n'.join(map(str,range(1,m+1)))+'\n-1\nEOF\n')
    if out.exists(): out.unlink()
    par.write_text(f'PROBLEM_FILE = {prob}\nINITIAL_TOUR_FILE = {init}\nOUTPUT_TOUR_FILE = {out}\nRUNS = {runs}\nMAX_TRIALS = {trials}\nMAX_CANDIDATES = {candidates}\nMOVE_TYPE = 5\nTIME_LIMIT = {max(1,int(cap-2))}\nSEED = {seed}\nTRACE_LEVEL = 1\n')
    t=time.monotonic(); start=utc(); timed=False
    with (wd/'stdout.log').open('w') as f:
        proc=subprocess.Popen([str(LKH),str(par)],stdout=f,stderr=subprocess.STDOUT)
        try: rc=proc.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            timed=True;proc.terminate()
            try: rc=proc.wait(timeout=1)
            except subprocess.TimeoutExpired: proc.kill();rc=proc.wait()
    result=None
    if out.exists():
        lines=out.read_text().split('TOUR_SECTION')[1].split(); tour=[]
        for x in lines:
            if x=='-1':break
            tour.append(int(x)-1)
        assert sorted(tour)==list(range(m))
        z=tour.index(0); tour=tour[z:]+tour[:z]
        result=[p[i-1] for i in tour[1:]] if full else [p[0]]+[starts[i] for i in tour[1:]]+[p[-1]]
        assert sorted(result)==sorted(p)
        if not full: assert result[0]==p[0] and result[-1]==p[-1]
    row=dict(start=start,end=utc(),seconds=time.monotonic()-t,rc=rc,timeout=timed,status=('timeout' if timed else 'feasible_only' if result else 'error'),seed=seed,full=full,n=n,nodes=m,runs=runs,trials=trials,candidates=candidates,move=5,cap=cap,word_length=len(word(result)) if result else None)
    (wd/'status.json').write_text(json.dumps(row))
    return result,row

def calibration():
    log=ROOT/'calibration-lkh.jsonl'
    w=json.loads((ROOT/'baseline.json').read_text())['word'];p=path(w,7)
    assert valid(w,7) and not valid(w[:3000]+w[3001:],7) and word(p)==w
    emit(log,event='checker_control',accepted=True,broken_rejected=True,roundtrip=True,weights=stats(p))
    for n,target,cap in [(5,153,60),(6,872,220)]:
        for seed in [1,2,3]:
            p=[''.join(q) for q in itertools.permutations('123456'[:n])]
            q,row=solve(p,ROOT/f'cal-n{n}-s{seed}',seed,cap,full=True,trials=5000 if n==5 else 20000,runs=5 if n==5 else 10)
            ok=q is not None and valid(word(q),n) and len(word(q))==target
            emit(log,event='optimum_control',target=target,passed=ok,**row)
            if not ok:return False
    return True

def search(deadline, rng_seed=20261118):
    log=ROOT/'lkh.jsonl'; rng=random.Random(rng_seed)
    paths=[path(json.loads((ROOT/f).read_text())['word'],7) for f in ['baseline.json','sol2.json']]
    seen=set(); best=5905;iteration=0
    # Full ATSP long runs from both distinct published paths, then fixed-end windows.
    while time.time()<deadline-10:
        full=iteration<2;which=iteration%2;p=paths[which]
        if full: lo,hi=0,len(p)
        else:
            heavy=[i for i in range(len(p)-1) if weight(p[i],p[i+1])>=3]
            anchor=rng.choice(heavy);size=rng.choice([1000,1500,2000,2500,3000])
            lo=max(0,min(len(p)-size,anchor-rng.randrange(size)));hi=lo+size
        seed=rng.randrange(1,2**30);cap=min(600 if full else 120,deadline-time.time()-3)
        if cap<5:break
        q,row=solve(p[lo:hi],ROOT/('full'+str(which) if full else 'segment'+str(which)),seed,cap,full=full,trials=20000,runs=10,candidates=30)
        if q:
            candidate=p[:lo]+q+p[hi:];w=word(candidate);assert valid(w,7)
            digest=hashlib.sha256(w.encode()).hexdigest();seen.add(digest)
            # Every returned tour is diagnosed immediately, even ties or worse.
            rc=diagnose(w,ROOT/f'latest-{which}.json')
            old=len(word(p));new=len(w)
            if new<=old:paths[which]=candidate
            if new<best:
                best=new;diagnose(w,ROOT/f'best-{new}.json')
            row.update(old=old,returned_length=new,accepted=new<=old,heavy=sum(v for k,v in stats(candidate).items() if k>=3),hash=digest,distinct_words=len(seen),distance=sum(a!=b for a,b in zip(p,candidate)),diagnose_rc=rc)
        emit(log,event='tour',iteration=iteration,start_word=which+1,lo=lo,hi=hi,best=best,**row)
        iteration+=1
    emit(log,event='end',best=best,iterations=iteration,distinct_words=len(seen))

if __name__=='__main__':
    os.environ['OPENBLAS_NUM_THREADS']='1'
    if sys.argv[1]=='calibrate':sys.exit(0 if calibration() else 2)
    search(float(sys.argv[1]))
