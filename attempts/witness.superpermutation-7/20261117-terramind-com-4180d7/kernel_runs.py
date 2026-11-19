"""Recorded external PermutationChains calls with file-based results and exit instrumentation."""
import datetime, hashlib, json, os, pathlib, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[2]
K='4666446666-6666466636666-666646646666-666646646666-6666366646666-6666446664'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def emit(**row):
    row['utc']=utc()
    with (ROOT/'kernel.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    print(json.dumps(row),flush=True)
def score(k):return sum(int(c) for c in k if c!='-')-5*len(k)
def run(k,options,cap,label,n=7):
    wd=ROOT/'pc-runs'/label;wd.mkdir(parents=True,exist_ok=True)
    cache=ROOT/'pc-runs/baseline5905/IntersectionFlags7.dat'
    if n==7 and cache.exists() and not (wd/cache.name).exists():
        (wd/cache.name).symlink_to(cache)
    start=utc();t=time.monotonic();timed=False
    with (wd/'stdout.log').open('w') as out:
        p=subprocess.Popen([str(ROOT/'PC-audit'),str(n)]+(['nsk'+k] if k else [])+options,cwd=wd,stdout=out,stderr=subprocess.STDOUT)
        try:rc=p.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            timed=True;p.terminate()
            try:rc=p.wait(timeout=1)
            except subprocess.TimeoutExpired:p.kill();rc=p.wait()
    meta=json.loads((wd/'status.json').read_text()) if (wd/'status.json').exists() else None
    words=[]
    for file in wd.glob(f'{n}_*.txt'):
        if 'twoCycles' in file.name:continue
        for line in file.read_text().splitlines():
            w=line.strip()
            if w and set(w)<=set('123456789'[:n]):words.append(w)
    checked=[]
    for i,w in enumerate(words):
        # Independent exact coverage check, plus Frontier for every n=7 result.
        windows={w[j:j+n] for j in range(len(w)-n+1) if len(set(w[j:j+n]))==n}
        import math
        assert len(windows)==math.factorial(n)
        dest=wd/f'word{i}.json';dest.write_text(json.dumps({'word':w}))
        if n==7:
            r=subprocess.run(['bun','frontier','diagnose',str(dest.relative_to(REPO)),'--problem','witness.superpermutation-7'],cwd=REPO,capture_output=True,text=True)
            (wd/f'word{i}.diagnose.log').write_text(r.stdout+r.stderr)
            assert 'valid:    yes' in r.stdout
        checked.append({'length':len(w),'sha256':hashlib.sha256(w.encode()).hexdigest()})
    status='timeout' if timed else 'error' if rc else 'completed_with_solutions' if words else 'completed_no_solution'
    row=dict(event='call',label=label,kernel=k,score=score(k) if k else None,n=n,options=options,cap=cap,start=start,end=utc(),seconds=time.monotonic()-t,rc=rc,timeout=timed,status=status,instrumentation=meta,solutions=checked)
    emit(**row);return row
def calibrate():
    run('',[],30,'n5',5)
    row=run(K,[],60,'baseline5905')
    assert any(w['length']==5905 for w in row['solutions'])
    # These are precisely the symmetry flags used for the published 5906 words.
    k='666466646646664666'
    row=run(k,['symmPairs','fullSymm'],900,'positive5906')
    ok=any(w['length']==5906 for w in row['solutions'])
    emit(event='positive_control',passed=ok)
    return ok

def search(deadline):
    import random,collections
    rng=random.Random(7132026);known=json.loads((ROOT/'seeds.json').read_text())
    unresolved=json.loads((ROOT/'unresolved.json').read_text())
    # Long, completely recorded runs for all four historically unresolved kernels.
    for i,k in enumerate(unresolved):
        cap=min(600,deadline-time.time()-3)
        if cap<5:break
        run(k,[],cap,f'unresolved-{i}')
    seen=set();batches=0;totals=collections.Counter()
    while time.time()<deadline-5:
        # Cycle all eight published starts before choosing a random seed.
        k=known[batches%len(known)]
        # Keep at least one digit on each side; suffix state is from this exact seed.
        cuts=[i for i in range(1,len(k)) if k[i-1]!='-' and k[i]!='-']
        a=rng.choice([i for i in cuts if i<=max(1,len(k)//3)])
        b=rng.choice([i for i in cuts if i>=2*len(k)//3 and i>a])
        limit=(b-a)+rng.choice([15,20,25,30,35]);seed=rng.randrange(1,2**31)
        cap=min(15,deadline-time.time()-2);t=time.monotonic();start=utc();timed=False
        args=[str(ROOT/'bridge'),str(seed),k,str(a),str(b),str(limit),'20','20000000','0','200']
        proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:out,err=proc.communicate(timeout=cap)
        except subprocess.TimeoutExpired:
            timed=True;proc.kill();out,err=proc.communicate()
        (ROOT/'bridge-last.stdout').write_text(out);(ROOT/'bridge-last.stderr').write_text(err)
        emitted=out.splitlines();fresh=[s for s in emitted if s not in seen]
        seen.update(emitted)
        # The generator's structured node counter is separate from completion classification.
        node_status=json.loads(err.splitlines()[-1]) if err.strip().startswith('{') else None
        emit(event='bridge',batch=batches,seed=seed,base=k,a=a,b=b,max_middle=limit,node_budget=20000000,start=start,end=utc(),seconds=time.monotonic()-t,rc=proc.returncode,timeout=timed,node_status=node_status,emissions=len(emitted),fresh=len(fresh),distinct_kernels=len(seen))
        for candidate in fresh:
            if time.time()>=deadline-3:break
            sc=score(candidate);totals[sc]+=1
            opts=['symmPairs','fullSymm'] if candidate==candidate[::-1] else []
            row=run(candidate,opts,min(120,deadline-time.time()-2),f'bridge-{batches}-{totals[sc]}')
            if any(w['length']<5905 for w in row['solutions']):
                emit(event='improvement',label=row['label'])
        batches+=1
    emit(event='end',batches=batches,distinct_kernels=len(seen),tested_per_score=dict(totals))

if __name__=='__main__':
    if len(sys.argv)==1:sys.exit(0 if calibrate() else 2)
    search(float(sys.argv[1]))
